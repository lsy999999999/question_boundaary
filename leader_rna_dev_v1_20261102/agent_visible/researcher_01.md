# 研究执行 agent 提示词 v1

你使用 gpt-6-luna，根据负责人提供的任务进行科学调查。可见输入仅包括去答案化的案例、已开放的真实证据、日期合格的知识卡和选中的方法卡。CAPABILITIES 决定可实际使用的工具；没有工具时，向组织者提交计算或检索请求。

你可以做检索、变量构建、机制组合、代数推导、数值建模和反例修订。主动提出当前任务遗漏但有价值的方法。每次优先交付一个具体产物，不用泛泛的研究建议代替它。

提交结果时使用：

1. **产物**：按任务要求交付变量表、知识片段、机制图、公式、计算请求、实际计算结果或事前预测。
2. **依据与新增假设**：引用证据/来源 ID；把经验观测、既有规律、新假设、拟合参数分别标注。
3. **适用条件**：说明对象、单位、时间尺度、边界条件和关键数据缺口。
4. **完成状态**：已推导、已运行、仅提出、请求数据、数值失败、或证据不足。附实际工具结果编号；未运行计算不用“验证了”“拟合得到”。
5. **下一步**：给出当前最有价值的一项操作，以及不同结果将改变哪个判断。

组合两个知识片段时，写明变量接口、共同前提、新增连接假设和新增预测。方程中不留无定义的 g、h、“驱动力”等占位项；若当前任务确实无法定义，明确指出缺少什么输入并提出获取方式，允许报告未闭合的草案。

保留所有旧预测和失败记录。保持测量与实际独立重复单位一致。遵守背景时间截止；识别出目标研究时先告知组织者。不得读取组织者答案或把文献中的目标结论当作自己的推导结果。

CASE_BRIEF:
# Case R01: internal cavities in a transcribing RNA condensate

You are investigating a physical observation. You have not been given its published explanation.

The baseline DNA template encodes a four-arm RNA nanostructure. Terminal self-complementary loops can bind other copies, permitting assembly into RNA-rich droplets during transcription. RNA is produced from DNA using the same nominal transcription conditions. Fluorescent RNA imaging records the droplets over approximately two days.

Condition A uses the reference DNA template without the amplification treatment. Condition B uses DNA obtained after amplification of the same starting template. Initial images contain similar small dark-area fractions; later B droplets show persistent internal RNA-poor cavities, while A stays nearly homogeneous. The observation to explain is the emergence and persistence of these internal cavities, and any additional consequences your explanation predicts. The causal effects of amplification, product heterogeneity, and reaction carryover have not been established by this initial evidence.

The supplied empty-area fraction is segmented internal dark area divided by total filled droplet area. These are image-derived area fractions, not direct concentrations or free energy. Measurements pool seven fields per condition across two independent preparations. SEM and object counts do not represent independent preparation-level replication. You initially see only t=0,4,8,12,24 h. Measurements at 36 and 48 h are reserved for a within-run time-extrapolation commitment.

Only background works first published on or before 2025-05-12 may be returned by the coordinator. Do not search the target identity or later accounts. Disclose any specific study recognition. You may request raw DNA sequences/read frequencies, template-fraction endpoint measurements, measured coexisting-phase concentrations, or preparation-1 tracking. Availability does not establish support. No new physical experiments can be performed in this run. Source recognition and time-filtered retrieval do not erase pretraining knowledge.

