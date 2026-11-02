# 跨领域理论发现 agent：受控原型

目标：比较结构化跨领域迁移、普通检索、主动实验与专业历史建模基线，在隐藏动力系统上的独立干预预测表现。

最近推进（2026-11-01）：[V5 可执行证据记忆与时间范围](concept_memory_v5/REPORT.md)。已完成旧记录回放、11 项工具检查，以及 12 个新参数系统的数值工具验收；真实 Luna 新实验待凭据接入。承接的真实模型结果见 [概念边界 V4](concept_boundary_v4/REPORT.md)，下一步依据见 [NEXT_STEP.md](concept_boundary_v4/NEXT_STEP.md)。

此前跨领域卡片对照：[第二轮结论](phase2_v4/REPORT.md)，168 个正式结果、480 次真实生成，已完成两机回传、完整性及记录审计。模型出现表征修订，正确卡片与错配卡片的性能差异尚不清晰；[正式统计](phase2_v4/runs/eval_v4_combined/REPORT.md)及[执行状态](phase2_v4/STATUS.md)已保存。

## 已完成的首轮结果

正式评测已完成 144 个结果、384 次真实模型生成，并完成审计和回传。专业历史建模基线表现最好；当前 structured 配置未显示稳定收益，也未实际引用有效跨领域机制卡片。

- [研究结论与后续提案](REPORT.md)
- [完整统计](runs/eval_v2_cpu_fp32/REPORT.md)与[审计](runs/eval_v2_cpu_fp32/AUDIT.md)
- [执行状态](STATUS.md)与[事后核对记录](postrun_analysis.json)

## 运行范围

- 本地目录保存源码、计划、运行记录和回传结果。
- 远端独立目录：`/home/lsy/theory_discovery_20261031`。
- 语言模型：Qwen2.5-7B-Instruct。GPU v1 使用 BF16；设备故障后，CPU v2 使用 FP32，分别保存结果。当前运行状态见 `STATUS.md`。
- 每个任务：3 个共同初始实验，3 个后续实验，最后提交模型，再评估 6 个未见干预。
- 开发集：4 个任务；独立评测：8 个机制族 × 3 个参数种子 = 24 个任务。
- 方法：state_fixed、history_cv、plain、retrieval、structured、no_active；完整首轮合计 168 个任务/方法结果，其中评测部分 144 个。

## 入口

```bash
python -m unittest discover -s tests -v
python orchestrate_server.py
python -m discovery.report runs/eval_v2_cpu_fp32
```

服务器环境用 `bootstrap_server.sh` 安装，公开模型用 `download_model.py` 下载。`sync_server.py` 通过已登录的 SSH 控制连接同步源码或取回结果，不保存登录凭据。

## 检查状态

`LIVE_STATUS.json` 保存阶段与各方法已完成任务数。`supervisor.log` 与 `runs/*/worker_*.log` 保存调度和逐轮日志。各任务的 `checkpoint.json` 支持同版本恢复；源码或冻结设置变化时必须使用新的运行目录。

CPU 后备运行使用环境变量 `THEORY_BACKEND=cpu-fp32` 启动调度器。GPU 故障与恢复尝试记录在 `OPERATIONS.md`。

## 解释边界

本原型使用共享的受约束表征操作集合和人工机制卡片。它检验证据驱动的表征选择、修订与实验选择，还没有实现开放表达式构造、开放文献检索或未知自然规律发现。专业基线可搜索全部共享表征，不能用只会当前状态回归的弱方法替代它。

所有正式结果以真实语言模型输出与独立数值评测为依据。程序会保存格式失败与确定性回退，不用预编程策略冒充模型输出。
