---
locale: zh-CN
purpose: 规定独立执行工作时的派发输入、agent 身份、运行态、角色边界与回传要求。
upstream: [GMGN §4](../../../../GMGN.zh-CN.md)
downstream: [GMGN 路由](../../SKILL.md), [代码审查](code-review.md)
status: approved
type: task
nature: normative
---

# 派发与 agent 生命周期契约

English: [../en/dispatch-and-handoff.md](../en/dispatch-and-handoff.md)

这是一份内容契约，不是填空 prompt。允许按任务和平台调整措辞与顺序，但不能漏掉要求的事实。

## 派发必填信息

每次派发都要说明：

- 一个可独立验收的目标与 `node_id`；
- 角色：`author | coder | critic | reviewer | verifier | researcher | integrator`；
- 新建 agent，还是恢复既有 `agent_ref`；
- 当前运行态、基线锚；已有候选时再写候选锚；
- 范围内路径/行为、明确禁区、权威链接和开工前必读材料；
- 当前阶段 Skill 规定的必备内容与自检项；
- 工作区权限、本机支持时的 effort、远端写入禁令；
- 交付物、原样验证命令或验收条件；需要时再写回传期限。

回传固定包含三类信息：产物/finding 与可重放证据；偏离与待裁决事项；Reflection。缺项时打回，
不能把不完整回传当作已审候选。

## 运行记录与状态

记录 `node_id`、`state`、`baseline_anchor`、`candidate_anchor`，以及当前需要的身份引用：
`author_ref`、`critic_ref`、`coder_ref`、`reviewer_ref`、`verifier_ref`、`integrator_ref`。
运行态与文档 `status`、工作项状态互不替代。

- `blocked-prerequisite`：缺硬前置。
- `awaiting-owner-input`：等负责人裁决、启动、批准或验收。
- `ready-to-dispatch`：输入与权威已齐，可派发。
- `author-active`：已登记 Author 正在写产物。
- `author-returned`：Author 已回传，只做过完整性与越界检查。
- `author-rework`：同一 Author 先修复缺项或越界，再进入评审。
- `candidate-anchored`：被审候选已有不可变版本锚。
- `critic-active`：独立 Critic 正在审候选。
- `critic-returned`：finding 已回主编排者，等待裁定。
- `author-revising`：同一 Author 正在处理已采纳 finding。
- `critic-rechecking`：同一 Critic 正在定向复核 blocker。
- `upstream-change-pending`：本节点暂停，等待上游权威受控变更完成。
- `acceptance-ready`：所需评审与检查无未解决 blocker。
- `accepted`：该层门禁负责人已接受当前候选锚。
- `integrating`：Integrator 正在刷新链接、状态、证据指针和提交材料。
- `node-complete`：产物、证据与表征一致，本节点完成。
- `agent-unavailable`：已登记 agent 无法恢复，进入替换规则。

实现和关账节点另用 `coder-active`、`coder-returned`、`coder-revising`、
`reviewer-active`、`reviewer-returned`、`reviewer-rechecking`、`verifier-active`、
`verifier-returned`；身份语义与对应的 Author/Critic 状态相同。

## 保持身份的评审循环

主编排者先派 Author，接收回传并固定候选锚，再派独立 Critic。Author 与 Critic 只向主编排者
回传，不直接协商，也不互改产物。

主编排者采纳 finding 后，必须恢复已登记的 `author_ref`，不能新派 Author。blocker 修完后回到
已登记的 `critic_ref` 做定向复核；非阻塞偏好不强制再开一轮。发现上游问题时保留当前 Author
身份并进入 `upstream-change-pending`，完成受控变更后把新权威锚交回同一 Author 续作。

平台无法恢复 agent 时进入 `agent-unavailable` 并记录原因。替换必须显式，接收完整节点记录，
不能冒充旧 agent。替换 Critic 必须重做完整审查；只有同一 Critic 才能做定向复核。进入下一
流程节点时，默认新建一组 Author/Critic，保持节点之间的独立性。

## 角色要求

- **Author**：读取必读锚，只写本节点产物或增量；满足阶段 Skill 的内容契约，但自行决定文档
  结构；自检后回传改动文件、候选锚、检查、偏离与 Reflection。
- **Critic**：只读且与 Author 独立，只审指定增量和最小必要上下文；每条 finding 写位置、证据、
  影响、规范改法与 blocker 等级；不改文件、不扩范围、不成为第二作者。
- **Coder**：按一张已批准任务卡实现；先有能区分错误实现的失败测试，选择首个足够方案，限制
  改动路径，并给出可重放真实路径证据。
- **Reviewer**：只读审查已固定锚的代码或组合增量，只报 finding，不代修。
- **Verifier**：在候选锚独立运行指定测试、启动/E2E、负向路径与门禁；回传原样命令、环境、
  退出码和限制；不得修改产品语义或源码。
- **Integrator**：只做已接受的机械传导，包括双向链接、映射、状态、证据指针和提交准备；遇到
  语义不清时上报，不能自行裁决。
- **Researcher**：收集限定范围内的证据，区分实测、来源支持与推断；建议不能直接成为权威。

本机支持时，机械工作用 low，常规执行用 medium，判断密集或高风险工作用 high。输入必须
自包含，不能假设 agent 读过主会话。命令由对应的 Reviewer、Verifier 或 Integrator 重放并落盘
证据；主编排者只核对候选锚、落盘输出与范围，不接管执行。生产 agent 的自述本身不是验收证据。

## 平台适配

- **Codex**：安装后的 Skill 在每次派发里携带上述角色要求。项目或用户级 custom-agent TOML
  可以细化角色，但插件内附的 `.codex/agents` 不会因此自动变成目标项目配置。记录新建 agent 的
  target/thread 引用，修订或复核时把 follow-up 发回该引用。
- **Claude Code**：插件 agent 位于插件根 `agents/`。记录回传的 agent ID，并用平台的 agent
  消息能力恢复它；节点记录要求同一 Author、Coder、Critic 或 Reviewer 时，不得重新调用一个
  新插件 agent。

某个 surface 没有 steering 或恢复能力时，进入 `agent-unavailable`，不能静默放宽身份规则。
