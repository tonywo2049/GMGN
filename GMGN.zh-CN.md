---
locale: zh-CN
purpose: 定义 GMGN 的角色、文档链、硬门禁、独立审查与关账方法。
upstream: none
downstream: [文档写作契约](skills/gmgn/references/zh-CN/writing-contract.md), [派发契约](skills/gmgn/references/zh-CN/dispatch-and-handoff.md), [上机前核对单](skills/gmgn/references/zh-CN/preflight-checklist.md), [合并前核对单](skills/gmgn/references/zh-CN/pre-merge-checklist.md), [关账前核对单](skills/gmgn/references/zh-CN/pre-close-checklist.md)
status: approved
type: whitepaper
nature: normative
---

# GMGN：轻量 Agent 协作工程方法

English: [GMGN.md](GMGN.md)

GMGN 协调一个负责裁决的人类负责人、一个掌握完整上下文的主编排者，以及若干短生命周期 agent。
它主要对冲两类风险：文档、状态和证据与事实脱节；writer 与 reviewer 共享前提，漏掉同一个问题。

对策只有三类：少量有版本锚的权威文档、按变化影响选择独立检查、事实变化时同批刷新状态。
GMGN 不是为了凑角色、文件或门禁。

## 1. 角色

- **负责人**：裁决范围、批准、验收、发布授权，以及完成判据的语义删除或重新分配。
- **主编排者**：保留完整 session 上下文，选择阶段、准备 brief、裁定 finding、集成候选并刷新共享
  状态。上下文最完整时可直接写 WhitePaper、ROADMAP、Goal、Requirement、Design、Task。只有当前
  没有实现 lane 能和有效编排工作并行时，才可承担一张卡的 Coder。
- **Author**：完成一次受委派的文档候选。
- **Coder**：完成一张 Card 的一次实现尝试。
- **Critic**：独立审查文档语义。
- **Reviewer**：独立审查实现或测试代码 diff。
- **Verifier**：针对一个固定候选独立执行所需检查。

所有受委派 agent 都只用一次。创建前准备完整 brief，只给一个边界明确的目标，接收一次回传后
结束。修订、重试、复核或后续验证都新建 agent 和 brief，不继承父会话或旧 agent 对话。主编排者
不是受委派 agent，持续负责集成；不存在 Integrator agent。

## 2. 权威与文档链

常规语义链：

```text
WhitePaper → ROADMAP → Goal → Requirement → Design → Task
```

- WhitePaper：问题、目标、范围、非目标、不变量。
- ROADMAP：Milestone 顺序、优先级、跨 Milestone 依赖，以及每个 Milestone 的定性验收图景。
- Goal：一个已启动 Milestone 的目标、边界、切片，以及 ROADMAP 验收图景到活动范围的映射。
- Requirement：需求、约束、验收标准（AC）。
- Design：实现结构、接口、数据和失败路径。
- Task：任务划分、AC 映射、依赖、宏观状态和 execution 指针。

一个事实只有一个权威，其他文档只链接。批准绑定不可变版本锚；编辑文件不会自动继承批准。
正文可用中文或英文，机器字段、ID、状态 token 和 Task 表头固定。完整结构见
[写作契约](skills/gmgn/references/zh-CN/writing-contract.md)。

## 3. 精简 Task 与单卡执行文件

`Task.md` 是 Milestone 索引，不是执行日记：

```markdown
| # | task | spec anchor | prerequisite | status | execution |
```

它还保存 AC→Task 映射和 Milestone 级执行指针；不保存 TDD、命令、write set、锁、blocker、候选锚、
审查轮次、验证证据或推进历史。

Task 拆分只能在已批准 Design 内优化有效的独立执行：每张卡只有一个主要责任和一个可独立判定的
结果；尽量减少不必要的依赖、共享写入和运行冲突，使没有真实依赖的任务能够并行。目标是提高有效
并行度，不是增加卡片数量。不得为了并行制造空壳任务、虚假接口或新的设计决定；协调成本高于隔离
收益时停止拆分。

负责人确认执行集后，`run-task` 在派 Coder 前为每个选中任务只创建两份文件：

- `execution/<card_id>/Card.md`：规范性的稳定执行/TDD 契约，精确链接 Task/Requirement/Design，
  并暴露 `execution_log: [Log.md](Log.md)`。
- `execution/<card_id>/Log.md`：描述性的当前快照和追加事件；快照中的 `latest_event` 指向本文件
  当前事件锚。

先建 Card，再建 Log，最后在同一检查候选中把 Task execution 指针更新到 Card。没有独立项目需求
时，不建 State、Verification、逐角色 Handoff 或项目总执行日志。

## 4. Review 与 Verification

独立检查前先冻结候选，按变化面选择角色：

