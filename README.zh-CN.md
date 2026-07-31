---
locale: zh-CN
purpose: 介绍 GMGN 的安装、快速使用、平台支持与开发入口。
status: approved
type: guide
nature: descriptive
---

# GMGN

**GM, GN.** 早安，晚安。

English: [README.md](README.md)

GMGN 是同时适配 **Codex（CLI / Desktop）** 与 **Claude Code** 的 agent 研发工作流。它把一个想法沿着十一件可组合 skill 推进到里程碑关账，再从已接受锚发布而不重复关账审查；硬门禁阻止跳步，独立评审减少同源盲区，可重放命令把“完成”绑定到真实证据。

```text
想法
 └─ brainstorm → WhitePaper
    → write-decision → Decision
    → roadmap → ROADMAP
       └─ write-goal
          → write-requirement
          → write-design
          → write-task
          → run-task
          → close-milestone
          → release（已授权分发时）
          → roadmap（下一里程碑）
```

`gmgn` 是总线：当你不知道当前该走哪一步时，它根据仓库状态路由到正确工序。

## 多语言模型

GMGN 只有一套 workflow，不维护中英两个插件。skill 根据项目现有文档和用户请求选择 `en` 或
`zh-CN`；标题与正文随语言变化，文件名、ID、命令、frontmatter 键与枚举、任务表头保持英文
机器 token。公共规范只维护英文单一权威，只有 README 保留中英文两份；项目规格链通常只选一个
活动语言，确需双语时分 locale 目录分别检查，避免相同 ID 重复定义。

统一写作规则见 [English writing rules](skills/gmgn/references/en/writing-rules.md)。GMGN 不维护
规范的翻译镜像，也不提供文档章节模板；每个阶段 Skill 规定必备内容和自检项，Author 可按项目
活动语言组织正文。

`Decision.md` 可以保存任意主题、任意 Milestone 范围内供下游消费的现行决议。下游文档链接适用
D-ID，不重复定义决议；`DecisionLog.md` 只记录已批准变更，不进入正常下游上下文。

ROADMAP 中每个 Milestone 都要映射 WhitePaper 和适用 D-ID，写明一个结果及其价值、必要产出物和一个结果级
成功信号，并分开表达 `now | next | later`、相对优先级和真实依赖。编排 Agent 提交一份完整推荐
候选，由负责人一次批准。ROADMAP 不拥有 E2E 路径。

每个阶段文档只增加一种信息：Decision 记录明确集中供下游使用的决议；ROADMAP 分配部分有序的
Milestone 及其结果；Goal 把当前 Milestone 细化为 Requirement 依据和定性 Close 标准；
Requirement 定义可观察要求和可判定 AC；Design 确定或链接实现所需的技术决定；Task 只索引可
独立完成的结果、依赖、状态和执行入口。阶段文档不写下游门禁、传导规则、下一阶段指令或推测性
占位。

Design 阶段始终产出根 `Design.md`。只有模块权威确有价值时才增加
`design/<module-id>.md`；存在独立开发边界时才要求 `design/Contract.md`，拆分契约与
`design/schemas/` 结构权威也按需创建，不生成空脚手架。所有链接文件构成同一锚点上的 Design
Bundle。只有两个互不沟通的 Coder 无需补充公共或跨单元决定，并能从同一权威得到兼容结果时，
Design 才可批准。
Design 阶段的 Contract 是已批准的工作基线，不是最终稿。编码证据可通过 `write-design` 受控修订；
Milestone 关账时再核对提供方、消费方、实现与证据，并记录关账时已审查的 Contract 状态。

## 支持范围

| 能力 | Codex | Claude Code |
|---|---|---|
| 十一件共享 skill | 支持 | 支持 |
| 自动触发与显式调用 | 自然语言或 `$gmgn` | 自然语言或 `/gmgn:gmgn` |
| 代码审查与确定性本地检查 | `/review`；CLI 用 `codex review --commit/--base`，并运行项目命令 | 独立 reviewer 并运行项目命令；`/code-review` 仅用于已授权评论的 GitHub PR |
| 风险触发的最终验证 | [由政策定义](skills/gmgn/references/en/assurance-policy.json) | [由政策定义](skills/gmgn/references/en/assurance-policy.json) |
| 平台清单 | `.codex-plugin/plugin.json` | `.claude-plugin/plugin.json` |

