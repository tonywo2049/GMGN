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
  `author | coder | critic | reviewer | verifier | researcher`；
- 新建 agent 还是恢复既有身份引用；
- 当前运行态、权威链接、必读材料、范围内路径/行为和明确禁区；
- 当前阶段 Skill 的必备内容与自检项；
- 工作区权限、本机支持时的 effort、远端写入禁令、交付物与原样验证或验收条件。

对 `run-task`，经过 Critic 与主编排者评审的 `Task.md` 任务卡是唯一静态执行权威。精确的任务卡与
权威锚已经满足本契约的静态部分，不把卡片正文复制成另一份 prompt 或文档。最小派发只补当前角色
与身份模式、权威仓库或 corpus 指针、运行态、lane/workspace/anchor 事实、权限、禁区和回传门禁；
DocStar 可用时必须附带已核验的同一基线 brief 作为派生索引；不可用时附降级记录和定向读取指针。
这不是逐 agent 的 `Handoff`；GMGN Handoff 只在
关账后，或不跨越活动 owner-bound lane 的会话边界记录接手态。

run-task lane 先解析不可变基线 commit；DocStar 支持时，用
`--baseline <baseline_anchor>` 生成 brief，并在派发前核对 manifest SHA 等于该完整 commit。
brief 是起始证据包，不禁止定向读取原文。证据缺失或冲突时，接收者可以沿
`omitted`／`boundary_pointers`、运行更窄的 DocStar 查询，或直接读取精确文件和行区间。
DocStar 缺失或失败要记录降级原因，再改用定向读取。
修订 Coder 接收该权威 brief，再加当前任务卡快照、已锚定候选、已采纳 finding、最近一个相关事件、
可重放失败证据和回传门禁。这里规定的是必备事实，不是强制 prompt 或检查点模板。

CodeGraph 是代码关系的定位工具，不是证据权威。存在 `.codegraph/` 时，Coder 在已检出的
`expected_head_anchor` 使用，
Reviewer 在候选锚独立使用，Verifier 只在失败或覆盖范围不明确时按需使用。索引无法证明对应当前
commit 时，只把结果当定位线索，并回到已检出源码、Git diff 与测试核验。

每次 run-task Coder 尝试都新建，且不继承父会话或此前 Coder 的历史。Reviewer、Verifier 可以新建
或恢复自己的身份，但不继承父会话历史。Codex 暴露
历史 schema 时设置 `fork_turns="none"`；暴露布尔 schema 时设置 `fork_context=false`，或在平台
明确以 false 为默认值时省略。不得对这些角色使用 `fork_turns="all"` 或 `fork_context=true`。
恢复 Reviewer 或 Verifier 可以保留该 agent 自己的历史，但不得导入 scheduler transcript；Coder
修订始终新建。若执行所需语义
只存在于聊天，任务卡就尚未 ready：停止受影响 lane，返回 `write-task`，先让权威经过评审并锚定。

详细执行历史不属于正常初次派发的必读集。只有修订、续跑、重试、失败、冲突、身份替换、审计或关账时，
才沿任务卡的 `execution_log` 指针，从已锚定的 `latest_event` 开始，定向提取该事件并只沿当前未解决
周期需要的链接读取，不整份读入描述性日志。执行单卡时只解析精确卡片、直接门禁行、受影响 AC 行、
当前共享基线与集成队列指针，不整份读入 `Task.md`。只存在于日志里的语义必须先
提升到正确的规范性权威，受影响工作才能继续。

