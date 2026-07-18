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

这是一份内容契约，不是填空 prompt。允许按任务和平台调整措辞与顺序，但不能漏掉以下事实。

## 派发必填信息

每次派发都要说明：

- 一个可独立验收的目标，以及角色
  `author | coder | critic | reviewer | verifier | researcher | integrator`；
- 新建 agent 还是恢复既有身份引用；
- 当前运行态、权威链接、必读材料、范围内路径/行为和明确禁区；
- 当前阶段 Skill 的必备内容与自检项；
- 工作区权限、本机支持时的 effort、远端写入禁令、交付物与原样验证或验收条件。

任何操作仓库的文档节点、实现 lane 或集成队列派发，都记录并核验现有
`workspace_mode`、`worktree_path`、`branch_ref`；这些是当前派发的工作区事实，不与 agent 身份
永久绑定。文档节点另外记录 `node_id`、`baseline_anchor`、`candidate_anchor`，以及需要的
`author_ref`、`critic_ref` 或 `integrator_ref`。实现 lane 只使用这些工作区/集成字段：`run_id`、`card_id`、
`workspace_mode`、`worktree_path`、`branch_ref`、`baseline_anchor`、`candidate_anchor`、
`write_set`、`conflict_domains`、`runtime_locks`、`integration_queue_ref`、
`shared_baseline_anchor`，另记录各自的 `coder_ref`、`reviewer_ref`、`verifier_ref`。共享集成队列
保留同一个 `integrator_ref`。任务规划还要说明 `depends_on` 和 semantic owner。

回传固定包含三类信息：产物/finding 与可重放证据；偏离与待裁决事项；Reflection。任何会写仓库的
派发进入 `workspace-prepared` 前，都运行 `git rev-parse --show-toplevel`，并要求解析结果等于绝对
`worktree_path`；还要让 `git rev-parse --verify "${baseline_anchor}^{commit}"` 成功，并要求
`git rev-parse HEAD` 精确等于该 commit。若已批准权威锚是内容 hash，派发前先把它映射到仓库中
已有且已批准的对应 commit，并用该 commit 作为 `baseline_anchor`，不新增第二个基线字段。若
`HEAD` 不同，切到已批准 commit 或重建 worktree，再重做两项核验。

每次 agent 回传前都重新核验当前派发路径。写仓库的回传还必须证明 `candidate_anchor` 精确指向
本次候选；候选是 commit 时，`git rev-parse --verify "${candidate_anchor}^{commit}"` 必须成功。
Writer 产出候选后，不要求 `HEAD` 仍等于旧 `baseline_anchor`。路径/锚不符或回传缺项时打回，
不能把它当作已审候选。

## 运行状态

运行态与文档 `status`、任务工作状态互不替代。

- `blocked-prerequisite`：缺硬依赖或权威。
- `awaiting-owner-input`：等负责人裁决、启动、批准或验收。
- `ready-to-dispatch`：输入、权威、依赖、冲突域和锁均可用。
- `workspace-prepared`：隔离工作区、仓库根核验和精确的
  `HEAD == baseline_anchor` commit 核验都已通过。
- `author-active`、`author-returned`、`author-rework`、`author-revising`：已登记 Author 正在写、
  已回传、修复不完整回传或处理已采纳 finding。
- `candidate-anchored`：被审候选已有不可变版本锚。
- `critic-active`、`critic-returned`、`critic-rechecking`：独立 Critic 正在审、已回传或由同一
  Critic 定向复核 blocker。
- `coder-active`、`coder-returned`、`coder-revising`：本 lane 的 Coder 正在实现、已回传或修订。
- `reviewer-active`、`reviewer-returned`、`reviewer-rechecking`：本 lane 的独立 Reviewer 正在审、
  已回传或复核受影响 diff。
- `verifier-active`、`verifier-returned`：本 lane 的 Verifier 正在执行或已回传。
- `upstream-change-pending`：只有受影响节点/lane 等待上游受控变更。
- `acceptance-ready`：所需评审和候选验证无未解决 blocker。
- `accepted`：隔离候选可以进入集成；实现任务卡此时还不是 `closed`。
- `integration-queued`：已接受任务卡在指定集成队列等待。
- `integrating`：单一 Integrator 正在把 lane 合入共享基线。
- `integration-conflict`：集成停止，必须回原 Coder 处置。
- `rebase-required`：机械应用不干净、依赖/规格语义在当前基线失效，或处置需要 Coder 判断；回原
  Coder 更新 lane。共享基线前移本身不进入该状态。
- `post-integration-verifying`：同一 Verifier 正在验证组合后的共享基线。
- `node-complete`：产物、共享基线、证据和表征一致；实现任务卡此时才可标 `closed`。
- `agent-unavailable`：已登记 agent 无法恢复，进入替换规则。

实现 lane 的正常尾段是 `accepted → integration-queued → integrating →
post-integration-verifying → node-complete`。

## 滚动 ready set 与工作区隔离

任一回传、集成、冲突或阻塞后，主编排者立即重算 ready set 并补满槽位。并发数取平台并发、
ready 卡、隔离工作区和排他资源容量四者的最小值，不写死。队列先按依赖拓扑，再按稳定
`card_id` 排序。一条 lane 及其依赖后代受阻时，无关 lane 继续。

`workspace_mode: worktree` 必须显式 provision 绝对 `worktree_path`，使用 detached `HEAD` 或唯一
`branch_ref`；同一分支不得挂到多个 worktree。Worktree 只隔离文件和 index，不消除 merge、
语义、接口或共享运行资源冲突。

