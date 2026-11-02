"""Assemble copied per-host evidence, preserving original provenance."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from discovery.report import build_report
from discovery.runner import BASELINE_METHODS, AGENT_METHODS

ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument("--split",choices=["dev","eval"],required=True);args=p.parse_args()
baseline=ROOT/"servers/a/runs"/f"baseline_{args.split}_v4"
agent=ROOT/"servers/b/runs"/f"{args.split}_v4"
ma=json.loads((baseline/"manifest.json").read_text());mb=json.loads((agent/"manifest.json").read_text())
for key in ("source_hashes","tasks","seeds","rounds","max_new_tokens","batch_size","acceptance_cv_threshold","failure_test_nmse_threshold","protocol_version"):
    if ma[key]!=mb[key]:raise RuntimeError(f"Cross-host configuration mismatch: {key}")
expected={t["task_id"] for t in mb["tasks"]}
for src,methods in [(baseline,BASELINE_METHODS),(agent,AGENT_METHODS)]:
    for method in methods:
        results=list((src/method).glob("*/result.json"))
        if {f.parent.name for f in results}!=expected or len(results)!=len(expected):raise RuntimeError(f"Incomplete: {method}")
out=ROOT/"runs"/f"{args.split}_v4_combined"
if out.exists():raise RuntimeError("Combined output exists; preserve it and choose a new output path")
out.mkdir(parents=True)
for src,methods in [(baseline,BASELINE_METHODS),(agent,AGENT_METHODS)]:
    for method in methods:shutil.copytree(src/method,out/method)
(out/"manifest.json").write_text(json.dumps({**mb,"host_provenance":{"baselines":"manifest_a.json","agents":"manifest_b.json"}},ensure_ascii=False,indent=2))
shutil.copy2(baseline/"manifest.json",out/"manifest_a.json");shutil.copy2(agent/"manifest.json",out/"manifest_b.json")
hashes={str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob('*') if f.is_file()}
(out/"copied_file_hashes.json").write_text(json.dumps(hashes,sort_keys=True,indent=2))
summary=build_report(out)
assert summary["complete"]
print(json.dumps({"results":summary["total_results"],"report":str(out/"REPORT.md")},ensure_ascii=False))
