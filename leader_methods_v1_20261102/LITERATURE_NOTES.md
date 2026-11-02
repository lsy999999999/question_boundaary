# 支持leader的方法文献

日期：2026-11-02。本轮围绕“怎样把已有知识组合成能计算、能被区分的解释”补充6个学术查询，得到18条返回、17个不同题名；结合上一轮已保存的相关正文，整理17项方法来源。进行了23次公开来源请求，22次成功；一次Crossref限流后换同一文章的另一DOI记录成功，失败记录保留。

检索记录见RETRIEVAL_LOG.json、RETRIEVAL_SUPPLEMENT.json；逐项来源、阅读等级与文件哈希见SOURCE_REGISTRY.json。这是定向方法整理，不是穷尽性综述，没有复现论文报告的性能。

## 最适合直接放进工作流程的几项

**MOOSE-Chem：逐步取灵感、组合、更新假说。** 本轮读2024-10-09预印本v1第4节。它把背景加多条灵感转成逐轮检索和假说更新，尝试多种连接方式，再筛选候选。可借用的是“缺什么知识就检索什么、每次把新知识接入当前假说”的具体工作方式。论文主要评价假说重发现，未替我们完成机制方程、参数识别或真实实验验证。对应M11–M16、M42。

**AI Feynman：利用结构把大推导拆小。** 重点读量纲、对称性、可分解性和递归模块。直接借用到M06、M09、M10、M26：先寻找不变量和可拆分子关系，再做表达式搜索。它面对数值表中的函数发现；换到部分可观测动态系统时，还需要状态和观测模型。

**AI-Descartes：既看拟合，也检查能否从背景规律推出。** 重读背景公理、符号回归与自动推理模块的连接。方法要求给定的公理体系有足够信息；正文明确讨论背景不完整、模型语言不足和测量噪声。可借用M08、M14、M23、M39中的可推导性与等价检查。普通语言检查不自动获得定理证明器的保证。

**SINDy与PDE-FIND：把“可能存在某种关系”落到候选项与系数。** 重读候选函数库、稀疏选择、导数估计、正则化和数据条件。可借用M27，但只有在状态、采样和导数估计足够可靠时才合适。缺关键状态时，不能指望库搜索自行补出正确机制。

**可识别性分析：解释为什么“有方程”还不能推出唯一答案。** Raue等的出版摘要区分结构与实际不可识别，并用profile likelihood诊断。对应M29：先检查数据能确定什么参数组合，再决定需要什么测量。这个来源本轮只读摘要，没有将其写作已完整实现的求解方案。

**Box’s Loop、LLM-SR、HypoGeniC与learning from failures：用具体失败改变下一轮。** 分别借用后验预测批评、方程骨架与参数分工、错误样本库、失败生成约束。本轮复读对应方法段落。形式逻辑中的剪枝保证不能照搬到带噪声机制模型，卡片明确保留这一边界。

## 17项来源与实际阅读深度

| ID | 来源 | 本轮阅读 | 放进系统的用途 |
|---|---|---|---|
| P01 | [Platt, Strong Inference, Science 1964](https://doi.org/10.1126/science.146.3642.347) | 元数据核对 | 竞争解释与区分实验的经典出处；具体操作由其他方法和项目整理补足 |
| P02 | [Buckingham, 1914](https://doi.org/10.1103/PhysRev.4.345) | 元数据核对 | 量纲方法的经典出处；实际操作重点读P07 |
| P03 | [Gentner, Structure-mapping, 1983](https://doi.org/10.1016/S0364-0213(83)80009-3) | 索引摘要＋原始元数据 | 映射关系结构，检查迁移条件；未全文审读 |
| P04 | [Box, Science and Statistics, 1976](https://doi.org/10.1080/01621459.1976.10480949) | 元数据核对 | 建模与批评的背景线索，不用元数据支持复杂算法细节 |
| P05 | [SINDy, PNAS 2016](https://doi.org/10.1073/pnas.1517384113) | 预印本正文重点段落 | 稀疏动力学、候选库、噪声和选择 |
| P06 | [PDE-FIND, Science Advances 2017](https://doi.org/10.1126/sciadv.1602614) | 预印本正文重点段落 | 空间导数库、STRidge和采样条件 |
| P07 | [AI Feynman, Science Advances 2020](https://doi.org/10.1126/sciadv.aay2631) | 预印本正文重点段落 | 量纲、对称性、可分解、递归求解 |
| P08 | [Raue et al., Bioinformatics 2009](https://doi.org/10.1093/bioinformatics/btp358) | 出版摘要与PubMed摘要 | 结构/实际可识别性、profile likelihood |
| P09 | [Chaloner & Verdinelli, Bayesian Experimental Design, 1995](https://doi.org/10.1214/ss/1177009939) | 出版摘要 | 用效用与成本选择实验；无概率时只用定性代理 |
| P10 | [Pearl, Causal inference in statistics, 2009](https://doi.org/10.1214/09-SS057) | 出版摘要 | 区分关联、干预与因果识别假设 |
| P11 | [Benner et al., Model Reduction Survey, 2015](https://doi.org/10.1137/130932715) | 出版摘要 | 约化与近似适用范围；卡片包含更宽工程整理 |
| P12 | [Automated Statistical Model Discovery with Language Models, ICML 2024](https://proceedings.mlr.press/v235/li24v.html) | 复用存档正文，重读关键段落 | 结构—拟合—预测检查—批评 |
| P13 | [AI-Descartes, Nature Communications 2023](https://www.nature.com/articles/s41467-023-37236-y) | 复用存档正文，重读关键段落 | 公理与经验候选结合、可推导性 |
| P14 | [MOOSE-Chem, 2024预印本v1](https://arxiv.org/abs/2410.07076v1) | 正文第4节重点审读 | 多条灵感、组合方式、逐轮更新；正式ICLR 2025信息见先前文献目录 |
| P15 | [LLM-SR, ICLR 2025](https://iclr.cc/virtual/2025/poster/28487) | 复用存档正文，重读关键段落 | 方程骨架与参数优化分开 |
| P16 | [Learning programs by learning from failures, Machine Learning 2021](https://link.springer.com/article/10.1007/s10994-020-05934-z) | 复用存档正文，重读关键段落 | generate–test–constrain；限定剪枝前提 |
| P17 | [HypoGeniC, NLP4Science workshop 2024](https://aclanthology.org/2024.nlp4science-1.10/) | 复用存档正文，重读关键段落 | 错误样本驱动候选更新；原任务主要是分类 |

## 如何使用这些来源

METHOD_LIBRARY中的44张卡是本项目编写的操作方案。部分是直接算法的改编，部分是把几类方法连接起来的工程整理。逐卡source_ids用于回溯基础来源，不表示某篇论文已经验证整张卡的触发规则或整套leader提示词。P04只保留背景出处。

历史盲测时，组织者仍需逐项核对实际提供给模型的知识及版本日期。方法文献的初版很早，不意味着它的最新版、引用列表和网页推荐也都早于截止日。整库不向agent提供目标论文或后续结论。
