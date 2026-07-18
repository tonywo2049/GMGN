---
locale: zh-CN
purpose: 定义 GMGN 中英文文档共享的机器字段、状态、文件名、编号、表头和写作模板。
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
仓库自己的说明/模板文档可使用扩展 `type`，但项目规格链只能使用上表固定值。

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

白皮书与 ROADMAP 由负责人批准；Goal / Requirement / Design / Task 经独立 critic 后由主编排者审核；
Milestone 关账由负责人验收。批准必须绑定 commit、内容 hash 或等价版本锚。

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

## 5. G-R-D-T 模板

### Goal.md

```markdown
---
locale: zh-CN
purpose: 定义 M1 的目标、边界、切片与完成景象。
upstream: [ROADMAP](../../ROADMAP.md)
downstream: [Requirement](Requirement.md)
status: draft
type: goal
nature: normative
---

# M1 Goal

## 目标
## 边界
## 工作切片
## 非目标
## 定性完成景象
## 已知缺口
```

### Requirement.md

```markdown
---
locale: zh-CN
purpose: 定义 M1 唯一需求权威与可判定验收标准。
upstream: [Goal](Goal.md)
downstream: [Design](Design.md)
status: draft
type: requirement
nature: normative
---

# M1 Requirement

## 功能需求
- **R1** — <必须满足什么，不写实现方案>
  - **R1-AC1** — GIVEN <前置> WHEN <动作> THEN <可观察结果>

## 非功能需求
## 参数与约束
## 非目标
## 追踪表
```

### Design.md

```markdown
---
locale: zh-CN
purpose: 把 M1 需求映射到实现结构、接口、数据与验证路径。
upstream: [Requirement](Requirement.md)
downstream: [Task](Task.md)
status: draft
type: design
nature: normative
---

# M1 Design

## 约束与现状
## 系统结构
## 接口与数据
## 失败路径与回滚
## 需求映射
| requirement | design location | verification |
|---|---|---|
| R1-AC1 | §2.1 | <测试或 E2E 路径> |
## 被拒方案
```

### Task.md

```markdown
---
locale: zh-CN
purpose: 定义 M1 的任务卡、依赖、测试与滚动状态。
upstream: [Design](Design.md)
downstream: none
status: draft
type: task
nature: normative
---

# M1 Task

## 任务
| # | task | spec anchor | prerequisite | failing test | status |
|---|---|---|---|---|---|
| **M1-T1** | <最小可验证工作单元> | R1-AC1 | none | `test_r1_ac1` | not-started |

## 追踪矩阵
| acceptance criterion | task | test | evidence |
|---|---|---|---|
| R1-AC1 | M1-T1 | `test_r1_ac1` | <命令与结果指针> |

## 滚动记录
```

## 6. 其他类型的最低内容

| type | 必须回答 |
|---|---|
| `whitepaper` | 问题、目标、非目标、用户/场景、损害排序、顶级不变量、验证方向 |
| `roadmap` | 定性 Milestone 目标、定性完成景象、依赖、状态、TODO 待分配 |
| `research` | 问题、证据、选项、反例、推断边界、建议；通常 `descriptive` |
| `decision` | 编号、触发、裁决、理由、附带条件、传导清单、版本锚 |
| `retrospective` | 事件、根因、哪些信号漏掉、推广后的测试/规则/核对问题 |
| `handoff` | 一句话状态、基线、已完成、剩余、风险、下一命令、权威指针；`descriptive` |

## 7. 写作纪律

1. 先读上游、下游和定义位置，再写正文。
2. 一个事实只设一个权威；其他位置用真实相对链接和 ID 指向它。
3. 探索稿与已定结论分目录存放。
4. 变更时列出受影响的下游并同批刷新状态。
5. 人类语言不同不改变 AC、任务、链接或状态的语义。

## 8. DocStar 验证

```bash
python3 docstar.py check --preset gmgn-v1 --corpus <locale-root>
python3 docstar.py dump --preset gmgn-v1 --json --corpus <locale-root>
python3 docstar.py brief M1-T1 --preset gmgn-v1 --json --corpus <locale-root>
```

项目已复制 `.docstar/conventions/conventions.json` 时可省略 `--preset gmgn-v1`。英文和中文镜像的
`dump --json` 应在排除自然语言正文后呈现相同实体、边、状态与诊断。
