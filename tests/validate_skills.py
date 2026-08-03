#!/usr/bin/env python3
"""Validate GMGN structure and machine-readable workflow invariants."""

from fnmatch import fnmatchcase
import json
from pathlib import Path
import re
import sys
import tomllib
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_release import release_metadata, validate_normative_layout


SKILLS = {
    "gmgn",
    "brainstorm",
    "write-decision",
    "roadmap",
    "write-goal",
    "write-requirement",
    "write-design",
    "write-task",
    "run-task",
    "close-milestone",
    "release",
}
ROLES = {
    "commander",
    "runner",
    "author",
    "coder",
    "researcher",
    "verifier",
    "critic",
    "reviewer",
}
CODEX_AGENT_NAMES = {role: f"gmgn_{role}" for role in ROLES}
ROLE_RUNTIME = {
    "commander": ("gpt-5.6-sol", "max"),
    "runner": ("gpt-5.6-sol", "max"),
    "author": ("gpt-5.6-sol", "max"),
    "coder": ("gpt-5.6-luna", "max"),
    "researcher": ("gpt-5.6-luna", "max"),
    "verifier": ("gpt-5.6-sol", "max"),
    "critic": ("gpt-5.6-sol", "max"),
    "reviewer": ("gpt-5.6-sol", "max"),
}
SPAWNING_ROLES = {
    "commander",
    "runner",
}
ROLE_SANDBOX = {
    "commander": "workspace-write",
    "runner": "workspace-write",
    "author": "workspace-write",
    "coder": "workspace-write",
    "researcher": "read-only",
    "verifier": "workspace-write",
    "critic": "read-only",
    "reviewer": "workspace-write",
}
TASK_HEADER = "| # | task | spec anchor | prerequisite | status | execution |"
OLD_TASK_HEADER = "| # | task | spec anchor | prerequisite | failing test | status |"
ASSURANCE_POLICY = Path("skills/gmgn/references/en/assurance-policy.json")
VERIFIER_TRIGGERS = [
    "artifact-not-fully-machine-checkable",
    "real-startup-or-e2e-not-covered-by-deterministic-local-checks",
    "explicit-independent-execution-requirement",
]
WRITING_RULES = Path("skills/gmgn/references/en/writing-rules.md")
RUN_TASK = Path("skills/run-task/SKILL.md")
WRITE_DECISION = Path("skills/write-decision/SKILL.md")
WRITE_DESIGN = Path("skills/write-design/SKILL.md")
DISPATCH_CONTRACT = Path("skills/gmgn/references/en/dispatch-and-handoff.md")
ROADMAP = Path("skills/roadmap/SKILL.md")
WRITE_GOAL = Path("skills/write-goal/SKILL.md")
RELEASE = Path("skills/release/SKILL.md")
CANONICAL_REFERENCES = {
    ASSURANCE_POLICY,
    WRITING_RULES,
    Path("skills/gmgn/references/en/dispatch-and-handoff.md"),
    Path("skills/gmgn/references/en/code-review.md"),
}
RUN_TASK_CONTROLS = (
    "create exactly two files for every newly materialized task",
    "The verification contract selects an executable oracle",
    "behavior, defect, algorithm, and interface work records the smallest set of authority-derived\n"
    "  test cases. Each case identifies its exact approved Requirement, AC, Design, Contract, or\n"
    "  Task completion-criterion anchor; scenario or input; observable expected result; and the\n"
    "  wrong behavior it detects.",
    "every changed behavior needs discriminating pre-implementation\n"
    "  failure coverage",
    "The Coder encodes the accepted criteria; it does not define acceptance meaning",
    "structural regression, not behavior TDD evidence",
    "This setup has no standalone preparation checkpoint",
    "The initial Coder brief names the exact accepted Task row and limits its `Task.md` write to\n`execution` and macro `status`.",
    "it authorizes the complete Task-local\ndocument, test, and production write boundary.",
    "The Coder does not request or wait for separate RED approval from the\nRunner, Commander, or primary orchestrator, and does not return an interim RED checkpoint for\nconfirmation.",
    "For RED-gated work, the Coder first changes only Task-local execution documents, tests, and\n"
    "test-only support, commits that production-unchanged checkpoint locally",
    "The checkpoint may include Card, Log,\nand the exact Task-row execution/status update, but no production implementation.",
    "without pausing or returning it to the Runner, and continue directly to GREEN.",
    "After recording RED, freeze target tests and every helper that can affect their verdict.",
    "The Coder implements the smallest sufficient production change and obtains GREEN with the same\n"
    "target command before required regression checks.",
    "Any result-affecting target-test change\ninvalidates RED evidence",
    "record valid RED again",
    "never\ndelete, skip, weaken, bypass, or move production logic into a test to obtain GREEN.",
    "After the first GREEN, refactor only to correct a concrete structure problem.",
    "otherwise skip refactoring without creating another checkpoint.",
    "Replay the target command at the RED checkpoint and final candidate",
    "Treat safe lane saturation as a scheduling invariant",
    "The Commander scans the entire\ntarget-Milestone Task set",
    "A Commander return\nseparates any caller-only mechanical workspace preparation from each complete Runner brief.",
    "If preparation fails, it\nreturns the exact failure facts to the same Commander and does not start the Runner.",
    "The Runner brief contains only this Task's changing facts and resolved selections",
    "does not copy stable Runner/Coder, RED/GREEN,\nmonitoring, Review, assurance-execution, or completion procedures.",
    "Authorization and missing-information pauses follow the dispatch contract",
    "largest number of currently blocked tasks ready",
    "break ties by stable `card_id`",
    "`ponytail:ponytail`",
    "`ponytail:ponytail-review`",
    "`codegraph init <workspace>`",
    "automatically run `codegraph init <workspace>` once",
    "do not ask the owner",
    "it returns a structured `needs_commander` event for cross-Task or shared-",
    "The primary orchestrator creates or resumes the applicable Commander",
    "Every Codex `wait_agent` call uses the actual tool argument\n"
    "`{\"timeout_ms\": 600000}` (10 minutes) as a maximum.",
    "An agent\ncompletion or attention event returns early",
    "without calling `list_agents`",
    "If the full ten minutes expires without an event, the caller calls `list_agents` once.",
    "Handle any completed\nor attention-needed dispatch immediately",
    "return to the same maximum ten-minute `wait_agent` call",
    "Do not call\n`list_agents` more than once for the same timeout",
    "Between lifecycle events and timeout boundaries, do not poll `list_agents`",
    "A\nmessage to an active agent must carry authorization, requested information, or a decision\npermitted by the dispatch contract.",
    "Do not infer a shorter polling interval",
    "A running dispatch remains unfinished work. Do not call `interrupt_agent`, end orchestration,\nor return a final Task result while a required direct agent is `running`.",
    "time or token budget are not such evidence",
    "Do not send heartbeat, unchanged `running`, timeout, agent-count, or routine progress\ndata to the Owner, Log, telemetry, or another agent.",
    "The Runner directly reviews the complete fixed implementation and test candidate under the",
    "Send an accepted in-scope finding to the same still-active Coder.",
    "reruns only checks affected by the finding or\nfix",
    "Ordinary deterministic local execution belongs to the Runner; Coder output remains supporting",
    "Do not dispatch a Verifier before\nrelevant Review blockers clear.",
    "Normal Task execution does not use an Author. The Coder creates or resumes Card/Log,\nmechanically updates only its accepted Task row's execution pointer and macro status",
    "change only its exact accepted Task row's execution pointer and macro status",
    "The Runner sends the exact Review,\nfinding, assurance, Verifier, and affected-check results to the same still-active Coder",
    "The Coder commits that closure candidate locally and returns it to the Runner.",
    "The Runner then returns one transient `ready_for_integration` event directly to the primary",
    "`ready_for_integration` as a Task, Card, Log, or workflow state.",
    "creates or marks ready the single pull request for that repository",
    "An earlier\nDraft pull request is allowed only when required host checks or requested early collaboration",
    "For a multi-repository Task, use one branch and pull request per changed repository",
    "If a required remote operation is\nnot authorized, request that authorization before this event.",
    "1. acquire the existing integration lock;\n2. synchronize the latest shared baseline;\n3. form the final candidate on that latest baseline;\n4. use existing Git commit/tree mechanisms to confirm candidate identity;\n5. run or verify every required gate bound to that exact candidate;\n6. update the shared baseline through the repository's declared merge policy; and\n7. release the integration lock.",
    "do not add a parallel lock or integration branch",
    "remains incomplete\nuntil every required repository candidate is integrated and cross-repository gates pass",
    "After all gates clear for one repository, the Commander atomically updates that repository's\nshared-baseline entry",
    "The Commander uses one separate authority-stage branch,\nwritable worktree, and pull request for the upstream candidate.",
    "The Author writes and commits\nthe candidate locally; the Commander publishes and integrates the accepted candidate",
    "Do not mix it into an affected Runner branch or pull request.",
    "does not perform another integration or semantic review.",
)
RUN_TASK_EXCLUSIVE_MARKERS = (
    "wait_agent",
    "list_agents",
    "interrupt_agent",
    "largest number of currently blocked tasks ready",
    "break ties by stable `card_id`",
    "ponytail:ponytail",
    "ponytail:ponytail-review",
    "codegraph init",
)
RUNTIME_SELECTION_CONTROLS = (
    "`scripts/install_codex_agents.py`",
    "`CODEX_HOME/agents`",
    "Create the role by its exact installed name: `gmgn_commander`",
    "named-Agent selector (`agent_type` in runtimes that expose the field)",
    "set `fork_turns=\"none\"`",
    "`task_name` is only the dispatch instance label; do not use it as a profile selector",
    "Model, reasoning effort, sandbox, and stable role instructions come from the installed TOML",
    "The TOML sandbox is the requested\nruntime mode; active parent permissions plus the workflow and brief remain the operative\nboundaries.",
)
DISPATCH_LIFECYCLE_CONTROLS = (
    "An authorization request,\nmissing-information request, Owner question, candidate checkpoint, or required wait is\ninterim",
    "Resume that same agent with\nthe exact answer or next action instead of retiring and recreating it.",
    "A terminal completion retires the agent.",
    "Never resume, repurpose, or send later work to a\nretired agent.",
    "One Commander owns one bounded global matter.",
    "Do not keep\na Commander pool or assign role variants by stage, scheduling, conflict, or integration use.",
    "An Author or Coder remains assigned after a candidate checkpoint",
    "Critic,\nReviewer, and Verifier returns are terminal for their selected fixed surface",
)
DISPATCH_ROLE_PROFILE_CONTROLS = (
    "dispatch to exactly one of `commander | runner | author | coder | critic | reviewer | verifier |\nresearcher`.",
    "These are the only GMGN agent roles.",
    "A task name or `dispatch_id` distinguishes\ninstances but never creates a role variant.",
    "The selected platform profile\nsupplies stable role rules; the brief supplies only this dispatch's changing facts.",
    "Resolved workflow selections belong in the brief; the selected procedures do not.",
    "Do not copy\nthe selected role's child-agent lifecycle, RED/GREEN, monitoring, Review, assurance-execution,\nor completion procedure into the brief.",
    "Author, Coder, Critic, Researcher, Reviewer, and Verifier do not create agents.",
    "This is a\nworkflow role boundary; platform agent availability does not grant broader creation authority.",
    "On Codex, install and invoke the exact `gmgn_*` Agent name",
    "load `agents/<role>.md` for the\nselected role.",
)
EXTERNAL_AUTHORIZATION_CONTROLS = (
    "One authorization may cover a named set of external operations against an exact target",
    "Expanding the operation set, target, or side effects requires another authorization",
)
RESEARCHER_CONTROLS = (
    "A Researcher brief defines one bounded collection question",
    "It does not synthesize, compare, infer, recommend, or select.",
    "Its caller owns analysis and conclusions.",
)
COMMANDER_SELECTION_CONTROLS = (
    "When the active workflow does not\nselect a Commander for a bounded matter",
    "Any stage may select one Commander for a bounded matter.",
    "The active workflow, not the role\nprofile, decides whether to use it.",
    "the primary\nsession keeps exact Owner relay, instructed mechanical actions, and final result recording.",
    "`run-task` requires Commander for its ready-set and integration matters and is the only stage\nthat uses Runner-based execution.",
    "When an owning Skill assigns one of those duties to the\nprimary orchestrator, a selected Commander performs it for its bounded matter; direct Owner\nrelay and explicit mechanical actions remain with the primary orchestrator.",
    "It must delegate creation or semantic revision of WhitePaper, Decision,\nROADMAP, Goal, Requirement, Design, Task, and other upstream authority, plan, or design\ncandidates to an independent Author.",
)
DISPATCH_WORKSPACE_CONTROLS = (
    "Caller-only mechanical setup stays outside the agent brief.",
    "If setup fails, return the exact failure\nto the same Commander without creating the Runner.",
    "records enough durable Git or platform metadata to\nprove which unfinished dispatch owns it.",
    "Never infer ownership from a path pattern.",
    "A Runner\nowns its Task workspace while its dispatch is active, under Review or correction, waiting on\na Commander, or queued for integration.",
    "Reuse it only for an already\nidentified next dispatch in the same repository",
    "If the scheduling pass finds no explicit next consumer, remove\nthe exact GMGN-managed worktree.",
    "Possible future reuse does not justify an idle pool, TTL,\nLRU, or reuse score.",
    "Never auto-remove the main workspace, a pre-existing or user-created worktree",
    "never delete by wildcard",
    "For each repository that a Git-backed Task changes, keep one Task-named branch, at most one\nactive pull request, and at most one writable worktree.",
    "The branch and pull request belong to\nthe Task-repository change, not to an agent identity.",
    "resumes the same branch and pull request instead of creating another pair.",
    "`shared baseline` means the recorded set containing one current\nintegrated commit per participating repository.",
    "publishes the first coherent checkpoint and pushes later coherent checkpoints",
    "A pull request is one integration surface for the complete\nTask-repository candidate, not one surface per commit or repair.",
    "Do not create a branch or writable worktree merely because a role is independent.",
    "use\na disposable detached worktree or copy without a branch",
    "After verified integration, remove the managed worktree and delete its no-longer-needed local\nTask branch only after native Git or host evidence proves the candidate integrated.",
    "delete its remote branch only when\nthe repository policy and shared authorization permit it.",
    "never delete an unmerged branch with material work merely to release a workspace.",
)
COMMANDER_RUNNER_SURFACE_CONTROLS = {
    Path("GMGN.md"): (
        "**Commander** is the single workspace-write global-judgment role available to any stage when\n  its active workflow selects it.",
        "Only the primary orchestrator\n  creates, resumes, or retires a Commander and mechanically creates Runners from its briefs.",
        "Any stage may select a Commander for one bounded matter; doing so is\noptional unless that workflow requires it.",
        "Runner-based execution\nremains specific to `run-task`.",
        "There is no Integrator role.",
        "each Task uses one stable Task-named branch,\none writable worktree, and at most one pull request in every repository it changes.",
        "A multi-repository Task closes\nonly after every required repository candidate and cross-repository gate is integrated",
        "its shared baseline is\nthe recorded set of one current commit per participating repository",
        "The Coder updates only that accepted row's `execution` link and macro `status`",
        "returns\nthose exact closure facts to the same Coder for final Task-execution recording.",
        "The primary orchestrator records the Commander result mechanically and does not repeat integration or\nsemantic review.",
    ),
    Path("skills/gmgn/SKILL.md"): (
        "Any stage may select one Commander for a bounded planning, scheduling, conflict, upstream-\nreturn, or integration matter.",
        "The active workflow, not the role profile, makes that selection;\ndo not create a Commander merely because a stage exists.",
        "Only the primary orchestrator creates,\nresumes, or retires it.",
        "other stages\nmay use Commander without using Runner.",
        "The same responsible primary orchestrator or Commander directly integrates an accepted document\ncandidate.",
        "Its Runner reviews under `code-review`; independent Reviewer only when explicitly required",
        "Critic and Reviewer do not maximize finding count. A valid return may contain no findings.",
        "Report an issue only when leaving it unresolved creates concrete material harm, no accepted\neffective fallback contains that harm, and a smallest sufficient correction can be stated.",
        "Apply a deletion test before dispatch: the caller must state which uncontained material outcome\nwould change if the Critic were omitted. A candidate does not inherit its downstream domain's\nrisk level. Conservative scheduling, delayed readiness, additional dependencies, and work with\nan existing effective pause or return fallback are not material harm unless current facts show\nan uncontained Milestone, external, or irreversible impact. If omitting the Critic changes\nneither acceptance nor the next action, skip it.",
        "`artifact-not-fully-machine-checkable` does not apply merely because a normative document's\nmeaning cannot be fully machine-checked. The responsible caller and optional Critic gate own\ndocument semantics. Require a Verifier only when an observation remains that no other check can\nreplace or that must occur in a real environment, or when independent execution is explicitly\nrequired.",
        "Do not create an Integrator role.",
    ),
    DISPATCH_CONTRACT: (
        *DISPATCH_ROLE_PROFILE_CONTROLS,
        "only the primary orchestrator creates, resumes, and retires a Commander;",
        "only the primary orchestrator mechanically creates or resumes a Runner from a Commander's\n  complete brief;",
        "a selected Commander may directly create any defined named Agent that the current workflow\n  assigns to it, and monitors those direct children.",
        "A Commander never creates another Commander.",
        "Under the normal ready-set path it returns Runner\nbriefs for the primary orchestrator to apply mechanically instead of creating Runners itself.",
        "a Runner may directly create its Coder, Researcher, and risk-triggered Verifier; and",
        "a Runner may create a Critic or Reviewer only when the Owner, applicable authority, current\n  workflow rule, or Commander brief explicitly requires that independent role.",
        "A Runner never creates a Commander, Author, another Runner, or any unnamed role.",
        "only structured substantive state or results go directly to the\nprimary orchestrator.",
        *DISPATCH_LIFECYCLE_CONTROLS,
        *EXTERNAL_AUTHORIZATION_CONTROLS,
        *RUNTIME_SELECTION_CONTROLS,
        *RESEARCHER_CONTROLS,
        *COMMANDER_SELECTION_CONTROLS,
        *DISPATCH_WORKSPACE_CONTROLS,
        "`needs_commander` and `ready_for_integration` are transient events, not Task, Card, Log, or\nworkflow states.",
        "after the Runner supplies accepted closure facts,\n  commits the final Task-local documentation and status candidate.",
        "does not perform a second integration or\nsemantic review.",
    ),
    RUN_TASK: (
        "This stage requires the Commander-and-Runner hub-and-spoke flow.",
        "Commander use in another stage follows that\nstage's owning workflow; Runner-based execution remains specific to this Skill.",
        "One Runner owns one Task and its assigned repository workspace set end to end.",
        "It normally reviews the Coder candidate itself\nunder the code-review contract.",
        "The Runner never creates a Commander, Author, another Runner, or an unnamed role.",
        "Normal Task execution does not use an Author. The Coder creates or resumes Card/Log,\nmechanically updates only its accepted Task row's execution pointer and macro status",
        "This setup has no standalone preparation checkpoint",
        "The Coder commits that closure candidate locally and returns it to the Runner.",
        "The Runner then freezes the complete candidate without updating the shared\nbaseline.",
        "The primary orchestrator creates one Commander with the complete integration brief. It does\nnot check or integrate the candidate first.",
        "The Commander may inspect and modify content within the current stage, brief, authority, and\nwrite boundary.",
        "A rebase, conflict resolution, or Commander edit that changes candidate\ncontent invalidates the affected RED/GREEN, Review, Verifier, and upstream evidence.",
        "Only a merge commit that leaves candidate content unchanged may reuse\nthe original evidence.",
        "creates or marks ready the single pull request for that repository",
        "do not add a parallel lock or integration branch",
    ),
    Path("skills/gmgn/references/en/code-review.md"): (
        "During normal `run-task`, the Task's Runner reviews the fixed implementation and test\ncandidate.",
        "Create one independent Reviewer only when the Owner, applicable authority, current workflow\nrule, or Commander brief explicitly requires it.",
        "Reviewer is used only for implementation and\ntest candidates; Critic covers normative document meaning.",
        "Report a finding only when the answers establish concrete material harm, no accepted effective\nfallback, and a smallest sufficient correction.",
        "The Runner adjudicates in-Task findings and sends an accepted minimum repair to the same\nCoder",
        "without automatically creating another Reviewer.",
        "any rebase, conflict resolution, or Commander edit that changes candidate\ncontent invalidates the affected Review and other candidate-bound evidence.",
    ),
    Path("agents/commander.md"): (
        "Work only for one bounded\nGMGN matter; never create another Commander or form a standing pool.",
        "The current workflow, not\nthis profile, selects your stage and assigned duties.",
        "Directly create and monitor any defined named Agent that the\nactive workflow assigns to you.",
        "Under the normal run-task ready-set\npath, return complete Runner briefs for the primary orchestrator to create mechanically rather\nthan creating Runners.",
        "keep caller-only mechanical workspace setup separate from\neach Runner brief.",
        "It otherwise contains only the Task's\nchanging facts, resolved selections, boundaries, checks, expected evidence, and return gates.",
        "Every complete Runner brief explicitly contains `dispatch_id`,\n`role: gmgn_runner`, `applicable_skill: gmgn:run-task`",
        "never restates Runner/Coder, RED/GREEN,\nmonitoring, Review, assurance-execution, or completion procedures.",
        "When an upstream\nchange is required, invoke its owning Skill inside this dispatch",
        "directly integrate the accepted candidate.",
        "The same Commander remains assigned until this matter is applied,\ncancelled, invalidated, or hard-fails; a later matter requires a new Commander.",
        "Do not emit `needs_commander` or finish the matter.",
        "remove the full\nTask-status inventory, complete blocked list, platform agent counts",
        "You may make mechanical or other permitted changes",
        "`needs_commander` and `ready_for_integration` are transient run-task\ninput events, never persistent states.",
        "do not create another lock or integration branch",
    ),
    Path("agents/runner.md"): (
        "directly create a Coder, Researcher, or Verifier only when the Task needs that\nrole.",
        "Do not create a Commander, Author, another Runner, or an unnamed role.",
        "Normally perform\nthe Critic- or Reviewer-equivalent check yourself.",
        "Create an independent Critic or Reviewer\nonly when the Owner, applicable authority, current workflow rule, or this Task's Commander\nbrief explicitly requires that role.",
        "The Coder creates or resumes Card/Log, mechanically updates only its accepted Task row's\nexecution pointer and macro status",
        "return those exact facts to the same Coder for Log, Task status, and\nother Task-execution closure writes.",
        "do not route child-agent calls or routine progress through it.",
        "Do not write\neither event into Task, Card, Log, or another state enum.",
        "use the assigned Task-named branch and single pull request as\nthe durable lane.",
        "Never create a branch or pull request per Coder, commit, review, or fix.",
    ),
    Path("agents/coder.md"): (
        "Do not create other agents.",
        "Create or restore the Task's stable Card and replaceable Log before\nimplementation when required",
        "In `Task.md`, change only this accepted Task row's\n`execution` pointer and macro `status`",
        "Create no standalone preparation checkpoint or pause",
        "Before recording a checkpoint as behavior RED",
        "Name or text presence, an invocation without an asserted\nresult, or ordinary compile failure cannot replace a behavior oracle",
        "Record the exact command, target failure, and rejected wrong behavior.",
        "Do not return the\nRED checkpoint or request or wait for separate approval.",
        "record the Runner's\nexact closure facts in Log, set only this Task row's status to `closed`",
    ),
    Path("agents/author.md"): ("Do not create other agents.",),
    Path("agents/researcher.md"): ("Do not\ncreate other agents.",),
    Path("agents/verifier.md"): (
        "checks belong to the caller.",
        "Do not create other agents.",
    ),
    Path("agents/critic.md"): (
        "Review\nonly the assigned document meaning",
        "create other agents.",
        "Report an issue only\nwhen leaving it unresolved creates concrete material harm, no accepted effective fallback\ncontains that harm, and the smallest sufficient correction can be stated.",
    ),
    Path("agents/reviewer.md"): (
        "Review only that fixed surface.",
        "Do not create other agents.",
        "Do not intentionally edit tracked candidate files.",
        "Report an issue only\nwhen leaving it unresolved creates concrete material harm, no accepted effective fallback\ncontains that harm, and the smallest sufficient correction can be stated.",
    ),
}
ROLE_PROFILE_CONTROLS = {
    "commander": (
        "GMGN 全局事项",
        "当前 Workflow 决定你所在的阶段和具体职责",
        "创建任意已定义的命名 Agent",
        "普通 Runner 是否由主 Session 机械创建，以当前 run-task 规则为准。",
        "将准备指令与 Runner 任务书分开返回",
        "dispatch_id、role=gmgn_runner、applicable_skill=gmgn:run-task",
        "Runner 任务书只写本次 Task 的变化事实",
        "不复述 Runner/Coder、RED/GREEN、监测、Review、assurance 执行或完成流程",
        "删除全量 Task 状态、完整 blocked 清单、Agent 数量",
        "同一 Commander dispatch 内执行对应的 owning Skill",
        "不得输出 needs_commander，也不得在事项完成前结束",
        "上游语义文档交给 Author 写",
        "通过主 Session 发送 ask_owner",
        "按当前 Workflow 直接集成",
        "候选内容发生变化时，不得绕过因此失效的检查和证据",
    ),
    "runner": (
        "端到端负责一个 Task",
        "直接创建和监测完成该 Task 所需的子 Agent",
        "不得创建 Commander",
        "needs_commander",
        "Coder 负责 Card/Log、自己唯一 Task 行的 execution/status、验证契约、RED/GREEN、实现和执行证据",
        "Task-local Review",
        "把精确 closure facts 返回同一 Coder 写入 Log 和 Task 状态",
        "Task branch 的远端 writer",
        "不得更新共享基线",
    ),
    "author": (
        "上游权威、计划或设计文档候选",
        "只修改指定文档",
        "不自行决定未决产品、需求、设计、验收或 Task 含义",
        "正常 run-task",
        "不属于 Author",
        "返回直接调用者",
        "不创建其他 Agent",
    ),
    "coder": (
        "最小充分候选",
        "负责 Card/Log、自己唯一 Task 行的 execution/status、验证契约、测试、RED/GREEN、实现和相关执行证据",
        "Task.md 只改自己行的 execution/status",
        "不创建或返回独立的准备 checkpoint",
        "到达权威定义的行为或 Contract 边界",
        "没有结果断言的调用或普通编译失败不能代替行为 oracle",
        "无法建立有效 RED 时，不得开始生产实现",
        "记录精确命令、目标失败和被拒绝的错误行为",
        "有效 RED 记录后不返回确认，直接继续 GREEN",
        "按 Runner 返回的精确 closure facts 更新 Log 和 Task 状态",
        "不决定上游语义",
        "不修改共享权威或共享基线",
        "不执行远端写入",
        "返回直接调用者",
        "不创建其他 Agent",
    ),
    "researcher": (
        "逐来源证据、版本或日期、缺失信息和实质限制",
        "不修改项目文件",
        "不替调用者作跨来源比较、方案推荐、Design 选择或最终决定",
        "不创建其他 Agent",
    ),
    "verifier": (
        "风险触发条件和最小验证计划",
        "不扩大计划",
        "不要修改 tracked 候选",
        "都不是通过",
        "不创建其他 Agent",
    ),
    "critic": (
        "上游规范文档候选",
        "具体实质损害",
        "no findings",
        "不编辑候选",
        "不审查实现代码",
        "不裁决自己的 finding",
        "不创建其他 Agent",
    ),
    "reviewer": (
        "固定的实现与测试候选",
        "具体实质损害",
        "no findings",
        "workspace-write 只用于运行检查",
        "不要主动修改 tracked 候选",
        "直接调用者负责裁定",
        "不创建其他 Agent",
    ),
}
LEGACY_ROLE = "adjud" + "icator"
ROADMAP_APPROVAL_CONTROLS = (
    "The independent Author writes one complete recommended candidate without asking the Owner to\napprove fields or allocations separately.",
    "That approval ratifies the ROADMAP-owned allocations and rulings expressed in the candidate",
)
GOAL_APPROVAL_CONTROLS = (
    "Prepare the Goal and proposed initiation as one candidate",
    "do not require a separate initiation authorization",
    "That approval both authorizes the\nMilestone state change and approves Goal meaning",
)
RELEASE_OPERATION_ORDER_CONTROLS = (
    "push the branch and tag together\natomically when the host supports it",
    "create or complete the Release from that tag",
    "upload the\nnamed assets",
    "read the final remote state back once",
)
GMGN_RUN_TASK_ROUTE_CONTROLS = (
    "An initiated Milestone has accepted Task rows that can run",
)
CONTRADICTORY_POLICY_MARKERS = (
    "Any return retires the agent",
    "Every external operation needs separate authorization",
    "scan only the separately confirmed execution set",
    "Every delegated agent inherits the primary orchestrator configuration",
    "Researcher** analyzes and recommends solutions",
    "The primary orchestrator delegates all semantic decisions",
    "The primary session normally writes implementation",
    "The primary orchestrator may act as one Coder",
    "Keep an unassigned worktree for possible future reuse",
    "A Runner creates a Commander",
    "Commander is used in every stage",
    "Commander may be used only in run-task",
    "A separate integrator updates the shared baseline",
    "Create one pull request per commit",
    "A replacement Runner creates a new Task branch",
    "Every independent read-only role gets a writable branch worktree",
    "A multi-repository Task closes when one repository pull request merges",
    "Keep recoverable checkpoints only in local storage",
    "Delete every Task branch when its Runner exits",
    "Mix the upstream semantic change into the Runner pull request",
)
CONTRADICTORY_DESIGN_TDD_EXCEPTION_MARKERS = (
    ("edit first", "research later"),
    ("implementation before RED", "approval later"),
)
LATEST_EVENT_VALUES = (
    "latest_event: [Current](#current)",
    "latest_event: [Final Evidence](#final-evidence)",
)
GIT_LOG_CONTROLS = (
    "Log may record each changed repository, Task branch, accepted base,\nand pull-request location.",
    "It never embeds the commit reference of the same commit that\ncontains that Log update.",
    "the native Git host and Commander return own the final pull-request\nhead and integrated commit records.",
)
MILESTONE_REOPEN_CONTROLS = (
    "state: closed → initiated when unfinished work is found",
    "replace its current `accepted_result` with `none`",
    "do not roll them back merely because a prerequisite was reopened",
)
DECISION_SCOPE_CONTROLS = (
    "regardless of subject or Milestone scope",
    "Decision may own any current ruling needed by planning or active work",
    "downstream artifacts link the applicable D-ID and keep only their own derived content",
    "Never keep the same ruling normative in both places",
)
DECISION_CONSUMPTION_CONTROLS = (
    "a direct specification for downstream artifacts or an implementation checklist for one\nMilestone",
    "A D-ID creates no Milestone allocation or execution obligation by itself",
    "no Milestone must implement the whole Decision",
)
DECISION_LINK_CONTROLS = (
    "`Decision.md` lists `DecisionLog.md` and its current direct consumer artifacts as downstream",
    "Downstream artifacts link an applicable D-ID without copying its ruling",
)
WRITE_DESIGN_RESEARCH_CONTROLS = (
    "The primary orchestrator derives one bounded research scope",
    "every semantic revision of the Design-stage Bundle require",
    "before drafting or editing any Design-stage artifact",
    "neither\ndelta size nor an already-clear problem waives it",
    "A meaning-preserving correction or mechanical change does not alter Design-owned meaning and is\noutside this trigger",
    "observable candidate and source inclusion and exclusion conditions",
    "the primary orchestrator performs\nthe bounded collection or creates one Researcher when independent or parallel collection is\nuseful.",
    "A Researcher brief authorizes discovery of up to three credible candidates",
    "whether a candidate or source enters the collection set only by those conditions",
    "The primary orchestrator aggregates collected evidence, compares only what can change the\ndecision, and selects the Design-owned solution",
    "inspect source code and tests relevant to the current problem at an\nexplicitly checked upstream release, version, or commit",
    "keep the smallest closed code slice",
    "exact reuse boundary at the smallest stable and useful file, module, or symbol granularity",
    "The bounded external research for the initial creation or current semantic revision is\n   complete",
    "Before editing that semantic delta, complete its bounded external research under External\n   solution research",
)
IN_SCOPE_REPAIR_CONTROLS = {
    Path("skills/gmgn/SKILL.md"): (
        "An omitted stage-owned decision required by an accepted finding remains a repair in the same\n"
        "batch.",
        "Only a change to accepted or upstream authority or a material expansion of the prepared\n"
        "objective or write boundary creates a separately scoped batch.",
        "An omitted stage-owned decision required by that finding remains a repair in the same Author dispatch.",
        "It becomes a new semantic batch\n"
        "only when accepted or upstream authority changes or the prepared objective or write boundary\n"
        "materially expands.",
    ),
    WRITE_DESIGN: (
        "A Design-owned\ndecision omitted from the fixed candidate but required by that finding remains a repair by that\n"
        "Author in the same batch",
        "Adding or changing Design-owned meaning alone does not create\na new semantic batch or restart the current research cycle.",
        "Only a change to accepted or\nupstream authority or a material expansion of the prepared objective or write boundary enters\nControlled revision as a new batch.",
        "It opens a new batch only when it changes accepted or upstream authority or materially\n"
        "   expands the prepared objective or write boundary",
    ),
}
IN_SCOPE_REPAIR_CONTRADICTIONS = {
    Path("skills/gmgn/SKILL.md"): (
        "A fix that introduces new meaning or widens the write boundary is a separately scoped case",
        "A change that invents new meaning is a new semantic case owned by its stage",
    ),
    WRITE_DESIGN: (
        "If a fix must invent or change Design-owned meaning, it is a new semantic case under Controlled revision",
    ),
}
RELEASE_VERIFIER_TRIGGER_CONTROLS = (
    "The `trigger` must exactly match a member of that policy's `verifier.triggers` list",
)
VERIFIER_TRIGGER_FALLBACK_MARKERS = {
    Path("GMGN.md"): (
        "installation, startup,\nnon-machine-checkable artifacts, or another recorded risk may still require one",
    ),
    Path("README.md"): (
        "| Risk-triggered final verification | Installation, startup, E2E, external environments, or artifacts not fully machine-checkable |",
    ),
    Path("README.zh-CN.md"): (
        "| 风险触发的最终验证 | 安装、启动、E2E、外部环境或无法完全机检的制品 |",
    ),
    RELEASE: ("Dispatch one fresh Verifier only for a recorded trigger such as:",),
}


