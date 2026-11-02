"""Summarize actual paired results, including failures and uncertainty."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from .runner import AGENT_METHODS, BASELINE_METHODS, write_json


def collect(root):
    return [json.loads(p.read_text()) for p in sorted(root.glob("*/*/result.json"))]


def paired(rows, left, right):
    a = {r["task_id"]: r for r in rows if r["method"] == left}
    b = {r["task_id"]: r for r in rows if r["method"] == right}
    keys = sorted(set(a) & set(b))
    if not keys:
        return None
    ratios = {k: float(np.log((a[k]["test"]["test_nmse"] + 1e-8) / (b[k]["test"]["test_nmse"] + 1e-8))) for k in keys}
    groups = defaultdict(list)
    for key in keys:
        groups[a[key]["family"]].append(key)
    families = sorted(groups)
    rng = np.random.default_rng(20261031)
    estimates = []
    # Hierarchical descriptive bootstrap: resample families, then instances.
    for _ in range(2000):
        values = []
        for family in rng.choice(families, len(families), replace=True):
            sample = groups[family]
            values.extend(ratios[k] for k in rng.choice(sample, len(sample), replace=True))
        estimates.append(np.exp(np.mean(values)))
    return {
        "left": left, "right": right, "paired_tasks": len(keys),
        "left_wins": sum(a[k]["test"]["test_nmse"] < b[k]["test"]["test_nmse"] for k in keys),
        "geometric_nmse_ratio": float(np.exp(np.mean(list(ratios.values())))),
        "descriptive_bootstrap_95_interval": np.quantile(estimates, [0.025, 0.975]).tolist(),
    }


def build_report(root, required_methods=None):
    root = Path(root)
    rows = collect(root)
    manifest = json.loads((root / "manifest.json").read_text())
    by_method = defaultdict(list)
    for row in rows:
        by_method[row["method"]].append(row)
    required_methods = required_methods or list(BASELINE_METHODS + AGENT_METHODS)
    expected = len(manifest["tasks"])
    complete = all(len(by_method[m]) == expected for m in required_methods)
    summary = {
        "split": manifest["split"], "complete": complete,
        "expected_tasks_per_method": expected, "methods": {},
        "total_results": len(rows), "paired_comparisons": [],
    }
    for method in required_methods:
        records = by_method[method]
        if not records:
            continue
        errors = np.array([r["test"]["test_nmse"] for r in records])
        accepted = [r for r in records if r["accepted_by_common_cv_rule"]]
        summary["methods"][method] = {
            "n": len(records), "median_test_nmse": float(np.median(errors)),
            "mean_test_nmse": float(np.mean(errors)),
            "test_nmse_below_0_1": int(np.sum(errors < 0.1)),
            "accepted": len(accepted),
            "false_accepted": sum(r["test"]["test_nmse"] > 0.1 for r in accepted),
            "invalid_outputs": sum(r["invalid_outputs"] for r in records),
            "generation_calls": sum(r["generation_calls"] for r in records),
            "input_tokens": sum(r["input_tokens"] for r in records),
            "output_tokens": sum(r["output_tokens"] for r in records),
            "generation_seconds_amortized": sum(r["generation_seconds_amortized"] for r in records),
            "peak_gpu_allocated_gb": max(r["peak_gpu_allocated_gb"] for r in records),
            "final_representations": dict(Counter(r["model"]["representation"] for r in records)),
        }
    for other in ("plain", "retrieval", "no_active", "history_cv"):
        comparison = paired(rows, "structured", other)
        if comparison:
            summary["paired_comparisons"].append(comparison)
    write_json(root / "summary.json", summary)
    lines = [
        "# 理论发现 agent：首轮受控实验结果", "",
        f"任务拆分：`{manifest['split']}`；每种方法应完成 {expected} 个任务；当前完整性：{'完整' if complete else '未完成'}。", "",
        "本实验检验共享表征操作集合中的模型修订与主动实验。模型只能选择预定义的表征操作，系数由数值工具拟合；结果用于评价受约束的再发现流程。", "",
        "## 实际结果", "",
        "NMSE 是独立干预轨迹的均方误差除以各轨迹方差（分母下限 0.02）；越低越好。共同接受规则为训练实验的留一轨迹验证 NMSE < 0.05；接受后测试 NMSE > 0.1 记为错误接受。这些阈值在运行前固定。", "",
        "| 方法 | 已完成 | 测试 NMSE 中位数 | 测试 NMSE 均值 | 测试 < 0.1 | 接受 / 错误接受 | 无效输出 / 调用 | 显存峰值 GB |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for method, m in summary["methods"].items():
        lines.append(f"| {method} | {m['n']} | {m['median_test_nmse']:.5f} | {m['mean_test_nmse']:.5f} | {m['test_nmse_below_0_1']} | {m['accepted']} / {m['false_accepted']} | {m['invalid_outputs']} / {m['generation_calls']} | {m['peak_gpu_allocated_gb']:.2f} |")
    lines += ["", "## 配对比较", "", "比值为 structured / 对照 的几何平均 NMSE 比值，小于 1 表示 structured 的误差较低。区间为按机制族及实例分层重采样得到的描述性区间，任务族较少，不能解释为对任意科学问题的泛化保证。", ""]
    for c in summary["paired_comparisons"]:
        lo, hi = c["descriptive_bootstrap_95_interval"]
        lines.append(f"- 对 {c['right']}：{c['paired_tasks']} 个配对任务，胜出 {c['left_wins']} 个；误差比 {c['geometric_nmse_ratio']:.3f}，描述性 95% 区间 [{lo:.3f}, {hi:.3f}]。")
    families = sorted(set(r["family"] for r in rows))
    lines += ["", "## 按机制族分解", "", "| 机制族 | " + " | ".join(required_methods) + " |", "|---|" + "---:|"*len(required_methods)]
    for family in families:
        values = []
        for method in required_methods:
            errors = [r["test"]["test_nmse"] for r in by_method[method] if r["family"] == family]
            values.append(f"{np.median(errors):.5f}" if errors else "—")
        lines.append(f"| {family} | " + " | ".join(values) + " |")
    lines += [
        "", "## 如何解释", "",
        "- plain：普通 agent；retrieval：同一 agent 加跨领域材料；structured：同样材料加显式结构映射与条件检查；no_active：结构化方法采用固定实验顺序。", 
        "- state_fixed：当前状态线性模型与固定实验；history_cv：专业算法在全部共享表征中按独立轨迹验证选择，并按预测分歧选实验。后者使用更多候选拟合计算，实际成本需与语言模型生成成本分别核对。",
        "- 跨领域材料是人工整理的四份机制卡片，当前实现没有开放网络检索。表征操作包含历史、延迟、非线性与时钟；选择这些操作尚不能视为自主创造新的科学概念。",
        "- dev 仅使用 linear、cubic、memory、clock；eval 包含新参数实例及 two_memory、delay、saturated_memory、memory_clock。它检验规定模拟器族中的迁移，不代表未知自然规律发现。",
        "- 单次任务的机制选择不具有唯一性。报告主要依赖独立干预预测，允许等价或近似表征。",
        "- 每个任务保留原始提示、真实模型输出、格式错误、预测先于观测的时间与哈希、观测数组、检查点及最终模型。无效输出采用显式确定性回退，并计入结果。",
        "- 语言模型未直接读取隐藏机制、参数或测试轨迹。记录中的 family 字段只用于完成模型提交后的评测汇总。",
        "", "## 产物", "",
        "`manifest.json` 保存任务、配置和源码哈希；`summary.json` 保存统计；每个方法/任务目录保存全部轨迹与决策。模型文件哈希和环境版本由服务器调度器另行保存。", "",
    ]
    if complete and summary["paired_comparisons"]:
        ref = next((c for c in summary["paired_comparisons"] if c["right"] == "retrieval"), None)
        if ref:
            lo, hi = ref["descriptive_bootstrap_95_interval"]
            if hi < 1:
                conclusion = "本轮 structured 相比 retrieval 的预测误差更低；仍需扩展任务、重复运行并检验映射质量，才能确定优势来源与适用范围。"
            elif lo > 1:
                conclusion = "本轮 structured 相比 retrieval 的预测误差更高。应检查额外映射约束与实验选择如何影响表现，当前结果不支持结构化提示带来收益。"
            else:
                conclusion = "本轮结果尚不能清楚区分 structured 与 retrieval 的表现；当前证据不支持宣称显式结构映射有稳定优势。"
            lines += ["## 本轮判断", "", conclusion, ""]
    (root / "REPORT.md").write_text("\n".join(lines))
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    print(json.dumps(build_report(args.root), ensure_ascii=False))


if __name__ == "__main__":
    main()
