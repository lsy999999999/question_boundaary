"""Local transformer inference; no paid API or unrestricted tool execution."""
from __future__ import annotations

import json
import time
import resource
import sys

from .models import DESCRIPTIONS

CARDS = [
    {
        "id": "storage", "domain": "electrical / thermal systems",
        "structure": "A storage element carries accumulated past influence into the future; leakage gives a finite relaxation timescale.",
        "conditions": "The stored state must have a measurable predictive consequence after controlling current input and visible state.",
        "failure": "Instantaneous curvature or measurement noise can mimic a poor fit without any storage mechanism.",
    },
    {
        "id": "transport", "domain": "transport and communication",
        "structure": "An effect can arrive after a travel time; a lag can differ from a smooth accumulation of history.",
        "conditions": "Response timing should persist across different input shapes.",
        "failure": "A slow sensor or a distributed relaxation can resemble a pure delay.",
    },
    {
        "id": "saturation", "domain": "population / resource constraints",
        "structure": "Growth and response can weaken at large state magnitudes because of limited capacity.",
        "conditions": "Compare responses across positive and negative amplitudes; determine whether history is necessary in addition to curvature.",
        "failure": "A visually flattening trajectory also occurs in a linear stable system approaching equilibrium.",
    },
    {
        "id": "external_clock", "domain": "seasonal and periodically driven systems",
        "structure": "A shared unobserved driver tied to elapsed time can generate persistent residuals without endogenous memory.",
        "conditions": "Compare different input interventions aligned in elapsed time.",
        "failure": "A decaying impulse response or input-driven oscillation is not sufficient evidence for an independent clock.",
    },
]

SYSTEM = """You are a scientist controlling a black-box simulator. Your task is to revise an executable predictive representation using noisy observations and controlled experiments. Hidden dynamics and independent final test trajectories are unavailable. Choose only from the shared representation grammar; numerical tools fit coefficients and check trajectory-level cross-validation. A representation choice is a constrained modeling operation, not proof of a new physical concept. All experiments reset the system to the same prepared state at elapsed time zero. Explain briefly and make a falsifiable prediction. Return exactly one JSON object, without markdown or text outside it."""


def make_prompt(state, method, final=False):
    from .models import diagnostics
    from .world import TRAIN_ACTIONS
    available = state.available_actions()
    structured = method in ("structured", "no_active")
    data = {
        "task_id": state.task.task_id,
        "round": state.round_index,
        "final_model_selection": final,
        "measurement": {"sample_interval_seconds": 0.05, "horizon_seconds": 12, "noise_std": 0.01},
        "current_diagnostics": diagnostics(state.model, state.observations),
        "recent_observations": [o.public_summary() for o in state.observations[-4:]],
        "prior_decisions": state.decisions[-3:],
        "representations": DESCRIPTIONS,
        "available_experiments": available,
        "experiment_definitions": {
            "positive_pulse": "+1 from 0.5 to 3.5 s; then zero",
            "negative_pulse": "-1 from 1 to 4 s; then zero",
            "step_rest": "+0.65 from 0.5 to 7 s; then zero",
            "double_pulse": "+1.2 at 0.5-2 and 5-6.5 s",
            "alternating": "rapid positive and negative input switches",
            "ramp_reverse": "slow ramp from zero to positive, then negative, then zero",
            "slow_wave": "slow sinusoidal input",
            "prbs": "irregular predetermined positive/negative step input",
        },
        "output_schema": {
            "representation": "one exact representation name",
            "experiment": "one available experiment name, ignored for final selection",
            "reason": "brief evidence-based reason, at most 40 words",
            "prediction": "one qualitative consequence to test, at most 30 words",
            "accept": "boolean: is the model currently adequate for unseen interventions?",
        },
    }
    if method != "plain":
        data["cross_domain_notes"] = CARDS
    if structured:
        data["instruction"] = "Explicitly map a source relation to this target and identify one assumption that might fail. Revise the current representation if observations warrant it. Use a discriminating experiment. Domain similarity alone is insufficient."
        data["output_schema"]["mapping"] = {"source_id": "exactly storage, transport, saturation, external_clock, or none", "target_relation": "at most 25 words", "condition_to_check": "at most 25 words"}
    else:
        data["instruction"] = "Use the observations and available notes to choose a predictive representation and informative experiment."
    if method == "no_active":
        data["instruction"] += " Experiment order is fixed by this ablation; still propose an action, but the scheduler will execute the fixed action."
    if final:
        data["instruction"] += " No more experiments remain; select the final representation using current evidence."
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": json.dumps(data, ensure_ascii=False, allow_nan=False)}]


