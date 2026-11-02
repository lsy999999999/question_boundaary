"""Bounded unattended execution on unused GPUs, with resumable artifacts."""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
PYTHON = ROOT / ".venv/bin/python"
MODEL = ROOT / "models/Qwen2.5-7B-Instruct"
RUN_ROOT = ROOT / "runs"
METHODS = ["state_fixed", "history_cv", "plain", "retrieval", "structured", "no_active"]
BACKEND = os.environ.get("THEORY_BACKEND", "cuda")
VARIANT = os.environ.get("THEORY_RUN_VARIANT", "v2_" + BACKEND.replace("-", "_") if BACKEND.startswith("cpu-") else "v1")


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2))
    temporary.replace(path)


def timestamp():
    return datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")


def status(stage, **extra):
    record = {"updated_at": timestamp(), "stage": stage, **extra}
    atomic_json(ROOT / "LIVE_STATUS.json", record)
    print(json.dumps(record, ensure_ascii=False), flush=True)


def gpu_inventory():
    indices = os.environ.get("THEORY_GPU_INDICES", "")
    selection = ["-i", indices] if indices else []
    result = subprocess.run(["nvidia-smi", *selection, "--query-gpu=index,uuid,name,memory.total,memory.used,utilization.gpu", "--format=csv,noheader,nounits"], capture_output=True, text=True, check=True)
    process_result = subprocess.run(["nvidia-smi", *selection, "--query-compute-apps=gpu_uuid,pid,used_memory", "--format=csv,noheader,nounits"], capture_output=True, text=True, check=True)
    occupied = {line.split(",")[0].strip() for line in process_result.stdout.splitlines() if line.strip()}
    devices = []
    for line in result.stdout.splitlines():
        index, uuid, name, total, used, util = [x.strip() for x in line.split(",")]
        devices.append({"index": int(index), "uuid": uuid, "name": name, "memory_total_mb": int(total), "memory_used_mb": int(used), "utilization": int(util), "free_for_job": uuid not in occupied and int(used) < 500 and int(util) < 5})
    return devices


def wait_environment():
    start = time.time()
    while not ((ROOT / "ENV_READY").exists() and (MODEL / "DOWNLOAD_COMPLETE.json").exists()):
        status("waiting_for_environment", env_ready=(ROOT / "ENV_READY").exists(), model_ready=(MODEL / "DOWNLOAD_COMPLETE.json").exists())
        if time.time() - start > 7200:
            raise TimeoutError("Environment/model preparation exceeded 2 hours")
        for name, ready in [("bootstrap", ROOT / "ENV_READY"), ("model_download", MODEL / "DOWNLOAD_COMPLETE.json")]:
            pidfile = ROOT / f"{name}.pid"
            if pidfile.exists() and not ready.exists():
                pid = int(pidfile.read_text())
                if not Path(f"/proc/{pid}").exists():
                    raise RuntimeError(f"{name} exited before readiness; inspect its log")
        time.sleep(20)


