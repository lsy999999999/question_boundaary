"""Post-run provenance/ordering audit, without altering decisions or scores."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

VALID_SOURCE_IDS = {"storage", "transport", "saturation", "external_clock", "none"}


def audit(root):
    root = Path(root)
    order_errors, hash_errors = [], []
    mapping = defaultdict(lambda: {"decisions": 0, "valid_source_id": 0, "missing_mapping": 0, "invalid_source_ids": Counter()})
    for path in root.glob("*/*/round_*/observation.json"):
        record = json.loads(path.read_text())
        forecast_path = path.with_name("forecast_before_observation.json")
        forecast = json.loads(forecast_path.read_text())
        digest = forecast.pop("sha256")
        if forecast["time_ns"] >= record["time_ns"]:
            order_errors.append(str(path.relative_to(root)))
        if digest != record["forecast_sha256"] or digest != hashlib.sha256(json.dumps(forecast, sort_keys=True).encode()).hexdigest():
            hash_errors.append(str(path.relative_to(root)))
    for method in ("structured", "no_active"):
        paths = list((root / method).glob("*/round_*/decision.json")) + list((root / method).glob("*/final_decision.json"))
        for path in paths:
            record = json.loads(path.read_text())
            m = record["decision"].get("mapping")
            mapping[method]["decisions"] += 1
            if not isinstance(m, dict):
                mapping[method]["missing_mapping"] += 1
            elif m.get("source_id") in VALID_SOURCE_IDS:
                mapping[method]["valid_source_id"] += 1
            else:
                mapping[method]["invalid_source_ids"][str(m.get("source_id"))] += 1
    source_counts = {}
    for method, row in mapping.items():
        source_counts[method] = {**row, "invalid_source_ids": dict(row["invalid_source_ids"]), "valid_source_id_rate": row["valid_source_id"] / max(1, row["decisions"])}
    final_order_errors = []
    for path in root.glob("*/*/result.json"):
        result = json.loads(path.read_text())
        commit = json.loads(path.with_name("final_model_before_evaluation.json").read_text())
        if commit["time_ns"] >= result["evaluation_after_commit_ns"]:
            final_order_errors.append(str(path.relative_to(root)))
    output = {"forecast_order_errors": order_errors, "forecast_hash_errors": hash_errors, "evaluation_order_errors": final_order_errors, "mapping_source_id_audit": source_counts,
              "fitting_calls_per_task_from_code_path": {"state_fixed": 7, "history_cv": 51, "language_model_methods": 8},
              "scope": "Source id checks validate declared provenance only; mapping semantics require independent review. GPU v1 checked mapping fields only; CPU v2 also validates source-id enum and records these errors in invalid-output counts."}
    (root / "audit.json").write_text(json.dumps(output, ensure_ascii=False, indent=2))
    lines = ["# 运行记录审计", "", f"预测先于观测的顺序错误：{len(order_errors)}；预测哈希错误：{len(hash_errors)}；最终模型提交与评测顺序错误：{len(final_order_errors)}。", "", "## 映射来源核对", "", "GPU v1 的解析器只检查 mapping 字段齐全，未将来源标识错误计入无效输出。CPU v2 已明确来源枚举并记录该错误。此处对两种版本统一核对引用可定位性，保持原始决策和得分不变。", "", "| 方法 | 映射决策数 | 有效来源标识 | 有效率 |", "|---|---:|---:|---:|"]
    for method, row in source_counts.items():
        lines.append(f"| {method} | {row['decisions']} | {row['valid_source_id']} | {row['valid_source_id_rate']:.1%} |")
    lines += ["", "有效标识包括明确选择 none。标识正确仅表示引用可定位，映射在语义上是否成立需要独立审读。", "", "## 计算预算", "", "按实际调用路径，每个任务 state_fixed 调用拟合函数 7 次，history_cv 51 次，语言模型方法各 8 次。每种方法均获得 6 次实验；各 agent 均为 4 次生成、每次上限 384 个新 token。专业基线和 agent 的计算构成不同，报告分别记录模型生成 token 和时间，未将它们折算成相同成本。", ""]
    (root / "AUDIT.md").write_text("\n".join(lines))
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.root), ensure_ascii=False))


if __name__ == "__main__":
    main()
