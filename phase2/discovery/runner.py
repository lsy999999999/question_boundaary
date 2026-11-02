"""Resumable, auditable experiment orchestration."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from collections import Counter
from dataclasses import asdict
from pathlib import Path

import numpy as np

from .llm import make_prompt, parse_decision
from .models import Model, diagnostics, disagreement_action, fit, select_cv
from .world import INITIAL_ACTIONS, TRAIN_ACTIONS, Observation, World, catalog, control

AGENT_METHODS = ("plain", "retrieval", "structured", "no_active", "shuffled")
BASELINE_METHODS = ("state_fixed", "history_cv")
FIXED_SEQUENCE = ("prbs", "ramp_reverse", "double_pulse", "alternating")


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))
    temporary.replace(path)


class State:
    def __init__(self, task, root):
        self.task = task
        self.root = root
        self.world = World(task)
        self.round_index = 0
        self.decisions = []
        self.invalid_outputs = 0
        self.calls = []
        self.start_time = time.time()
        checkpoint = root / "checkpoint.json"
        if checkpoint.exists():
            data = json.loads(checkpoint.read_text())
            self.round_index = data["round_index"]
            self.decisions = data["decisions"]
            self.invalid_outputs = data["invalid_outputs"]
            self.calls = data["calls"]
            self.start_time = data["start_time"]
            self.observations = [Observation(o["action"], np.array(o["t"]), np.array(o["u"]), np.array(o["y"]), o["repeat"]) for o in data["observations"]]
            m = data["model"]
            self.model = Model(m["representation"], np.array(m["coefficients"]), m["ridge"], m["cv_nmse"])
        else:
            self.observations = [self.world.experiment(action) for action in INITIAL_ACTIONS]
            self.model = fit(self.observations, "state")
            self.checkpoint()

    def available_actions(self):
        counts = Counter(o.action for o in self.observations)
        return [a for a in TRAIN_ACTIONS if counts[a] < 2]

    def checkpoint(self):
        write_json(self.root / "checkpoint.json", {
            "task_id": self.task.task_id, "round_index": self.round_index,
            "decisions": self.decisions, "invalid_outputs": self.invalid_outputs,
            "calls": self.calls, "start_time": self.start_time,
            "model": {"representation": self.model.representation, "coefficients": self.model.coefficients.tolist(), "ridge": self.model.ridge, "cv_nmse": self.model.cv_nmse},
            "observations": [{"action": o.action, "repeat": o.repeat, "t": o.t.tolist(), "u": o.u.tolist(), "y": o.y.tolist()} for o in self.observations],
        })

    def step(self, decision, call=None, errors=None, forced_action=None):
        step_root = self.root / f"round_{self.round_index:02d}"
        step_root.mkdir(parents=True, exist_ok=True)
        write_json(step_root / "decision.json", {"time_ns": time.time_ns(), "decision": decision, "parse_errors": errors or [], "generation": call})
        candidate = fit(self.observations, decision["representation"])
        action = forced_action or decision["experiment"]
        repeats = sum(o.action == action for o in self.observations)
        t = self.observations[0].t
        prediction = candidate.rollout(t, control(action, t))
        forecast = {"time_ns": time.time_ns(), "action": action, "prediction": prediction.tolist(), "model": candidate.public()}
        forecast_hash = hashlib.sha256(json.dumps(forecast, sort_keys=True).encode()).hexdigest()
        forecast["sha256"] = forecast_hash
        # This file is durably written BEFORE the next simulator call.
        write_json(step_root / "forecast_before_observation.json", forecast)
        with (step_root / "forecast_before_observation.json").open("rb") as f:
            os.fsync(f.fileno())
        observation = self.world.experiment(action, repeats)
        observed = {"time_ns": time.time_ns(), "forecast_sha256": forecast_hash, "summary": observation.public_summary(), "forecast_mse": float(np.mean((prediction - observation.y)**2))}
        np.savez_compressed(step_root / "observation.npz", t=observation.t, u=observation.u, y=observation.y)
        write_json(step_root / "observation.json", observed)
        self.observations.append(observation)
        self.model = fit(self.observations, decision["representation"])
        self.decisions.append({**decision, "executed_experiment": action, "new_forecast_mse": observed["forecast_mse"], "updated_cv_nmse": self.model.cv_nmse})
        self.invalid_outputs += int(bool(errors))
        if call:
            self.calls.append({k: v for k, v in call.items() if k != "text"})
        self.round_index += 1
        self.checkpoint()

    def finish(self, method, decision=None, call=None, errors=None):
        if decision is not None:
            self.model = fit(self.observations, decision["representation"])
            write_json(self.root / "final_decision.json", {"time_ns": time.time_ns(), "decision": decision, "parse_errors": errors or [], "generation": call})
            self.invalid_outputs += int(bool(errors))
            if call:
                self.calls.append({k: v for k, v in call.items() if k != "text"})
        committed = {"time_ns": time.time_ns(), "model": self.model.public()}
        write_json(self.root / "final_model_before_evaluation.json", committed)
        evaluation = self.world.evaluate(self.model)
        result = {
            "task_id": self.task.task_id, "split": self.task.split,
            "family": self.task.family, "seed": self.task.seed, "method": method,
            "n_experiments": len(self.observations), "rounds": self.round_index,
            "model": self.model.public(), "test": evaluation,
            "accepted_by_common_cv_rule": self.model.cv_nmse < 0.05,
            "self_accept": decision.get("accept") if decision else None,
            "invalid_outputs": self.invalid_outputs,
            "generation_calls": len(self.calls),
            "input_tokens": sum(c["input_tokens"] for c in self.calls),
            "output_tokens": sum(c["output_tokens"] for c in self.calls),
            "generation_seconds_amortized": sum(c["amortized_seconds"] for c in self.calls),
            "elapsed_wall_seconds": time.time() - self.start_time,
            "selected_actions": [d["executed_experiment"] for d in self.decisions],
            "selected_representations": [d["representation"] for d in self.decisions] + [self.model.representation],
            "peak_gpu_allocated_gb": max([c["peak_gpu_allocated_gb"] for c in self.calls] or [0.0]),
            "peak_process_ram_gb": max([c.get("peak_process_ram_gb", 0.0) for c in self.calls] or [0.0]),
            "inference_backend": self.calls[0].get("backend", "cuda") if self.calls else "numerical_baseline",
            "evaluation_after_commit_ns": time.time_ns(),
        }
        write_json(self.root / "result.json", result)
        return result


def task_root(root, method, task):
    return root / method / task.task_id


def run_baselines(tasks, root, methods, rounds):
    for method in methods:
        for task in tasks:
            dest = task_root(root, method, task)
            if (dest / "result.json").exists():
                continue
            state = State(task, dest)
            while state.round_index < rounds:
                if method == "state_fixed":
                    rep = "state"
                    action = FIXED_SEQUENCE[state.round_index]
                else:
                    best, models = select_cv(state.observations)
                    rep = best.representation
                    action = disagreement_action(state.observations, models, state.available_actions(), control)
                state.step({"representation": rep, "experiment": action, "reason": "algorithmic baseline", "prediction": "stored numerical trajectory", "accept": False})
            if method == "history_cv":
                state.model, _ = select_cv(state.observations)
            result = state.finish(method)
            print(json.dumps({"event": "completed", "method": method, "task_id": task.task_id, "family": task.family, "test_nmse": result["test"]["test_nmse"]}), flush=True)


def run_agents(tasks, root, methods, rounds, llm, batch_size):
    # Batch only independent tasks; each task's actions remain sequential.
    for method in methods:
        states = [State(task, task_root(root, method, task)) for task in tasks if not (task_root(root, method, task) / "result.json").exists()]
        for round_index in range(rounds + 1):
            final = round_index == rounds
            pending = [s for s in states if s.round_index == round_index and not (s.root / "result.json").exists()]
            for start in range(0, len(pending), batch_size):
                batch = pending[start:start + batch_size]
                prompts = [make_prompt(s, method, final) for s in batch]
                responses = llm.generate(prompts)
                for state, prompt, response in zip(batch, prompts, responses):
                    attempt = f"request_{round_index:02d}_{time.time_ns()}.json"
                    write_json(state.root / attempt, {"messages": prompt, "response": response})
                    decision, errors = parse_decision(response["text"], state.available_actions(), state.model.representation, method in ("structured", "no_active", "shuffled"))
                    if final:
                        result = state.finish(method, decision, response, errors)
                        print(json.dumps({"event": "completed", "method": method, "task_id": state.task.task_id, "family": state.task.family, "test_nmse": result["test"]["test_nmse"], "invalid_outputs": state.invalid_outputs}), flush=True)
                    else:
                        forced = FIXED_SEQUENCE[state.round_index] if method == "no_active" else None
                        state.step(decision, response, errors, forced)
                        print(json.dumps({"event": "round", "method": method, "task_id": state.task.task_id, "round": state.round_index, "representation": state.model.representation, "cv_nmse": state.model.cv_nmse, "parse_errors": errors}), flush=True)


def source_hashes():
    root = Path(__file__).resolve().parents[1]
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((root / "discovery").glob("*.py"))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=["dev", "eval"], required=True)
    parser.add_argument("--seeds", default="0,1,2")
    parser.add_argument("--methods", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--rounds", type=int, default=3, choices=[1, 2, 3, 4])
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--max-new-tokens", type=int, default=384)
    parser.add_argument("--backend", choices=["cuda", "cpu-int8", "cpu-fp32"], default="cuda")
    parser.add_argument("--threads", type=int, default=16)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    methods = args.methods.split(",")
    if any(m not in AGENT_METHODS + BASELINE_METHODS for m in methods):
        raise ValueError("Unknown method")
    seeds = [int(s) for s in args.seeds.split(",")]
    tasks = catalog(args.split, seeds)
    manifest = {
        "split": args.split, "seeds": seeds, "rounds": args.rounds,
        "batch_size": args.batch_size, "max_new_tokens": args.max_new_tokens,
        "model": str(args.model), "source_hashes": source_hashes(),
        "backend": args.backend, "threads": args.threads,
        "python": sys.version, "platform": platform.platform(),
        "tasks": [asdict(t) for t in tasks],
        "acceptance_cv_threshold": 0.05, "failure_test_nmse_threshold": 0.1,
        "initial_experiments": list(INITIAL_ACTIONS), "test_actions_hidden_from_agent": True,
        "protocol_version": "v3-evidence-revision", "agent_fits_per_task": 52,
        "card_permutation": "cyclic bundle shift by one for shuffled; same card ids/domains",
    }
    # A different source version cannot silently resume an existing experiment.
    frozen = args.output / "manifest.json"
    if frozen.exists():
        old = json.loads(frozen.read_text())
        for key in ("split", "seeds", "rounds", "source_hashes", "model", "max_new_tokens", "backend", "threads"):
            if old[key] != manifest[key]:
                raise RuntimeError(f"Frozen configuration mismatch: {key}; use a new output directory")
    else:
        write_json(frozen, manifest)
    baselines = [m for m in methods if m in BASELINE_METHODS]
    if baselines:
        run_baselines(tasks, args.output, baselines, args.rounds)
    agents = [m for m in methods if m in AGENT_METHODS]
    if agents:
        if args.model is None:
            raise ValueError("--model is required for real language-model agents")
        from .llm import LocalModel
        llm = LocalModel(args.model, args.max_new_tokens, args.backend, args.threads)
        run_agents(tasks, args.output, agents, args.rounds, llm, args.batch_size)
    print(json.dumps({"event": "worker_complete", "methods": methods, "split": args.split}), flush=True)


if __name__ == "__main__":
    main()
