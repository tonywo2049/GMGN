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
Dispatch a Researcher for scoped evidence and an Author for the WhitePaper; the orchestrator
does not write the artifact.

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
7. qualitative validation direction and weakest assumption.

Do not introduce R-AC IDs or quantitative requirement criteria here.

## Author and critic loop

1. Enter `awaiting-owner-input` while a material problem, scope, or harm-order decision is
   missing. Once inputs are sufficient, create the node record and enter `ready-to-dispatch`.
2. `author-active`: dispatch one Author with the evidence, owner rulings, required content
   above, allowed paths, baseline anchor, and self-check. Record `author_ref`.
3. `author-returned`: check only return completeness, scope, and forbidden changes. Send an
   incomplete return to the same Author as `author-rework`. Otherwise enter `candidate-anchored`.
4. `critic-active`: dispatch an independent Critic against that anchor and minimum context.
   The Critic reports to the orchestrator and does not edit the WhitePaper.
5. At `critic-returned`, adjudicate findings. Resume the same `author_ref` in
   `author-revising`; send blocker fixes to the same `critic_ref` in `critic-rechecking`.
6. With no blocker, enter `acceptance-ready`, present the anchored candidate and weakest
   assumption to the owner, then use an Integrator for accepted mechanical links, state, and
   commit material. Finish at `node-complete` only after those representations agree.

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

Require the Author to self-check placeholders, contradictions, scope gaps, and ambiguity.
Run the identity-preserving loop above using the locale-matched dispatch contract; adjudicate
findings without letting the Critic expand scope. Bind owner approval to a commit or hash. In
creation mode, integrate and use **REQUIRED next skill: `roadmap`**. In
revision mode, commit, propagate the approved delta through its impact cone, and return to
the stage that raised the change rather than restarting the full chain.

End every substantive response with **Reflection**: weakest assumption; neglected
counterexample; measured versus inferred.