def read(relative: Path | str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"缺少文件: {relative}")
    return path.read_text(encoding="utf-8")


def normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def active_markdown(text: str) -> str:
    without_comments = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return re.sub(
        r"(?ms)^[ \t]*(`{3,}|~{3,})[^\n]*\n.*?^[ \t]*\1[ \t]*$",
        "",
        without_comments,
    )


def require_fragments(
    text: str, fragments: tuple[str, ...], label: str, errors: list[str]
) -> None:
    haystack = normalized(text)
    missing = [fragment for fragment in fragments if normalized(fragment) not in haystack]
    if missing:
        errors.append(f"{label}: 缺少 {missing}")


def require_active_fragments(
    text: str, fragments: tuple[str, ...], label: str, errors: list[str]
) -> None:
    require_fragments(active_markdown(text), fragments, label, errors)


def active_policy_files() -> tuple[Path, ...]:
    paths: set[Path] = set()
    for pattern in (
        "GMGN.md",
        "README*.md",
        "skills/**/*.md",
        "skills/**/*.yaml",
        "skills/**/*.json",
        "agents/*.md",
        ".codex/agents/*.toml",
    ):
        for path in ROOT.glob(pattern):
            relative = path.relative_to(ROOT)
            if "archive" not in {part.casefold() for part in relative.parts}:
                paths.add(relative)
    return tuple(sorted(paths))