def parse_decision(text, available, current_rep, structured=False):
    decoder = json.JSONDecoder()
    obj = None
    for i, char in enumerate(text):
        if char == "{":
            try:
                value, _ = decoder.raw_decode(text[i:])
                if isinstance(value, dict) and "representation" in value:
                    obj = value
                    break
            except json.JSONDecodeError:
                pass
    errors = []
    if obj is None:
        obj = {}
        errors.append("unparseable_json")
    rep = obj.get("representation")
    if rep not in DESCRIPTIONS:
        rep = current_rep
        errors.append("invalid_representation")
    action = obj.get("experiment")
    if action not in available:
        action = available[0]
        errors.append("invalid_experiment")
    mapping = obj.get("mapping")
    if structured and (not isinstance(mapping, dict) or not all(k in mapping for k in ("source_id", "target_relation", "condition_to_check"))):
        errors.append("missing_structural_mapping")
    elif structured and mapping.get("source_id") not in {"storage", "transport", "saturation", "external_clock", "none"}:
        errors.append("invalid_mapping_source_id")
    decision = {
        "representation": rep, "experiment": action,
        "reason": str(obj.get("reason", ""))[:600],
        "prediction": str(obj.get("prediction", ""))[:450],
        "accept": obj.get("accept") is True,
        "mapping": mapping if isinstance(mapping, dict) else None,
    }
    return decision, errors


class LocalModel:
    def __init__(self, path, max_new_tokens=384, backend="cuda", threads=16):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.torch = torch
        self.backend = backend
        self.device = "cuda" if backend == "cuda" else "cpu"
        torch.set_num_threads(4 if backend == "cuda" else threads)
        torch.manual_seed(20261031)
        self.tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True, padding_side="left")
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        dtype = torch.bfloat16 if backend == "cuda" else torch.float32
        self.model = AutoModelForCausalLM.from_pretrained(path, local_files_only=True, torch_dtype=dtype, device_map={"": 0 if backend == "cuda" else "cpu"}, attn_implementation="sdpa")
        self.model.eval()
        if backend == "cpu-int8":
            torch.backends.quantized.engine = "x86"
            qconfig = {torch.nn.Linear: torch.ao.quantization.per_channel_dynamic_qconfig, "lm_head": None}
            torch.ao.quantization.quantize_dynamic(self.model, qconfig_spec=qconfig, dtype=torch.qint8, inplace=True)
        self.max_new_tokens = max_new_tokens
        self.path = str(path)

    def generate(self, messages_batch):
        torch = self.torch
        texts = [self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True) for messages in messages_batch]
        tokens = self.tokenizer(texts, padding=True, return_tensors="pt")
        if tokens["input_ids"].shape[1] > 6500:
            raise RuntimeError("Prompt exceeds the predefined 6500-token limit")
        lengths = tokens["attention_mask"].sum(dim=1).tolist()
        tokens = {k: v.to(self.device) for k, v in tokens.items()}
        if self.backend == "cuda":
            torch.cuda.synchronize()
        start = time.perf_counter()
        with torch.inference_mode():
            output = self.model.generate(**tokens, do_sample=False, max_new_tokens=self.max_new_tokens, pad_token_id=self.tokenizer.pad_token_id, use_cache=True)
        if self.backend == "cuda":
            torch.cuda.synchronize()
        elapsed = time.perf_counter() - start
        generated = output[:, tokens["input_ids"].shape[1]:]
        results = []
        for i, row in enumerate(generated):
            nonpad = row[row != self.tokenizer.pad_token_id]
            results.append({
                "text": self.tokenizer.decode(row, skip_special_tokens=True),
                "input_tokens": lengths[i], "output_tokens": int(len(nonpad)),
                "batch_elapsed_seconds": elapsed,
                "amortized_seconds": elapsed / len(messages_batch),
                "peak_gpu_allocated_gb": torch.cuda.max_memory_allocated() / 2**30 if self.backend == "cuda" else 0.0,
                "backend": self.backend,
                "peak_process_ram_gb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (2**30 if sys.platform == "darwin" else 2**20),
                "model_path": self.path,
            })
        return results
