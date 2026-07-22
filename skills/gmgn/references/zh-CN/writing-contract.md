---
locale: zh-CN
purpose: 定义 GMGN 中英文文档共享的稳定机器字段、状态、文件名、编号和解析接口。
upstream: [GMGN 方法论](../../../../GMGN.zh-CN.md)
downstream: [GMGN 路由](../../SKILL.md)
status: approved
type: design
nature: normative
---

# GMGN 文档写作契约

English: [../en/writing-contract.md](../en/writing-contract.md)

## 1. 语言与元信息块

项目根据现有文档和用户请求选择 `en` 或 `zh-CN`。正文使用所选语言；下列机器字段、枚举、文件名、
ID、命令和 Task 表头不翻译。中英镜像放在不同 locale 目录，避免相同 ID 被当成一份语料扫描。

每份 GMGN 管理的文档使用以下七个元信息键：

```yaml
---
locale: zh-CN
purpose: <一句话说明本文回答什么>
upstream: [<上游名称>](<相对路径>)
downstream: [<下游名称>](<相对路径>)
status: draft
type: requirement
nature: normative
---
```

- `locale`: `en | zh-CN`
- `status`: `draft | pending-approval | approved | closed`
- `type`: `whitepaper | roadmap | goal | requirement | design | task | task-card |
  execution-log | research | decision | retrospective | handoff`
- `nature`: `normative | descriptive`

链根写 `upstream: none`；下游尚不存在时写 `downstream: none`，创建下游的同一检查批次中替换为真实
相对链接。规范性内容拥有语义；描述性内容只记录观察，不产生范围或批准。

## 2. 状态与版本锚

规范性文档状态：

```text
draft → pending-approval → approved → closed
```

Task 工作状态：

```text
not-started → prepared → active | blocked → closed
```

`prepared` 表示 Card 和 Log 已存在。`blocked` 只是 Task 的宏观信号，原因由 Log 保存。`closed` 表示
已接受实现和所需证据已进入共享基线。只有可执行行为、环境或包输入需要独立证明时才要求 Verifier。

批准和验收绑定不可变 commit、内容 hash 或等价版本锚；编辑文件不会移动既有决定。WhitePaper 和
ROADMAP 由负责人批准；Goal、Requirement、Design、Task 经独立 Critic 后由主编排者接受；Milestone
关账由负责人验收。

## 3. 受控变更

只修改拥有该语义的权威：

| 权威 | 路由 |
|---|---|
| WhitePaper | `brainstorm` 修订 |
| ROADMAP | `roadmap` 维护 |
| Goal | `write-goal` 修订 |
| Requirement 或 AC | `write-requirement` 修订 |
| Design | `write-design` 修订 |
| Task | `write-task` 修订 |

语义变更可能改变范围、义务、验收含义、设计意图或执行权威，必须在新版本锚上接受该权威对应的
评审或批准。机械变更保持语义不变，例如格式、链接、状态镜像或生成元数据，只运行受影响的机检，
不自动触发语义重审。

只传导影响范围。把触发原因、旧锚、分类、准确变化、受影响 ID/文件/测试/证据、所需评审和新锚
写在语义权威或现有的关联决议记录中。不要预留空变更章节，也不要把同一记录复制到所有文档。

## 4. 稳定名称与 Task 接口

- 项目：`WhitePaper.md`、`ROADMAP.md`
- Milestone：`Goal.md`、`Requirement.md`、`Design.md`、`Task.md`
- 单卡：`execution/<card_id>/Card.md`
- 运行记录：`execution/<card_id>/Log.md`
- Milestone：`M1`, `M2`, ...
- 需求：`R1`, `R2`, ...
- AC：`R1-AC1`, `R1-AC2`, ...
- Task：`M1-T1`, `M1-T2`, ...；单 Milestone 语料可用 `T1`

ID 被下游引用后不得重排；删除时保留 tombstone 或决议指针。

Task 解析表头固定为：

```markdown
| # | task | spec anchor | prerequisite | status | execution |
|---|---|---|---|---|---|
| **M1-T1** | <可独立判定结果> | R1-AC1 | none | not-started | none |
```

中文文档也使用相同表头。另设 `| AC | task |` 映射。Task 只拥有任务划分、规格锚、依赖 DAG、宏观
状态、execution 指针和编排/集成确实需要的少量 Milestone 级指针。不得放 TDD、命令、write set、
锁、blocker、候选锚、证据或推进历史。更新时替换当前值，不追加执行叙事。

## 5. Card 与 Log

负责人确认执行集后，`run-task` 在派 Coder 前为每个选中任务只创建两份文件：

- `Card.md` 是规范性文档。元信息使用 `type: task-card`，upstream 指向精确 Task 行，downstream 指向
  `Log.md`。最小稳定契约只有结果、Requirement 与 Design 锚、完成判据、TDD 契约，以及
  `execution_log: [Log.md](Log.md)`。
- `Log.md` 是描述性文档。元信息使用 `type: execution-log`，upstream 指向 Card。正文保存可替换的
  当前快照和追加事件；快照包含 `latest_event: [<event_id>](#<event_id>)`，每个事件有稳定 ID、结果，
  以及重放或理解裁定所需的证据。

只有委派 writer 的边界确实需要时，才加入范围排除或 allowed path/write set；只有真实共享资源冲突
存在时，才加入 conflict domain 或 runtime lock。Task 是依赖权威，Card 链接 Task 行，不复制依赖 DAG。

先创建 Card，再创建 Log，最后在同一检查候选中发布 Task execution 链接。历史错误通过后续事件
纠正，不改写旧事件。没有独立需要时，不创建项目总 execution log，也不创建单独的 Verification、
State、逐角色 brief 或 Handoff 文件。

Card 只能细化实现机制，不能增加既有权威没有的范围、依赖、验收语义或设计决定。Log 不拥有规范语义。

## 6. 内容契约，不是版式模板

除上述解析字段外，GMGN 不规定章节名、顺序或正文形态。当前阶段 Skill 决定产物要回答什么、如何
自检。主编排者的完整上下文使直接写作最清楚时，由主编排者自己写；只有边界清楚，且隔离、专业性
或并行价值真实存在时，才委派全新 Author。独立 Critic 必须与 writer 分离。