每个受委派角色都遵循
[派发契约](skills/gmgn/references/en/dispatch-and-handoff.md)。每个语义候选批次最多一轮 Critic，
每个实现候选恰好一轮 Reviewer。主 session 裁定已接受问题、检查修复差异并运行受影响机器检查，
不再派第二个 Critic 或 Reviewer。Verifier 仍由
[`gmgn-assurance-v2`](skills/gmgn/references/en/assurance-policy.json)按风险触发。审查范围由
[代码审查契约](skills/gmgn/references/en/code-review.md)定义。

`Task.md` 仍是 Milestone 索引。Milestone 启动后，`run-task` 为每个已接受 Task 创建稳定的
`Card.md` 执行与验证契约和可替换的 `Log.md`，无需另行确认执行集，Task ready 后直接调度。它还
负责隔离 writer lane、运行时工具、监测、审查、集成与关闭。只有已审内容集成后，项目声明的全部
必需检查都在准确的共享基线候选上通过，Task 才能关闭。
完整规则只在 [`run-task`](skills/run-task/SKILL.md) 中维护。

Milestone 关闭后发现未完成工作时，直接回到 `initiated`，清空当前 `accepted_result`，只重开受
影响工作。只有影响分析确认下游受影响时才调整下游状态。负责人复核只是关账审查节点，不产生不可
撤销的决定。