def run_checks():
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", TOKENIZERS_PARALLELISM="false")
    with (ROOT / "protocol_tests.log").open("w") as log:
        result = subprocess.run([str(PYTHON), "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=300)
    if result.returncode:
        raise RuntimeError("Protocol validation failed; inspect protocol_tests.log")
    result = subprocess.run([str(PYTHON), "-m", "pip", "freeze"], capture_output=True, text=True, check=True)
    (ROOT / "environment_freeze.txt").write_text(result.stdout)
    files = sorted(MODEL.glob("*.safetensors")) + sorted(MODEL.glob("*.json"))
    hashes = {}
    for path in files:
        digest = hashlib.sha256()
        with path.open("rb") as f:
            for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
                digest.update(block)
        hashes[path.name] = {"bytes": path.stat().st_size, "sha256": digest.hexdigest()}
    atomic_json(ROOT / "model_identity.json", {"model": "Qwen/Qwen2.5-7B-Instruct", "source": "public ModelScope mirror", "files": hashes})


def start_worker(split, seeds, methods, directory, gpu=None):
    label = "_".join(methods)
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", TOKENIZERS_PARALLELISM="false", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", PYTHONUNBUFFERED="1")
    if gpu:
        env["CUDA_VISIBLE_DEVICES"] = gpu["uuid"]
    else:
        env["CUDA_VISIBLE_DEVICES"] = ""
    log_path = directory / f"worker_{label}.log"
    command = [str(PYTHON), "-m", "discovery.runner", "--split", split, "--seeds", seeds, "--methods", ",".join(methods), "--output", str(directory), "--model", str(MODEL), "--rounds", "3", "--batch-size", "4", "--max-new-tokens", "384"]
    command += ["--backend", BACKEND, "--threads", "12"]
    with log_path.open("a") as log:
        child = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    return {"process": child, "label": label, "gpu": gpu, "log": str(log_path), "started": time.time(), "methods": methods}


def run_stage(split, seeds, name):
    directory = RUN_ROOT / name
    directory.mkdir(parents=True, exist_ok=True)
    free = [g for g in gpu_inventory() if g["free_for_job"]] if BACKEND == "cuda" else []
    if BACKEND == "cuda" and not free:
        raise RuntimeError("No unused GPU is available; no existing job was stopped")
    free = free[:2]
    status(f"starting_{split}", directory=str(directory), gpus=free, backend=BACKEND)
    workers = [start_worker(split, seeds, METHODS[:2], directory)]
    if BACKEND.startswith("cpu-"):
        workers += [start_worker(split, seeds, METHODS[2:], directory)]
    elif len(free) == 2:
        workers += [start_worker(split, seeds, ["plain", "retrieval"], directory, free[0]), start_worker(split, seeds, ["structured", "no_active"], directory, free[1])]
    else:
        workers += [start_worker(split, seeds, METHODS[2:], directory, free[0])]
    atomic_json(directory / "worker_registry.json", [{k: (v.pid if k == "process" else v) for k, v in w.items()} for w in workers])
    try:
        while True:
            counts = {method: len(list((directory / method).glob("*/result.json"))) for method in METHODS}
            state = [{"label": w["label"], "pid": w["process"].pid, "returncode": w["process"].poll()} for w in workers]
            status(f"running_{split}", directory=str(directory), completed=counts, workers=state)
            failed = [w for w in workers if w["process"].poll() not in (None, 0)]
            if failed:
                raise RuntimeError("Worker failure: " + ", ".join(w["label"] for w in failed))
            if all(w["process"].poll() == 0 for w in workers):
                break
            if any(time.time() - w["started"] > (43200 if BACKEND.startswith("cpu-") else 10800) for w in workers):
                raise TimeoutError("A worker exceeded its stage time limit")
            time.sleep(20)
    finally:
        for worker in workers:
            if worker["process"].poll() is None:
                os.killpg(worker["process"].pid, signal.SIGTERM)
        for worker in workers:
            try:
                worker["process"].wait(timeout=30)
            except subprocess.TimeoutExpired:
                os.killpg(worker["process"].pid, signal.SIGKILL)
    result = subprocess.run([str(PYTHON), "-m", "discovery.report", str(directory)], cwd=ROOT, env=dict(os.environ, OPENBLAS_NUM_THREADS="1"), capture_output=True, text=True)
    (directory / "report_generation.log").write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError("Report generation failed")
    summary = json.loads((directory / "summary.json").read_text())
    if not summary["complete"]:
        raise RuntimeError("The stage exited with missing results")
    return summary


def main():
    lock = (ROOT / "supervisor.lock").open("w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("A supervisor is already running", flush=True)
        return
    (ROOT / "supervisor.pid").write_text(str(os.getpid()))
    try:
        wait_environment()
        status("validating_protocol_and_model")
        run_checks()
        development_path = RUN_ROOT / f"dev_{VARIANT}/summary.json"
        if development_path.exists() and json.loads(development_path.read_text()).get("complete"):
            development = json.loads(development_path.read_text())
        else:
            development = run_stage("dev", "101", f"dev_{VARIANT}")
        calls = sum(m["generation_calls"] for m in development["methods"].values())
        invalid = sum(m["invalid_outputs"] for m in development["methods"].values())
        if calls and invalid / calls > 0.25:
            raise RuntimeError("Development invalid-output rate exceeds 25%; revise interface before independent evaluation")
        status("development_complete", development_summary=str(development_path), invalid_outputs=invalid, generation_calls=calls)
        evaluation = run_stage("eval", "0,1,2", f"eval_{VARIANT}")
        status("completed", results=str(RUN_ROOT / f"eval_{VARIANT}/REPORT.md"), total_results=evaluation["total_results"], completed_at=timestamp())
    except Exception as exc:
        status("failed", error=repr(exc), action="Inspect logs; completed checkpoints are preserved.")
        raise


if __name__ == "__main__":
    main()