任何操作仓库的文档节点、实现 lane 或主编排者集成操作，都记录并核验现有
`workspace_mode`、`worktree_path`、`branch_ref`；这些是当前仓库操作的工作区事实，不与 agent 身份
永久绑定。文档节点另外记录 `node_id`、`baseline_anchor`、`candidate_anchor`，以及需要的
`author_ref` 或 `critic_ref`。实现 lane 只使用这些工作区/集成字段：
`project_scope_id`、`lane_key`、`owner_thread_id`、`owner_run_id`、`ownership_epoch`、`run_id`、
`card_id`、`workspace_mode`、`worktree_path`、`branch_ref`、`baseline_anchor`、
`repository_identity`、`coder_epoch`、`candidate_anchor`、`candidate_coder_epoch`、
`write_set`、`conflict_domains`、`runtime_locks`、`integration_queue_ref`、
`shared_baseline_anchor`，另记录各自的 `coder_ref`、`reviewer_ref`、`verifier_ref`。共享集成队列由
`owner_thread_id` 与 `owner_run_id` 指向的主编排者持有。任务规划还要说明 `depends_on` 和 semantic owner。
`owner_thread_id` 是拥有 writer lane 的主任务，`owner_run_id` 是持有 claim 的 scheduler run，
`coder_ref` 与 `coder_epoch` 共同标识本 lane 当前的 Coder 尝试：通常是受委派 Coder；满足“当前无法
与主编排工作并行”规则时也可以是主 session。三者不能互相替代。`run_id` 仍只表示执行来源，不是
唯一键。写入前用 `bind-coder` 绑定首轮 Coder；后续尝试用原子 `rotate-coder`，禁止静默接管已绑定
给其他 Coder 的 lane。

WhitePaper、ROADMAP、Goal、Requirement、Design、Task 在开写前先记录 writer 选择。
`author_ref` 可以指向主 session，也可以指向受委派 Author agent。主编排者的上下文使直接写作最
清楚、最省交接时优先自己写；只有边界清楚，且隔离、专业性或并行收益足以覆盖交接成本时才委派。
`author_ref` 绑定主 session 表示生命周期身份，不是 Author-agent 派发。Critic 必须独立于实际 writer。

每个 agent 回传前都按当前阶段契约、已有证据和任务特定失败方式自检，并先修正范围内缺陷；
自检过程不是回传产物，不输出固定 `Reflection` 段。回传包含产物/finding 与可重放证据、偏离与
待裁决事项；只有未解决风险足以改变结论、裁决、验收或下游工作时才披露，没有就省略。
批准、验收和关账候选必须说明剩余实质风险，或明确没有已知风险。任何会写仓库的派发进入
`workspace-prepared` 前，先派生 `expected_head_anchor`：初次尝试使用 `baseline_anchor`，修订使用
当前 `candidate_anchor`。运行 `git rev-parse --show-toplevel`，并要求解析结果等于绝对
`worktree_path`；还要让 `git rev-parse --verify "${baseline_anchor}^{commit}"` 与
`git rev-parse --verify "${expected_head_anchor}^{commit}"` 成功，并要求 `git rev-parse HEAD` 精确
等于 expected-head commit。若已批准权威锚是内容 hash，派发前先把它映射到仓库中已有且已批准的
对应 commit，并用该 commit 作为 `baseline_anchor`，不新增第二个基线字段。若 `HEAD` 不同，切到
expected commit 或重建 worktree，再重做核验。

每次 agent 回传前都重新核验当前派发路径。写仓库的回传还必须证明 `candidate_anchor` 精确指向
本次候选；候选是 commit 时，`git rev-parse --verify "${candidate_anchor}^{commit}"` 必须成功。
Writer 产出候选后，不要求 `HEAD` 仍等于旧 `baseline_anchor`。路径/锚不符或回传缺项时打回，
不能把它当作已审候选。

## 运行状态

运行态与文档 `status`、任务工作状态互不替代。

- `blocked-prerequisite`：缺硬依赖或权威。
- `awaiting-owner-input`：等负责人裁决、启动、批准或验收。
- `ready-to-dispatch`：输入、权威、依赖、冲突域和锁均可用；规格文档此时可选择并绑定实际 writer。
- `workspace-prepared`：已分配工作区、仓库根核验和精确的 `HEAD == expected_head_anchor` commit
  核验都已通过；初次尝试的 expected head 是 `baseline_anchor`，修订是当前 `candidate_anchor`。