def frontmatter(relative: Path) -> dict[str, str]:
    match = re.match(r"\A---\n(.*?)\n---(?:\n|\Z)", read(relative), re.S)
    if not match:
        raise AssertionError(f"{relative}: frontmatter 缺失")
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            raise AssertionError(f"{relative}: frontmatter 行无冒号")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"')
    return fields


def validate_release(errors: list[str]) -> None:
    try:
        release_metadata(ROOT)
    except ValueError as exc:
        errors.append(f"发布版本门禁失败: {exc}")
    try:
        validate_normative_layout(ROOT)
    except ValueError as exc:
        errors.append(str(exc))


def validate_skill_layout(errors: list[str]) -> None:
    actual = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
    if actual != SKILLS:
        errors.append(
            f"skill 集合不一致: expected={sorted(SKILLS)}, actual={sorted(actual)}"
        )
    for name in sorted(SKILLS):
        relative = Path("skills") / name / "SKILL.md"
        try:
            fields = frontmatter(relative)
            if fields.get("name") != name:
                errors.append(f"{relative}: name 必须等于目录名 {name}")
            if not fields.get("description"):
                errors.append(f"{relative}: description 缺失")
            extra = sorted(set(fields) - {"name", "description"})
            if extra:
                errors.append(f"{relative}: frontmatter 多出 {extra}")
            if len(read(relative).splitlines()) > 500:
                errors.append(f"{relative}: 超过 500 行")
            agent = relative.parent / "agents/openai.yaml"
            if not (ROOT / agent).is_file():
                errors.append(f"{agent}: 缺失")
        except AssertionError as exc:
            errors.append(str(exc))


