---
name: gmgn
description: 凡要按流程或 workflow 推进项目研发先调本 skill 定位——新项目起步、产品构思落地、调研、功能开发、修 bug、重构、写白皮书/ROADMAP/PRD/需求/设计/任务文档、派活写代码、上线发布、验收或关账,以及不确定当前该做哪一步、要找工序与文档契约时使用;用户说「按 GMGN/按流程办」「下一步做什么」时必调。
---

# GMGN 总线(状态→下一步路由)

全流程两段:**需求澄清**(brainstorm→白皮书→roadmap)→ **需求实现**(逐 Milestone:write-goal→write-requirement→write-design→write-task→run-task→close-milestone)。

原理见仓根 [GMGN.md](../../GMGN.md)(两条根线:表征-实体脱节/同源盲区);文档契约见 [references/文档写作契约.md](references/文档写作契约.md)。本文只路由。

## 路由:先判状态,再进对应 skill

判定手段:DocStar 已安装时用 `docstar graph` / `docstar docs --fields 状态,性质` 看链与状态;未安装时按标准文件名查存在性、元信息链接与状态字段。两种路径都要回读原文,派生图不作裁决。

| 当前状态 | 下一步 |
|---|---|
| 无白皮书(WhitePaper) | `brainstorm` |
| 白皮书未批 / 需大改 | `brainstorm`(修订态) |
| 白皮书已批,无 ROADMAP | `roadmap` |
| ROADMAP 已批,负责人点名启动某 Milestone(行状态=未立项) | `write-goal` |
| 单元已立项:无/未批 Requirement → Design → Task | `write-requirement` → `write-design` → `write-task`(依次) |
| Task 已批,有确认要做的卡 | `run-task`(逐卡) |
| 全卡关账、追踪矩阵满格 | `close-milestone` |
| Milestone 已关账 / 新想法 / 要重排 | `roadmap`(维护态) |
| 缺陷修复、琐碎单步改动 | **旁路**:走受控变更闸/直接修,不过全链 |

## 硬门总则(HARD-GATE,分层授权)

链上任一 skill:**上游产物不存在或未过其所需审核,不得进入**——skill 自带前置检查,缺则指回上游。审核分层:白皮书与 ROADMAP=critic 后**负责人批准**;G-R-D-T 链内文档=critic 后**编排者审核**即可;立项启动与关账仍是负责人停点。负责人明示豁免除外(跳步须留痕可见)。

## 全局纪律(一行版;完整叙述见 GMGN.md 第 4/5 章)

每次回答带 Reflection 三问(最弱假设/被忽略的反例/哪些实测哪些推断)｜派发 subagent 按本机工具实际支持的字段显式选档(机械=低/常规=中/判断密集=高),回传三段缺段打回｜落盘即按主题 commit;只有负责人或项目规则已明确授权远端写入时才 push。