- `author-active`、`author-returned`、`author-rework`、`author-revising`：已登记 writer 正在写、
  已回传或到达自检检查点、修复不完整候选或处理已采纳 finding。实际 writer 可以是主 session，
  也可以是受委派 Author agent。
- `candidate-anchored`：被审候选已有不可变版本锚。
- `critic-active`、`critic-returned`、`critic-rechecking`：独立 Critic 正在审、已回传或由同一
  Critic 定向复核 blocker。
- `coder-active`、`coder-returned`、`coder-revising`：本 lane 当前 Coder 尝试正在实现、已回传或
  修订；修订使用新一代 Coder。
- `candidate-awaiting-anchor`：Coder 已回传初版或修订候选，但 scheduler 尚未完成身份/diff 检查与
  原子 anchor；此时禁止派 Reviewer。
- `review-authorized`：scheduler 已锚定精确候选，并显式授权该候选与 ownership epoch 进入审查。
- `reviewer-active`、`reviewer-returned`、`reviewer-rechecking`：本 lane 的独立 Reviewer 正在审、
  已回传或复核受影响 diff。
- `verifier-active`、`verifier-returned`：本 lane 的 Verifier 正在执行或已回传。
- `upstream-change-pending`：只有受影响节点/lane 等待上游受控变更。
- `acceptance-ready`：所需评审和候选验证无未解决 blocker。
- `accepted`：锚定候选已通过裁定或负责人批准。文档候选只有工作区拓扑要求时才跨集成边界；
  实现任务卡进入集成队列，此时还不是 `closed`。
- `integration-queued`：已接受任务卡在指定集成队列等待。
- `integrating`：主编排者正在把候选跨隔离工作区、并发 writer 或共享基线边界应用。
- `integration-conflict`：集成停止，从当前候选启动新 Coder 处置。
- `rebase-required`：机械应用不干净、依赖/规格语义在当前基线失效，或处置需要 Coder 判断；从当前
  候选启动新 Coder 更新 lane。共享基线前移本身不进入该状态。
- `post-integration-verifying`：同一 Verifier 正在验证组合后的共享基线。
- `node-complete`：产物、共享基线、证据和表征一致；实现任务卡此时才可标 `closed`。
- `agent-unavailable`：已登记 agent 无法恢复，进入替换规则。
- `owner-unreachable`：活动 writer lane 的已登记 owner 无法确认；禁止新 writer 自动 claim、复用、
  过期或抢占该 lane。
- `worker-create-requested`、`worker-queued`、`worker-resolved`、`worker-bootstrap-returned`、
  `lane-claimed`、`coder-bound`、`worker-activated`：Codex 跨主任务启动状态；排队 client ID 不是
  活动 worker target。

实现 lane 的正常尾段是 `accepted → integration-queued → integrating →
post-integration-verifying → node-complete`。

## 滚动 ready set 与工作区隔离

任一回传、集成、冲突或阻塞后，主编排者立即重算 ready set 并补满槽位。并发数取平台并发、
ready 卡、隔离工作区和排他资源容量四者的最小值，不写死。队列先按依赖拓扑，再按稳定
`card_id` 排序。一条 lane 及其依赖后代受阻时，无关 lane 继续。

实现 lane 在整个项目的所有主任务间唯一：`lane_key` 由 `project_scope_id + card_id` 确定，
`run_id` 只表示执行来源。任何 Coder 写入前，scheduler 必须在权威项目的共享 lane registry 中
原子 claim 任务卡与 canonical `worktree_path`，再核验 `owner_thread_id`、`owner_run_id`、
`ownership_epoch`、`coder_ref`、`coder_epoch` 和路径。同一卡或同一 canonical 路径最多有一个活动
writer。跨任务 `claim` 不携带 Coder 身份，随后用 `bind-coder` 显式绑定首轮 Coder；后续用
`rotate-coder` 从当前已锚候选原子绑定新 Coder。每次 verify、anchor、rotate 和正常 release 都必须
携带并精确匹配当前 `coder_ref` 与 `coder_epoch`。绑定前只能用 `cancel-unbound` 取消 claim。跨任务
扫描只用于诊断冲突，不是锁。旧 owner、旧 epoch、缺失/错误 Coder、旧 Coder generation 或重建
仓库路径的回传必须在审查、集成前拒绝。Reviewer、Verifier 只能按已登记锚只读共存。

