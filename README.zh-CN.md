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

GMGN 是同时适配 **Codex（CLI / Desktop）** 与 **Claude Code** 的 agent 研发工作流。它把一个想法沿着九件可组合 skill 推进到里程碑关账，用硬门禁阻止跳步，用独立评审减少同源盲区，用可重放命令把“完成”绑定到真实证据。

```text
想法
 └─ brainstorm → 白皮书 → roadmap
                         └─ write-goal
                            → write-requirement
                            → write-design
                            → write-task
                            → run-task
                            → close-milestone
                            → roadmap（下一里程碑）
```

`gmgn` 是总线：当你不知道当前该走哪一步时，它根据仓库状态路由到正确工序。

## 多语言模型

GMGN 只有一套 workflow，不维护中英两个插件。skill 根据项目现有文档和用户请求选择 `en` 或
`zh-CN`；标题与正文随语言变化，文件名、ID、命令、frontmatter 键与枚举、任务表头保持英文
机器 token。公共仓库文档使用英文主文件和 `.zh-CN.md` 镜像；项目规格链通常只选一个活动语言，
确需双语时分 locale 目录分别检查，避免相同 ID 重复定义。

统一机器契约见[中文写作契约](skills/gmgn/references/zh-CN/writing-contract.md)和
[English writing contract](skills/gmgn/references/en/writing-contract.md)。GMGN 不提供文档章节模板；
每个阶段 Skill 规定必备内容和自检项，Author 自行组织章节。

## 支持范围

| 能力 | Codex | Claude Code |
|---|---|---|
| 九件共享 skill | 支持 | 支持 |
| 自动触发与显式调用 | 自然语言或 `$gmgn` | 自然语言或 `/gmgn:gmgn` |
| 代码审查 | `/review`；CLI 用 `codex review --uncommitted/--commit/--base` | 独立只读 reviewer；`/code-review` 仅用于已授权评论的 GitHub PR |
| 运行验证 | 项目测试、启动与 E2E 命令 | 项目命令；可用 `/verify` |
| 平台清单 | `.codex-plugin/plugin.json` | `.claude-plugin/plugin.json` |

原生审查不替代真实运行。GMGN 始终要求项目测试和改动路径的可重放证据；Codex 自定义 review prompt 与范围 flags 互斥，审查后还要用 `git status --short` 检查可能产生的缓存等副产物。同一节点内，修改回到原 Author / Coder，blocker 定向复核回到原 Critic / Reviewer；平台无法恢复身份时显式替换，审查角色变更后重做完整审查。

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
| “把白皮书拆成版本和里程碑” | `roadmap` | ROADMAP |
| “启动 M1，明确范围” | `write-goal` | Goal.md |
| “写 PRD 和验收标准” | `write-requirement` | Requirement.md |
| “出技术设计和系统方案” | `write-design` | Design.md |
| “拆实施计划和任务卡” | `write-task` | Task.md |
| “实现这张卡 / 修这个 bug” | `run-task` | 代码、测试、审查证据 |
| “里程碑完成了，准备上线关账” | `close-milestone` | 回归、E2E、关账记录 |
| “下一步做什么？” | `gmgn` | 状态判断与工序路由 |

缺陷修复和琐碎单步改动可以走受控旁路，不强迫补齐整条规格链；白皮书、ROADMAP、立项与关账等停点仍需对应授权。

## 仓库结构

```text
skills/                     九件跨平台共享 skill
  */agents/openai.yaml      Codex 展示与默认提示元数据
  gmgn/references/{en,zh-CN}/ 中英文镜像机器/派发契约和核对单
agents/                     Claude Code 插件 subagent 角色
.docstar/conventions/       与 DocStar gmgn-v1 一致的约定集
.codex-plugin/plugin.json   Codex 插件清单
.claude-plugin/             Claude Code 插件与市场清单
.codex/agents/              本仓可选的 Codex 项目级角色配置
.agents/plugins/            Codex marketplace 清单
tests/                      结构、触发、双平台与发布包校验
scripts/package_release.py  可复现发布包与 SHA-256 生成器
GMGN.md                     工作流原理与条款权威
```

共享规则只写在 `skills/` 与 [GMGN.md](GMGN.md)；平台目录只承载发现、安装和原生能力适配，避免两套工作流漂移。

## 开发与发布

```bash
./tests/validate.sh
python3 -m unittest discover -s tests
python3 scripts/package_release.py
```

打包器默认拒绝脏工作树，从 Codex manifest 读取版本，只收录运行所需白名单，并生成确定性 ZIP 与 SHA-256。开发中验证可显式使用 `--allow-dirty`。

## 可选增强

[DocStar](https://github.com/tonywo2049/DocStar) 可机检文档链的断链、单向边和任务闭包。GMGN 不依赖 DocStar 才能安装；项目未安装时，用文件检查和项目现成命令完成同等门禁。

## License

MIT