R-D-T 的方案最简性由 GMGN 自己检查；代码最简性使用外部
[Ponytail](https://github.com/DietrichGebert/ponytail) 插件，run-task 代码工作必须安装它。
Ponytail、CodeGraph、DocStar 的具体运行规则只在 `run-task` 中维护。

## 安装

### Codex

```bash
codex plugin marketplace add DietrichGebert/ponytail
codex plugin add ponytail@ponytail
codex plugin marketplace add tonywo2049/GMGN
codex plugin add gmgn@GMGN
```

新建一个 Codex 任务使插件生效。验证安装：

```bash
codex plugin list
```

然后输入：

```text
$gmgn 判断这个项目下一步该做什么
```

### Claude Code

```bash
claude plugin marketplace add DietrichGebert/ponytail
claude plugin install ponytail@ponytail --scope user
claude plugin marketplace add tonywo2049/GMGN
claude plugin install gmgn@GMGN --scope user
```

新建会话后输入 `/gmgn:gmgn`，或直接描述要做的事。

### 本地开发版

把上面 marketplace 的来源换成本仓绝对路径：

```bash
codex plugin marketplace add /absolute/path/to/GMGN
claude plugin marketplace add /absolute/path/to/GMGN
```

再执行对应平台的安装命令。不要同时安装同一 skill 的手动副本，以免出现重复触发。

## 升级

### 通过 GitHub marketplace 安装

Codex 先刷新 marketplace，再检查已安装版本：

```bash
codex plugin marketplace upgrade GMGN
codex plugin list
```

如果仍显示旧版本，从刷新后的 marketplace 重新安装插件：

```bash
codex plugin remove gmgn@GMGN
codex plugin add gmgn@GMGN
codex plugin list
```

Claude Code 先刷新 marketplace，再更新插件：

```bash
claude plugin marketplace update GMGN
claude plugin update gmgn@GMGN --scope user
claude plugin list --json
```

把命令中的 `user` 替换为安装时使用的 `user`、`project` 或 `local` scope。`managed`
scope 由管理员控制，普通用户不能自行更新。

### 本地开发 marketplace

先更新源仓库，再明确刷新已安装副本：

```bash
git -C /absolute/path/to/GMGN pull --ff-only
codex plugin remove gmgn@GMGN
codex plugin add gmgn@GMGN
codex plugin list
claude plugin marketplace update GMGN
claude plugin update gmgn@GMGN --scope user
claude plugin list --json
```

Claude Code 仍须把 `user` 换成原安装 scope；`managed` scope 仍由管理员处理。本地路径
marketplace 不要执行 `codex plugin marketplace upgrade GMGN`；删除并重新添加插件才能刷新
已安装副本。

### Release ZIP 或手工副本

上述 marketplace 命令不会更新从 Release ZIP 解压或手工复制的目录。应使用新版本完整包
整体替换旧目录，或迁移到上面的 marketplace 安装方式。不要叠加覆盖文件、同时保留手工副本
和 marketplace 副本，也不要修改平台缓存目录。

任何方式升级后都要新建 Codex 任务或 Claude Code 会话；Claude Code 的活动会话可在命令
受支持时执行 `/reload-plugins`。

## 卸载

Codex：

```bash
codex plugin remove gmgn@GMGN
codex plugin marketplace remove GMGN
```

Claude Code：

```bash
claude plugin uninstall gmgn@GMGN --scope user
claude plugin marketplace remove GMGN --scope user
```

## 使用

安装后直接说事；描述越接近当前状态，路由越准确。

| 你的说法 | 接管的 skill | 主要产物 |
|---|---|---|
| “我有个想法，先调研一下可不可行” | `brainstorm` | WhitePaper |
| “记录这项决议供下游使用” | `write-decision` | 当前 Decision 权威和描述性 DecisionLog |
| “按照白皮书和项目决议拆版本与里程碑” | `roadmap` | ROADMAP（结果型里程碑、成功信号、时域、优先级和真实依赖） |
| “启动 M1，明确范围” | `write-goal` | Goal.md（Requirement 依据和定性 Close 标准） |
| “写 PRD 和验收标准” | `write-requirement` | 可观察需求与可判定 AC |
| “出技术设计和系统方案” | `write-design` | 根 Design.md 中的必要技术决定及按需权威 |
| “拆实施计划和任务” | `write-task` | Task.md 执行索引 |
| “实现这些 ready 卡 / 修这个 bug” | `run-task` | 已集成代码、测试、审查和所需验证证据 |
| “里程碑完成了，准备上线关账” | `close-milestone` | 适用的回归/E2E 证据、已审查 Contract 状态、关账记录 |
| “发布已接受版本 / 重试这次发布” | `release` | 复用验收证据、确定性发布物、tag 与 Release |
| “下一步做什么？” | `gmgn` | 状态判断与工序路由 |

缺陷修复和琐碎单步改动可以走受控旁路，不强迫补齐整条规格链；WhitePaper、Decision、ROADMAP、
Milestone/Goal 合并批准、范围扩张与关账仍遵循各自门禁。

## 可选 telemetry

### 安装与配置

在解压后的 GMGN 发布包或仓库根目录运行：

```bash
python3 telemetry/install.py --dry-run
python3 telemetry/install.py --print-codex-config
python3 telemetry/install.py
python3 telemetry/report.py <session-id...> [--json]
```

`--dry-run` 预览安装内容，`--print-codex-config` 打印应合并到用户级
`~/.codex/config.toml` 的精确配置；项目级 `otel` 配置会被 Codex 忽略。本地 Collector
保持常驻，通过 `/v1/logs` 接收 Codex 原生 OTLP/HTTP JSON 日志。落盘前只把已知 Codex
事件转换为严格的元数据白名单，不保存原始 OTLP body。记录可提供 actual 的 API 尝试、
原生 tool-result 耗时，以及 Codex 实际发出的任务 token 计数；trace 和 metrics 明确关闭。
安装后在 Codex `/hooks` 中检查并信任这些选定的用户级 hooks。等待 hook 只把输出归一为隐私安全的
`update | timeout | interrupted | error | unknown`，不保存 agent 消息。

使用默认本机监听地址时，打开 `http://127.0.0.1:4318/` 即可进入只读仪表盘。页面列出已观测
任务，并展示任务时长、实际任务 Token、工具与 Skill、GMGN 编排、DocStar 活动、数据来源
覆盖和数据质量。页面只使用发布包内的静态资源，不访问外网，也不返回 prompt、命令、工具
输出或原始 session 记录。

### 隐私与报告

Codex 使用 `log_user_prompt=false`。Collector 丢弃 prompt、命令、tool 输出、错误正文、
主机与用户身份、凭据和未知字段。用户级 hooks 只在已配置的 session/subagent 生命周期事件
和匹配的 Bash/Agent/wait 事件上运行，记录时间、不可读的 session/turn/tool ID、模型、项目路径
哈希、输入输出字节数、成功/退出状态、分类、等待结果、fork policy 与结构化 GMGN 关联 ID。模型不手工
写 telemetry 日志，也不把日志放进 prompt、`Task.md` 或 `Handoff`。

只有用户要求复盘时才运行报告命令。报告优先使用 Collector 与 hook 记录，再从 session JSONL
补缺，并明确标注 `unstable fallback`；每个指标都报告来源与 coverage。actual token 缺失时显示
`unknown`，不能写成 0。报告给出等待结果、状态变化/超时数、最大连续超时、等待风暴数，以及等待
结果触发模型重激活时关联到的 actual 累计 token 差值。等待调用按 `tool_use_id` 逐次合并：结构化
hook 结果优先，session JSONL 只补未覆盖调用，同一次等待不重复计数；没有可靠失败状态的旧版
非结构化拒绝输出保持 `unknown`，错误分类不依赖参数/错误消息文案。当前 session token 事件没有 tool call ID，
所以该关联明确标为 `session_sequence_delta`，同时报告 matched/eligible coverage，不冒充原生精确
关联；per-tool/skill I/O token 仍是 estimates。安装后也可运行
`~/.codex/gmgn-telemetry/bin/report.py`。`--json` 只改变报告格式。

## 仓库结构

```text
skills/                     十一件跨平台共享 skill
  */agents/openai.yaml      Codex 展示与默认提示元数据
  gmgn/references/en/       英文单一权威的契约与核对单
agents/                     Claude Code 插件 subagent 角色
.docstar/conventions/       GMGN 项目本地 DocStar 约定集
.codex-plugin/plugin.json   Codex 插件清单
.claude-plugin/             Claude Code 插件与市场清单
.codex/agents/              本仓可选的 Codex 项目级角色配置
.agents/plugins/            Codex marketplace 清单
tests/                      结构、触发、双平台与发布包校验
scripts/package_release.py  可复现发布包与 SHA-256 生成器
telemetry/                  发布包内置的 Collector、hooks、安装器、报告器与本地仪表盘
GMGN.md                     工作流原理与条款权威
```

共享规则只写在 `skills/` 与 [GMGN.md](GMGN.md)；平台目录只承载发现、安装和原生能力适配，避免两套工作流漂移。

## 开发与发布

```bash
./tests/validate.sh
python3 -m unittest discover -s tests
python3 scripts/package_release.py
python3 scripts/package_release.py --set-version 0.2.19
```

打包器默认拒绝脏工作树，从 Codex manifest 读取版本，只收录运行所需白名单，并生成确定性 ZIP 与
SHA-256。该校验和只证明制品完整性，不能作为流程锚点。`--set-version` 校验 SemVer 并同步四处现有
版本声明；开发中验证可显式使用 `--allow-dirty`。

## 可选增强

[DocStar](https://github.com/tonywo2049/DocStar) 可机检文档链的断链、单向边和任务闭包；
本仓 `.docstar/conventions/conventions.json` 是当前 GMGN 的适配约定，包含 D-ID 索引。
Decision 项目应把它放入文档语料根；只有已安装 `gmgn-v1` preset 含等价 Decision 规则时才直接
使用 preset。CodeGraph 可辅助源码定位。GMGN 不依赖它们才能安装。Task 执行阶段如何使用它们，由
[`run-task`](skills/run-task/SKILL.md)定义。每次 DocStar 调用仍实时全量重建，不使用缓存。
Telemetry hooks 与报告器只在 DocStar 外部统计调用次数、耗时、命令类型和后续 grep/read；
`grep_avoided` 是描述性统计，不表示 DocStar 导致某次 grep 被避免。

## License

MIT