claim 还把 canonical Git common-dir、git-dir 路径、两个目录的本机 stat 身份和 object format 记为
`repository_identity`。每次 bind、verify、anchor、release 或取消未绑定 claim 都重新计算该身份，
并确认原 `baseline_anchor` 仍存在。同一绝对路径换成另一 clone 后，即便包含同一 baseline commit，
也不是原仓库。

`workspace_mode: worktree` 必须显式 provision 绝对 `worktree_path`，使用 detached `HEAD` 或唯一
`branch_ref`；同一分支不得挂到多个 worktree。Worktree 只隔离文件和 index，不消除 merge、
语义、接口或共享运行资源冲突。

`workspace_mode: shared` 无法给每个 writer 独立锚定时，并行 agent 只返回 proposal/patch，不直接
编辑、stage 或 commit；由一个已登记 writer 串行应用和锚定。同一权威文档默认单
writer；只有 section/ID 稳定且互不相交、无共享语义/接口、独立
worktree 时才可受控并行，组合候选必须重新 Critic。Frontmatter、目录、共享表、全文件格式化，
以及相同 decision、AC 或段落不得并行写。

## 保持身份的循环与集成所有权

受委派 Author 与 Critic、Coder 与 Reviewer 只经主编排者中转。已采纳文档 finding 回同一
`author_ref`；该引用是主 session 时，由它直接修改，不经过 Author-agent handoff。blocker 回同一
`critic_ref`。代码 finding、实现失败、`integration-conflict` 和 `rebase-required` 都从当前已锚候选
启动新 Coder 尝试；所有受影响 diff 回同一 `reviewer_ref`，受影响验证回同一 `verifier_ref`。同一
Critic 保留用于 blocker 定向复核；替换 Critic 或 Reviewer 必须重做完整审查。

worker 的每个初版或修订候选都停在 `candidate-awaiting-anchor` 并回传 scheduler。worker 不得改
registry 或派 Reviewer。scheduler 核验已绑定 lane/仓库/路径、当前 `coder_ref` 与 `coder_epoch`、
候选 commit 和 `write_set`，执行原子 anchor，记录 `candidate_coder_epoch`，结束本次 Coder，再发送
绑定候选与 epoch 的 `review-authorized`。只有此后 worker 才能派 Reviewer。修订先新建只读 Coder，
scheduler 核验 `HEAD == candidate_anchor` 后原子 rotate 并激活；修订使旧授权失效，并重走该门禁。

规格文档的已接受同批机械传导、机检与提交控制都由主编排者完成，包括跨隔离工作区、并发 writer
或共享基线边界的候选。实现阶段由主编排者串行拥有集成工作区、`integration_queue_ref`、共享基线、
`Task.md`、单卡执行日志和追踪矩阵。实现集成分两阶段：
从干净的当前 `shared_baseline_anchor` 创建隔离临时组合，机械应用已接受的
本地 commit `candidate_anchor`，但不推进共享锚。事件/证据保留前一锚，不新增同义 top-level
runtime 字段。同一 Verifier 改收临时组合当前的 `workspace_mode`、`worktree_path`、`branch_ref`。

只有集成后验证通过，并完成已接受的机械台账刷新，才原子推进 `shared_baseline_anchor`。
merge/cherry-pick 冲突或验证失败时，中止操作或丢弃临时工作区，恢复前一个共享锚，并用
`git status --short` 确认其 index/worktree clean；失败实现候选不得推进该锚。主编排者可从这个
干净锚另建并机械检查状态候选，只把持久事件追加到 `execution/<card_id>.md`，并在 `Task.md` 中
替换当前阻塞、状态、版本锚、证据与 `latest_event`；该描述性提交随后可以推进共享锚。不得把详细历史
复制回 Task，也不得把多张卡合并进一个总日志。未验证实现组合不得成为共享基线。

