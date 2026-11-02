# 第二轮：工具辅助的假设修订

研究问题、对照、预算和开发放行条件见 [PLAN.md](PLAN.md)，执行进展见 [STATUS.md](STATUS.md)。首轮原始结果保留在上一层的 runs/ 中。

两台机器分工执行：第一台只做数值基线；第二台使用独立克隆环境 `.env_gpu` 和空闲 GPU 做真实 Qwen2.5-7B-Instruct 生成。所有 agent 共用候选验证误差及实验预测分歧，比较无卡片、正确卡片、显式映射、机制内容错配和固定实验。

本地协调与回传：

```bash
python3 manage_hosts.py
python3 manage_hosts.py --pull
/Applications/deep_learning_hm/.venv/bin/python collect_results.py --split dev
/Applications/deep_learning_hm/.venv/bin/python collect_results.py --split eval
```

`manage_hosts.py` 使用已有 SSH 控制连接，不读写密码；按开发门槛结果通知第一台是否进入正式评测。原始产物按服务器保存在 servers/a 与 servers/b，汇总到新的 runs/*_v4_combined，保留两台 manifest。汇总命令拒绝覆盖已有目录。

开发操作门槛只检查格式、映射调用、修订和记录顺序；映射语义需要单独审读。正式结论以完整配对结果、独立干预预测和实际成本为依据。
