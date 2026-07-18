---
locale: en
purpose: Unify incremental code-review scope and finding format across Codex, Claude Code, and read-only reviewers.
upstream: [coder brief](coder-brief.md), [dispatch and handoff](dispatch-and-handoff.md)
downstream: [pre-merge checklist](pre-merge-checklist.md)
status: approved
type: task
nature: normative
---

# Code review: native entry and shared checks

中文版本：[../zh-CN/code-review.md](../zh-CN/code-review.md)

## 1. Select the surface

- Codex Desktop: `/review`.
- Codex CLI: `codex review --uncommitted`, `--commit <sha>`, or `--base <branch>`;
  do not combine a scope flag with a custom prompt.
- Claude Code: an independent read-only reviewer; use `/code-review` only when the user
  has authorized work on a GitHub PR.
- If the native surface is unavailable, dispatch a read-only reviewer; do not skip review.

## 2. Review surface

1. Does the task-card diff satisfy its spec anchor?
2. Which outputs, error paths, no-baseline branches, and sibling call paths lack assertions?
3. Can each changed test fail when the implementation is wrong? Mutate only in isolation.
4. Did the change weaken boundary validation, security, data protection, performance, or accessibility?
5. Complexity labels: `delete | stdlib | native | empty abstraction | shrink`.

Report findings and do not modify the reviewed worktree. Each finding contains
`location · evidence · impact · normative fix · priority`. End with `git status --short`
and disclose review-generated caches or side effects.