集成后验证通过后，验证过的组合候选本身必须追加最终事件、关闭日志元信息、精简并关闭 Task 卡，
同批刷新受影响追踪与证据。只有这个精确候选可以推进共享锚，之后运行态 lane 才进入
`node-complete`，随后结束已完成角色的 thread。

平台无法恢复 agent 时进入 `agent-unavailable`，记录原因并显式替换，把完整 lane 记录交过去。
替换 Critic/Reviewer 必须做完整审查；替换 Verifier 必须重跑全部要求的验证。活动 lane 不得变更
`owner_thread_id` 或 `owner_run_id`；原主 session 无法恢复时进入 `owner-unreachable`，新 session
不得重建 owner、冒用旧 ID、anchor、集成或 release 该 lane。只有原 session 拥有的全部 lane 都已
`node-complete` 并 release 后，才允许主 session 交接。

## 角色要求

- **Author**：只在写作已委派时使用；只写指定文档或关账产物/增量，满足当前 `brainstorm`、
  `write-*` 或 `close-milestone` 内容契约，自行组织结构并自检，回传检查结果及仍未解决的实质风险。
  只有派发是 run-task 卡时才启用卡级规则。
- **Critic**：只读且独立；finding 写位置、证据、影响、规范改法与 blocker，不改文件或成为
  第二作者。
- **Coder**：只为一张已批准卡实现一次不可变候选，只在记录工作区和 `write_set` 内工作；在
  detached `HEAD` 或唯一分支只 stage/commit 本卡写集，回传可解析本地 commit SHA 作为不可变
  `candidate_anchor`，锚定后结束本次 thread。后续修订新建 Coder，只接收权威 brief 与当前周期增量，
  不继承此前 Coder 对话。禁止远端写入或夹带无关路径。只有当前没有实现 lane 能与有用的主编排工作
  并行时，主 session 才可在一条 lane 上承担该身份；隔离、锚定、独立 Reviewer 与独立 Verifier
  均不豁免。
- **Reviewer**：是文档、代码或里程碑关账增量的通用只读审查角色。当前派发为 run-task 卡时，
  只有收到精确 `review-authorized` 后，才按 `baseline_anchor..candidate_anchor` 和卡级冲突/复核规则
  审查。
- **Verifier**：按当前阶段独立运行测试、真实路径、负向场景和门禁。当前派发为 run-task 卡时，
  同一 `verifier_ref` 在候选阶段接收卡 worktree，集成后阶段接收主编排者的临时组合 worktree，
  两次都核验当前派发路径。
- **Researcher**：收集限定证据并区分实测、来源支持与推断；建议不能直接成为权威。

## 平台适配