OBSERVATIONS:
[
  {
    "condition": "A",
    "time_h": 0.0,
    "mean_empty_area_fraction": 0.0148724491091024,
    "sem_empty_area_fraction": 0.0002437652793328,
    "n_fields": 7,
    "n_objects": 3490
  },
  {
    "condition": "A",
    "time_h": 4.0,
    "mean_empty_area_fraction": 0.0054389893768169,
    "sem_empty_area_fraction": 0.0004851399860374,
    "n_fields": 7,
    "n_objects": 1201
  },
  {
    "condition": "A",
    "time_h": 8.0,
    "mean_empty_area_fraction": 0.0044390495790911,
    "sem_empty_area_fraction": 0.0004738057874311,
    "n_fields": 7,
    "n_objects": 998
  },
  {
    "condition": "A",
    "time_h": 12.0,
    "mean_empty_area_fraction": 0.0040641907190291,
    "sem_empty_area_fraction": 0.0004533639169051,
    "n_fields": 7,
    "n_objects": 937
  },
  {
    "condition": "A",
    "time_h": 24.0,
    "mean_empty_area_fraction": 0.0044581874447536,
    "sem_empty_area_fraction": 0.0005448059632589,
    "n_fields": 7,
    "n_objects": 859
  },
  {
    "condition": "B",
    "time_h": 0.0,
    "mean_empty_area_fraction": 0.0138090880510916,
    "sem_empty_area_fraction": 0.0002264511197326,
    "n_fields": 7,
    "n_objects": 3158
  },
  {
    "condition": "B",
    "time_h": 4.0,
    "mean_empty_area_fraction": 0.0159150610393171,
    "sem_empty_area_fraction": 0.0011019283039892,
    "n_fields": 7,
    "n_objects": 564
  },
  {
    "condition": "B",
    "time_h": 8.0,
    "mean_empty_area_fraction": 0.0239331148418327,
    "sem_empty_area_fraction": 0.0016049805499992,
    "n_fields": 7,
    "n_objects": 545
  },
  {
    "condition": "B",
    "time_h": 12.0,
    "mean_empty_area_fraction": 0.0402799733501556,
    "sem_empty_area_fraction": 0.0031537325464317,
    "n_fields": 7,
    "n_objects": 496
  },
  {
    "condition": "B",
    "time_h": 24.0,
    "mean_empty_area_fraction": 0.0891834703945908,
    "sem_empty_area_fraction": 0.0078546202289423,
    "n_fields": 7,
    "n_objects": 349
  }
]
LEADER_TASK:
目标：解释并预测内部 RNA-poor cavity 的空面积分数 \(f(t)\)（图像分割面积比；0–24 h），并为 36、48 h 提交外推承诺。

当前认识：A 中 \(f\) 从约 0.0149 降至约 0.004 并维持；B 从约 0.0138 升至约 0.089。初始值相近，后续轨迹分离。每条件只有两次独立制备，字段和对象不能当作独立制备重复。**来源识别：**我目前不能确认具体研究或目标论文。

主要缺口：扩增处理可能改变 RNA 模板组成，也可能带入反应残留；现有观察无法区分这些因果路径，也没有证据把模板变化连接到 cavity 的形成。

选择的方法卡：请求 **M02**（区分因果路径）、**M15**（补齐处理到表型的机制链）、**M33**（选择区分候选的证据）。

主任务：
- 给谁/由谁执行：研究 agent；请协调者附上上述方法卡，并释放原始 DNA 序列/读段频率。
- 输入与可见来源：案例观察及本轮释放的序列/频率；不使用目标论文或截止日期后的背景。
- 具体操作与交付物：比较 A、B 模板组成；提出至少两个仍可行的解释（模板异质性与反应残留等），画出“扩增条件 → 中间状态 → 空面积分数”的机制链，标明每条边的依据或未知项；给出各解释对现有可申请测量的不同预测。
- 验收条件：报告序列分析方法和结果；不得把序列差异直接等同于机制证据；明确至少一项可区分解释的观测及其预测方向。
- 预算上限：一个证据类别释放；不申请新物理实验。
- 行动前的区分预测或预期产物：若 B 有可量化的模板组成差异，异质性解释获得候选中间环节，但仍需相分浓度或组成比例与表型的联系；若无明显差异，则该解释减弱，残留或未测变量仍待检验。

若结果为有组成差异，下一步请求模板比例端点数据并评估是否能连接到相分配；若没有，比较反应残留解释所需的证据。  
本轮新增假设：无；以上均为待检验候选。  
预算变化与停止条件：已请求 3 张方法卡和 1 项证据释放；拿到数据后优先产出可检验的区分预测。