`workspace_mode: shared` 无法给每个 writer 独立锚定时，并行 agent 只返回 proposal/patch，不直接
编辑、stage 或 commit；由一个已登记 Author 或 Coder 串行应用和锚定。同一权威文档默认单
writer；只有 section/ID 稳定且互不相交、无共享语义/接口、独立
worktree 时才可受控并行，组合候选必须重新 Critic。Frontmatter、目录、共享表、全文件格式化，
以及相同 decision、AC 或段落不得并行写。

## 保持身份的循环与集成所有权

Author 与 Critic、Coder 与 Reviewer 只经主编排者中转。已采纳文档 finding 回同一
`author_ref`，blocker 回同一 `critic_ref`。代码 finding、`integration-conflict` 和
`rebase-required` 回同一 `coder_ref`；所有受影响 diff 回同一 `reviewer_ref`；受影响验证回同一
`verifier_ref`。

一个 `integrator_ref` 串行拥有集成工作区、`integration_queue_ref`、共享基线、`Task.md` 和追踪
矩阵。集成分两阶段：从干净的当前 `shared_baseline_anchor` 创建隔离临时组合，机械应用已接受的
本地 commit `candidate_anchor`，但不推进共享锚。事件/证据保留前一锚，不新增同义 top-level
runtime 字段。同一 Verifier 改收临时组合当前的 `workspace_mode`、`worktree_path`、`branch_ref`。

只有集成后验证通过，并完成已接受的机械台账刷新，才原子推进 `shared_baseline_anchor`。
merge/cherry-pick 冲突或验证失败时，中止操作或丢弃临时工作区，保持原共享锚不变，并用
`git status --short` 确认其 index/worktree clean 后再处理无关队列项。未验证组合不得成为共享
基线。

平台无法恢复 agent 时进入 `agent-unavailable`，记录原因并显式替换，把完整 lane 记录交过去。
替换 Critic/Reviewer 必须做完整审查；替换 Verifier 必须重跑全部要求的验证；替换 Integrator
必须重读队列与共享基线并重放机械检查。

## 角色要求

- **Author**：只写指定文档或关账产物/增量，满足当前 `write-*` 或 `close-milestone` 内容契约，
  自行组织结构并自检；只有派发是 run-task 卡时才启用卡级规则。
- **Critic**：只读且独立；finding 写位置、证据、影响、规范改法与 blocker，不改文件或成为
  第二作者。
- **Coder**：只实现一张已批准卡，只在记录工作区和 `write_set` 内工作；在 detached `HEAD` 或
  唯一分支只 stage/commit 本卡写集，回传可解析本地 commit SHA 作为不可变 `candidate_anchor`；
  禁止远端写入或夹带无关路径。
- **Reviewer**：是文档、代码或里程碑关账增量的通用只读审查角色。当前派发为 run-task 卡时，
  才按 `baseline_anchor..candidate_anchor` 和卡级冲突/复核规则审查。
- **Verifier**：按当前阶段独立运行测试、真实路径、负向场景和门禁。当前派发为 run-task 卡时，
  同一 `verifier_ref` 在候选阶段接收卡 worktree，集成后阶段接收 Integrator 的临时组合 worktree，
  两次都核验当前派发路径。
- **Integrator**：为文档和里程碑阶段执行已接受的机械传导。当前派发为 run-task 卡时，才作为
  共享基线单一写者并执行上述两阶段集成与回滚协议。
- **Researcher**：收集限定证据并区分实测、来源支持与推断；建议不能直接成为权威。

## 平台适配

- **Codex**：每次派发都携带这些要求，记录 target/thread，并把修订或复核 follow-up 发回原
  target。插件内 `.codex/agents` 不会自动成为目标项目配置；subagent 也不代表自动隔离，必须
  provision 并传入绝对 worktree。
- **Claude Code**：普通 subagent 默认共享主会话 cwd，也不共享调度 DAG 或自动 ready set。主
  session 在等待前，用具名 `Agent` call 把当前所有 ready 项派到实际平台容量；任一 agent 完成后
  立即更新 ready set 并补上空槽。并发容量读取平台实际能力，不从写死的环境变量默认值推断。

  需要恢复身份的 Author、Critic、Coder、Reviewer、Verifier、Integrator 使用 custom 或
  `general-purpose` agent，并记录 agent ID。只有启用
  `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 时才可使用 `SendMessage`；启用该 flag 不等于必须采用
  Agent Teams。消息能力可用时按 agent ID 恢复；不可用时进入既有 `agent-unavailable` 显式替换
  规则，不能声称做原身份的定向复核、使用同一 Verifier 或同一 Integrator。`Explore` 与 `Plan`
  不能承担必须恢复身份的角色。插件 agent 位于根 `agents/`。

  不能把普通 subagent 写成自动 worktree。只有 agent frontmatter/call 显式
  `isolation: worktree`，或 Agent View/background、Desktop、`/batch` 等隔离 surface 才提供独立
  工作区。Agent Teams 是实验性的可选调度器：可以解锁依赖和自动认领任务，但不自动创建
  worktree，且进程内 teammate 不会跨 `/resume` 保留；它不是 GMGN 默认的正确性路径。只有显式
  启用、每个 writer 分别隔离，且文件域与冲突域都互不重叠时，才允许 Agent Teams 写入；否则
  teammate 只读或只返回 proposal。同文件并行 writer 会互相覆盖。

  GMGN 不依赖自动 merge，仍由已登记 Integrator 显式集成。原生 worktree 默认基线可能是
  fresh/origin default，不保证等于已批准 `baseline_anchor`；开工前必须核验精确 commit，不一致时
  选择批准 head、使用 `WorktreeCreate` hook 或手动 provision。不得写死 Claude 临时路径或分支名。
  Reviewer、Verifier、Integrator 按当前派发路径工作，不盲目新建另一个 worktree。

Surface 缺 steering、恢复或安全工作区能力时，按对应降级规则处理，不能静默放宽身份或隔离。
