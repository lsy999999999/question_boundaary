# 第二轮执行状态

## V3 开发门槛失败，接口修订转入 V4

13:11 完成五种 agent 的 20 个开发结果、80 次真实生成，连同第一台 8 个基线结果，共 28 个开发结果。模型已选择不同表征，但 structured 与 shuffled 经常将表征名误写为来源卡片标识，无效输出超过预设 25%；开发门槛失败，未执行 V3 正式评测。已回传两台原始记录并汇总到 runs/dev_v3_combined/。评分与阈值保持原样；另建 ../phase2_v4/ 修订来源字段说明、重新验证，V3 源码与结果保留。

## 准备及运行历史

2026-10-31，Asia/Shanghai。

- 用户已授权建立第二台服务器环境并让两台共同运行。
- [研究方案](PLAN.md)：相同数值证据下的五种 agent，加两种专业/简单基线；开发 seed 201，独立评测 seeds 31、32、33。与首轮 CPU FP32 结果独立保存。
- 第一台：`/home/lsy/theory_discovery_phase2_20261031`；调度器 PID 2702060。8 项协议检查通过，开发集 state_fixed/history_cv 各 4 个结果已完成，等待第二台开发门槛。继续避免使用故障 GPU。
- 第二台：`/home/lsyedith/theory_discovery_phase2_20261031`；启动器 PID 3363249。独立 `.env_gpu` 环境已建立，PyTorch 2.5.1、Transformers 4.48.3、NumPy 1.26.4、SciPy 1.12.0；在该副本中的 CUDA 小张量运算及模型类导入成功，原 ml 环境仍为 NumPy 2.2.6、Transformers 4.52.2。Qwen2.5-7B-Instruct 最后两个分片正在下载；完整模型生成须在就绪及身份校验后核对，不能以 CUDA 小测试替代。
- 环境选择：初次使用 Python 3.13 不兼容目标旧包版本，随后 Python 3.12 从网络安装过慢，均保留日志并停止其安装进程；改为克隆已有 Python 3.10 / PyTorch 2.5.1 CUDA 12.4 环境，在副本固定 NumPy、SciPy、Transformers 等版本，不修改原环境。上述准备阶段尚无语言模型实验得分。
- GPU 调度器就绪后会重新检查空闲资源，最多使用五张卡。开发全部完成且预设格式/映射调用/修订/记录审计门槛通过，才启动正式 agent 评测；`manage_hosts.py` 转发门槛结果后第一台开始正式基线。
- SSH 通道有本轮限时保活，凭据不保存。`manage_hosts.py --pull` 按 `servers/a`、`servers/b` 分别回传；`collect_results.py` 校验配置并汇总，保留各机 manifest。
- 当前聊天自动跟进已恢复，每 20 分钟检查；正常无实质变化保持安静，完成或需要处理时通知。开发门槛失败则保留记录并报告，不修改阈值强行放行。

运行日志：第二台 `environment_clone.log`、`model_download.log`、`supervisor.log`；第一台 `protocol_tests.log` 和 `runs/baseline_dev_v3/`。最新实况由两台 `LIVE_STATUS.json` 及本地 `remote_status_a.json` / `remote_status_b.json` 保存。
