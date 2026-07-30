---
name: release
description: "Use after a candidate is already accepted to prepare or retry a version tag, deterministic package, checksum, GitHub/GitLab release, publication, deployment handoff, or local plugin update without repeating milestone closure. 已接受候选需要打 tag、生成发布包与校验和、创建或重试版本发布、交付部署或更新本地插件时使用；复用已绑定锚的验收证据，不重复里程碑关账。"
---

# Release an accepted commit

A release distributes an accepted candidate; it is not another acceptance cycle. Reuse
review, test, closure, and verification evidence while their content, scope, inputs, and target
environment remain unchanged.

<HARD-GATE>Require an accepted Git commit, applicable successful review evidence, disclosed
material risks, and explicit owner authorization before external writes. Human-facing release
records use the shortest unambiguous commit reference before tagging and the release tag after
tagging. A full-length commit object ID, diff/content hash, archive checksum, or artifact
checksum is never a workflow anchor; checksums are evidence only. If source behavior,
specification meaning, acceptance, scope, design intent, execution authority, dependency
behavior, packaging behavior, or target obligations changed without accepted evidence, stop
and route only that impact cone through `gmgn`.</HARD-GATE>

## Recover missing historical acceptance

Never infer an accepted commit from a historical status, tag, summary, or unbound test output.
When usable acceptance history is missing, prepare and review one current committed candidate,
run only the verification required by its risk and environment, obtain owner acceptance, and
release that commit. Do not rewrite historical closure records.

## 1. Reuse accepted evidence

Compare only inputs that can invalidate existing evidence. When reviewed content, required
test plan, target environment, and relevant package inputs are unchanged, reuse the accepted
review, regression, E2E, DocStar, closure, and verification evidence. Do not repeat independent
review when the reviewed content and every validity input are unchanged.

When the release commit differs from the accepted commit only through version manifests,
checksums, generated release metadata, or meaning-preserving links, prove that small allowed
diff and run affected machine checks. Do not request another semantic approval or full test
run. If meaning or behavior changed, return to the owning workflow instead of expanding the
release task.

Use existing commit, CI, checksum, tag, and release records as provenance. A checksum supports
artifact integrity but never replaces the accepted commit or release tag. Do not create a
separate release document or evidence tuple unless a receiver independently requires one.

## 2. Prepare the release once

For an ordinary version-only release:

1. synchronize and validate existing version declarations;
2. commit the version-only release delta;
3. run the repository's release metadata/structure checks;
4. build the artifact once from the clean release commit;
5. record its member identity and checksum.

Deterministic packaging is proved by the packaging code's own tests when that code changes; do
not rebuild every ordinary release merely to re-prove an unchanged algorithm. Do not rerun full
regression, E2E, DocStar, closure, or independent review when the accepted product content and
their validity inputs are unchanged.

Classify the committed final candidate as `not-required` or `required:<trigger>` using the current
assurance policy loaded through the registered `gmgn` Skill. A deterministic archive whose
members and bytes are fully checked by an unchanged packaging recipe is `not-required`.
Dispatch one fresh Verifier only for a recorded trigger such as:

- `artifact-not-fully-machine-checkable`;
- `installation-or-startup`;
- an external mutable environment, high-risk behavior, unavailable required Reviewer
  execution, or an explicit independent-execution requirement.

Put the classification, reason, and minimum verification plan in its brief. The Verifier runs
only that plan and stops once the trigger is decided. Missing or failed required Verifier
evidence blocks publication. A fallback satisfies verification only when it is the accepted
required path and is successfully verified.

## 3. Publish and reconcile idempotently

Before external writes, check once for a conflicting remote tag or release. After explicit
authorization, perform the smallest ordered writes required by the target. Prefer an atomic
branch-and-tag push where supported, create or complete one release, upload only the required
assets, then read the final remote state back once. Confirm the release commit, tag, asset
identity, and checksum.

If a partial matching release already exists, create only missing objects. Stop on a
conflicting tag, checksum, artifact, or target identity. Authentication, upload, or network
retry does not invalidate accepted product evidence and does not trigger another Critic,
Reviewer, full test run, or Milestone closure.

Local installation is a separate authorized operation. Reinstall only when needed, then check
the reported version and one distinguishing shipped file; state whether reload or a new
session is required.

## Exit

Return the shortest unambiguous release commit reference, published tag/release or deployment
reference, artifact checksum,
any requested installation evidence, and unresolved material risk. Release success returns to
`roadmap`; an operational retry stays in `release` with the same accepted evidence.
