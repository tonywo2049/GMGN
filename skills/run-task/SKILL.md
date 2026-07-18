---
name: run-task
description: 任务卡已确认要做、要开始写代码实现(派 coding agent)并经收卡审查关卡时使用;用户说「开做这张卡」「实现这个任务」「开始编码」时触发。
---

# 逐卡实现(coding agent + 编排者收卡审查)

<HARD-GATE>前置:卡存在于已过 critic+编排者审核的 `Task.md` 且被确认要做;缺则拒绝执行并指回 `write-task`。</HARD-GATE>

每次回答末尾带 Reflection 三问(最弱假设/被忽略的反例/哪些实测哪些推断)。主会话在本环是编排者:派发、验收、合并,不亲自写实现;一次一卡,无依赖的多卡可并行派发。

## 流程(六步)

1. **取上下文**:`docstar brief <卡> --json`——卡的前置/规格锚引用/测试闭包一次拿到,贴进任务书;完成判据以卡文本为准(brief 不必然结构化带出),缺的让 agent 用 `id`/`doc` 自拉。
2. **派 coding agent**:按 [coder-任务书](../gmgn/references/coder-任务书.md) 填槽(含代码写作准则块与失败先行测试要求);**显式选档**:机械=低档/常规=中档/判断密集=高档,禁 fable,model 不省略。多张无依赖卡并行派发。
3. **收回传**:三段缺段打回(成果与实证/偏离与待裁/Reflection);agent 自述不作数,`/verify` 可重放清单与关键声明按命令重放抽验,不重跑。
4. **收卡审查**(编排者执行,独立于实现者;详见 [code-review-任务书](../gmgn/references/code-review-任务书.md)):① 编排者亲自 Skill 调用内置 `/code-review` 审卡级增量 diff——**不得由实现者自调**(2.1.212 实测:opus 族 medium/high/xhigh 审查在调用者上下文内执行,作者自调即失独立性);显式选档:常规卡 medium/high、资产/安全/跨模块接口 xhigh,ultra 仅负责人手动,关账级组合审(max)落点在 `close-milestone`;findings 由编排者裁,只报不改。② 补两查(测试判别力变异自证+规格锚对齐):默认编排者亲自,重卡才派独立 agent。正确性五角度、清理与 CLAUDE.md 规约由内置件覆盖,不自造审查提示词;`/verify` 已左移至 coder(第 2 步任务书),此处只重放抽验。
5. **处置**:阻塞项修复后定向复核;判定对象零改动(review 发现缺陷→停、上报、重开卡,不许修完算到原版本头上)。
6. **卡关账**:台账+追踪矩阵同批刷新,按主题 commit+push。

## 出口

单卡完→回台账领下一卡;**全卡关账且追踪矩阵满格→REQUIRED 下一环:`close-milestone`**。中途新冒的需求/架构问题不就地扩:需求走 Requirement 受控变更,架构回选型与架构线,新想法进 ROADMAP TODO。
