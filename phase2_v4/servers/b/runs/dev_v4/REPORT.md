# 理论发现 agent：第二轮工具辅助修订实验

任务拆分：`dev`；每种方法应完成 4 个任务；当前完整性：完整。

语言模型执行后端：`cuda`。不同后端与精度的运行分别保存，不合并得分。

本实验检验共享表征操作集合中的模型修订与主动实验。模型只能选择预定义的表征操作，系数由数值工具拟合；结果用于评价受约束的再发现流程。

## 实际结果

NMSE 是独立干预轨迹的均方误差除以各轨迹方差（分母下限 0.02）；越低越好。共同接受规则为训练实验的留一轨迹验证 NMSE < 0.05；接受后测试 NMSE > 0.1 记为错误接受。这些阈值在运行前固定。

| 方法 | 已完成 | 测试 NMSE 中位数 | 测试 NMSE 均值 | 测试 < 0.1 | 接受 / 错误接受 | 无效输出 / 调用 | 显存峰值 GB | 进程内存峰值 GB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| plain | 4 | 0.00083 | 0.00127 | 4 | 4 / 0 | 0 / 16 | 14.86 | 5.02 |
| retrieval | 4 | 0.00068 | 0.00119 | 4 | 4 / 0 | 0 / 16 | 14.92 | 5.02 |
| structured | 4 | 0.00171 | 0.00178 | 4 | 4 / 0 | 3 / 16 | 14.99 | 5.03 |
| no_active | 4 | 0.00113 | 0.00131 | 4 | 4 / 0 | 2 / 16 | 14.99 | 5.03 |
| shuffled | 4 | 0.00055 | 0.00113 | 4 | 4 / 0 | 0 / 16 | 14.99 | 5.02 |

## 配对比较

比值为 structured / 对照 的几何平均 NMSE 比值，小于 1 表示 structured 的误差较低。区间为按机制族及实例分层重采样得到的描述性区间，任务族较少，不能解释为对任意科学问题的泛化保证。

- 对 plain：4 个配对任务，胜出 1 个；误差比 1.223，描述性 95% 区间 [0.686, 2.669]。
- 对 retrieval：4 个配对任务，胜出 0 个；误差比 1.387，描述性 95% 区间 [1.000, 2.669]。
- 对 shuffled：4 个配对任务，胜出 0 个；误差比 1.510，描述性 95% 区间 [1.000, 3.445]。
- 对 no_active：4 个配对任务，胜出 0 个；误差比 1.468，描述性 95% 区间 [1.074, 2.006]。

## 按机制族分解

| 机制族 | plain | retrieval | structured | no_active | shuffled |
|---|---:|---:|---:|---:|---:|
| clock | 0.00087 | 0.00087 | 0.00321 | 0.00182 | 0.00062 |
| cubic | 0.00294 | 0.00294 | 0.00294 | 0.00276 | 0.00294 |
| linear | 0.00080 | 0.00048 | 0.00048 | 0.00021 | 0.00048 |
| memory | 0.00047 | 0.00047 | 0.00047 | 0.00044 | 0.00047 |

## 如何解释

- plain：普通 agent；retrieval：同一 agent 加跨领域材料；structured：同样材料加显式结构映射与条件检查；no_active：结构化方法采用固定实验顺序。
- state_fixed：当前状态线性模型与固定实验；history_cv：全部共享表征的验证搜索及预测分歧选实验。本轮各 agent 得到相同的候选验证误差和实验预测分歧。每任务拟合调用为 state_fixed 7 次、history_cv 51 次、各 agent 52 次；agent 另有 4 次真实模型生成。shuffled 的机制内容束被循环错配，标识与领域保留。
- 跨领域材料是人工整理的四份机制卡片，当前实现没有开放网络检索。表征操作包含历史、延迟、非线性与时钟；选择这些操作尚不能视为自主创造新的科学概念。
- dev 使用 seed 201 的 linear、cubic、memory、clock；eval 为 seeds 31、32、33，含全部八个机制族。与首轮任务分离，检验规定模拟器族中的迁移。
- 单次任务的机制选择不具有唯一性。报告主要依赖独立干预预测，允许等价或近似表征。
- 每个任务保留原始提示、真实模型输出、格式错误、预测先于观测的时间与哈希、观测数组、检查点及最终模型。无效输出采用显式确定性回退，并计入结果。
- 语言模型未直接读取隐藏机制、参数或测试轨迹。记录中的 family 字段只用于完成模型提交后的评测汇总。

## 产物

`manifest.json` 保存任务、配置和源码哈希；`summary.json` 保存统计；每个方法/任务目录保存全部轨迹与决策。模型文件哈希和环境版本由服务器调度器另行保存。

## 本轮判断

本轮结果尚不能清楚区分 structured 与 retrieval 的表现；当前证据不支持宣称显式结构映射有稳定优势。

## 映射与修订操作

```json
{
  "source_counts": {
    "structured": {
      "counts": {
        "storage": 8,
        "none": 1,
        "saturation": 3,
        "memory_multiscale": 3,
        "external_clock": 1
      },
      "total": 16,
      "valid_non_none": 12,
      "invalid": 3
    },
    "no_active": {
      "counts": {
        "none": 3,
        "storage": 7,
        "saturation": 2,
        "external_clock": 4
      },
      "total": 16,
      "valid_non_none": 13,
      "invalid": 0
    },
    "shuffled": {
      "counts": {
        "storage": 8,
        "saturation": 3,
        "none": 1,
        "external_clock": 4
      },
      "total": 16,
      "valid_non_none": 15,
      "invalid": 0
    }
  },
  "representation_changes": {
    "no_active": {
      "tasks": 4,
      "tasks_with_revision": 2,
      "transitions": 12,
      "revisions": 2
    },
    "retrieval": {
      "tasks": 4,
      "tasks_with_revision": 2,
      "transitions": 12,
      "revisions": 3
    },
    "plain": {
      "tasks": 4,
      "tasks_with_revision": 2,
      "transitions": 12,
      "revisions": 3
    },
    "structured": {
      "tasks": 4,
      "tasks_with_revision": 3,
      "transitions": 12,
      "revisions": 4
    },
    "shuffled": {
      "tasks": 4,
      "tasks_with_revision": 2,
      "transitions": 12,
      "revisions": 3
    }
  }
}
```

有效非空来源仅表示操作被调用，语义正确需要独立审读。分机执行时的完整判断需合并基线与 agent 配对结果，保留各主机 manifest。
