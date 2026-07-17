---
目标: 沉淀对 obra/superpowers 的调研结论——skill 写法规范、流程保障机制、生态与官方规范关系，供本仓 skill 体系设计削减吸收
上游: 负责人指令（2026-07-18 对话：流程切割与 skill 化调研）
下游: [结论-流程切割与skill化方向](结论-流程切割与skill化方向.md)；（待立项）skill 体系设计单元
状态: 已定稿（快照型调研，基于下述版本锚，不随上游仓滚动）
类型: 调研
性质: 记述
---

# 调研 · superpowers 的 skill 写法

**调研方法与版本锚**：两路独立来源。① 仓库实测——`git clone --depth 1` 于 2026-07-17，commit `d884ae0`（v6.1.1，2026-07-02），逐文件带行号引用；② 网络信源——作者博客一手原文、GitHub API、agentskills.io 官方规范、Hacker News 三帖。下文 `文件:行` 均指克隆仓实读；标「推断」的为调研 agent 归纳，非原文自陈。

## 1. 仓库形态

- 定位：多平台 agent 插件，自述是「完整的软件开发方法论，建立在一组可组合 skill 与确保 agent 使用它们的初始指令之上」（README.md:3）。
- 部件：`skills/` 14 件；`hooks/` 仅 SessionStart 一种；**无任何 slash command**；无预注册 subagent 类型——subagent 角色由 prompt 模板文件定义（如 requesting-code-review/code-reviewer.md）。跨约十种 harness 各有适配层。
- 14 件分四组：Testing 1（test-driven-development）；Debugging 2（systematic-debugging、verification-before-completion）；Collaboration 9（brainstorming、writing-plans、executing-plans、subagent-driven-development、dispatching-parallel-agents、requesting-code-review、receiving-code-review、using-git-worktrees、finishing-a-development-branch）；Meta 2（writing-skills、using-superpowers）。

## 2. SKILL.md 写法规范

- **frontmatter 仅 `name`/`description` 两字段**，14 件无一例外。name 小写连字符、动名词惯例。
- **description 只写触发条件（"Use when..." 开头、第三人称，仓内建议 <500 字符、官方上限 1024），不泄露流程步骤**（writing-skills/SKILL.md:99-104,148-172）。一手反例：subagent-driven-development 早期 description 带工序摘要，agent 只读 description 照做、漏掉正文的两阶段 review；改纯触发后才回读正文（:154-158）。实测口径：14 条里 8 条纯触发、6 条带一句效果说明——「不泄步骤」是底线，「带一句效果」被容忍；13/14 以 "Use when" 开头，唯 brainstorming 刻意破格用第二人称强制句式（"You MUST use this before any creative work"）（分类与破格动机归因为调研判断，推断）。
- **触发词安排**：塞报错原文、症状词、同义词簇；非技术特定 skill 描述问题本质而非某语言符号（:176-206）。
- **正文参考骨架**：Overview → When to Use（症状清单）→ Core Pattern → Quick Reference → Implementation → Common Mistakes（:105-137）；实际各件按内容取舍，不逐字套用。
- **篇幅分级（自定预算 vs 实测为双轨，后者是推断）**：规则为起步型 <150 词/高频加载 <200 词/其它 <500 词（:213-266）；实测常驻注入的 using-superpowers 481 词且有专门瘦身记录（RELEASE-NOTES v6.1.0），而按需加载的 writing-skills 3807 词、subagent-driven-development 3083 词远超预算——**「常驻必须极薄」才是被严格执行的硬约束**。
- **语气**：第二人称祈使；关键禁令全大写（MUST/NEVER/STOP）；自创 XML 伪标签（`<HARD-GATE>`、`<EXTREMELY-IMPORTANT>`）标最高优先级指令；称呼统一 "your human partner"（CLAUDE.md:108，刻意措辞）。
- **流程图只画非平凡决策点**，Graphviz DOT 语法，线性步骤不画（:290-316）。
- **skill 互引**：`**REQUIRED SUB-SKILL:** superpowers:<name>` 显式点名接力（writing-plans/SKILL.md:169,173）；编排类末尾设 Integration 节列上下游；**禁止 `@` 强制加载语法**——会在需要前吃掉大量上下文（:286-289）。跨环节传**文件路径**而非贴正文（subagent-driven-development/SKILL.md:219-245）。
- **文件拆分判据**：原则与 <50 行代码全内联；只有 100+ 行重参考或交给 subagent 原样使用的 prompt 模板才独立成文件（:72-92）。**文档产物（spec/plan）的结构要求全部内联在 SKILL.md，不设独立模板文件**——内联的不是空骨架，是「要求＋判据＋自检清单」（brainstorming 的四项 spec 自检：占位符/内部矛盾/范围/歧义，brainstorming/SKILL.md:106-126）。

