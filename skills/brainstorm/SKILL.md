---
name: brainstorm
description: "Use when a WhitePaper does not exist, needs a major rethink, or an approved WhitePaper needs a controlled semantic revision to its problem, goals, scope, harm order, invariants, or interpretation. Also covers a new idea, product concept, problem, opportunity, vague requirement, research request, feasibility study, brainstorm, or starting a direction. 需求澄清入口：新想法、产品构思、待解决问题、新机会、模糊需求、调研、可行性研究、脑暴/头脑风暴，以及已批准白皮书的问题、目标、范围、损害排序、不变量或理解需要受控语义修订；不改变语义的机械小修或纯闲聊不触发。"
---

# Brainstorm → WhitePaper

<HARD-GATE>In creation mode, do not enter `roadmap`, create execution documents, or write implementation code before an independent critic reviews the WhitePaper and the owner approves a version anchor. In revision mode, pause only dependent work whose premise changed until the owner approves the semantic delta at a new anchor. “The project is simple” is not a bypass.</HARD-GATE>

## Language and contract

Use the active project/user locale. Load the matching layout-free
[English](../gmgn/references/en/writing-contract.md) or
[中文](../gmgn/references/zh-CN/writing-contract.md) contract. The WhitePaper uses
`type: whitepaper`, `nature: normative`, and stable English frontmatter tokens.

## Working rhythm

The primary orchestrator stays in the owner dialogue, asks one question at a time, records
rulings, and challenges premature implementation or solutions disguised as requirements.
Before writing, it selects and records the actual WhitePaper writer. Prefer the primary
session because it already holds the complete Brainstorm context; delegate to an Author only
when a bounded context package and a concrete isolation, specialization, or parallelism
benefit outweigh the handoff cost. A delegated Author or Researcher receives a complete
brief before creation and is single-use. Dispatch an independent fresh Critic only after
anchoring the candidate.

Use as needed:

- repository and user evidence;
- primary-source research for unstable or specialized claims;
- small experiments where argument cannot resolve feasibility.

## Required WhitePaper content

1. problem and why now;
2. users, actors, and real scenarios;
3. goals and explicitly ordered harms;
4. top-level invariants;
5. non-goals and scope boundary;
6. major options, evidence, unknowns, and rejected directions;
7. qualitative validation direction and remaining material risks, or an explicit statement
   that none are known.

Do not introduce R-AC IDs or quantitative requirement criteria here.

## Writer and critic loop

1. Resolve material problem, scope, and harm-order questions with the owner. Then select the
   writer. The primary session normally writes directly from the dialogue; if delegation has
   real value, prepare the complete brief before creating one fresh Author.
2. The writer self-checks completeness, scope, placeholders, and contradictions, then freezes
   one candidate. A delegated Author ends after its return.
3. Prepare one brief and create one fresh independent Critic. Collect its full review before
   editing. The primary orchestrator adjudicates once and applies accepted findings directly
   or uses a fresh Author. Only a changed semantic surface gets a fresh Critic recheck.
4. With no blocker, present the anchored candidate and remaining material risks—or that none
   are known—to the owner. After approval, apply mechanical links and state, then run machine
   checks.

## Revision mode

An approved WhitePaper revision handles the change delta; it is not a new brainstorm for the
whole project.

1. Start from the approved old anchor and state the trigger, proposed semantic delta, and
   impact cone.
2. Edit only the WhitePaper sections that are authoritative for the changed meaning. Preserve
   unaffected conclusions and prior decision history.
3. Scope research and independent criticism to the delta plus the minimum context needed to
   falsify it.
4. Have the owner approve the semantic delta at a new version anchor. The old approval remains
   attached to the old anchor.
5. Propagate only to affected ROADMAP or G-R-D-T content, then return to the stage that raised
   the change. Do not rerun unaffected stages.

Meaning-preserving renames, moves, links, formatting, hashes, and status mirrors are
mechanical changes: refresh them in the same batch and run machine checks without entering
revision mode or seeking reapproval.

## Exit

Bind owner approval to a commit or hash. In creation mode, complete any
workspace-topology-required integration and
use **REQUIRED next skill: `roadmap`**. In revision mode, commit, propagate the approved delta
through its impact cone, and return to the stage that raised the change rather than restarting
the full chain.

Before every substantive return, perform a task-specific self-check and correct defects. Do
not output a fixed `Reflection` section. Disclose only material unresolved risks that could
change the conclusion, decision, acceptance, or downstream work; otherwise omit the
disclosure. Approval, acceptance, and closure always state remaining material risks or that
none are known.
