## 八、我认为最值得继续讨论的，是科学家究竟如何产生新的概念

上面讨论的系统仍有一个更深的局限。

所有方程都在已经给定的变量上进行搜索。

但是，重大科学突破有时不是发现了变量之间的新关系，而是发现了一个过去没有被正确定义的新变量。

例如，过去物理学家看到许多运动现象，后来才逐渐形成能够统一解释现象的动量、能量等概念。

这和只在一个预先给定的表达式空间中搜索完全不同。

2025 年的 [AI-Newton: A Concept-Driven Physical Law Discovery System without Prior Physical Knowledge](https://arxiv.org/abs/2504.01538?utm_source=chatgpt.com)就沿着这个问题开展研究，尝试从多种力学实验中自动构建物理概念并重新发现牛顿力学定律。Nature 也专门报道了这一方向，不过其研究仍属于早期概念验证。

这意味着，未来真正具有突破性的 Scientific Agent，可能需要同时做到：

\\[ \\boxed{ \\begin{aligned} \\text{发现变量}&\\rightarrow\\text{构造概念}\\\\ &\\rightarrow\\text{推导方程}\\\\ &\\rightarrow\\text{识别适用边界}\\\\ &\\rightarrow\\text{设计实验}\\\\ &\\rightarrow\\text{修正理论} \\end{aligned} } \\]

这比单纯让 Agent 调用工具、预测数据、做符号回归难得多，但也更接近科学发现的本质。

## 九、我们下一步应该选哪一个问题？

我现在会把值得继续深入的研究机会分成三个方向。

A. Agent 自主创造新的科学概念

让模型从多组实验中发现能够统一不同现象的中间变量，而不是只寻找已知变量的函数关系。

科学想象空间最大，但与 AI-Newton 等已有工作存在直接竞争，任务难度也最高。

B. Agent 发现规律在什么条件下失效

寻找相变、机制转换、策略突变和稳定性边界，并通过主动实验和数学证书验证。

可以结合复杂系统、博弈论、统计物理、经济学与 AI，较容易建立清晰的理论问题。

C. Agent 从微观行为推导宏观经济规律

先学习真实人的选择，再研究价格、社会互动和市场规则如何共同决定群体均衡与政策效果。

与你之前研读的 Centaur 衔接最好，实际应用潜力强，但因果识别和外部验证尤其困难。

我的建议是：先深入 B，再考虑把 C 作为真正的应用场景。A 可以同时作为长期研究方向阅读，但不宜一开始就承诺实现通用科学概念创造。

这样研究的起点不是“我要做一个什么 Agent”，而是一个具体、可证明且可实验检验的科学问题：

能否让 AI 从有限观测和主动干预中，发现复杂系统发生机制转换的条件，并可靠地判断哪些结论已经得到证明、哪些只是尚待验证的猜想？

如果我们最终能够让系统在从未见过的物理、行为或经济模型上，发现正确的机制边界，以比已有方法更少的实验获得可校验的结论，那才是一项有实质贡献的研究。



# 研究方向 B：让 AI Agent 发现科学规律的失效边界

研究定位 · 数学模型 · Agent 架构 · 原创性 · 实验方案

我认为这个方向值得认真做，而且它可能比单纯开发一个科学研究 Agent 更有深度。不过，经过进一步检索，我想把研究目标修改得更加精确：

我们不是让 Agent 寻找一个模型预测不准的地方，而是让它发现一个系统在什么条件下，会从一种运行机制转变为另一种运行机制，并解释为什么这种变化必然发生。

这里面包含三个层次：

1. 发现边界（Discovery）：临界条件在哪里？
2. 解释边界（Explanation）：为什么到了这个条件，系统的行为会改变？
3. 验证边界（Certification）：能否证明边界存在，或者给出带有可靠误差保证的临界区间？

我最看重第三个层次。因为它有机会让研究从一般的 AI for Science 应用，进入机器学习理论、非线性动力学和自动科学发现的交叉领域。

## 一、为什么这个科学问题重要？

科学中很多重大现象，并不是某个变量平稳变化，而是在一定条件下发生性质上的突然改变。

[PPT - Tipping Points in Ecology: Dynamics of Bifurcations and Regime Shifts PowerPoint Presentation - ID:5082080](https://images.openai.com/static-rsc-4/KavSuG3V70dY13UA3E1Epl6v6VyW0kPa2vPRhtSU3HwCn3Dr4tV0VQgKAl4E_rw8qdgNcE6L39FCbEMvpPE5yefiZne-s8j4c01_jN8pt0YNI-bzFuxLm8gAWIxYndZK-oRhjpYLfESx_fVsUw_pcf9Ke86USkrsqRujew_A6ng?purpose=inline)

生态系统：湖泊从清澈变得浑浊

当营养物输入和生态反馈发生变化，湖泊可能从清水状态转向藻类占优的浑水状态。某些系统甚至具有滞后效应：恢复原来的营养输入，也未必能立即恢复清水状态。

[Magnetisches Glühen, thermische und thermo-chemische industrielle Teilebehandlung](https://images.openai.com/static-rsc-4/kal69wJeQLpNXEpnQ8XSwS_U_xkzr7t4GZ3tsfGvHytQSpvs3-XsGEbkLlnKLIvzhfiJCybiASy-w3ifdPlTvjm2THIVzO7imj2R6Aufd694935ug0YBY7aEo1BKT126IcqWKJbEJQMfOY2t3xRAYRktfIXQKDFN2kMKngcb3FA?purpose=inline)

物理学：材料发生相变

铁磁性材料在居里温度附近，其宏观磁有序性质发生变化。描述材料的微观相互作用可以连续变化，但宏观状态呈现出不同的物理性质。

[Critical Infrastructure Protection | Ultra I&C](https://images.openai.com/static-rsc-4/AqezetOIRPbd1KSnF_oi1LuvItavldgaVFQf-Uj0Psw6eEpd5opcuXewMgEM1aVJ807LiGsTyGOT9AZ3pmxwat-9iuV83F6edNfCm8NBRA3Uu-LZkyr8nRvrDkWdTuqmUsaNXafDFOnVgFJIn0nQ5jSbIEdJiTt2QncJGVaeWTk?purpose=inline)

能源系统：从正常运行到失稳

随着负载增加，系统可能逼近电压稳定性边界。继续增加负载可能导致运行点失去稳定性，甚至触发更严重的系统故障。

Nature 在 2009 年发表的经典综述 [Early-warning signals for critical transitions](https://www.nature.com/articles/nature08227?utm_source=chatgpt.com)就指出，生态、气候、金融等复杂系统可能存在临界转变，一些系统在接近临界点时会表现出恢复速度减慢等预警信号。

Nature

但这也带来了一个难题：

我们观察到一个系统正在变化，究竟是在逐渐适应新的环境，还是即将失去原来的稳定状态？

这两种情况的科学含义完全不同。

### 先严格区分三种“边界”


| 类型                              | 数学上发生什么                           | 典型问题                       |
| --------------------------------- | ---------------------------------------- | ------------------------------ |
| 机制切换（RegimeSwitching）       | 控制系统的方程发生改变                   | 什么时候从摩擦滑动切换到静止？ |
| 分岔（Bifurcation）               | 同一方程随着参数变化，长期动力学性质改变 | 什么时候一个稳定均衡消失？     |
| 统计分布漂移（DistributionShift） | 数据生成分布发生变化                     | 为什么原来的预测模型突然失效？ |

这三个概念不能混用。

比如，一个神经网络突然预测不准了，可能只是数据噪声变大，不能直接宣称系统发生了物理相变。

我建议我们的主要研究对象是 分岔与稳定性边界，然后再逐步拓展到机制切换。这样研究对象清晰，也更容易建立理论保证。

## 二、一个关键发现：仅仅主动寻找临界点，已经有人做过了

这次检索发现了三篇直接影响我们研究定位的论文。

CHAOS · 2025 · MIT

[Active search for bifurcations](https://doi.org/10.1063/5.0226625?utm_source=chatgpt.com)

Psarellis、Sapsis 和 Kevrekidis 利用贝叶斯优化，根据少量向量场观测主动寻找 saddle-node 和 Hopf 分岔。

直接竞争点：用最少实验定位动力系统临界点，这已经不是一个空白问题。

dspace.mit.edu

PHYSICAL REVIEW LETTERS · 2026

[Unsupervised Learning for Anticipating Critical Transitions](https://doi.org/10.1103/2v76-dmg6?utm_source=chatgpt.com)

Panahi 等通过 VAE 与 Reservoir Computing，从时间序列中学习潜在驱动因子，预测复杂系统中的临界转变。

直接竞争点：即使不知道显式分岔参数，AI 也已经可以学习潜在参数并预测转变。

Phys. Rev. Lett.

SCIENCE ADVANCES · 2025

[Real-time experiment–theory closed-loop interaction for autonomous materials science](https://pubmed.ncbi.nlm.nih.gov/40601733/?utm_source=chatgpt.com)

Liang 等的 AMASE 系统通过自主实验与热力学理论模型交互，绘制 Sn–Bi 材料的温度—成分相图，报告实验次数减少约六倍。

直接竞争点：Agent 或自动化系统主动寻找实际材料相边界，也已经有强实证工作。

pubmed.ncbi.nlm.nih.gov

这说明，研究如果只是：

> 用 LLM + Bayesian Optimization + Simulator，更快找到一个分岔点。

我不建议投入大量精力，因为很难证明本质创新。

更有价值的切入点可能是：

当我们不知道真实方程、实验存在噪声、临界参数还可能有多个时，能不能让 Agent 自动发现稳定与失稳的数学条件，并在证据不足时主动拒绝作出确定结论？

下面我们从一个可以完整推导的模型开始，把它变成严肃的研究问题。

## 三、从一个真正的数学问题开始：Agent 能否自己发现“临界曲线”？

我想用一个经典的非线性动力系统，先把研究目标彻底讲清楚。

假设有一个系统，其状态 \\(x(t)\\)随时间变化，我们可以调整外界环境参数 \\(\\mu\\)和内部反馈参数 \\(\\nu\\)。

真实机制是：

\\[ \\boxed{ \\frac{dx}{dt}=\\mu+\\nu x-x^3 } \\tag{1} \\]

你可以把它想象成：

* \\(x\\)：生态系统中某种生物的相对状态、神经元群体活动的简化指标，或者抽象的市场状态变量；
* \\(\\mu\\)：外部刺激、政策干预或环境压力；
* \\(\\nu\\)：内部正反馈的强度。

这里使用的是经典的 cusp catastrophe 正规形（尖点分岔模型），不是我们提出的新自然定律，也不意味着所有这些应用都服从这个方程。

关键是：研究者知道真实方程，但我们的 Agent 不知道。

Agent 只能选择实验条件，观察状态如何变化。

### 1. 为什么这个简单方程很有意思？

一个系统长期停留的平衡状态满足：

\\[ \\frac{dx}{dt}=0 \\]

所以：

\\[ \\boxed{x^3-\\nu x-\\mu=0} \\tag{2} \\]

这是一个三次方程。

我们最感兴趣的，不仅是它的解是多少，而是 它有多少个平衡点，以及这些平衡点是否稳定。

首先，一个平衡点 \\(x^\*\\)局部渐近稳定的充分条件是：

\\[ \\left.\\frac{\\partial f}{\\partial x}\\right|\_{x^\*}<0 \\]

其中：

\\[ f(x;\\mu,\\nu)=\\mu+\\nu x-x^3 \\]

因此：

\\[ \\boxed{f\_x(x;\\mu,\\nu)=\\nu-3x^2} \\]

如果导数小于 0，系统偏离平衡点一点点后，会倾向于回到原来的位置。

如果导数大于 0，微小扰动就会被放大。

### 2. 临界点什么时候出现？

当两个平衡点合并并消失时，会出现典型的 saddle-node（鞍结）分岔。

其必要的退化条件是：

\\[ \\begin{cases} f(x;\\mu,\\nu)=0\\\\ f\_x(x;\\mu,\\nu)=0 \\end{cases} \\]

将第二个条件代入：

\\[ \\nu-3x^2=0 \\]

得到：

\\[ x\_c=\\pm\\sqrt{\\frac{\\nu}{3}},\\qquad \\nu>0 \\]

再代回第一个方程：

\\[ \\mu\_c=x\_c^3-\\nu x\_c \\]

整理：

\\[ \\boxed{ \\mu\_c=\\mp\\frac{2\\nu^{3/2}}{3\\sqrt3} } \\]

所以整个系统的临界边界是：

\\[ \\boxed{ 27\\mu^2=4\\nu^3,\\qquad \\nu\\ge0 } \\tag{3} \\]

这就是我们希望 Agent 最终从实验中自主发现的规律。

在适当的非退化条件下，曲线上的非尖点位置就是 saddle-node 分岔点；\\((0,0)\\)则是一个更高阶的 cusp 退化点，不能直接用普通 saddle-node 的条件处理。

### 3. 我们观察一下临界点究竟意味着什么

固定 \\(\\nu=1\\)，有：

\\[ \\mu\_c=\\pm\\frac{2}{3\\sqrt3}\\approx\\pm0.3849 \\]

交互实验：改变外部参数

固定 \\(\\nu=1\\)

## μ = 0.38

−0.50

+0.50

# 3

平衡点数量

# 2

稳定平衡点数量

当前位于双稳态区间：有两个稳定均衡和一个不稳定均衡。不同初始状态可能导致不同长期结果。

这是已知解析方程的数学可视化，不是 Agent 已经完成的发现。调节 μ，观察平衡分支在临界点附近如何产生或消失。

我希望你特别注意中间这一段。

当：

\\[ |\\mu|<0.3849 \\]

同一个环境参数下，可能存在两个稳定均衡。

例如，同样的外部刺激条件下，一个生态系统可能停留在低状态，也可能停留在高状态，这取决于历史路径和初始条件。

而当 \\(\\mu\\)越过某个临界值，原来的稳定状态消失，系统就可能发生快速的状态转换。

这就是数学上的多稳态与分岔。

### 4. 为什么说“发现临界条件”比预测时间序列更重要？

假设传统 AI 预测某个系统下一步的状态：

\\[ \\hat x\_{t+1}=F\_\\theta(x\_t,\\mu\_t) \\]

如果它在训练分布内非常准确，我们仍然不知道：

* 系统是否存在多个稳定状态；
* 当前处于哪一个吸引域；
* 哪个参数变化会让原来的均衡消失；
* 为什么系统接近某个区域时，长期预测会变得不可靠。

但如果一个 Agent 找到了：

\\[ 27\\mu^2=4\\nu^3 \\]

它就不仅知道某几个样本上的数值结果，还获得了一条描述整个参数空间结构的规律。

尤其值得研究的是该边界的幂律关系：

\\[ \\boxed{ |\\mu\_c|=\\frac{2}{3\\sqrt3}\\nu^{3/2} } \\]

这里的 \\(3/2\\)指数反映了这一正规形下的临界曲线几何结构。

在一个不知道真实方程的实验环境中，Agent 能否从有限次实验中发现临界曲线及其指数，并证明结果不只是偶然拟合？

这才是我们要研究的科学问题。这个经典模型只是最初的验证案例；若仅恢复上述已知指数，不足以构成原创性贡献。

## 四、假如我们真的开发这个 Agent，它要做哪些事情？

刚才的推导是我们作为研究者知道答案的情况。现在反过来：把真实方程完全隐藏，只让 Agent 通过实验来认识系统。

### 1. 先定义科学实验环境

设真实系统为：

\\[ \\dot{\\mathbf x}(t)=f^\*(\\mathbf x(t),\\boldsymbol\\lambda) \\]

其中：

* \\(f^\*\\)：未知的真实动力学；
* \\(\\mathbf x\\)：系统状态；
* \\(\\boldsymbol\\lambda\\)：外部可调节参数。

Agent 每次可以申请一个实验：

\\[ e\_t=(\\boldsymbol\\lambda\_t,\\mathbf x\_{0,t},T\_t) \\]

也就是：设置什么参数、从哪个初始状态开始、观测多长时间。

实验平台返回：

\\[ \\mathcal O\_t= \\{y(t\_1),y(t\_2),\\ldots,y(t\_m)\\} \\]

其中：

\\[ y(t\_k)=h(\\mathbf x(t\_k))+\\epsilon\_k \\]

\\(h\\)是观测函数，\\(\\epsilon\_k\\)是测量误差。

注意，这里只给 Agent 带噪声的轨迹观测，而不是直接提供真实方程或精确导数。

这比直接查询 \\(f(\\mathbf x,\\lambda)\\)的实验环境更困难，也更接近现实。MIT 2025 年的 Active Search for Bifurcations 明确利用少量向量场观测，而我们的一个潜在差异化方向，是研究只能获得有限轨迹的实验环境。

dspace.mit.edu

但这不是说以前没人研究过从轨迹识别分岔；区别必须通过严谨基准测试来证明。

### 2. Agent 的完整工作过程

Scientific Hypothesis

根据已有实验，建立多个候选动力学模型

模型 A

\\(\\dot x=\\mu-x^3\\)

模型 B

\\(\\dot x=\\mu+x-x^3\\)

Disagreement Analysis

找到两个候选模型预测结果分歧最大的实验条件

Active Experimentation

控制参数、初始化状态、运行实验并收集数据

Model Revision

淘汰不符合证据的模型，更新候选方程

Mathematical Verification

求解分岔条件，检验稳定性，生成可核查证书

下一轮实验或输出研究结果

若证据不足，标记未知区域并继续实验

这类系统不一定需要六个乃至十几个 LLM Agent。

我建议一开始只设一个负责提出假设和选择工具的 LLM Agent，其他部分使用确定性的统计、优化和数学工具。

真正要设计的是 Agent 的决策算法，不是多 Agent 的聊天结构。

### 3. Agent 该如何选择下一个实验？

最基础的思路是：选择预测分歧大的地方。

假设当前有 \\(K\\)个候选模型：

\\[ \\mathcal M=\\{M\_1,\\ldots,M\_K\\} \\]

针对一次实验 \\(e\\)，每个模型都会产生预测：

\\[ p(y\\mid e,M\_k) \\]

一个经典的实验选择目标是最大化模型身份的信息增益：

\\[ e^\*= \\arg\\max\_e I(M;Y\_e\\mid\\mathcal D\_t) \\]

但这仍然是现有主动学习和贝叶斯实验设计的思想。

我想提出一个不同的目标：不只是最大化模型之间的分歧，而是优先让我们能够证明哪些区域稳定、哪些区域存在临界转变。

定义：

* \\(\\Lambda\\)：需要研究的参数空间；
* \\(\\mathcal C\_t\\)：当前已经能够可靠判定动力学性质的区域；
* \\(c(e)\\)：一次实验的总成本。

可以考虑：

\\[ \\boxed{ e\_t^\*= \\arg\\max\_e \\frac{ \\mathbb E\\left[ \\operatorname{Vol}(\\mathcal C\_{t+1}) -\\operatorname{Vol}(\\mathcal C\_t) \\mid e \\right] }{ c(e) } } \\tag{4} \\]

换句话说：

> 哪一次实验最有希望让原本无法确定的区域，变成我们能够提供数学或统计保证的区域？

这是一种 Certification-aware Experiment Design的候选算法目标。

它与传统实验选择的主要区别是：


| 传统方法可能优化 | 我们希望优化             |
| ---------------- | ------------------------ |
| 预测误差下降     | 可验证区域扩大           |
| 模型预测方差减少 | 临界边界的不确定区间收缩 |
| 找到单个临界点   | 获得整个参数区域的性质   |
| 实验数量最少     | 实验与观测时间总成本最小 |
| 输出一个预测标签 | 输出结论、证书或未知     |

必须强调，这一形式目前是研究设计，不是已经证明优于现有 acquisition function 的新算法。它能否比已有方法更有效，需要理论分析与实验检验。

## 五、这个方向真正困难的地方，是科学上的“不可识别性”

我认为这里存在一个非常有价值、但经常被忽略的问题。

假设我们只做了十次实验，全部远离临界区域。

那么可能存在两个不同的动力系统：

* 系统 A 在所有已经观察的位置表现正常，在别的参数位置仍然稳定。
* 系统 B 在所有已经观察的位置与 A 完全相同，但在某个还没有采样的狭小区域发生分岔。

例如，对一个已知函数 \\(f\_0(x,\\lambda)\\)，构造：

\\[ f\_1(x,\\lambda)= f\_0(x,\\lambda)+a\\phi(x,\\lambda) \\]

其中 \\(\\phi\\)是一个只在尚未观测区域非零的光滑 bump function。

通过适当选择它的幅度和形状，可以让 \\(f\_1\\)在未观测区域具有与 \\(f\_0\\)不同的平衡结构。

但在所有已观测区域：

\\[ f\_0(x,\\lambda)=f\_1(x,\\lambda) \\]

因此，即使模型在已有数据上完全正确，也无法据此排除尚未发现的临界现象。

这说明：

\\[ \\boxed{ \\text{有限观测} \\not\\Rightarrow \\text{全局规律完全可识别} } \\]

这并不是模型能力不足，而是信息本身不足。

2026 年的一篇 [Nature Communications：Adversarial dynamical systems characterize when data-driven learning succeeds or fails](https://www.nature.com/articles/s41467-026-74220-8?utm_source=chatgpt.com)专门研究了动力系统数据驱动学习的可学习性边界，表明即使算法不断改进，也存在需要从数学上认真处理的不可学习情形。

Nature Communications

因此，我认为我们的研究必须预先规定一些假设，例如系统具有有界光滑性、实验可干预范围已知、观测噪声有合理限制，或者真实方程属于某个受约束的函数族。

如果这些假设不成立，Agent 必须能够回答：

“目前证据不足，不能判定。”

这反而可能成为一项非常重要的设计原则：不是追求永远给出结论，而是研究在何种证据条件下，结论才可以被可靠宣布。

## 六、我们真正能证明什么？先推导一个小定理

为了避免把“证明”只当成一个包装词，我们可以先建立一个形式上严谨的目标。

假设现在考虑一维连续系统：

\\[ \\dot x=f(x;\\lambda) \\]

Agent 学到一个估计模型：

\\[ \\hat f(x;\\lambda) \\]

并且通过有效统计方法，在一个区间 \\(I=[a,b]\\)上获得了如下误差保证：

\\[ \\sup\_{x\\in I}|f(x;\\lambda)-\\hat f(x;\\lambda)| \\leq\\epsilon\_0 \\]

\\[ \\sup\_{x\\in I}|f\_x(x;\\lambda)-\\hat f\_x(x;\\lambda)| \\leq\\epsilon\_1 \\]

现在提出三个可验证条件：

\\[ \\begin{cases} \\hat f(a;\\lambda)>\\epsilon\_0\\\\ \\hat f(b;\\lambda)<-\\epsilon\_0\\\\ \\sup\_{x\\in I}\\hat f\_x(x;\\lambda)<-\\epsilon\_1 \\end{cases} \\tag{5} \\]

如果这些条件成立，我们可以证明：

在区间 \\((a,b)\\) 中，真实系统存在唯一的平衡点，并且它局部渐近稳定。

为什么？

首先，根据误差界：

\\[ f(a;\\lambda)>0,\\qquad f(b;\\lambda)<0 \\]

由连续函数的介值定理，至少存在一个 \\(x^\*\\in(a,b)\\)，使得：

\\[ f(x^\*;\\lambda)=0 \\]

其次，因为：

\\[ f\_x(x;\\lambda) \\leq\\hat f\_x(x;\\lambda)+\\epsilon\_1<0 \\]

所以 \\(f\\)在整个区间严格递减。

因此，平衡点只能有一个。

最后：

\\[ f\_x(x^\*;\\lambda)<0 \\]

说明该平衡点局部渐近稳定。事实上，在该区间内，向量场还指向这个平衡点。

证毕。

注意这个证明的真正价值和局限：

* 价值：给定有效的函数和导数误差界，就能将一个学习模型转化为关于真实系统的可验证结论。
* 局限：上述证明本身是标准微积分和动力系统结论，不构成创新。真正困难的是从有限、带噪声、可能被自适应选择的数据中，得到可信的统一误差界。

如果我们能够证明这样的误差界以至少 \\(1-\\delta\\)的概率同时成立，那么相应的稳定性结论也具有至少 \\(1-\\delta\\)的覆盖保证。

我们还可以反过来构造不能存在平衡点的证书，以及使用区间 Newton、Krawczyk 算子等方法验证分岔点附近的方程组。

对于 saddle-node，通常需要验证：

\\[ \\boxed{ \\begin{aligned} f(x\_c,\\lambda\_c)&=0\\\\ f\_x(x\_c,\\lambda\_c)&=0\\\\ f\_{xx}(x\_c,\\lambda\_c)&\\ne0\\\\ f\_\\lambda(x\_c,\\lambda\_c)&\\ne0 \\end{aligned} } \\tag{6} \\]

前两项定位退化平衡点，后两项提供通常的一参数非退化条件。

这样才有机会从“Agent 猜测临界位置”上升为“Agent 提交一个可以独立检查的临界点证书”。

另外，自适应实验不能简单套用固定样本量的置信区间。2024 年的 [Semiparametric Efficient Inference in Adaptive Experiments](https://proceedings.mlr.press/v236/cook24a.html?utm_source=chatgpt.com)研究了自适应实验中的高效推断与 anytime-valid confidence sequences，可以作为我们处理自适应停止和统计覆盖问题的理论参考。

proceedings.mlr.press

## 七、这里还有一个很有意思的数学现象：越接近临界点，实验反而可能越昂贵

这是我认为 B 方向值得重点挖掘的一个细节。

考虑 saddle-node 分岔最简单的正规形：

\\[ \\dot z=\\eta-z^2 \\]

当 \\(\\eta>0\\)时，有两个平衡点：

\\[ z\_\\pm=\\pm\\sqrt{\\eta} \\]

其中稳定平衡点为：

\\[ z^\*=\\sqrt{\\eta} \\]

在稳定点附近进行线性化，令：

\\[ z=z^\*+\\delta z \\]

得到：

\\[ \\frac{d(\\delta z)}{dt} \\approx-2\\sqrt{\\eta}\\,\\delta z \\]

因此：

\\[ \\delta z(t)\\approx \\delta z(0)e^{-2\\sqrt{\\eta}t} \\]

系统的特征恢复时间为：

\\[ \\boxed{ \\tau=\\frac{1}{2\\sqrt{\\eta}} } \\]

当：

\\[ \\eta\\rightarrow0^+ \\]

就有：

\\[ \\boxed{\\tau\\rightarrow\\infty} \\]

这叫 Critical Slowing Down（临界减速）。

它告诉我们：一个系统越接近临界点，受到扰动之后恢复得可能越慢。

接近临界点时，系统恢复时间快速增加

根据 τ=1/(2√η) 计算的理论示例，非真实实验数据。

![Chart](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAvAAAAFUCAYAAABCwwgfAAAQAElEQVR4AeydC5xVZbn/nw1ycUARQgjxApam4QX8aEhaKkclS450UdE08XLSRBA9x8h7ZmqmJpTmLT2eIiU7KVon/3hI6YIimHisrNQUNUQBEeR+/8/vnf3Amj17z+yZ2Ze19vry4bee9T7r9r7fd+09v3nn3Wt32MI/CEAAAhCAAAQgAAEIQCAxBDoY/yAAAQi0iQAHQQACEIAABCBQDQIY+GpQ55oQgAAEIACBNBOg7RCAQLsItGjgN23aZO+++67V/02hXRfiYAhAAAIQgAAEIAABCECg/QQKGngZ9vvvv9/OP/98u+qqq2zcuHF2zz332PLly1t11YULF5oreqDnFKuUj152ax2pD/2lG0P3gUtll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPaeosktll+cUPReNBQ38T37yE3vmmWds9OjRduWVV9rIkSPtueeeszvuuCN6POsQgAAEUkiAJkMAAhCAAASqRyCvgf/ggw9s1qxZdsIJJ9hRRx1lu+66q40YMcIOPfRQe/31123FihVF17hfv37mih7kOUXyDYzgAAe9HlzcD9wPfi8ocj9wP+g+cHE/JPh+wBeF29fvZcWQyC5UdmVTIXhOMSSyC5Vd2VQInlMMiexCZVc2FYLnFEMiu1DZlU2F4DnFkMguVHZlUyF4TjEksguVXdlUCJ5TDImcRV4D//TTT4fdhg8fHqIvTj/9dLvpppuse/funiJCAAIQgAAEIAABCEAAAhUkkNfAL1iwwHr37m1Lly61u+66y8aPH2+XX365TZ8+3XbYYQfLZDIVrCKXKgMBTgkBCEAAAhCAAAQgkFACeQ38e++9Z5s3b7bvfOc7tnHjxjB9Zscdd7THHnvM9MHWhLaVakMAAhCAQLsJcAIIQAACEKg2gbwGfu3atWH0fdiwYTZ27Fj73Oc+ZxMnTrS99trLZs+ebUuWLKl2vbk+BCAAAQhAAAIQgECSCFDXkhHIa+B79OgRLnDEEUeE6Asvv/HGG54iQgACEIAABCAAAQhAAAIVJJDXwPfs2TNUQdNmwkp2UVdXF9Y0rSassIBA8ghQYwhAAAIQgAAEIJBoAnkN/MEHHxwaNXfu3BB9oekzWt9tt90UEAQgAAEIQCBFBGgqBCAAgXgQyGvg9913X+vVq5f94he/CF/etGjRIvvNb35jc+bMsX322cd22WWXeNSeWkAAAhCAAAQgAAEIQCDuBEpcv7wGPpPJ2BVXXBGM+j333GNXXnmlPfTQQ3bAAQfYV7/61RJXgdNBAAIQgAAEIAABCEAAAsUSyGvgdXC3bt3ssssus8mTJ4dnwCvqiTTKazuCAAQSR4AKQwACEIAABCBQAwQKGnhvW9euXW333Xc3Rc8RIQABCEAAAhBIEwHaCgEIxIlAiwY+TpWlLhCAAAQgAAEIQAACEEg7gUQZ+LR3Fu2HAAQgAAEIQAACEIAABp57AAIQSAMB2ggBCEAAAhCoGQIY+JrpShoCAQhAAAIQgEDpCXBGCMSPAAY+fn1CjSAAAQhAAAIQgAAEIFCQAAa+IJp4baA2EIAABCAAAQhAAAIQEAEMvCggCEAAArVLgJZBAAIQgECNEcDA11iH0hwIQAACEIAABCBQGgKcJa4EMPBx7RnqBQEIQAACEIAABCAAgTwEMPB5oJCKFwFqAwEIQAACEIAABCCwjQAGfhsL1iAAAQhAoLYI0BoIQAACNUkAA1+T3UqjIAABCEAAAhCAAATaTiDeR2Lg490/1A4CEIAABCAAAQhAAAKNCGDgG+GgAIF4EaA2EIAABCAAAQhAIJcABj6XCGUIQAACEIBA8gnQAghAoIYJYOBruHNpGgQgAAEIQAACEIBA7REor4GvPV60CAIQgAAEIAABCEAAAlUlgIGvKn4uDgEIFCJAHgIQgAAEIACB/AQw8Pm5kIUABCAAAQhAIJkEqDUEap4ABr7mu5gGQgACEIAABCAAAQjUEgEMfLl6k/NCAAIQgAAEIAABCECgDAQw8GWAyikhAAEItIcAx0IAAhCAAASaI4CBb44O2yAAAQhAAAIQgEByCFDTlBDAwKeko2kmBCAAAQhAAAIQgEBtEMDA10Y/xqsV1AYCEIAABCAAAQhAoGwEMPBlQ8uJIQABCECgtQTYHwIQgAAEWiaAgW+ZEXtAAAIQgAAEIAABCMSbQKpqh4FPVXfTWAhAAAIQgAAEIACBpBPAwCe9B6l/vAhQGwhAAAIQgAAEIFBmAhj4MgPm9BCAAAQgAIFiCLAPBCAAgWIJYOCLJcV+EIAABCAAAQhAAAIQiAGBHAMfgxpRBQhAAAIQgAAEIAABCECgIIFYGPgZM2bYWWedZQcddFCQ1pUrWGs2QAAC8SNAjSAAAQhAAAIQqAiBqhv42267zS655BKbN2+ebdmyJUjrymlbRShwEQhAAAIQgAAEqkaAC0MAAq0jUFUDr1H2e++9N9R4da/D7P3dzw7SupLapn20jiAAAQhAAAIQgAAEIAABs6oa+AceeCD0gQz7uu771q9ngrSuXH3BfB+tl1ecHQIQgAAEIAABCEAAAvEnUFUD/8ILLwRC67rvE2J04TnfJ7qNdQhAAAKxIkBlIAABCEAAAhUkUFUDX8F2cikIQAACEIAABCAQOwJUCAJtIVBVAz948OBQ5y4r/xZidOE53ye6jXUIQAACEIAABCAAAQiklUBVDfypp54auNctnWVdVv61fn1LkNaVqy/YH97qZbP/vECrqGwEODEEIAABCEAAAhCAQFIIVNXAH3300eH574Ilw97zzXtN0rpyPfc83NbXDbTRl0+zSVPnKoUgAAEIQCBOBKgLBCAAAQhUnEBVDbxaO27cOLvppptsyJAhlslkgrSu3JO/+IFNOOUT2s0mPTgHEx9IsIAABCAAAQhAAALJJ0AL2k6g6gZeVddI/H333WfPP/98kNaV07YJow9pZOIHnHA7Rl5gEAQgAAEIQAACEIBAKgnEwsC3RF4mfv6jYxsZeabUtESN7cURYC8IQAACEIAABCCQLAKJMPCOVEY+OqVGc+N9GxECEIAABCBQUQJcDAIQgECVCCTKwIuRTPzU60Zp1fR0GqbUBBQsIAABCEAAAhCAAAQSQqC91UycgVeDD92vvzGlRiQQBCAAAQhAAAIQgEDaCCTSwHsnTcj5gKum1GhU3rcTIQCB5giwDQIQgAAEIACBJBJItIEXcJl4TanRqLzMu0w8H3AVGQQBCEAAAhAoEwFOCwEIVJVA4g286Mm8y8RHP+CKiRcZBAEIQAACEIAABCBQawSSbOCb9IVG46MmXh9w1ah8kx1JQAACEIAABCAAAQhAIKEEasrAqw9k4vUBV43Kq8yUGlFAEIBAYwKUIAABCEAAAsklUHMG3ruCKTVOgggBCEAAAhCAQMkIcCIIxIBAzRp4sdVofO6UGubGiwyCAAQgAAEIQAACEEgqgZo28OoUmXhNqYka+Row8WoaggAEIAABCEAAAhBIIYGaN/DepzLyUROvufG+jQgBCEAgPQRoKQQgAAEIJJ1Aagy8OkomXnPjta6n0+gpNYzGiwaCAAQgAAEIQAACLRBgc2wIpMrAi7qeTsOUGpFAEIAABCAAAQhAAAJJJJA6A++dpNH43Ck1GpX37cTYEqBiEIAABCAAAQhAINUEUmvg1esy8ZpSo1F5mXfNi2dKjcggCEAAArVIgDZBAAIQqA0CqTbw6kKZd5n46Gg8Jl5kEAQgAAEIQAACEIBAIBCzReoNvPeHRuOjJl4fcNWovG8nQgACEIAABCAAAQhAIA4EMPCRXpCJ1wdcNSqvNFNqRAHFiABVgQAEIAABCEAAAoaBz3MTMKUmDxRSEIAABCCQYAJUHQIQqCUCGPgCvanR+NwpNcyNLwCLNAQgAAEIQAACEIBAxQhU1MBXrFUlupBMvKbURI08Jr5EcDkNBCAAAQhAAAIQgECbCGDgi8AmIx818ZobX8Rh7AIBCJSOAGeCAAQgAAEIQCBLAAOfBdFSkInX3Hjtp6fT6Ck1jMaLBoIABCAAAQjEmQB1g0DtEcDAt6JP9XQaptS0Ahi7QgACEIAABCAAAQiUnAAGvg1INRqfO6VGo/LNnYptEIAABCAAAQhAAAIQKAUBDHwbKcrEa0qNRuVl3jUvnik1bYTJYRCAQHME2AYBCEAAAhBoRAAD3whH6woy7zLx0dF4THzrGLI3BCAAAQhAAALlIsB5a5UABr4EPavR+KiJ5wOuJYDKKSAAAQhAAAIQgAAE8hLAwOfF0vqkTLw+4KpReR096cE5xmi8SJixhAAEIAABCEAAAhAoHQEMfOlYhjMxpSZgYAEBCECgFAQ4BwQgAAEI5CGAgc8Dpb0pjcYzpaa9FDkeAhCAAAQgAAEItJVAbR+HgS9T/8rEa0pN1MgzpaZMsDktBCAAAQhAAAIQSBEBDHyZO1tGPmri9bjJMl+S08eIAFWBAAQgAAEIQAACpSaAgS810Tznk4nX3Hht0jPjeUqNSCAIQAACEGiGAJsgAAEIFCSAgS+IprQb9HQaptSUlilngwAEIAABCEAAAmkk0LyBTyORMrdZo/G5U2o0Kl/my3J6CEAAAhCAAAQgAIEaIVCUgd+0aZNdffXVdu6559ZIs6vbDJl4TanRqLzMu+bF8wHX6vYJVy89Ac4IAQhAAAIQgEB5CBRl4B966CF75513ylODlJ5V5l0mPjoaj4lP6c1AsyEAAQhAIEqAdQhAoAUCLRr4F1980WbOnGkDBgxo4VRsbgsBjcZHTTwfcG0LRY6BAAQgAAEIQAAC6SHQrIFftmyZ3X333TZ8+HDbf//900NFLa2gZOL1AVeNyuuykx6cY4zGiwSCAAQgAAEIQAACEMglUNDAb9myxW677Tbr1auXnXjiibnHUS4DAabUlAEqp4RAFQhwSQhAAAIQgEA5CRQ08I899pgtWLDAxo8fbx06FNytxbotXLjQXNGdPadIvoGROGg0SEZ9zwAAEABJREFUvrkpNeLl0v4uzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlFll8ouzyl6TlHlhQsXBs+ksot8Awk4NHDwZV5n/sorr9ivf/1rGzNmjPXu3dv3JVaIgEz8M3d+waJGnik1FYLPZSAAAQhAAAIQgEDMCTQx8KtXr7bbb7/dDj74YBs6dGi7q9+vXz9zRU/mOUXyDYxyOcjIR028HjcpXq7c/UuWz/YZ58/fL3C2ra9pseA+4T7RfeDifuB+8HtBkfuB+0H3gYv7of33gzNsYuD1uMg1a9bYc889F577rme/S7/85S/DMVq/8sorwzqL8hOQidfceF1Jz4znKTUigSAAgbgSoF4QgAAEIFB+Ak0MfN++fe3MM89sIn8KjbaNHj26/DXjClsJ6Ok0ekpNdDSeKTVb8bACAQhAAAIQgEDyCdCCVhBoYuC7detmhx56aBMNGDAgnFbbBg0aFNZZVJaARuOjJl5TajQqX9lacDUIQAACEIAABCAAgWoSaGLgq1kZrt0yAZl4TanRqLzMu0w8o/Etcyt6D3aEAAQgAAEIQAACMSdQtIE//vjj7a677jL+VZ+AzLtMfHQ0HhNf/X6hBhCAQLoJ0HoIQAAClSJQtIGvVIW4TvEENBofNfF8wLV4duwJAQhAAAIQgAAEYkKg1dXAwLcaWbwOkInXB1w1Kq+aTXpwjjEaLxIIAhCAAAQgAAEI1CYBDHyN9CtTamqkI6vZDK4NAQhAAAIQgEAiCGDgE9FNxVVSo/FMqSmOFXtBAAIQgEDpCHAmCECgsgQw8JXlXfarycRrSk3UyDOlpuzYuQAEIAABCEAAAhCoGIEaMvAVY5aIC8nIR028HjeZiIpTSQhAAAIQgAAEIACBZglg4JvFk+yNMvGaG69W6JnxPKVGJBAE8hAgBQEIQAACEEgQAQx8gjqrLVXV02mYUtMWchwDAQhAAAIQaJkAe0CgGgQw8NWgXoVrajQ+d0qNRuWrUBUuCQEIQAACEIAABCDQDgIY+HbAi8+hxdVEJl5TajQqL/OuefF8wLU4duwFAQhAAAIQgAAE4kIAAx+XnqhQPWTeZeKjo/GY+ArB5zIQiCMB6gQBCEAAAokjgIFPXJeVpsIajY+a+OgHXP/4xz/a5MmTbezYsXbxxRfbT37yE3v33XdLc2HOAgEIQAACEIBATRCgEdUjgIGvHvuqX1kmPvcDrmdecJWdc845dv/999vTTz9tTz31lH3ve9+zkSNH2syZM6teZyoAAQhAAAIQgAAE0k4AA5/2O6C+/TLyGo3vvOoVe2HWL+szZmt3HGwrPnyCrexznK2v29M2bNhg//7v/24LFiwI2+OzoCYQgAAEIAABCEAgXQQw8Onq74KtlYnvn3k5bF/d63Bbs9PBtrHzzraha39b1Xu4re/2Udu8ebNNnz497MMCAhCAQOIJ0AAIQAACCSWAgU9ox5W62osXL7ZlSxba5o51tq77Pk1Ov677x0NO8+PDCgsIQAACEIAABCCQUgLVbjYGvto9EJPrr1u3rqEmme0aYs5yc8euIbNmzZoQWUAAAhCAAAQgAAEIVIcABr463GN31f79+1unTp2sw8YPrOOG95vUr/OaN0JuS5deIbKIAwHqAAEIQAACEIBAGglg4NPY63nanMlk7Mwzzwxb6pb+vt7ELw/rWnRaPd+6LntOq/aH1zpZ9JGTIckCAhCAAASSRYDaQgACiSaAgU9095W28meffbYNGzbMtlu3yHZc+HPb8Z1p9fG/rfuSGZbZssn2GzrCxp75hXDRSQ/OwcgHEiwgAAEIQAACEIBAZQlU08BXtqVcrUUCnTt3tltuucXOOuussG/H9UvqR+KXWa9eveyyyy6zn9z5HdPTavTISUk7YeRFAUEAAhCAAAQgAIHKEcDAV451Iq60/fbb27hx42zOnDk2depUe/jhh+03v/mNnXjiiVvrH0z86ENMJl7SBoy8KKDKEeBKEIAABCAAgfQSwMCnt++bbbk+0Pqxj33MBg4cWHC/qJH3nTDyToIIAQhAAAKxJEClIFADBDDwNdCJ1W6CjPz8R8eGEXmvi4z86Mun2aSpcz1FhAAEIAABCEAAAhAoAQEMfAkgtuEUNXlIrpGf/ecFJiMvEy/VZKNpFAQgAAEIQAACEKgwAQx8hYGn4XK5Rj6Y+AfnhNF4jHwa7gDaWF4CnB0CEIAABNJOAAOf9jugjO1vzsiX8bKcGgIQgAAEIACBfATI1QwBDHzNdGV8G5LPyPNlUPHtL2oGAQhAAAIQgEC8CWDg490/NVW7rJHf+mFXTa3ByNdUF9MYCEAAAhCAAAQqQAADXwHIXKIxAYx8Yx6UIACBYgmwHwQgAAEIiAAGXhRQVQhg5KuCnYtCAAIQgAAE0kegxlqMga+xDk1iczDySew16gwBCEAAAhCAQLUIYOCrRZ7rNiEgIz/1ulG1PEe+SZtJQAACEIAABCAAgdYSwMC3lhj7l5XAofv1Nxn5Cad8wiRdjA+7igKCAATSTYDWQwACENhGAAO/jQVrMSIQTPzoQ4KJx8jHqGOoCgQgAAEIQAACVSfQKgNf9dpSgdQRiBp5jc4LACPyooAgAAEIQAACEEgrAQx8Wns+Ye2WkY/Oj1f1MfKikBhRUQhAAAIQgAAESkQAA18ikJymMgRk5Oc/OjZMrfEryshPmjrXJM8RIQABCECgVgjQDghAIJcABj6XCOVEEMg18sHEPzgnmHiMfCK6kEpCAAIQgAAEINBGAhj4IsGxWzwJYOTj2S/UCgIQgAAEIACB8hHAwJePLWeuIIHmjHwFq8GlIJCPADkIQAACEIBASQlg4EuKk5NVm0A+Iz/ghNvD1Jpq143rQwACEIAABFpHgL0hkJ8ABj4/F7IJJ4CRT3gHUn0IQAACEIAABAoSwMAXRMMGJ5DkiJFPcu9RdwhAAAIQgAAE8hHAwOejQq7mCGDka65LaVAyCFBLCEAAAhAoAwEMfBmgcsr4EsDIx7dvqBkEIAABCEBgGwHWmiOAgW+ODttqloCM/NTrRm39Qig9R54Pu9Zsd9MwCEAAAhCAQE0RwMDXVHfSmNYQOHS//iYjP+GUT5ikY3ONvHIIAhCAAAQgAAEIxIkABj5OvUFdqkIgmPjRhwQTj5GvShdwUQjUIgHaBAEIQKBsBDDwZUPLiZNGIGrkve6MyDsJIgQgAAEIQAAClSHQ8lUw8C0zYo+UEZCRn//o2DAi703HyDsJIgQgAAEIQAAC1SaAga92D3D92BIoZOQnTZ2bim92jW3HUDEIQAACEIBAyglg4FN+A9D8lgnkGnmNxgdh5FuGxx4QgEAaCdBmCECgzAQw8GUGzOlrhwBGvnb6kpZAAAIQgAAEkkygdg18knuFuseaQHNGPtYVp3IQgAAEIAABCNQEAQx8TXQjjagGgXxGni+DqkZPlP6anBECEIAABCAQZwIY+Dj3DnVLBAGMfCK6iUpCAAIQqAQBrgGBihDAwFcEMxdJAwGMfBp6mTZCAAIQgAAEqk8AA1/9Pih9DThjVQlg5KuKn4tDAAIQgAAEap4ABr7mu5gGVosARr5a5LluewhwLAQgAAEIxJ8ABj7+fUQNE05ARn7CKZ/Y+s2ueoY8H3ZNeKdSfQhAAAIQyCVAuYIEMPAVhM2l0ksgmPjRhwQTLzMvEhh5UUAQgAAEIAABCLSWAAa+tcTYP94EYl47jHzMO4jqQQACEIAABBJAAAOfgE6iirVHIGrkvXWFRuSnTp1qo0aNsiFDhthhhx1mEydOtL/85S/GPwhAoLQEOBsEIACBpBDAwCelp6hnTRKQkZ//6FjzaTVqpBv57/10tl100UV244032htvvKFNtnr1anviiSfstNNOs+nTpxv/IAABCEAAAhCoOoGKVwADX3HkXBACTQnkM/L33H2HzZw50zZ16mUr+xxn7+9+ji3v/2Vbt8OgcILLL7/cFi1aFNZZQAACEIAABCCQHgIY+PT0NS1NAAE38uePGmRdP3gx1HhV7+G2oWv/sL654/a2uucwW1+3p23atMlmzJgR8mHBAgIQgAAEIACBVBDAwKeim2lk0ggcOaguVHlj113qR+B3CuvRxYZ6A6/ySy+9pIAgAAEItIsAB0MAAskigIFPVn9RWwg0IvDagmWNyhQgAAEIQAACEKh9AjEy8LUPmxZCoFgCH/vYx8Ku26192zpuaGrSO61+LWz/4xubzL8UavafF4QcCwhAAAIQgAAEapsABr62+5fWJZRAjx49bMyYMaH23ZY8aZ3WNpjzDpvWWN37z1jnegPfoUMH2/+gYWEfPblm9OXTtpr5kEzTgrZCAAIQgAAEUkQAA5+izqapySIwduxYO/LII+tH4Jda90WPW883f2Q9FvzUuqxoeAb89ddfb/9981ds6nWj8j6GctLUuSYlq9XUFgIQgEBlCXA1CCSRAAY+ib1GnVNBYLvttrNbb701fHHTHnvsEdpcV1dnxx57rE2ZMsVGjBgRcofu19/86TV6nrykDRqVl3yKDWZeVBAEIAABCEAg+QQw8LHoQyoBgcIERo8ebdOmTbN58+bZrFmzwhc7DRrU8Cx4y/knIy/5l0MVMvPMl88BRxECEIAABCCQIAIY+AR1FlWFQGsIyMhLbub9WI3Ka768xKi8U0lwpOoQgAAEIJA6Ahj41HU5DU4jATfy0fnyGoWXmWeKTRrvCNoMAQhAwAwGySWAgU9u31FzCLSaAPPlW42MAyAAAQhAAAKxI4CBj12XpK1CtLdaBDQqL/kUG5l71UWj8pKPzCuHIAABCEAAAhCIDwEMfHz6gppAoGoEZOQ1vcbNvFfEjTzz5Z0IMVYEqAwEIACBlBLAwKe042k2BAoRkJl3I+9PsWG+fCFa5CEAAQhAIIkEkl5nDHzSe5D6Q6BMBGTkpVwzr1F5yafYyNyXqQqcFgIQgAAEIACBPAQw8HmgkIJAZQgk5yoy8pKb+eh8eU2vcTOfnBZRUwhAAAIQgEByCWDgk9t31BwCVSEgI6/58pJPsVFFovTfjQIAABAASURBVKPyPF9eRBAEykiAU0MAAqkmgIFPdffTeAi0nYBG4WXmfVTezbyMvOSj8pj5tjPmSAhAAAIQgEA+Au0x8PnORw4CEEghARl5qSUzz3z5FN4cNBkCEIAABEpOAANfcqScEALpJiAjL7mZdxoaldd8eWnS1LmeJkIAAhCAAAQg0EoCLRr4devW2dtvv21r165t5anZHQIQSDsBN/LR+fIahZeZZ4pN2u8O2g+BNhLgMAhAwAoa+OXLl9t3v/tdGz9+vF1zzTV24YUX2i233GIffPAB2CAAAQi0igDz5VuFi50hAAEIQAACzRIoaOAnTZpkr7/+up111ll2xRVX2Gc/+1l7+eWX7Yc//GGzJ0zJRpoJAQi0kYBG5SWfYiNzr1NpVF7ykXnlEAQgAAEIQAACTQnkNfB///vfw7SZk08+2YYOHWq77babnXDCCTZkyJBg6levXt30TGQgAAEItJKAjLym17iZ98PdyNfmfHlvJRECEIAABCDQNgJ5Dfxbb70VzjZ48OAQfbHXXnuF1RUrVoTIAgIQgECpCMjMu5H3R1IyX75UdDkPBCBQEwRoBASyBPIa+P3339/OP/9869GjR3a3hjBv3jzr0KGD9enTpyHBEgIQgECJCcjIS7lmXqPykk+xkbkv8aU5HQQgAAEIQCARBPIa+L59+9qBBx5omUzG/N/06dPtlVdesREjRjTK+/ZCceHCheaK7uM5RfINjBLCIVrNrX1LPzb0IRxKy+HkI3a1qJkfNGDHcP/JyGt6jZt5cXeFHbILzylmUyGo7AqJ7MJzitlUCCq7QiK78JxiNhWCyq6QyC48p5hNhaCyKySyC88pZlMhqOwKiezCc4rZVAgqu0Iiu/CcYjYVgsqukMguPKeYTYWgsisksgvPKWZTIajsConswnOK2VQIKrtCIrvwnGI2FYLKrpDILjynmE2FoLIrJLILzylmUyGo7AqJ7MJzitlUCCq7QiK78JxiNhWCyq6QyC48p5hNhaCyKySyC88pZlMhqOwKiezCc4rZVAgqu0Iiu/CcYjYVgsqukMguPKeYTYWgsisksgvPKWZTIajsConswnOK2VQIKrtCIrvwnGI2FYLKrpDILjynmE2FoLIrJLILzylmUyGo7AqJ7MJzitlUCCq7QiK78JxiNhWCyq6QyC48p5hNhaCyKySyC88pZlMhqOwKiezCc4rZVAgqu0Iiu/CcYjYVgsqukMguPKeYTYWgsisksgvPKWZTIajsConswnOK2VQIKrtCIrvwnGI2FYLKrpDILjynmE2FoLIrJLILzylmU41CXgMf3WPjxo1233332cMPP2z77LOPjRw5MrqZdQhAAAIVISAj/6NvHG331Mun2OjCMvPDznvYFCXlUFwJUC8IQAACECgFgWYN/HvvvRceIfnss8/acccdZxMmTLCOHTu26rr9+vUzV/RAzymSb2AEBzjo9eDifsh/Pxwz7GMmM587xeZnv/2nST4qP2nq3K3vPWIKz/w8xUaCD3x0H7i4H7gf/F5QjMX9gJ+MdkPh58BryP7qq6+2JUuW2Lhx42zUqFGtmjrT6CoUIAABCJSBgIy8lGvmNRIvuZlnvnwZ4HNKCEAAAhCoGoG8I/CbN2+273//+7Zp0ya78sorbb/99qtaBbkwBGJEgKrEmICMvORm3qsqI6/58pJG5T1PhAAEIAABCCSVQF4DP3fuXFu6dKl95CMfCc99nzVrlkW1atWqpLaXekMAAikg4EZez5j3+fIahZeZ91F5zHwKboRYNZHKQAACECgdgbwG/vXXXw9X0FNnfvzjH1uuFi9eHLazgAAEIBBnAvqWVzfzMvKS6isjL2HmRQNBAAIQgECsCeSpXF4DP3r0aLvrrrsKasCAAXlORQoCEIBAfAnIyEs+xUbmXrWVkZfczCvXnLZs2RL+Iqkncz311FPGXySbo8U2CEAAAhAoB4G8Br4cF+KcEIBAognUVOVl5DW9xs28N86NfKH58o899pgNHz7cLrjgArv22mvt4osvtk9/+tM2ZcoUPwURAhCAAAQgUHYCGPiyI+YCEIBAnAnIzLuR9yk2+ebLP/roo6Yncy1btsw2dulr67rvYxu69jd96P+WW26xe++9N87NpG4QqCIBLg0BCJSaAAa+1EQ5HwQgkEgCMvJSrpnXqPzkB2bb1d+6PrRrTc+htqLvSFvd63Bb2ec4W9X7qJC/7bbb7O233w7rLCAAAQhAAALlJJAaA19OiJwbAhCoLQIy8pKb+UF9Vllm8/r6kfd+tnaH/Rs1dn3dR2x9t71C7g9/+EOILCAAAQhAAALlJICBLyddzg0BCCSewITRh9iX/2WP0I5NnXuFmLvY2Ll3SL3zzjshsoAABCAAAQiUkwAGvpx0OTcEIFATBHr27Bna0WHjyhBzFx03rgipHz7ykvnTbHjOfEDCAgIpJ0DzIVAeAhj48nDlrBCAQA0RGDp0aGhNpzVvWKc1b4Z1X3Rc/551Xvm3UNyw/a4hat68JDMvycxLYSMLCEAAAhCAQDsJYODbCTAJh1NHCECgfQQ0An/hhReGk3Rf/ITVLZ1lXepN+/bL5tgOi35lmS0b7cwzz7R//PoK0+Mp9TQbKRxQv5CZl2Tm/RGVGPp6MPyHAAQgAIE2EcDAtwkbB0EAAmkjMGbMGDvvvPNCs7us/Gu9if+Ddf3gRcts3mDaNn78+LBNXxClD8BK+hCsG3rltYM/ojLX0Cuv7TET1YEABCAAgRgSwMDHsFOoEgQgEE8C5557rj3yyCN2ySWX2Omnn24aldc3sioWqrGMu8y8jHxzhl4j89ERegx9IaLkIQCBZBCgluUkgIEvJ13ODQEI1ByBAQMG2Kmnnhq+hVUj7wMHDmxVG3MNvabaSMrrRDLuGp13Q6+pNpLy2o4gAAEIQAACGHjugZomQOMgEHcCGp2XfIReZl5yQy8zL+Ua+ri3i/pBAAIQgED5CGDgy8eWM0MAAhBoNQGZeSnX0PuJZOYlTbeRNDov+XZiyQhwIghAAAKxJYCBj23XUDEIQAACZjLzkubPSxqdl5yNzLwkMy/JzEu+nQgBCEAAApUmUP7rYeDLz5grQAACECgZAZl5SWZeo/Qy85JfQGZekpnXtBuZecm3EyEAAQhAIPkEMPDJ70NaAIG8BEjWPgHNk5eZl6KGXnm1Xh98lZmXooZeeW1HEIAABCCQTAIY+GT2G7WGAAQg0ISAjLvMvEbmmzP0GpnH0DfBR2IbAdYgAIGYE8DAx7yDqB4EIACBthLINfSaaiMpr3NqJF6j827oNdVGUl7bEQQgAAEIxJNAfA18PHlRKwhAAAKJJaDReclH6GXmJTf0MvNSrqFPbIOpOAQgAIEaJYCBr9GOpVkQSDMB2l4cAZl5KdfQ+9Ey85Km20ganZd8OxECEIAABKpDAANfHe5cFQIQgEDsCMjMS5o/L2l0XvKKysxLMvOSzLzk24kQqAECNAECiSCAgU9EN1FJCEAAApUnIDMvycxrlF5mXvKayMxLMvOadiMzL/l2IgQgAAEIlIcABr48XNt3Vo6GAAQgEDMCmicvMy9FDb3yqqo++CozL0UNvfLajiAAAQhAoHQEMPClY8mZIAABCFSdQKUqIOMuM6+R+eYMvUbmMfSV6hWuAwEIpIUABj4tPU07IQABCJSRQK6h11QbSXldViPxGp13Q6+pNpLy2o4gAIGqE6ACCSKAgU9QZ1FVCEAAAkkhoNF5yUfoZeYlr7/MvJRr6H17sXHBggX20EMP2V133WXTpk2zxYsXF3so+0EAAhBILAEMfGK7rkYrTrMgAIGaJCAzL2m6jSQzL3ljZeYlTbeRNDov+fZ88e6777bjjz/ebrjhBrvzzjvtmmuusWOPPdb+67/+K9/u5CAAAQjUDAEMfM10JQ2BAAQgkBwCMvOSzLwkMy95C2TmJZl5SWZe8u133HGHSSqv7/ZRW9vjINtQN0BFmzRpkk2ZMiWss4AABCBQiwQw8LXYq7QJAhCAQMIIyMxLMvOadiMzL3kzZOYlmfkTL77PNPqubSv7HGerPnSkrelxkK3sfXT9+qeVtltvvdVWrFgR1llAAAIQaIFA4jZj4BPXZVQYAhCAQG0T0AdfZealqKFXXi3/0wvPKdi67vvahq79w7ov1nfbuz63q23evNlmz57taSIEIACBmiKAga+p7qQxiSZA5SEAgbwEZNxl5jUyL0M/ctguYb9NnXYKMXexuVOPkLrghkdMH5LV1BsXT70JaFhAAAIJJ4CBT3gHUn0IQAACaSMwZNCeockdNywLMXfRYcPykNrSsc5k2DX1xiVDr2k4LpXd3Ctq/3BwwhZUFwIQSBcBDHy6+pvWQgACEEg8gSOOOCK0ocvKv1qntQvCui86r3q5PvdP69Chg9357a+aRu01l96l0XzfV1GG3c29ogy9m3tFlWXsXdpfxyEIQAAC1SRQQgNfzWZwbQhAAAIQSAuB/v3721e/+tXQ3O6LHrdu78207Zc/b92XzKhf/13IX3TRRTZ86N4mwz5h9CHmkqHXNBxJ65Kbe0XtH06QXciwy9i7ZOhl7F0qu7lX1P7ZQwkQgAAEykYAA182tJwYAhAomgA7QqCVBL72ta+ZpMM6r3rVutYb+E6r56toEyZMsNNOOy2sN7eQWZfc3CvK0MvcS1qXZOxd2j96Thl2N/eKMvRu7hVVlrF3af/o8axDAAIQaAsBDHxbqHEMBCAAAQhUnYBG4X/1q1/ZpZdeauedd55dffXV9sQTT9gZZ5xRkrrJrEsy9i4Zepl7SeuSm3tF7R+9uAy7jL1Lhl7G3qWym3tF7R89nvWWCbAHBNJIAAOfxl6nzRCAAARqhICm05x00kl27rnn2qhRo2znnXeuWMtk1iU394oy9DL3ktYlGXuX9o9WUIbdzb2iDL2be0WVZexd2j96POsQgEA6CWDgS9LvnAQCEIAABCDQmIDMuiRj75Khl7mXtC65uVfU/tGzyLDL2Ltk6GXsXSq7uVfU/tHjWYcABGqTAAa+NvuVVkEAAkkhQD1TS0BmXXJzryhDL3MvaV2SsXdp/ygwGXY394oy9G7uFVWWsXdp/+jxpVz/y1/+YhMnTrTDDjvMhgwZEv4iMnXq1FJegnNBAAJZAhj4LAgCBCAAAQhAIE4EZNYlGXuXDL3MvaR1yc29ovaPtkGGXcbeJUMvY+9S2c29ovaPHl/s+vTp08MHh/UZhNWrV4fD3njjDbvxxhtNTwTauHFjyLEoLQHOll4CGPj09j0thwAEIACBBBOQWZfc3CvK0MvcS1qXZOxd2j/aZBl2N/eKMvRRc6+yjL1L+0eP1/qiRYvs8ssv16qt22GQLe//ZXt/93NsZZ/jbFOnXjZz5ky7/fbbw3YWEIBAaQhg4EvDMcVnoekQgAAEIBBHAjLrkoy9S4Ze5l7SuuTmXlH7e1tk1iUZe5cMfa7Bn3j9PbZp0yZbX7enre7SQHl+AAAQAElEQVQ5zDZ33D6cYkPX/raq9/Cwfv/999vy5cvDOgsIQKD9BDDw7WfIGSAAAQhAoC0EOKaqBGTWJTf3ijL0MveS1iUZe5f290rL3EtznnshpDbUG/iwElls6rSTbey6S8g88v9mhcgCAhBoPwEMfPsZcgYIQAACEIBAzRGQWZdk7F0y9DL3ktalA/fqW1Tbv33fLIuO3vu0HEX9IlDUSdgJAlkCaQ8Y+LTfAbQfAhCAAAQg0AYCMvfS8cd8MhzdafVrIUYXHTcss+3Wvh1SBx24X4hayLD7tBzF3Kk5MvUu7atjEAQgsI0ABn4bC9Yg0EoC7A4BCEAAAkcffbR17NjROtcb+Lr3n7EOm9aY/nVau8C6LXlSqzZmzBh76LunmEbuJY3c+7QcRf0iEHasX8iwy9S7Cpl77SfVH8J/CKSOAAY+dV1OgyEAAQhAoOoEaqgCffr0seuuuy60qMuKv1iPBT+1nm/+yLovetw6blhqRx55pI0dOzZs94UMu0/LUZShl7GXtC5TL2k/yY+TYY8a++bMvR9DhEAtEsDA12Kv0iYIQAACEIBABQmMGDHCpkyZYscee6zV1dWFK++xxx7hi51uvfVW22677UKumIUMu0y9JDMvydhLWpexl7Sf5OfMNffR+fYy+kzJcVLEpBNQ/THwooAgAAEIQAACEGgXgUGDBoUvbpo1a5bNmzfPpk2bZqNHj27XOXMPlmGXsZdk5iU39lqXsZe0nx8rYy9FR+6j5t6NvaL28+OIEIgzAQx8nHuHukEgtgSoGAQgAIH4EJBhl2TsJZl5GXtJ6zL1Lu3nNZdhd2OvqJF6zL3TIcaZAAY+zr1D3SAAAQhAAAK1RqDC7ZFhl6l3ydDL2Etad2OvqH29eph7J0GMIwEMfBx7hTpBAAIQgAAEIFB2AjLsbuwVZehl7CWty9S7tK9XqFhzr/0kP44IgVIRSKuBLxU/zgMBCEAAAhCAQA0SkGGXqXfJ0MvYS1qPGnvt6whk2DUdR9KUHEnTchQlzbWXtJ8fU664ePFimzlzpj3xxBP26quvlusynLcKBDDwVYDOJSEAgSQToO4QgEDaCciwR429DL2MvaT1qLl3VjLskoy9JDMvYy9pXZKxl7SfH9fWOHny5PBUoIsuuig8DejEE0+08847z157rekXbrX1GhxXPQIY+Oqx58oQgAAEIAABCNQYgVxzL1MvydhPvW6UtcXcy9S7ijH3V1xxhd1///2B7Ibtd7P1dXva5o519uyzz9o555xjb7/9dtjGIrkEMPDJ7TtqDgEIQAACEIBAQgjI2EvRkXsZe0nm3o29ovbzZsmwa8TepZF6jdpLWndjr6h958yZY//zP/9jm7frbh98+PO2cucRtqr3cFve/1TbUDfA3n//fbvtttv89MSEEsDAJ7Tj2lFtDoUABCAAAQhAIEYEZNjd2CvK0MvYS1qXqXdpX6+6DLsbe0UZ+jMvvjlsXtPjINvU+UNh3Rerex4WVh9//HHbuHFjWGeRTAIY+GT2G7WGAAQgUAUCXBICEKg0ARl2mXqXDL2MvaT1qLHXvh02fhCquLHLh0OMLjZ33L5+ZH7HkDrpkh+bDL9G7l36hUAKO7CINQEMfKy7h8pBAAIQgAAEIACB/ARk2KPGXob+Xw7dJ+zcceOKEHMXmc3rQmreq8tMZl0j9y4ZeknTc1wqu8H3qOOkcKJiF+xXUgIY+JLi5GQQgAAEIAABCECgegSGDRsWLt7lgz+FGF10Xf68ycAfcMAB9uANJ5sMv4/gK+oXAil6jIy6G3yPMvVS1OSr7AZfUcdJ0XOxXjoCGPjSseRM8SdADSEAAQhAAAI1TWDkyJHWt29f67T2n7bDu49ZlxUvWedVr1i3JU/Z9vUGXo3Xk2hk1KUJow8xlwy9pOk5ktYlmfuodJzO45JRl9zgK8rQS27yFVWWZPBdOk7ycxGLI4CBL44Te0EAAhCAQKoJ0HgIJINAXV2d3XrrrTZw4EDbbt0iq3v/aev23m+t8+p/hAZcddVV9qlPfSqst7SQUZfc4HuUqZfBd6ks5Zp8HRu9hoy6JIPvkqGXZPAlrUtu8D3quOi50r6OgU/7HUD7IQABCEAAAhCoKQL77ruvPfzww3bDDTfYKaecYl/84hft61//uunpM5///OdL3lYZdckNvqIMveQmX1FlqTmjL6MuucH3KFMvg+9SWXKDr6jjpJI3sL0nLMPxGPgyQOWUEIAABCAAAQhAoNoEPvOZzwTjri92kpH/8IebPpmmknWUyZdk8F0y9JIMvqR1qTmTrzrLqEtu8BVl6CU3+YoqSzL4Lh0n6TyV0owZM+yss86ygw46KEjryrX1+hj4tpLjOAgkiwC1hQAEIAABCMSegAy+5AZfUYZeksF3qSyVwujL4Etu8D2WyuT/4Ac/sEsuucTmzZtnW7ZsCdK6ctrWlk7BwLeFGsdAAAIQgAAEUkOAhkIgfgRk8iUZfJcMveQmX1FlqTmjL6MuaRQ/Kpl6jeK7VJbc4CvqOKkQIY2y33fffWHz6l6H2fu7nx2kdSW1TftovTXCwLeGFvtCAAIQgAAEIAABCCSGgEy+5CZfUYZeksGXtC41Z/LVYBl1Kdfky9S7yVdUWZLBv3ny3TrUZNjXdd+3fj0TpHXl6gv2wAMPKLRKiTHwrWoVO0MAAhCAAAQgAAEIQKAIAjL4ksy9S4ZeksF3qSy1xui/+89XQg3WdW/4gq1QyC4898ILL2QzxQcMfPGs2BMCEEgmAWoNAQhAAAIQaDcBmXzJTb6iDL3kJl9RZUlGP5PRiHu7L93kBBj4JkhIQAACEIAABCAAARFAEGg9AZl8SQZ/8ODB4QRdVv4txOjCc75PdFtL6xj4lgixHQIQgAAEIAABCEAAAm0gcOqpp4aj6pbOsi4r/1q/viVI68rVF8z30XqxwsAXS6qK+3FpCEAAAhCAAAQgAIHkETj66KPD899Vcxn2nm/ea5LWldPz4LWP1lsjDHxraLEvBCAAgWQRoLYQgAAEIFBlAuPGjbObbrrJhgwZYplMJkjrymlbW6qHgW8LNY6BAAQgAAEIQAACNU2AxpWSgEbZ9cz3559/3iStK9fWa2Dg20qO4yAAAQhAAAIQgAAEIFAFAhj4KkDnksUTYE8IQAACEIAABCAAgcYEMPCNeVCCAAQgAIHaIEArIAABCNQsAQx8zXYtDYMABCAAAQhAAAIQaD2B+B+BgY9/H1FDCEAAAhCAAAQgAAEIbCWAgd+KghUIxIsAtYEABCAAAQhAAAL5CGDg81EhBwEIQAACEEguAWoOAQjUOAEMfI13MM2DAAQgAAEIQAACEKgtAuUz8LXFidZAAAIQgAAEIAABCEAgFgQw8LHoBioBAQhECbAOAQhAAAIQgEBhAhj4wmzYAgEIQAACEIBAsghQWwikggAGPhXdTCMhAAEIQAACEIAABGqFQIsGft26dfbuu+/ali1baqXN5W8HV4AABCAAAQhAAAIQgECZCBQ08GvXrrUbb7zRxo8fb1dddZWNGzfOZsyYUaZqcFoIQAACEBABBAEIQAACEGiJQEEDf/PNN9v8+fPt9NNPt4kTJ9qBBx5oP//5z2327NktnZPtEIAABCAAAQhAAAKVJcDVUkQgr4F/7bXX7K233rKTTjrJDj/8cNtzzz3t7LPPtr59+9qjjz6aIjw0FQIQgAAEIAABCEAAAvEikNfAz5kzJ9RS5j2s1C86dOhgRx11lC1dutQWLVpUn+E/BPIQIAUBCEAAAhCAAAQgUFYCeQ28DHqvXr2sU6dOjS4+cODAUF6yZEmILCAAAQhAAAKlIsB5IAABCECgOAJ5DfyyZcusW7duTc7gueXLlzfZViixcOFCc0X38Zwi+QZGcICDXg8u7gfuB78XFLkfuB90H7i4H7gf/F5Q5H5YGLxmGjh4G/MaeN9IhAAEIAABCEAAAhCAAATiRSCvgd9pp51s1apVTWrquR49ejTZVijRr18/c0X38Zwi+QZGcEg4h+y9Tj/Sj3pfc3E/cD/4vaDI/cD9oPvAxf3A/eD3gmIx94Pvk9fA9+nTJ3xYdf369b5fiK+//nqIO++8c4gsIAABCEAAAhBoPwHOAAEIQKA1BPIa+E984hPhHLNmzQpRi82bN9uTTz5p+nArBl5EEAQgAAEIQAACEIAABCpPIGLgt11cz33fY4897KGHHrLf//73pufC33PPPeHxkaNGjdq2I2sQgAAEIAABCEAAAhCAQEUJ5DXwqsHFF19su+++u02ZMsVuvPFGe+GFF+xLX/qSDR06VJsRBCAAgW0EWIMABCAAAQhAoGIEChr4rl272qWXXmqTJ0+2q666yn74wx/aMcccU7GKcSEIQAACEIAABGqfAC2EAARaT6CggfdTycj379/fMpmMp4gQgAAEIAABCEAAAhCAQJUItGjgS1GvxYsX29q1a1t9qrYe1+oLWTqOWLFihelLulrb2mKO27RpU/gShQ8++KC1p0/t/sVwzQeH10U+Ku3PtYWrPtz/zjvvmO7/5mqgL797++23bd26dc3txrYcAuL17rvv2pYtW3K2tL24aNEi27hxY9tPkMIji73Pc9Go/3Tft+Xnf+65KDdPQKxL/Vpp/opsrTaBshr42bNn2wUXXGBXXHGFXXjhhXbNNddYMQav2OMefvhhO/fcc+3//u//qs0x1tdfsGCBff3rX7f/+I//sIkTJ5o+3/DKK6+0WOdijtMPwgcffNDOP/98++Y3v2mXXHKJfeMb3wgffG7xAindoRiu+dAU+7rwY2Uqr7766vAa8RyxKYHWcvUz6L4fO3asXV3PWPe/Pugvo+PbFfXeNGHChPD60/vf+PHj7Xvf+16bfpHW+dIiGT599kq8NIVz3LhxNmPGjBabLxNzyy23hHte69EDfve734WfR1deeaXpfLfeeqv94x//iO7Ceh4CxdznuYfpF9bvfve7pv7Tfa+f/+qX6M//+fPnh37Sz/Bc/eAHP8g9JeUCBNryWoF9AZgVSuvnwte+9jXTa6s9lyybgX/ppZfsP//zP+2jH/1oMHVnn322aYTr+uuvb3a0qpjjXnzxRbv22mtt+vTpoe2lHJ0JJ6yhhd4wb7jhBuvQoYPJbOiNVF/EJROhkcNCTS32uEceecRmzpxpn/3sZ01mcfTo0abvD9D5V69eXej0qc0XyzUXUDGvi9xj9BSp5vo4d/80ltvCVZw0eKD7/uijj7bLLrvMRo0aZc8995zdf//92hwkA3nnnXdaz549Te9/MqIjR440/fKszxSFnVjkJXDzzTfb/HqDd/rpp4dBhwMPPNB+/vOfm37ZyneAfll96qmnwue2Xn755Sa7zJ07137605+aHpEsA/+Vr3zF3nrrLZOJlwFqcgCJQKCY+zzsmLOYNGmS6XtjzjrrrDCAp58P6pfoff/++++Ho/Qz44wzzrCoRowYEbalYdHeNrb2taLrwV4UKi8NHefnjgAADV1JREFU3ulngl4HGuyR2lOLshn4X/7yl9atW7cwMisTrzfOf/u3fzPdOPrto1CliznuRz/6UTj8y1/+coiZDPPzA4g8Cz0GdMOGDWEk5IADDrCPf/zj4a8h2rW5Ea1ijtPou86h855wwgm2yy672FFHHRXMjK75t7/9TZdBEQLFcI3svnW1mNfF1p3rV/RL7sz6X6wGDBhQX+J/IQKt5arz6L7/3//9X9N9/8UvftH0yN3jjjvOjjzySHv22WdNU6O0329/+1vTG7RGF/X+p88SHX/88Xb44YfbG2+80aZphTpvrUuPLZa5PumkkwIrPdZYvwD17dvXHn300bzNf++992zq1Knh/U3vQbk7/eIXv7C99trLZNx33XVXGzZsmMk46n3qT3/6k/GvKYFi7/PcI//+97+bps2cfPLJ4al1u+22m+nnw5AhQ4Kp94Edn86p180nP/lJi2rvvffOPS3lPATa8lrRaWAvCpWX3r/0i6y8sAZVpfbUoiwGXiMaurEOO+ww69y589b6aRSlU6dOBUdRij1Of67WKIoec7n15KzkJaARKxkHmWvfYaeddrJBgwbZnDlzzMyzjWMxx2kuqY466KCDFLZKPyhV0GizItpGoBiu2/ZuWCv2ddGwt5nenO+++24bPny47b///p4m5hBoLVc/XKP2Mubi6zlFN45//OMfVTS912kl+h6ocpcuXRSsY8eOIbJoTMDfl/SLjm/RDzrxXbp0afg+Es977N69u11++eV2zjnn2I477ujpEN98880wcPSZz3wmlH1xyCGH2E033WQylp4jbiNQ7H2+7YiGNf3ypbXBgwcrbJX/XPBfcDXN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)

这对于 Agent 的实验设计非常重要。

因为传统主动学习可能倾向于不断在预测最不确定的位置采样，通常就是临界点附近。

但假如一次实验需要等待系统接近稳态，那么越接近临界点，实验可能越耗时。

所以我们真正需要优化的也许不是：

\\[ \\min \\text{Number of Experiments} \\]

而是：

\\[ \\boxed{ \\min \\left( \\text{Total Observation Time} +\\lambda\\cdot\\text{Experiment Cost} \\right) } \\]

同时满足：

\\[ P(\\text{错误认证})\\leq\\delta \\]

这可能形成一个比普通贝叶斯优化更明确的研究问题：

如何设计一个知道临界减速规律的 Scientific Agent，使它能够在有限实验时间内，最有效地识别和认证临界边界？

但我们需要谨慎：临界减速、成本敏感实验设计和主动分岔搜索分别都有成熟研究基础。要获得原创贡献，需要证明将这些结构结合后，确实产生了新的理论界或实证优势。

## 十、实验应该与什么方法对比？

我不希望最后只和 GPT-4、GPT-5、GPT-6 等不同基础模型比较。这样很可能没有回答科学问题。

真正的竞争对手是已经成熟的科学计算和主动学习方法。


| Baseline                                                                                                   | 作用                     | 我们需要比较什么           |
| ---------------------------------------------------------------------------------------------------------- | ------------------------ | -------------------------- |
| [PySINDy](https://pysindy.readthedocs.io/en/stable/?utm_source=chatgpt.com)                                | 从数据恢复稀疏动力学方程 | 方程恢复后能否正确分析分岔 |
| [BifurcationKit.jl](https://bifurcationkit.github.io/BifurcationKitDocs.jl/stable/?utm_source=chatgpt.com) | 给定方程时分析分岔       | 当恢复方程不准确时如何处理 |
| ActiveSearchforBifurcations                                                                                | 主动学习临界点           | 实验效率与定位精度         |
| GP/BayesianActiveLearning                                                                                  | 概率建模与实验选择       | 不确定区域收缩速度         |
| 纯LLMScientificAgent                                                                                       | 自主设计实验与提出假设   | Agent是否真正带来改进      |

其中 BifurcationKit 是非常有力的工具，它已经支持数值延拓、稳定性分析及分岔检测。我们的工作不应该重新实现这些数值方法，而是应当将它们作为可靠的专业工具调用。

Bifurcation Analysis in Julia+1

### 我会重点看五个指标


| 指标                   | 定义                           | 目标         |
| ---------------------- | ------------------------------ | ------------ |
| BoundaryError          | 学到的临界边界与真实边界的距离 | 越小越好     |
| FalseCertificationRate | 被认证但实际上错误的结论比例   | 必须严格控制 |
| CertifiedCoverage      | 被可靠判定的参数空间比例       | 越大越好     |
| ExperimentCost         | 观测时间、实验次数、资源成本   | 越小越好     |
| OODGeneralization      | 未见系统上的临界边界识别能力   | 越强越好     |

这里的 certified coverage 尤其值得单独讨论。

假如：

* 方法 A 判断了全部参数区域，但其中有不少错误；
* 方法 B 只判断了 70% 的区域，不过输出的结论具有明确且有效的可靠性保证；

那么在高风险科学研究场景下，B 可能更有价值。

我们还需要将 Agent 设计成能够主动放弃没有证据支持的结论，而不是为了扩大覆盖率随意认证。