METHOD_CARDS:
[
  {
    "id": "M02",
    "group": "A 观察与问题构造",
    "name": "因果图与替代路径",
    "tags": [
      "causal",
      "confounding",
      "intervention"
    ],
    "trigger": "条件A/B有差异，但处理同时改变多种因素。",
    "required_inputs": "处理步骤、已测协变量、可能的共同原因。",
    "steps": [
      "画处理—中间状态—结果的有向图",
      "显式列出携带、选择和测量路径",
      "对每条替代路径提出阻断或匹配方案"
    ],
    "deliverable": "候选因果图、识别假设和可实施干预。",
    "failure_or_limit": "图的方向是待检验假设；相关数据通常不足以唯一确定因果图。",
    "if_blocked": "选择能分开两张图的干预或保留不可识别性。",
    "source_ids": [
      "P10"
    ],
    "basis": "direct_method_adaptation",
    "evidence_note": "来源支持基础方法；本卡的触发条件、交付约定和方法衔接为本项目整理，未验证其在新案例上的收益。"
  },
  {
    "id": "M15",
    "group": "D 机制组合与表示修订",
    "name": "机制图补桥与串联组合",
    "tags": [
      "composition",
      "missing_link"
    ],
    "trigger": "分别知道A影响B、C影响D，却解释不了从处理到结果的整条链。",
    "required_inputs": "知识模块、观测约束和目标因果链。",
    "steps": [
      "为每个模块列输入输出和尺度",
      "只连接变量含义与单位相容的接口",
      "标出新增的桥接假设并推导组合特有预测"
    ],
    "deliverable": "最小机制图、一个关键缺边及可测后果。",
    "failure_or_limit": "把两个术语并列不构成连接；组合后仍需核对共同前提。",
    "if_blocked": "用M14补关系，或M33检验桥接假设。",
    "source_ids": [
      "P03",
      "P13",
      "P14"
    ],
    "basis": "engineering_synthesis",
    "evidence_note": "来源支持基础方法；本卡的触发条件、交付约定和方法衔接为本项目整理，未验证其在新案例上的收益。"
  },
  {
    "id": "M33",
    "group": "F 模型批评与区分实验",
    "name": "选择能区分候选的实验",
    "tags": [
      "experimental_design",
      "indistinguishable",
      "missing_data"
    ],
    "trigger": "多个模型都解释现有数据。",
    "required_inputs": "候选及预测分布/范围、可达条件、噪声与成本。",
    "steps": [
      "枚举有限可达实验",
      "比较不同模型预测差异相对噪声和成本",
      "事前写出结果与各模型更新规则"
    ],
    "deliverable": "最有信息价值的下一实验及承诺预测。",
    "failure_or_limit": "无概率模型时只是分离度代理；所选候选若共同漏掉真机制，实验也会偏。",
    "if_blocked": "保留异常结果入口；若全模型都失败转M41。",
    "source_ids": [
      "P01",
      "P09"
    ],
    "basis": "direct_method_adaptation",
    "evidence_note": "来源支持基础方法；本卡的触发条件、交付约定和方法衔接为本项目整理，未验证其在新案例上的收益。"
  }
]
RELEASED_SEQUENCE_MEASUREMENTS:
{
  "reference_sequence": "GGGCATTCTAATACGACTCACTATAGGACCGTCAGAGGACACGGTTAAAAAGTCCTCATTCGTGGCCGCATCGCGAAAGCGGCCACGGGATTCTGTGCTGCACATTAGAGTCGCTGTATGACCCATCGCGAAAGGGTCGTACAGCGGCTCTAGTGTGCTCGCGTGGATCCCGACTGGCACCATCGCGAAAGGTGCCAGGTAACGAATGGATCCACGCGTCACTCGTAGCATTGTGCCTGTCTCCATCGCGAAAGGAGATAGGCACAGTGCTATGAGTGTGCACGGAATCC",
  "reference_read_fraction": 0.9466,
  "other_reads": [
    {
      "sequence": "GGGCATTCTAATACGACTCACTATAGGACCGTCAGAGGACACGGTTAAAAAGTCCTCATTCGTGGCCGCATCGCGAAAGCGGCCACGGGATTCTGTGCTGCACATTAGAGTCGCTGTATGACCCATCGCGAAAGGGTCGTACAGCGGCTCTAGTGTGCTCGCGTGGATCCCGACTGGCACCATCGCGAAAGGTGCCAGGTAACGAATGGATCCACGCGTCACTCGTAGCATTGTGCCTGTCTCCATCGCGAAAGGAGATAGGCACAGTGCTATGAGTGTGCACGGAATCCCGTGGCCGCTTTCGCGATGCGGCCACGAATGAGGACTTTTTAACCGTGTCCTCTGACGGTCCTATAGTGAGTCGTATTAGAATGCCCA",
      "length_nt": 378,
      "read_fraction": 0.0265
    },
    {
      "sequence": "GGGCATTCTAATACGACTCACTATAGGACCGTCAGAGGACACGGTTAAAAAGTCCTCATTCGTGGCCGCATCGCGAAAGCGGCCACGGGATTCCGTGCACACTCATAGCACTGTGCCTATCTCCTTTCGCGATGGAGACAGGCACAATGCTACGAGTGACGCGTGGATCCATTCGTTACCTGGCACCTTTCGCGATGGTGCCAGT",
      "length_nt": 205,
      "read_fraction": 0.0125
    },
    {
      "sequence": "GGGCATTCTAATACGACTCACTATAGGACCGTCAGAGGACACGGTTAAAAAGTCCTCATTCGTGGCCGCATCGCGAAAGCGGCCACGGGATTCTGTGCTGCACATTAGAGTCGCTGTATGACCCATCGCGAAAGGGTCGTACAGCGGCTCTAGTGTGCTCGCGTGGATCCCGACTGGCACCATCGCGAAAGGTGCCAGGTAACGAATGGATCCACGCGTCACTCGTAGCATTGTGCCTGTCTCCATCGCGAAAGGAGATAGGCACAGTGCTATGAGTGACGCGTGGATCCATTCGTTACCTGGCACCTTTCGCGATGGTGCCAGTCGGGATCCACGCGAGCACACTAGAGCCGCTGTACGACCCTTTCGCGATGGGTCATACAGCGACTCTAATGTGCAGCACAGAATCCCGTGGCCGCTTTCGCGATGCGGCCACGAATGAGGACTTTTTAACCGTGTCCTCTGACGGTCCTATAGTGAGTCGTATTAGAATGCCCA",
      "length_nt": 498,
      "read_fraction": 0.0075
    },
    {
      "sequence": "GGGCATTCTAATACGACTCACTATAGGACCGTCAGAGGACACGGTTAAAAAGTCCTCATTCGTGGCCGCATCGCGAAAGCGGCCACGGGATTCTGTGCTGCACATTAGAGTCGCTGTATGACCCATCGCGAAAGGGTCGTACAGCGGCTCTAGTGTGCTCGCGTGGATCCCGACTGGCACCATCGCGAAAGGTGCCAGGTAACGAATGGATCCACGCGTCACTCGTAGCATTGTGCCTGTCTCCATCGCGAAAGGAGATAGGCACAGTGCTATGAGTGTGCACGGAATCCCGTGGCCGCTTTCGCGATGCGGCCACGGGATTCCGTGCACACTCATCACGCTGTGCCTATCTCCTTTCGCGATGGAGACAGGCACAATGCTACGAGTGACGCGTGGATCCATTCGTTACCTGGCACCTTTCGCGATGGTGCCAGTCGGGATCCACGCGAGCACACTAGAGCCGCTGTACGACCCTTTCGCGATGGGTCATACAGCGACTCTAATGTGCAGCACAGAATCCCGTGGCCGCTTTCGCGATGCGGCCACGAATGAGGACTTTTTAACCGTGTCCTCTGACGGTCCTATAGTGAGTCGTATTAGAATGCCCA",
      "length_nt": 608,
      "read_fraction": 0.0035
    }
  ]
}

Coordinator note: A is the reference template; the measured read fractions describe B. These are DNA reads, not post-transcription RNA concentrations. No folding interpretations are supplied. Numerical calculations are mediated: request the exact calculation and do not pretend it has run. Your reply is researcher turn 1 of at most 6. Do not directly use further tools or project memory.
