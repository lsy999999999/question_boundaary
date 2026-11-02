"""Version-three provenance audit; semantics remain a separate judgment."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

VALID = {"storage", "transport", "saturation", "external_clock", "none"}


def audit(root):
    root = Path(root)
    out = {"forecast_order_errors": [], "forecast_hash_errors": [], "evaluation_order_errors": [], "source_counts": {}, "representation_changes": {}}
    for p in root.glob("*/*/round_*/observation.json"):
        obs = json.loads(p.read_text())
        pred = json.loads(p.with_name("forecast_before_observation.json").read_text())
        digest = pred.pop("sha256")
        if pred["time_ns"] >= obs["time_ns"]:
            out["forecast_order_errors"].append(str(p.relative_to(root)))
        if digest != obs["forecast_sha256"] or digest != hashlib.sha256(json.dumps(pred,sort_keys=True).encode()).hexdigest():
            out["forecast_hash_errors"].append(str(p.relative_to(root)))
    for p in root.glob("*/*/result.json"):
        result = json.loads(p.read_text())
        commit = json.loads(p.with_name("final_model_before_evaluation.json").read_text())
        if commit["time_ns"] >= result["evaluation_after_commit_ns"]:
            out["evaluation_order_errors"].append(str(p.relative_to(root)))
        reps = result["selected_representations"]
        method = result["method"]
        out["representation_changes"].setdefault(method, {"tasks":0,"tasks_with_revision":0,"transitions":0,"revisions":0})
        row=out["representation_changes"][method]
        row["tasks"] += 1
        row["tasks_with_revision"] += int(len(set(reps))>1)
        row["transitions"] += len(reps)-1
        row["revisions"] += sum(a!=b for a,b in zip(reps,reps[1:]))
    for method in ("structured","no_active","shuffled"):
        counts=Counter()
        paths=list((root/method).glob("*/round_*/decision.json"))+list((root/method).glob("*/final_decision.json"))
        for p in paths:
            item=json.loads(p.read_text())
            mapping=item["decision"].get("mapping") or {}
            counts[str(mapping.get("source_id","missing"))] += 1
        out["source_counts"][method]={"counts":dict(counts),"total":sum(counts.values()),"valid_non_none":sum(v for k,v in counts.items() if k in VALID-{"none"}),"invalid":sum(v for k,v in counts.items() if k not in VALID)}
    out["semantic_review"]="Nonempty valid references establish invocation only, not semantic correctness."
    out["fits_per_task"]={"state_fixed":7,"history_cv":51,"agents":52}
    (root/"audit.json").write_text(json.dumps(out,indent=2,ensure_ascii=False))
    (root/"AUDIT.md").write_text("# V3 记录审计\n\n```json\n"+json.dumps(out,ensure_ascii=False,indent=2)+"\n```\n")
    return out


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("root",type=Path)
    print(json.dumps(audit(parser.parse_args().root),ensure_ascii=False))
