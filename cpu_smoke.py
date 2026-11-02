"""Measure a real CPU quantized generation before committing a long run."""
import json
import time
import argparse
from pathlib import Path

from discovery.llm import LocalModel, make_prompt
from discovery.runner import State
from discovery.world import make_task

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--backend", choices=["cpu-int8", "cpu-fp32"], default="cpu-fp32")
args = parser.parse_args()
start = time.perf_counter()
model = LocalModel(root / "models/Qwen2.5-7B-Instruct", max_new_tokens=256, backend=args.backend, threads=12)
load_seconds = time.perf_counter() - start
state = State(make_task("dev", "memory", 101), root / "runs/cpu_smoke_state")
responses = model.generate([make_prompt(state, "structured")])
result = {"load_seconds": load_seconds, "response": responses[0]}
(root / f"runs/smoke_{args.backend}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps(result, ensure_ascii=False), flush=True)
