---
name: release
description: "Use after a candidate is already accepted to prepare or retry a version tag, deterministic package, checksum, GitHub/GitLab release, publication, deployment handoff, or local plugin update without repeating milestone closure. 已接受候选需要打 tag、生成发布包与校验和、创建或重试版本发布、交付部署或更新本地插件时使用；复用已绑定锚的验收证据，不重复里程碑关账。"
---

# Release an accepted anchor

Use release evidence; do not recreate closure evidence. A release is distribution of an
accepted candidate, not another semantic acceptance cycle.

<HARD-GATE>Require an immutable `accepted_anchor`, its approval or acceptance reference,
the review evidence required by its scope, any required verification evidence, disclosed
remaining material risks, and explicit owner authorization for every external write. If the
proposed release contains a semantic change not covered by that evidence, stop and route only
the affected content through `gmgn`; do not publish first or repeat all closure work by
default.</HARD-GATE>

## Missing historical acceptance anchor

Never fabricate or infer `accepted_anchor` from a historical closed status, tag, prose summary,
or unanchored test output. For a repository adopted without usable history, record the current
clean commit as an adoption baseline and its missing-history limitation. That baseline is not
reusable release evidence. Prepare an immutable current candidate, run applicable review and
the verification actually required by its release scope and environment, obtain new owner acceptance,
and only then use the resulting anchor as `accepted_anchor`. Historical closed records remain
closed; this recovery creates present evidence and does not rewrite their history.

## 1. Bind reusable evidence

Record a release evidence tuple in the existing release record, Handoff, or CI provenance;
do not create a new document when an existing authority can hold it:

- `accepted_anchor` and `release_anchor`;
- approval or acceptance reference, applicable review evidence, and required verification
  evidence or an explicit `not-required` classification;
- `semantic_delta`, with `none` only when established rather than assumed;
- exact `allowed_diff` when the release anchor differs from the accepted anchor;
- packaging recipe anchor and target distribution environment.

Review evidence remains reusable while the reviewed content and review scope are unchanged.
Verification evidence remains reusable while the accepted content, required test plan, and
target execution environment are unchanged. Artifact evidence remains reusable only for the
same release anchor, packaging recipe, and artifact inputs. Accessible evidence is required;
an agent summary without the anchored commands and results is not reusable evidence.

## 2. Classify the release delta

Choose exactly one path:

1. **Exact-anchor release.** `release_anchor == accepted_anchor`. Before reuse, compare the
   reviewed content and scope, required test plan, target execution environment, and every
   other recorded evidence-validity input. Only when those inputs are unchanged, reuse the
   accepted review, regression, E2E, DocStar, and closure evidence. If an input changed,
   invalidate and regenerate only evidence that depends on it. Do not dispatch another closure Author,
   combined Critic/Reviewer, or closure Verifier unless that role's evidence was invalidated.
2. **Mechanical equivalent.** The release anchor differs only by an explicit allowlist such
   as version manifests, checksums, generated release metadata, or meaning-preserving links.
   Record old and new anchors, `semantic_delta: none`, `allowed_diff`, and
   `approval_inherited_from: <accepted_anchor>`. Prove the diff stays inside the allowlist and
   run the affected machine checks; do not request new semantic approval or full review.
3. **Semantic delta.** Source behavior, specification meaning, acceptance, scope, design
   intent, execution authority, or user-visible obligations changed. Invalidate only the
   affected review and verification evidence, route that impact cone to its authority, and
   resume release after a new accepted anchor exists.

Changing a packaging recipe, signing method, dependency lock, target platform, or deployment
configuration invalidates the corresponding artifact or environment checks. It does not by
itself invalidate unrelated semantic review or product regression evidence. When the delta's
meaning is uncertain, use the semantic path.

## 3. Verify the artifact boundary

Run only checks required by the selected path and repository policy:

- prove the worktree is clean and the release anchor is immutable and locally available;
- prove all version declarations agree and the requested tag names that version;
- build from the release anchor with the recorded packaging recipe;
- compare the artifact member allowlist and bytes to the release anchor, reject missing,
  extra, duplicate, traversing, or symlink entries, and record the checksum;
- rebuild when deterministic packaging is promised and compare bytes;
- run the installation or startup smoke path for the distributed form when applicable;
- check whether the remote tag, release, and assets already exist before writing.

Do not rerun full regression, E2E, combined review, DocStar, or closure authoring merely
because a tag, upload, authentication step, or local installation is retried. Rerun an item
only when its evidence-validity inputs changed or its earlier result is missing or failed.

## 4. Publish and reconcile idempotently

Present the release anchor, evidence references, delta classification, artifact checksum,
target, remaining material risks, and explicit owner authorization. External authorization is operation-specific: approval
to tag or publish does not imply deployment, PR mutation, notification, or local installation.

After authorization, perform the smallest ordered writes required by the target. After every
write, read the remote state back and bind it to the release anchor. If a partial release
already exists, reconcile matching objects and create only missing ones; never manufacture a
second release or repeat semantic review to recover from an operational retry. Stop on a
conflicting tag, checksum, artifact, or target identity.

For local delivery, refresh the configured marketplace or package source, reinstall only when
the platform cache requires it, verify the reported version and one distinguishing shipped
file, and state whether a new session or plugin reload is required.

## Exit

Record the published tag/release or deployment reference, artifact checksum, installed-version
evidence when requested, and any failed external operation. Release success returns to
`roadmap` for maintenance or the next Milestone; an operational retry remains in `release`
with the same reusable evidence tuple.

Before every substantive return, perform a task-specific self-check and correct defects. Do
not output a fixed `Reflection` section. Disclose only material unresolved risks that could
change the conclusion, decision, acceptance, or downstream work; otherwise omit the
disclosure. Approval, acceptance, and closure always state remaining material risks or that
none are known.
