---
locale: zh-CN
purpose: 定义 GMGN 中英文文档共享的机器字段、状态、文件名、编号和解析接口，但不规定文档版式。
upstream: [GMGN 方法论](../../../../GMGN.zh-CN.md)
downstream: [GMGN 路由](../../SKILL.md)
status: approved
type: design
nature: normative
---

# GMGN 文档写作契约

English: [../en/writing-contract.md](../en/writing-contract.md)

## 1. 一套流程，两种人类语言

项目根据现有文档和用户请求选择 `en` 或 `zh-CN`。标题与正文使用所选语言；下列机器字段、
枚举、文件名、ID、命令和任务表头不翻译。不要维护两套 skill。

同一规格链通常只选一个活动语言。确需中英镜像时，放入两个独立 locale 目录，分别运行检查；
不要把含相同 ID 的两棵树同时作为一个 DocStar 语料根，否则会形成重复定义。

## 2. 元信息块

每份正式文档出生即写：

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

固定键：`locale | purpose | upstream | downstream | status | type | nature`。

- `locale`: `en | zh-CN`
- `status`: `draft | pending-approval | approved | closed`
- `type`: `whitepaper | roadmap | goal | requirement | design | task | research | decision | retrospective | handoff`
- `nature`: `normative | descriptive`

`normative` 表示下游依赖其条款，变更必须传导；`descriptive` 表示记录事实或过程，不作为门禁依据。
仓库自己的说明文档可使用扩展 `type`，但项目规格链只能使用上表固定值。

链根写 `upstream: none`；尚不存在的下游写 `downstream: none`，建成后同批替换成真实链接。
不要把普通文字伪装成链接。

## 3. 两套状态不能混用

文档审批状态使用：

```text
draft → pending-approval → approved → closed
```

Milestone、切片和任务卡的工作状态使用：

```text
not-started → initiated → in-progress → closed
```

对任务卡而言，`initiated` 表示执行 lane 已被认领，`in-progress` 覆盖编码直到集成。隔离分支通过
review 或 verification，只能让运行时候选进入 `accepted`，不能把任务标成 `closed`。只有候选合入
记录的 `shared_baseline_anchor`、完成集成后验证，并由共享基线 Integrator 同批刷新 `Task.md`、
追踪矩阵与证据后，任务卡才是 `closed`。
卡片 Coder 只在 assigned detached-HEAD 或唯一分支 worktree stage/commit 本卡 `write_set`，回传
可解析的本地 commit SHA 作为不可变 `candidate_anchor`；允许本地 commit，禁止远端写入。

集成先从干净的当前共享基线生成临时组合 `candidate_anchor`。验证失败或 merge/cherry-pick 冲突时
丢弃候选或中止操作，保持前一个 `shared_baseline_anchor` clean 且不变。只有验证通过的组合候选加
机械台账刷新才能原子推进共享锚；未验证组合不是基线。

白皮书与 ROADMAP 由负责人批准；Goal / Requirement / Design / Task 经独立 critic 后由主编排者审核；
Milestone 关账由负责人验收。批准必须绑定 commit、内容 hash 或等价版本锚。

### 3.1 已批准文档的受控变更

流程节点不是只能向前移动。下游发现上游缺陷或前提变化时，回到该语义的唯一权威文档：

| 语义归属 | 修订路由 |
|---|---|
| WhitePaper | `brainstorm` 修订态 |
| ROADMAP | `roadmap` 维护态 |
| Goal | `write-goal` 修订态 |
| Requirement 或 R-AC | `write-requirement` 修订态 |
| Design | `write-design` 修订态 |
| Task | `write-task` 修订态 |

**语义变更**是可能改变决策或正常读者对范围、义务、验收语义、设计意图、执行权威的理解。
新版按该权威层级重新评审或批准，并绑定新版本锚。旧批准继续指向旧版本锚，不会随文件修改
自动转移到新版。

**机械变更**不改变语义，例如改名、移动、链接、格式、hash 或状态镜像刷新。不能只因文件内容
变化就要求重新批准；同批刷新所有受影响表征并运行机检。变更记录明确新旧版本语义等价且机检
通过后，新版本锚可以引用旧批准锚并保持文档批准状态；这不构成一次新批准。不能确定分类时，
按语义变更处理。