def validate_shared_surfaces(errors: list[str]) -> None:
    for relative in sorted(CANONICAL_REFERENCES):
        if not (ROOT / relative).is_file():
            errors.append(f"{relative}: 共享规则文件缺失")

    policy_files = active_policy_files()
    writing_rules = read(WRITING_RULES)
    write_decision = read(WRITE_DECISION)
    write_task = read("skills/write-task/SKILL.md")
    dispatch_contract = read(DISPATCH_CONTRACT)
    require_fragments(
        writing_rules,
        (
            TASK_HEADER,
            *LATEST_EVENT_VALUES,
            *GIT_LOG_CONTROLS,
            *MILESTONE_REOPEN_CONTROLS,
            *DECISION_LINK_CONTROLS,
        ),
        "writing-rules 机器字段",
        errors,
    )
    require_active_fragments(
        writing_rules,
        DECISION_CONSUMPTION_CONTROLS,
        "Decision 下游消费边界",
        errors,
    )
    require_active_fragments(
        write_decision,
        DECISION_SCOPE_CONTROLS,
        "write-decision 决议范围",
        errors,
    )
    require_fragments(write_task, (TASK_HEADER,), "write-task 表头", errors)
    for relative, controls in COMMANDER_RUNNER_SURFACE_CONTROLS.items():
        require_active_fragments(
            read(relative), controls, "Commander/Runner 权威边界", errors
        )
    require_active_fragments(
        read(ROADMAP),
        ROADMAP_APPROVAL_CONTROLS,
        "ROADMAP 一次批准",
        errors,
    )
    require_active_fragments(
        read(WRITE_GOAL),
        GOAL_APPROVAL_CONTROLS,
        "Goal 合并批准",
        errors,
    )
    require_active_fragments(
        read(RELEASE),
        RELEASE_OPERATION_ORDER_CONTROLS,
        "release 外部操作顺序",
        errors,
    )
    require_active_fragments(
        read(WRITE_DESIGN),
        WRITE_DESIGN_RESEARCH_CONTROLS,
        "write-design 外部调研边界",
        errors,
    )
    for relative, controls in IN_SCOPE_REPAIR_CONTROLS.items():
        active_text = active_markdown(read(relative))
        require_fragments(active_text, controls, "范围内 finding 修复边界", errors)
        normalized_active_text = normalized(active_text)
        for contradiction in IN_SCOPE_REPAIR_CONTRADICTIONS[relative]:
            if normalized(contradiction) in normalized_active_text:
                errors.append(f"{relative}: 范围内 finding 修复边界含冲突规则 {contradiction}")
    require_active_fragments(
        read("skills/gmgn/SKILL.md"),
        GMGN_RUN_TASK_ROUTE_CONTROLS,
        "gmgn run-task 路由",
        errors,
    )

    if (ROOT / "skills/gmgn/references/en/writing-contract.md").exists():
        errors.append("旧 writing-contract.md 不应恢复")
    for relative in policy_files:
        text = read(relative)
        active_text = active_markdown(text)
        normalized_active_text = normalized(active_text)
        if LEGACY_ROLE in text.casefold():
            errors.append(f"{relative}: 含已删除角色词")
        if OLD_TASK_HEADER in text:
            errors.append(f"{relative}: 含旧 Task 表头")
        if "writing-contract.md" in text.casefold():
            errors.append(f"{relative}: 引用旧 writing-contract.md")
        if relative != WRITING_RULES:
            copied = [value for value in LATEST_EVENT_VALUES if value in text]
            if copied:
                errors.append(f"{relative}: 复制了 writing-rules 的 latest_event 值 {copied}")
        for legacy in ("review_policy: single-pass", "gmgn-assurance-v1"):
            if legacy in text:
                errors.append(f"{relative}: 含旧审查策略 {legacy}")
        for obsolete_review in (
            "review_mode: full",
            "review_mode: delta",
            "at most two Review rounds",
            "second Review round",
            "fresh delta Review",
            "full and delta review",
        ):
            if obsolete_review.casefold() in active_text.casefold():
                errors.append(f"{relative}: 含已废止多轮审查规则 {obsolete_review}")
        for obsolete in (
            "A closed foundation remains closed.",
            "Only explicit acceptance authorizes integrating",
            "rulings that constrain multiple Milestones and are not already",
            "Do not absorb WhitePaper meaning, ROADMAP allocation",
            "no current material cross-Milestone ruling",
            "One return ends the agent",
            "owner confirms the execution set",
            "one material allocation question at a time",
            "Local installation is a separate authorized operation",
            "Researcher** distinguishes direct observation, sourced fact, and inference",
        ):
            if obsolete in active_text:
                errors.append(f"{relative}: 含已废止规则 {obsolete}")
        for contradiction in CONTRADICTORY_POLICY_MARKERS:
            if contradiction.casefold() in active_text.casefold():
                errors.append(f"{relative}: 含冲突规则 {contradiction}")
        for markers in CONTRADICTORY_DESIGN_TDD_EXCEPTION_MARKERS:
            if all(normalized(marker) in normalized_active_text for marker in markers):
                errors.append(f"{relative}: 含 Design/TDD 冲突例外 {list(markers)}")


