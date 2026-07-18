---
name: brainstorm
description: "Use when a WhitePaper does not exist or needs a major rethink and the user brings a new idea, product concept, problem, opportunity, vague requirement, research request, feasibility study, brainstorm, or wants to start a direction. 需求澄清入口：新想法、产品构思、待解决问题、新机会、模糊需求、调研、可行性研究、脑暴/头脑风暴；白皮书仅小修或纯闲聊不触发。"
---

# Brainstorm → WhitePaper

<HARD-GATE>Before an independent critic reviews the WhitePaper and the owner approves a version anchor, do not enter `roadmap`, create execution documents, or write implementation code. “The project is simple” is not a bypass. The only terminal route is `roadmap`.</HARD-GATE>

## Language and contract

Use the active project/user locale. Load the matching
[English](../gmgn/references/en/writing-contract.md) or
[中文](../gmgn/references/zh-CN/writing-contract.md) contract. The WhitePaper uses
`type: whitepaper`, `nature: normative`, and stable English frontmatter tokens.

## Working rhythm

Act as a thinking partner, not a stenographer. Ask one question at a time. Explore the
problem before solution details; challenge premature implementation, solutions disguised
as requirements, and claims that need research.

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

## Exit

Self-check placeholders, contradictions, scope gaps, and ambiguity. Dispatch one independent
critic with the locale-matched `critic-brief.md`; adjudicate findings without letting the
critic expand scope. Present the weakest assumption to the owner, bind approval to a commit
or hash, commit the document, then **REQUIRED next skill: `roadmap`**.

End every substantive response with **Reflection**: weakest assumption; neglected
counterexample; measured versus inferred.