| 变化面 | 独立检查 |
|---|---|
| WhitePaper/ROADMAP/Goal/Requirement/Design/Task 语义 | 新 Critic |
| 实现或测试代码 diff | 新 Reviewer |
| 可执行结果、环境或打包输入 | 审查清零后的新 Verifier |
| 等价链接、格式、指针或状态 | 只跑机器检查 |

先收齐 Critic/Reviewer finding，再由主编排者一次裁定、集中修复 blocker。只有新 brief 能证明影响
边界时才定向复核；不重新派未受影响角色。非阻塞建议不重开候选。

相关 review blocker 未清零前不得派 Verifier。默认先形成最终临时组合候选，再只派一个新 Verifier。
不要在 lane 和集成边界重复同一验证。第二个验证边界必须记录理由，例如环境证据不可转移、基线或
测试输入变化、集成决定本身需要运行证据，或项目明确要求双重验证。

纯机械或只改文档的任务可以不派 Verifier。Verifier 用于独立建立可执行证据，不用于凑角色。

## 5. 任务执行与集成

`run-task` 按依赖持续补满 ready set。前置任务已集成，且已声明的共享资源约束可用时，任务才
ready。并发数取决于真实容量；GMGN 不规定固定 agent 数，也不设整波等待屏障。

并发 writer 使用独立 worktree 或等价工作区；没有其他 writer 会冲突时，单 writer 可以使用已
核对的当前工作区。一张卡同时只有一个 writer。Coder 只写 brief 允许的范围，回传不可变本地候选。
Task/Card/Log 运行态、集成队列和共享基线由主编排者维护。

review 清零后，主编排者把隔离 lane 候选机械应用到临时组合。单 writer 的冻结候选已经基于未变的
共享基线时，它本身就是最终组合，不再复制。干净应用不需要 Coder；冲突或需要判断时新建 Coder，
并只重走受影响的 review/verification。未经所需验证的可执行组合不得成为共享基线。

派发、本地检查、集成和状态刷新都无事可做后再等待。使用一次最长安全事件等待；超时只是存活
检查点，不得变成 list/status/wait 轮询。只有调度/容量决策需要当前状态、等待超时后 agent 状态仍
不明确，或收到的生命周期事件互相矛盾时，才调用一次 `list_agents`。一次查询只服务一个决策点；
新的实质生命周期事件、候选、blocker 或调度条件变化出现前不得再次查询。不存在定时查询周期；
等待超时参数只控制当次等待。

## 6. 变更、关账与发布

证据与已批准语义冲突时，把变更送回所属权威，只暂停影响范围。记录新旧锚，只传播受影响的任务、
代码、测试、证据和状态。等价机械变化只需机器检查，不需语义重批。

Milestone 关账要求：

1. 每个 ROADMAP 验收场景都经 Goal 切片和范围内 AC 追踪到证据；
2. 所有范围内 AC 已完成，或在新权威锚上完成语义删除/转移；
3. 每条保留判据都有可重放证据；
4. Task、Card/Log、追踪关系和 ROADMAP 同批刷新；
5. 负责人验收绑定关账锚。

只有接手者确实需要、且现有权威无合适位置时，才单独创建 Handoff。源码、语义、测试计划、环境和
打包输入未变时，发布复用已有 review/verification 证据；打 tag、上传重试和本地安装不重复关账。

窄 bug 或单步机械修改只需找到最小权威与验收条件、实现、独立 review diff、在需要时验证可执行
行为并刷新状态，不得为了流程补造完整文档链。

## 7. 工具与反过度设计

自动化可以解析、链接、比较、执行和报告，不能发明产品语义或批准。DocStar 是可选结构工具，
CodeGraph 是可选导航工具；权威文档、源码、diff、测试和真实运行才是证据。Telemetry 只是带外
观测，不改变路由、ready、验收或关账。

按下列顺序选择第一个足够方案：

1. 不实现；
2. 复用仓库现有能力；
3. 标准库或平台原生能力；
4. 现有依赖；
5. 直接实现；
6. 最少的新结构。

没有当前需求，不新增角色、状态机、身份历史、配置、包装层或文档。简化不能删除信任边界、安全、
无障碍和数据防丢保护。

每次实质回传前按当前契约自检并修正范围内问题。不输出固定 `Reflection` 段，只报告会改变裁决、
验收或下游工作的未解决实质风险。

操作细节位于阶段 Skill 和共享契约：

- [派发](skills/gmgn/references/zh-CN/dispatch-and-handoff.md)
- [写作](skills/gmgn/references/zh-CN/writing-contract.md)
- [代码审查](skills/gmgn/references/zh-CN/code-review.md)
- [上机前核对](skills/gmgn/references/zh-CN/preflight-checklist.md)
- [合并前核对](skills/gmgn/references/zh-CN/pre-merge-checklist.md)
- [关账前核对](skills/gmgn/references/zh-CN/pre-close-checklist.md)