def validate_assurance_policy(errors: list[str]) -> None:
    try:
        policy = json.loads(read(ASSURANCE_POLICY))
    except (AssertionError, json.JSONDecodeError) as exc:
        errors.append(f"{ASSURANCE_POLICY}: JSON 无效 ({exc})")
        return
    if not isinstance(policy, dict):
        errors.append(f"{ASSURANCE_POLICY}: 顶层必须是对象")
        return
    expected_keys = {"schema_version", "policy_id", "verifier"}
    if set(policy) != expected_keys:
        errors.append(
            f"{ASSURANCE_POLICY}: 顶层字段应为 {sorted(expected_keys)}"
        )
    if policy.get("schema_version") != "gmgn.assurance-policy.v3":
        errors.append(f"{ASSURANCE_POLICY}: schema_version 无效")
    if policy.get("policy_id") != "gmgn-assurance-v3":
        errors.append(f"{ASSURANCE_POLICY}: policy_id 无效")

    verifier = policy.get("verifier")
    if not isinstance(verifier, dict) or verifier.get("default") is not False:
        errors.append(f"{ASSURANCE_POLICY}: Verifier 必须默认关闭")
        return
    if verifier.get("candidate") != "blocker-resolved-final":
        errors.append(f"{ASSURANCE_POLICY}: Verifier candidate 无效")
    if verifier.get("classification") != {
        "not_required": "not-required",
        "required_prefix": "required:",
    }:
        errors.append(f"{ASSURANCE_POLICY}: Verifier classification 无效")
    if verifier.get("triggers") != VERIFIER_TRIGGERS:
        errors.append(f"{ASSURANCE_POLICY}: Verifier triggers 必须等于 {VERIFIER_TRIGGERS}")


