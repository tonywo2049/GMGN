---
locale: zh-CN
purpose: 规定 GMGN 委派工作的最小 brief、全新 agent 生命周期、工作区边界、角色选择与回传契约。
upstream: [GMGN 中文版 §4](../../../../GMGN.zh-CN.md)
downstream: [GMGN 路由](../../SKILL.md), [代码审查](code-review.md)
status: approved
type: task
nature: normative
---

# 派发与全新 agent 契约

English: [../en/dispatch-and-handoff.md](../en/dispatch-and-handoff.md)

这是内容契约，不是固定 prompt，也不要求创建一份 Handoff 文档。

## 一次派发，一个全新 agent

每个受委派的 `author | coder | critic | reviewer | verifier | researcher` 都只处理一次
边界明确的派发，不继承父会话或此前 agent 的对话历史。一次回传即结束。禁止恢复、重新激活、
改变用途，或把后续工作发给已回传 agent。修订、重试、复核或后续验证都先准备新 brief，再创建
新 agent。

主编排者是持续存在的协调与裁决权威，不属于受委派 agent。它可以在上下文最完整时直接写规格
文档，也可在明确无法并行时承担一张卡的 Coder；这两种情况都不豁免独立审查和所需验证。

新身份不等于每次都派所有角色。只按变化面选择角色：

- 文档语义变化 → Critic；
- 实现或测试代码 diff → Reviewer；
- 可执行行为、结果、环境或打包输入变化 → 审查清零后派 Verifier；
- 等价的链接、格式、指针和状态机械刷新 → 只跑机器检查。

## 创建 agent 前准备完整 brief

每份 brief 必须包含：

1. `dispatch_id`、角色、一个有边界的目标和返回格式；
2. 精确的权威、基线、候选与相关证据锚；
3. 必要上下文指针，以及现有上下文未解决的具名问题；
4. 仓库/工作区事实、写权限、允许路径与禁止事项；
5. 仅与本次有关的已采纳 finding 或失败证据；
6. 必跑检查、预期证据、需报告的限制和回传门槛。

不得先创建 agent，再通过 follow-up 扩大任务。澄清只能解释 brief 里已有事实；新目标或新候选必须
新建 brief 和 agent。不要把凭据、telemetry 指令或无关项目历史放进 brief。

run-task Coder 的静态输入是精确 `Card.md`、`Log.md` 当前快照和权威锚。DocStar 可用时附带与
基线 commit 完全匹配的 brief，但它只是索引，不是权威。只按需补读精确指针，不默认读完整 Task
或 Log 历史。CodeGraph 只用于定位，结论必须回到当前源码、diff 和测试确认。

## 工作区与候选边界

仓库写入前必须确认：

- `git rev-parse --show-toplevel` 等于分配的绝对工作区；
- `baseline_anchor` 与 `expected_head_anchor` 都能解析为 commit；
- `HEAD` 等于本次初始或修订锚；
- 本次派发只有一个 writer，允许路径明确。

并发 writer 使用独立 worktree。Worktree 只隔离文件和 index，不解决语义、接口、merge 或共享资源
冲突。共享工作区不能安全隔离时，并行 agent 只返回 proposal，由一个 writer 串行应用。

写入回传必须给出一个不可变 `candidate_anchor`、修改文件、命令/结果、偏离和未解决实质风险。
回传时重新核验工作区与候选。未锚定、路径错误、权威过期或越界候选不得进入审查。

## 冻结候选与审查轮次

writer 先完成自检和机器检查，再冻结候选并进入独立审查。Critic 或 Reviewer 启动后，先收齐本轮
所有活动审查结果，再修改候选。主编排者一次裁定，并集中处理已采纳 blocker。

需要复核时使用新 agent。只有 brief 能证明原 finding、精确变化 diff、周边证据未变和影响边界时，
才允许定向复核；否则检查完整受影响面。未受影响的角色不得重新派发。非阻塞建议不重新打开候选。

相关 Critic/Reviewer blocker 未清零前不得派 Verifier。需要可执行证据时，只对最终候选派一个全新
Verifier。需要第二个验证边界时必须记录风险原因；在干净机械集成前后重复相同测试不增加证据。

## 各角色回传

- **Author**：返回指定文档候选、自检证据和偏离。
- **Critic**：只读；每条 finding 写位置、证据、影响、规范改法和 blocker 等级，不成为第二作者。
- **Coder**：实现一张 Card 的一次尝试，只写允许范围，补判别性测试，返回一个本地候选 commit；
  后续修正使用新 Coder。
- **Reviewer**：只读；检查固定实现 diff、规格对齐、未测路径、断言判别力、副作用和不必要复杂度。
- **Verifier**：不改产品语义或源码；针对指定最终候选返回原样命令、环境、退出码、限制和副作用。
- **Researcher**：区分直接观察、来源支持和推断；研究结果只有经主编排者裁定后才进入权威。

每个 agent 在唯一回传前自检，并直接修正范围内缺陷。不输出固定 `Reflection` 段；只报告足以改变
裁决、验收或下游工作的未解决实质风险。

## 平台说明

- Codex 每次创建角色都不 fork 父会话上下文。进度留在 agent 自己的 thread；只有 blocker、待裁决
  项、候选、finding、验证结果和完成属于主编排者事件。
- Claude Code 每次派发都创建新的 custom 或 general-purpose agent。禁止用 resume 或 SendMessage
  把后续工作发给已回传角色；Agent Teams 不自动提供 worktree 隔离。
- 只有派发、本地检查、状态刷新和集成都无事可做时才等待。使用一次最长安全事件等待；超时只是
  存活检查点，不得变成 list/status/wait 轮询。
- 在 Codex 中，只有调度/容量决策需要当前状态、等待超时后 agent 状态仍不明确，或收到的生命周期
  事件互相矛盾时，才调用一次 `list_agents` 获取状态快照。新的实质生命周期事件、候选、blocker 或
  调度条件变化出现前不得再次查询。`path_prefix` 只缩小查询范围，不是时间间隔；不存在定时查询周期。

平台能力不足不能成为静默复用 agent、扩大写权限或取消独立审查的理由。
