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

GMGN 是同时适配 **Codex（CLI / Desktop）** 与 **Claude Code** 的 agent 研发工作流。它把一个想法沿着十件可组合 skill 推进到里程碑关账，再从已接受锚发布而不重复关账审查；硬门禁阻止跳步，独立评审减少同源盲区，可重放命令把“完成”绑定到真实证据。

```text
想法
 └─ brainstorm → 白皮书 → roadmap
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

统一机器契约见 [English writing contract](skills/gmgn/references/en/writing-contract.md)。GMGN 不维护
规范的翻译镜像，也不提供文档章节模板；每个阶段 Skill 规定必备内容和自检项，Author 可按项目
活动语言组织正文。

## 支持范围

| 能力 | Codex | Claude Code |
|---|---|---|
| 十件共享 skill | 支持 | 支持 |
| 自动触发与显式调用 | 自然语言或 `$gmgn` | 自然语言或 `/gmgn:gmgn` |
| 代码审查与确定性本地检查 | `/review`；CLI 用 `codex review --uncommitted/--commit/--base`，并运行项目命令 | 独立 reviewer 并运行项目命令；`/code-review` 仅用于已授权评论的 GitHub PR |
| 风险触发的最终验证 | 安装、启动、E2E、外部环境或无法完全机检的制品 | 项目命令；可用 `/verify` |
| 平台清单 | `.codex-plugin/plugin.json` | `.claude-plugin/plugin.json` |

Reviewer 在同一轮内完成代码判断与既定的确定性本地检查。每个受委派角色在创建前取得完整 brief，
只回传一次后结束；后续写作、编码或验证使用全新 agent，不继承父会话或旧 agent 历史。每个语义
变更批次或任务执行最多只有一轮 Critic/Reviewer；已采纳 finding 由主编排者核对修复并重跑受影响
的机器检查，不再做第二轮独立检查。单独的 Verifier 是例外：按
[`gmgn-assurance-v1` 策略](skills/gmgn/references/en/assurance-policy.json)分类为
`not-required` 或 `required:<trigger>`，只有后者才派发。
Critic 和 Reviewer 不追求 finding 数量；没有 finding 是有效结果。只报告没有被已接受有效兜底
控制、会造成具体实质影响的问题，并只要求最小充分修复。Verifier 只运行判定 recorded trigger
所需的检查，判定成立即停止。

`run-task` 按依赖 ready set 持续补满可用槽位。主 session 等待或承担 Coder 前，必须扫描已确认
执行集中的全部任务，不能只看当前卡片或 lane。`Task.md` 只保留任务划分、AC 映射、依赖、宏观状态
和 execution 指针；每个选中任务用 `execution/<card_id>/Card.md` 保存稳定执行/TDD 契约，用
`Log.md` 保存当前状态、关键决策和最终证据；不记录普通派发、等待、未变化状态和已被最终证据覆盖
的成功中间检查。并发 writer 使用隔离工作区，单 writer 可直接使用当前工作区；只有真实交接或
实质状态变化才检查 workspace、HEAD 和候选身份。单 writer 冻结 diff/内容哈希，隔离交接传递
完整候选；集成前只确认集成内容仍是已审内容。

发现问题不会扩大 active Card。新问题只有在不修会阻止 Card 结果或既定必需检查、没有已接受的
有效兜底、且最小充分修复仍在现有权威内时才属于当前任务；否则忽略低价值问题、将确有价值的事项
单独交给主 Session，或返回上游。Card 契约满足后立即关闭任务。

Reviewer 在唯一审查轮内运行既定的确定性本地检查；已采纳
finding 修复后，主编排者核对精确修复差异并重跑受影响的机器检查，不再进行独立复核。只有记录了
上述风险触发理由，才对最终候选派一个全新 Verifier；干净机械集成也不重复同一测试。
Agent 等待采用事件驱动：先做完有用本地工作，只发起一次平台允许的最长安全等待，把超时只当存活
检查点，禁止把 status/list/wait 串成轮询循环。只有调度决策、等待超时后状态仍不明确，或生命周期
事件互相矛盾时才调用一次 `list_agents`；实质状态变化前不得再次查询，也不配置定时查询周期。
Agent 进度只在自己的 thread 内显示，只向主编排者推送实质生命周期事件。长任务中，主 session
禁止发送无状态变化的心跳；只在产生实质进展、阻塞、决策请求或最终结果时更新。

已评审的 `Task.md` 行选择工作，物化后的 `Card.md` 是静态执行/TDD 权威。run-task 角色只接收精确
权威指针、Log 当前快照与 lane 事实，不继承父会话，也不复制逐 agent handoff。

## 安装

### Codex

```bash
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
| “把白皮书拆成版本和里程碑” | `roadmap` | ROADMAP（含 Milestone 验收图景） |
| “启动 M1，明确范围” | `write-goal` | Goal.md |
| “写 PRD 和验收标准” | `write-requirement` | Requirement.md |
| “出技术设计和系统方案” | `write-design` | Design.md |
| “拆实施计划和任务卡” | `write-task` | Task.md |
| “实现这些 ready 卡 / 修这个 bug” | `run-task` | 已集成代码、测试、审查和所需验证证据 |
| “里程碑完成了，准备上线关账” | `close-milestone` | 回归、E2E、关账记录 |
| “发布已接受版本 / 重试这次发布” | `release` | 复用验收证据、确定性发布物、tag 与 Release |
| “下一步做什么？” | `gmgn` | 状态判断与工序路由 |

缺陷修复和琐碎单步改动可以走受控旁路，不强迫补齐整条规格链；白皮书、ROADMAP、立项与关账等停点仍需对应授权。

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
skills/                     十件跨平台共享 skill
  */agents/openai.yaml      Codex 展示与默认提示元数据
  gmgn/references/en/       英文单一权威的契约与核对单
agents/                     Claude Code 插件 subagent 角色
.docstar/conventions/       与 DocStar gmgn-v1 一致的约定集
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
SHA-256。`--set-version` 校验 SemVer 并同步四处现有版本声明；开发中验证可显式使用
`--allow-dirty`。

## 可选增强

[DocStar](https://github.com/tonywo2049/DocStar) 可机检文档链的断链、单向边和任务闭包。GMGN 不依赖 DocStar 才能安装；项目未安装时，用文件检查和项目现成命令完成同等门禁。DocStar 0.2.3 及以上版本提供 commit-bound brief，run-task 把它作为起始证据包，但 agent 在证据不足时仍可沿指针或直接定向读取原文。CodeGraph 索引已获授权且 CLI 可用时，GMGN 为每个隔离工作区初始化独立索引，源码定位和代码关系优先使用 CodeGraph，并把其返回源码视为已读取；索引缺失、过期、不支持、查询后文件已变或结果不足时仍可定向读取文件。结论仍落到源码、diff、测试与真实运行。每次 DocStar 调用仍实时全量重建，不使用缓存。Telemetry hooks 与报告器只在 DocStar 外部统计调用次数、耗时、命令类型和后续 grep/read；`grep_avoided` 是描述性统计，不表示 DocStar 导致某次 grep 被避免。

## License

MIT
