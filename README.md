# GMGN

**GM, GN.** 早安,晚安——用上这套 workflow 之后,每天和 agent 一起工作都轻松愉快,让人忍不住对它说一声早安和晚安。

GMGN 是一套装进 Claude Code 的 **agent 研发工作流 skill 集**:从一个想法开始,走完「需求澄清 → 需求实现」全程,每一步有硬门禁、有独立评审、有可机检的文档链——你不需要记流程,描述你想做的事,对应的 skill 会自己接管。

```
想法
 │  brainstorm      多轮探索 → 白皮书(WhitePaper) → critic → 负责人批准
 ▼
 │  roadmap         白皮书拆成 Milestone(目标+定性验收标准) → critic → 批准
 ▼                                            ┌──────────────┐
 │  write-goal      立项,拆解 Milestone 目标   │   需求澄清    │
 │  write-requirement  需求池+编号验收标准     │      ↓       │
 │  write-design    需求→结构映射              │   需求实现    │
 │  write-task      任务卡(三锚)+台账          └──────────────┘
 │  run-task        逐卡编码 + 收卡审查(可并行)
 ▼
 │  close-milestone 全量回归+E2E+组合审 → 关账 → 回填 Roadmap → 下一个 Milestone
 └──────────────────────────────────────────────→ 循环
```

## 安装

**方式一:插件市场(推荐)**

在 Claude Code 中执行:

```
/plugin marketplace add tonywo2049/GMGN
/plugin install gmgn@GMGN
```

**方式二:手动安装**

```bash
git clone https://github.com/tonywo2049/GMGN.git
# 全局可用:拷贝 skills/ 下九个目录到 ~/.claude/skills/
# 或仅当前项目:拷贝到 <项目>/.claude/skills/
```

安装后重启会话生效。验证:新会话里说「我有个想法,想做一个 X」,`brainstorm` 应自动接管;或输入 `/gmgn` 查看当前该走哪一步。

## 卸载

- 插件方式:`/plugin uninstall gmgn@GMGN`(如需连市场一起移除:`/plugin marketplace remove GMGN`)
- 手动方式:删除拷入 `~/.claude/skills/` 或项目 `.claude/skills/` 的对应目录

## 使用

装好后不需要记任何命令——直接说事:

| 你说 | 接管的 skill |
|---|---|
| 「我想做一个 X,帮我想想」 | `brainstorm`(产出白皮书) |
| 「把项目拆成里程碑/排个路线图」 | `roadmap` |
| 「启动 M1/立项」 | `write-goal` |
| 「写需求/定验收标准」 | `write-requirement` |
| 「出设计/技术方案」 | `write-design` |
| 「拆任务卡」 | `write-task` |
| 「开做这张卡」 | `run-task`(派 coding agent+收卡审查) |
| 「这个里程碑收尾/关账」 | `close-milestone` |
| 「下一步该做什么?」 | `gmgn`(总线,按状态路由) |

三条不变的底线:上游文档没批就进不了下游(硬门禁);实质产出必过独立 critic;关账前必有真实运行证据(全量回归+E2E),纸面绿灯不算数。

## 组成

- `skills/` — 九件工序 skill(gmgn 总线+八件链上工序),每件自带前置检查、写作要求、出口接力
- `skills/gmgn/references/` — 共享件:文档写作契约、critic/coder/code-review 三份 agent 任务书、三张核对单、信任面登记表、派发与回传骨架等
- [METHODOLOGY.md](METHODOLOGY.md) — 方法论八章全文(原理层:为什么这么设计,条款权威)
- `docs/` — 本仓自身的调研与设计结论(吃自己狗粮的痕迹)

## 可选增强

- [DocStar](https://github.com/tonywo2049/DocStar) — 文档链机检(断链/单向边/任务闭包);GMGN 的文档写法与它兼容,装上后各 skill 的 `verify`/`check --gate`/`brief` 钩子即可用
- Claude Code 内置 `/code-review` 与 `/verify` — run-task 与 close-milestone 的审查主体,无需额外安装

## License

MIT