def validate_verifier_trigger_authority(errors: list[str]) -> None:
    release = active_markdown(read(RELEASE))
    require_fragments(
        release,
        RELEASE_VERIFIER_TRIGGER_CONTROLS,
        "release Verifier trigger 权威",
        errors,
    )
    copied = [trigger for trigger in VERIFIER_TRIGGERS if trigger in release]
    if copied:
        errors.append(f"{RELEASE}: 不得复制 Verifier trigger {copied}")
    for relative, markers in VERIFIER_TRIGGER_FALLBACK_MARKERS.items():
        active_text = active_markdown(read(relative))
        for marker in markers:
            if marker in active_text:
                errors.append(f"{relative}: 含旧 Verifier 宽泛触发描述")


def validate_run_task_controls(errors: list[str]) -> None:
    run_task = read(RUN_TASK)
    require_active_fragments(run_task, RUN_TASK_CONTROLS, "run-task 关键执行控制", errors)
    require_active_fragments(
        read("skills/run-task/agents/openai.yaml"),
        (
            "Commander decide ready work",
            "one Runner execute each Task",
            "Commander directly integrate each checked final candidate",
        ),
        "run-task OpenAI 默认入口",
        errors,
    )
    for relative in active_policy_files():
        if relative == RUN_TASK:
            continue
        text = read(relative).casefold()
        copied = [
            marker
            for marker in RUN_TASK_EXCLUSIVE_MARKERS
            if marker.casefold() in text
        ]
        if copied:
            errors.append(f"{relative}: 复制了 run-task 专属规则 {copied}")

    install_commands = (
        "codex plugin marketplace add DietrichGebert/ponytail",
        "codex plugin add ponytail@ponytail",
        "claude plugin marketplace add DietrichGebert/ponytail",
        "claude plugin install ponytail@ponytail --scope user",
    )
    for relative in (Path("README.md"), Path("README.zh-CN.md")):
        require_fragments(read(relative), install_commands, f"{relative} Ponytail 安装", errors)