两类变更都只向影响范围传导：受影响的上下游链接、ID、映射、文档、任务、测试、证据和状态。
只重新评审、批准和验证受影响内容。返回权威节点不等于重走无关流程。

语义修订要在权威文档或其链接的决议记录中新增或更新变更记录。机械变更可以只保留一份批次级
等价记录，不要为了追加历史而逐个修改所有受影响文档。新建文档不要预留空记录：

| 项目 | 必填内容 |
|---|---|
| 触发原因 | 已批准基线为什么不足 |
| 旧版本锚 | 既有批准继续适用的版本 |
| 变更分类 | `semantic` 或 `mechanical`，并写理由 |
| 权威与增量 | 唯一权威位置和改变的确切语义 |
| 影响范围 | 受影响的 ID、文档、工作、测试、证据和状态 |
| 评审或批准 | 新版由谁评审或批准；无需重批时写明理由 |
| 新版本锚与检查 | 新版锚，以及传导和验证证据 |

## 4. 稳定名称与编号

- 项目级：`WhitePaper.md`、`ROADMAP.md`
- Milestone：`Goal.md`、`Requirement.md`、`Design.md`、`Task.md`
- Milestone：`M1`, `M2`, ...
- 需求：`R1`, `R2`, ...
- 验收标准：`R1-AC1`, `R1-AC2`, ...
- 任务：`M1-T1`, `M1-T2`, ...；单里程碑局部语料可用 `T1`

编号一旦被下游引用就不重排。删除时保留 tombstone 或决议指针。

任务表头固定为英文：

```markdown
| # | task | spec anchor | prerequisite | failing test | status |
|---|---|---|---|---|---|
| **M1-T1** | <任务> | R1-AC1 | none | `test_name` | not-started |
```

这是 GMGN 与 DocStar 的共同解析面；中文文档也不得翻译这些表头。

固定六列不承载全部执行契约。围绕同一稳定任务 ID 的卡片内容还要记录 `depends_on`、`write_set`、
`conflict_domains`、`runtime_locks` 和 semantic owner；这些内容不改变 DocStar 的表格 schema。
`workspace_mode: shared` 无法为每个 writer 独立锚定时，并行 worker 只返回 proposal/patch，由一个
已登记 writer 串行应用和锚定。

## 5. 内容契约，不提供版式模板

GMGN 不规定章节名、章节顺序或行文形态。当前阶段的 Skill 是“产物必须回答什么、writer 必须
自检什么”的唯一权威。WhitePaper、ROADMAP、Goal、Requirement、Design、Task 由主编排者选择
实际 writer：上下文使直接写作最清楚、最省交接时由主编排者自己写；边界清楚，且隔离、专业性或
并行收益足以覆盖交接成本时才委派 Author。`author_ref` 绑定实际 writer，独立 Critic 必须与它
分离。不得在项目或插件 reference 中重新制作可复制的章节骨架。

正文只固定编号和解析器要读取的表格接口。`Task.md` 必须保留第 4 节的固定任务表头；外围标题
与解释文字可由已登记 writer 自由组织。

## 6. 写作纪律

1. 先读上游、下游和定义位置，再写正文。
2. 一个事实只设一个权威；其他位置用真实相对链接和 ID 指向它。
3. 探索稿与已定结论分目录存放。
4. 变更时列出受影响的下游并同批刷新状态。
5. 人类语言不同不改变 AC、任务、链接或状态的语义。

## 7. DocStar 验证

```bash
python3 docstar.py check --preset gmgn-v1 --corpus <locale-root>
python3 docstar.py dump --preset gmgn-v1 --json --corpus <locale-root>
python3 docstar.py brief M1-T1 --preset gmgn-v1 --json --corpus <locale-root>
```

项目已复制 `.docstar/conventions/conventions.json` 时可省略 `--preset gmgn-v1`。英文和中文镜像的
`dump --json` 应在排除自然语言正文后呈现相同实体、边、状态与诊断。