## 3. 元技能 writing-skills：skill 的 TDD

核心断言：「写 skill 就是把 TDD 应用于流程文档」（writing-skills/SKILL.md:10-18）。要点：

- **建 skill 门槛**：技术不直觉、跨项目复用、模式通用才建；**可机械校验的约束直接自动化，不写成 skill**（:49-59）。
- **Iron Law**：没先跑失败测试不许写/改 skill，「只是加一节」不豁免（:374-393）。
- **RED-GREEN-REFACTOR**（testing-skills-with-subagents.md）：RED＝不带 skill 用压力场景跑 subagent，**逐字记录**agent 真实借口；GREEN＝写「刚好覆盖这些借口」的最小 skill 重跑至合规；REFACTOR＝新借口补条目。**Meta-Testing**：agent 违规后反问「skill 怎么写你才会遵守」，按三类回答分别修（加公理/照写/调布局权重）（:240-266）。
- **压力场景规范**（:96-160）：零压力提问无效（agent 只会复述）；须 3 种以上压力叠加（时间/沉没成本/权威/经济/疲劳/社会/务实）；必须逼出明确选择，禁止「我会去问搭档」这种不选之选。
- **低成本预检**（SKILL.md:575-585）：单发调用＋无引导对照组＋至少 5 次重复＋人工逐条读；**把方差当指标**——5 次跑出 5 种理解＝写法没管住行为。禁止批量建多个 skill 最后一起测（:617-625）。
- **按 skill 类型分派测试法**（:395-442）：纪律型（压力下仍选对）/技法型（新场景能正确应用）/模式型（知道何时不该用）/参考型（能查到并正确用）各有成功判据。
- **对抗绕过六件套**：① 一句话铁律＋前置公理「违反字面就是违反精神」（test-driven-development/SKILL.md:14,31-35；堵「按精神做」狡辩，writing-skills:506-514）；② 借口表（Excuse|Reality 两栏），条目必须来自压测逐字记录、不许编造（testing-skills-with-subagents.md:167-176,202-208）；③ Red Flags 自查触发器（using-superpowers/SKILL.md:33-50 共 12 条）；④ 显式堵变通说法（「删除就是删除：不许留作参考、不许边看边改」，test-driven-development:37-45）；⑤ **按失败模式选写法**（writing-skills:459-474）：明知故犯型用禁令＋借口表＋红旗；「做了但形状不对」型**禁用禁令**、给正面配方（有 A/B 证据：禁令组反而产出更多不想要内容）；漏填型用 REQUIRED 结构化槽位；条件依赖型用「若可观察谓词则…」而非「规则＋例外条款」；⑥ 说服学措辞（persuasion-principles.md 引 Cialdini 2021 与 Meincke et al. 2025，N=28000，合规率 33%→72%——注意测的是通用说服，非 skill 合规的直接测量）。
- **发现路径是设计目标**：遇问题→搜描述→description 命中→扫 Overview→读 Quick Reference→真要实现才加载重料，内容摆放服务此路径（:668-679）。

## 4. 工作流链与门禁

- 主链：brainstorming → writing-plans →（subagent-driven-development | executing-plans）→ 代码评审 → finishing-a-development-branch；receiving-code-review 为收意见侧配对件。评审细部有仓内张力：requesting-code-review 自述「在 subagent-driven-development 中逐任务强制」，但后者逐任务实际用自带 task-reviewer 模板、code-reviewer.md 仅用于末次全分支评审；executing-plans 无逐任务代码评审环。
- 门禁表述：brainstorming 用 `<HARD-GATE>`——用户批准 spec 前不准调实现类 skill、不准写代码，「项目简单」不是绕过理由（brainstorming/SKILL.md:12-18）；**终态锁死**句式「终态＝调用 writing-plans」（:61）。
- 产物固定落盘路径并吃狗粮：仓内 docs/superpowers/ 下 specs 14 件、plans 11 件，其中 9 对按基名对应（实测；非严格一一对应）。
- 人工分叉点：writing-plans 结尾给用户二选一菜单再声明 REQUIRED SUB-SKILL（writing-plans/SKILL.md:156-174）。
- 长流程配进度台账 `.superpowers/sdd/progress.md`，防上下文压缩后失忆重复派发（subagent-driven-development:246-264）。
- 派发选档警告：「不显式指定模型＝默认继承全场最贵模型」被专门点名（:99-125）。