def validate_roles(errors: list[str]) -> None:
    actual_markdown = {path.stem for path in (ROOT / "agents").glob("*.md")}
    actual_toml = {path.stem for path in (ROOT / ".codex/agents").glob("*.toml")}
    if actual_markdown != ROLES:
        errors.append(
            f"Claude 角色集合不一致: expected={sorted(ROLES)}, "
            f"actual={sorted(actual_markdown)}"
        )
    expected_toml = set(CODEX_AGENT_NAMES.values())
    if actual_toml != expected_toml:
        errors.append(
            f"Codex 角色集合不一致: expected={sorted(expected_toml)}, "
            f"actual={sorted(actual_toml)}"
        )
    for role in sorted(ROLES):
        markdown = Path("agents") / f"{role}.md"
        toml_path = Path(".codex/agents") / f"{CODEX_AGENT_NAMES[role]}.toml"
        try:
            fields = frontmatter(markdown)
            text = read(markdown)
            if fields.get("name") != role:
                errors.append(f"{markdown}: name 不一致")
            if len(text.splitlines()) > 80:
                errors.append(f"{markdown}: 超过 80 行")
            require_fragments(
                text, ("prepared", "brief"), str(markdown), errors
            )
            try:
                config = tomllib.loads(read(toml_path))
            except tomllib.TOMLDecodeError as exc:
                errors.append(f"{toml_path}: TOML 无效 ({exc})")
                continue
            required_keys = {
                "name",
                "description",
                "model",
                "model_reasoning_effort",
                "sandbox_mode",
                "developer_instructions",
            }
            expected_keys = required_keys | (set() if role in SPAWNING_ROLES else {"agents"})
            if set(config) != expected_keys:
                errors.append(
                    f"{toml_path}: 字段应为 {sorted(expected_keys)}，实际 {sorted(config)}"
                )
            for key in required_keys:
                if not isinstance(config.get(key), str):
                    errors.append(f"{toml_path}: {key} 必须是字符串")
            if config.get("name") != CODEX_AGENT_NAMES[role]:
                errors.append(f"{toml_path}: name 应为 {CODEX_AGENT_NAMES[role]}")
            expected_model, expected_effort = ROLE_RUNTIME[role]
            if config.get("model") != expected_model:
                errors.append(f"{toml_path}: model 应为 {expected_model}")
            if config.get("model_reasoning_effort") != expected_effort:
                errors.append(
                    f"{toml_path}: model_reasoning_effort 应为 {expected_effort}"
                )
            if config.get("sandbox_mode") != ROLE_SANDBOX[role]:
                errors.append(
                    f"{toml_path}: sandbox_mode 应为 {ROLE_SANDBOX[role]}"
                )
            if role in SPAWNING_ROLES:
                if "agents" in config:
                    errors.append(f"{toml_path}: 不应覆盖 [agents]，沿用父 Session 与平台配置")
            elif config.get("agents") != {"enabled": False}:
                errors.append(f"{toml_path}: [agents].enabled 必须为 false")
            instructions = config.get("developer_instructions", "")
            if isinstance(instructions, str) and "任务书" not in instructions:
                errors.append(f"{toml_path}: 缺少任务书边界")
            if isinstance(instructions, str):
                require_fragments(
                    instructions,
                    ROLE_PROFILE_CONTROLS[role],
                    f"{toml_path}: 角色边界",
                    errors,
                )
        except AssertionError as exc:
            errors.append(str(exc))


