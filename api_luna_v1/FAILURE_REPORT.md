# V1 参数兼容失败

V1 已停止，未完成全部正式对照。28 个开发结果、120 个正式结果（48 个基线和 plain/retrieval/structured 各 24 个结果）以及其他组检查点全部保留。它们不并入 V2 的独立重跑得分。

停止由本地预算校验触发，不是网络错误：第 492 条请求是 shuffled / 7dc2896588f5 / round 2，HTTP 正常返回、JSON 可读，但 usage 报告 completion_tokens=541、reasoning_tokens=399，而请求参数为 max_tokens=512。原始返回位于 wire/eval/0492_1754ee41838d49ba94f0b1ec0734f7d9/。该返回未传给科学 runner，不作为模型决策计分；其他在途请求正常结束后进程退出。

OpenAI 文档把 max_tokens 列为旧参数，max_completion_tokens 明确覆盖可见输出和推理 token。无法仅凭此返回确认第三方如何实现旧参数；它不足以保证本轮设定的总生成上限。因此 V2 用 max_completion_tokens=512 重新运行全部任务，而不是放宽校验、补齐部分组或选择性替换分数。

V1 共 493 条真实 API 返回，均 finish_reason=stop，请求及返回名均为 gpt-6-luna。输入 1,501,553 token，生成 108,872 token，其中服务标记推理 54,195 token。这些包含触发停止的返回和已完成但未完整计分的任务；成本不会因排除得分而删除。

保留正式结果的先预测后观测、预测哈希和先提交后评测审计错误均为 0。尚未完成的任务没有最终评测结果，不能当作完成或失败预测来补分。

来源：https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create