- **Codex**：每次派发都携带这些要求，记录 target/thread。Reviewer、Verifier 的定向复核 follow-up
  发回原 target；Coder 修订新建 target。插件内 `.codex/agents` 不会自动成为目标项目配置；
  subagent 也不代表自动隔离，必须
  provision 并传入绝对 worktree。

  先补满当前任务的实际 subagent 容量。若仍有 ready 卡，只有负责人明确授权本轮跨任务
  fan-out，且 `create_thread`、`list_threads`、`read_thread`、`wait_threads`、
  `send_message_to_thread` 都可用时，才创建 worker 主任务。第一次阻塞等待前发出当前允许的全部
  创建请求；创建容量不足时让 lane 保持 ready，任一完成后再补位。

  每个 worker 初始 prompt 只读，只写一张卡/一个 worktree，禁止递归创建主任务，并可创建一个只读
  Coder；回传精确 worktree/仓库事实和 `coder_ref`。`clientThreadId`、`threadId`、`hostId`、wait
  cursor 都按原样保留。创建只返回排队 `clientThreadId` 时，用非阻塞任务观察解析为实际
  `threadId + hostId`；解析前禁止放入 `wait_threads`、claim lane 或激活。解析并 bootstrap 完成后，
  scheduler 执行 `claim → bind-coder → verify`，再激活该首轮 Coder。修订时 bootstrap 另一个只读
  Coder，等待 scheduler 完成 `rotate-coder` 后再写入。

  原 scheduler 是全局 ready set、lane registry、integration queue 与共享基线的唯一
  owner。worker 禁止改 registry、递归创建主任务、裁决、接受、执行集成、修改共享 `Task.md` 或追踪
  矩阵、push、发布。活动 worker 超过一次 `wait_threads` 的运行时 target 上限时，按实测能力动态
  分组；支持并行等待就并行，不支持则只在分组变化时做一次 `timeoutMs: 0` 快照，再用平台允许的
  最长安全等待阻塞一个选定组。超时后只记录下一次外部重新激活时应选择的组并立即 yield；本轮不得
  再调用任何 wait，也不得列出/读取任务。超时只是存活检查点，不是本轮轮转信号。任一实质更新后
  立即补位。worker 可在自己的 thread 显示进度，但只向 scheduler 推送 blocker、需要批准或裁决、
  候选、审查、验证和完成事件，不发进度或周期 heartbeat。缺能力或未获本轮授权时，退化为当前
  任务内滚动调度。不得把当前/默认 subagent 数、
  wait target 数或轮询间隔写成方法常量。

  当前任务内，只在 ready 派发、主 session Coder 工作、集成、状态刷新和本地检查都已做完时，调用
  一个覆盖任一 live agent 的事件驱动 `wait_agent`。等待时长取 surface 的用户更新与存活约束允许的
  最长安全值。超时后恢复有用本地工作或让出控制权，禁止自动串联 `list_agents`、status/worktree
  探测和下一次 `wait_agent`；只有跨过由任务本身推导的存活阈值后，才发送一次定向状态请求。
- **Claude Code**：普通 subagent 默认共享主会话 cwd，也不共享调度 DAG 或自动 ready set。主
  session 在等待前，用具名 `Agent` call 把当前所有 ready 项派到实际平台容量；任一 agent 完成后
  立即更新 ready set 并补上空槽。并发容量读取平台实际能力，不从写死的环境变量默认值推断。

  Author、Critic、Coder、Reviewer、Verifier 工作委派给需要恢复身份的 agent 时，
  使用 custom 或 `general-purpose` agent，并记录 agent ID。主 session 作为文档 writer 不属于
  Author-agent 派发。只有启用
  `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 时才可使用 `SendMessage`；启用该 flag 不等于必须采用
  Agent Teams。消息能力可用时按 agent ID 恢复；不可用时进入既有 `agent-unavailable` 显式替换
  规则，不能声称做原身份的定向复核或使用同一 Verifier。`Explore` 与 `Plan`
  不能承担必须恢复身份的角色。插件 agent 位于根 `agents/`。

  不能把普通 subagent 写成自动 worktree。只有 agent frontmatter/call 显式
  `isolation: worktree`，或 Agent View/background、Desktop、`/batch` 等隔离 surface 才提供独立
  工作区。Agent Teams 是实验性的可选调度器：可以解锁依赖和自动认领任务，但不自动创建
  worktree，且进程内 teammate 不会跨 `/resume` 保留；它不是 GMGN 默认的正确性路径。只有显式
  启用、每个 writer 分别隔离，且文件域与冲突域都互不重叠时，才允许 Agent Teams 写入；否则
  teammate 只读或只返回 proposal。同文件并行 writer 会互相覆盖。

  GMGN 不依赖自动 merge。候选跨集成边界时由主编排者显式集成；实现候选始终如此。
  原生 worktree 默认基线可能是
  fresh/origin default，不保证等于已批准 `baseline_anchor`；开工前必须核验精确 commit，不一致时
  选择批准 head、使用 `WorktreeCreate` hook 或手动 provision。不得写死 Claude 临时路径或分支名。
  Reviewer、Verifier 按当前派发路径工作，不盲目新建另一个 worktree。

Surface 缺 steering、恢复或安全工作区能力时，按对应降级规则处理，不能静默放宽身份或隔离。