## 5. 强制执行机制

- **唯一 hook＝SessionStart，matcher 覆盖 `startup|clear|compact`**——新会话、/clear、**上下文压缩后**都重新注入（hooks/hooks.json:2-14）。注入物＝using-superpowers 全文（62 行）包 `<EXTREMELY_IMPORTANT>` 标签（hooks/session-start:27），核心为元规则「有 1% 可能相关就必须查 skill」（using-superpowers/SKILL.md:10-16）与 12 条 Red Flags，另含四条对下游设计直接有用的规则：任何回应（含澄清提问）前先查 skill（:18-24）；流程类 skill 优先于实现类（:26-31）；**SUBAGENT-STOP——被派发执行具体任务的 subagent 豁免此 bootstrap**（:6-8，即「常驻注入不污染 subagent」的现成解法）；用户指令＞skill＞默认行为的优先序（:60-62）。
- 其余 13 件不常驻，靠 description 触发词按需发现——**两层结构：hook 保证元层规则必达，发现机制负责按需加载**（此概括为推断表述）。
- 平台无关抽象；仅对仍需特殊指令的平台各留一份 reference 映射文件（现 3/10 种，v6.1.0 刻意裁剪后的形态），其余平台不设（using-superpowers/SKILL.md:52-58；RELEASE-NOTES v6.1.0）。
- **验收做成可验证行为**：新平台支持 PR 必须附「干净会话发 'Let's make a react todo list'，brainstorming 在写代码前自动触发」的完整会话记录，手动拷贝/每次手动 opt-in 的方案判「不是真集成」（CLAUDE.md:74-91）；tests/ 按 harness 分目录跑真实 CLI 断言；另有外部 evals 仓（CLAUDE.md:102-104，未克隆验证）。
- 边界：仓库明确拒绝「为合规 Anthropic 官方 skill 指南而重构」的 PR，除非附 eval 证据（CLAUDE.md:40-42）——官方指南镜像只是背景参考，writing-skills 本身才是其真实规范。

## 6. 生态、反响与官方规范关系

- 规模（GitHub API 实测 2026-07-17）：star 256,593、fork 22,846，创建于 2025-10-09，前一日仍在更新。已入 Anthropic 官方插件市场（anthropics/claude-plugins-official PR #148）。
- 时间线：仓库创建（2025-10-09）先于 Anthropic 官方 Agent Skills 发布（2025-10-16）约一周；「提前知情」无证据，判为趋势收敛（推断）。官方规范（agentskills.io）：必填 name（≤64 字符）/description（≤1024，建议 what+when 都写）；三层渐进加载（元数据常驻约 100 token→正文激活加载、建议 <5000 token→资源按需）；正文建议 <500 行。**张力点**：官方建议 description 写 what+when，作者 2025-12-18 实战教训是写了 what 模型自以为懂就不读正文（blog.fsck.com/2025/12/18/superpowers-4/）——本仓从作者。
- 作者其它一手教训（blog.fsck.com/2025/10/09、/2025/12/18）：skill 应无感自动触发；因 harness 对 skill 描述总量有隐性限制而做过 skill 合并瘦身。
- 社区批评（HN id 45580766/47623101/48739459）：过度工程化、token 开销大、缺独立基准测试；共识「挑着用别整套搬」。衍生/竞品：GSD-2（防上下文腐化）、gstack（角色制）、Spec-Kit（只管规格）、Metaswarm（建于 superpowers 之上）。
- 反响数字告诫：各站「安装量/开发者数」互相矛盾达 10 倍，均无原始出处，不采信。

## 7. 语态标注（实测 / 推断汇总）

实测：全部 `文件:行` 引用、hook 与 OpenCode 插件源码、GitHub API 数字、作者博客两篇与 agentskills.io 全文、HN 三帖。推断：description 8/6 分类、篇幅「双轨制」概括、「两层机制」表述、「先于官方是巧合」、机制有效性（作者自述＋自家评测，无独立基准）。未验证：外部 evals 仓、13 件 skill 是否都留有 RED-GREEN 演化记录、三个辅助脚本的实现源码。
