---
locale: en
purpose: Check integration, verification strength, claim truth, tool degradation, and complexity before parallel output enters a shared baseline.
upstream: [code review](code-review.md)
downstream: none
status: approved
type: design
nature: normative
---

# Template: pre-merge checklist

中文版本：[../zh-CN/pre-merge-checklist.md](../zh-CN/pre-merge-checklist.md)

1. **Integration completeness** — Is the impact larger than the file diff; are interfaces, callers, migrations, and docs covered?
2. **No verification downgrade** — Were tests removed, assertions weakened, errors swallowed, or real paths bypassed?
3. **Claim–disk alignment** — Do completion state, files, test output, and the Git diff agree?
4. **Operation–shape fit** — How do commands degrade for paths, empty/large sets, duplicate names, and failure codes?
5. **Name and number provenance** — Do mechanism names and key numbers point to Requirement, Design, or Decision authorities?
6. **Overdesign scan** — Check `delete | stdlib | native | empty abstraction | shrink` separately.

Replay relevant commands, run `git diff --check` and `git status --short`, then let the
primary orchestrator merge.