def validate_docstar_adapter(errors: list[str]) -> None:
    relative = Path(".docstar/conventions/conventions.json")
    try:
        config = json.loads(read(relative))
    except (AssertionError, json.JSONDecodeError) as exc:
        errors.append(f"{relative}: JSON 无效 ({exc})")
        return
    if config.get("task_columns") != {
        "spec": "spec anchor",
        "prereq": "prerequisite",
        "status": "status",
        "execution": "execution",
    }:
        errors.append("DocStar task_columns 无效")
    if config.get("task_execution") != {
        "card_fields": {"execution_log": ["execution_log"]},
        "log_fields": {"latest_event": ["latest_event"]},
        "canonical_task_table_only": True,
    }:
        errors.append("DocStar task_execution 无效")
    if config.get("archive_globs") != ["[Aa]rchive"]:
        errors.append("DocStar archive_globs 无效")
    if config.get("namespaces", {}).get("kind_namespace", {}).get("决议") != "Decision":
        errors.append("DocStar D-ID namespace 无效")
    if config.get("def_forms", {}).get("决议") != r"^-\s*\*\*(D-\d{3})\*\*":
        errors.append("DocStar D-ID 定义格式无效")
    decision_kind = [
        "决议",
        r"(?<![A-Za-z0-9_])D-\d{3}(?![A-Za-z0-9_-])",
        "GMGN decision ID D-NNN",
    ]
    if decision_kind not in config.get("doc_id_kinds", []):
        errors.append("DocStar 未识别 D-ID")
    if "决议" not in config.get("uncovered_kind_exclusions", []):
        errors.append("DocStar 决议覆盖规则无效")


def validate_relative_links(errors: list[str]) -> None:
    try:
        config = json.loads(read(".docstar/conventions/conventions.json"))
    except (AssertionError, json.JSONDecodeError):
        return
    archive_globs = config.get("archive_globs")
    if not isinstance(archive_globs, list) or not archive_globs:
        return

    def is_archived(relative: Path) -> bool:
        return any(
            fnmatchcase(part, pattern)
            for part in relative.parts
            for pattern in archive_globs
        )

    link_pattern = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
    root = ROOT.resolve()
    for path in sorted(ROOT.rglob("*.md")):
        relative = path.relative_to(ROOT)
        if any(part in {".git", "dist"} for part in relative.parts) or is_archived(relative):
            continue
        visible: list[str] = []
        fenced = False
        for line in path.read_text(encoding="utf-8").splitlines():
            if re.match(r"^\s*(```|~~~)", line):
                fenced = not fenced
                continue
            if not fenced:
                visible.append(re.sub(r"`[^`\n]*`", "", line))
        for target in link_pattern.findall("\n".join(visible)):
            target = target.strip().strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            file_part = unquote(target.split("#", 1)[0])
            if not file_part or "<" in file_part or ">" in file_part:
                continue
            resolved = (path.parent / file_part).resolve()
            try:
                target_relative = resolved.relative_to(root)
            except ValueError:
                errors.append(f"{relative}: 链接越出仓库 {target}")
                continue
            if is_archived(target_relative):
                errors.append(f"{relative}: 活动文档不得引用 archive 文档 {target}")
            elif not resolved.exists():
                errors.append(f"{relative}: 链接目标不存在 {target}")
            elif path.name == "SKILL.md" and path.parent.parent == ROOT / "skills":
                try:
                    resolved.relative_to(path.parent.resolve())
                except ValueError:
                    errors.append(f"{relative}: Skill 运行时链接越出自身目录 {target}")


def main() -> int:
    errors: list[str] = []
    validate_release(errors)
    validate_skill_layout(errors)
    validate_shared_surfaces(errors)
    validate_assurance_policy(errors)
    validate_verifier_trigger_authority(errors)
    validate_run_task_controls(errors)
    validate_roles(errors)
    validate_docstar_adapter(errors)
    validate_relative_links(errors)
    if errors:
        print("GMGN 校验失败:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("GMGN 结构与机器契约校验通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
