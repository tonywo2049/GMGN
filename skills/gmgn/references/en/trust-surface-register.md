---
locale: en
purpose: Record each input acceptance point's trusted source, validation, failure behavior, and evidence during design.
upstream: [GMGN §8](../../../../GMGN.md)
downstream: [pre-close checklist](pre-close-checklist.md)
status: approved
type: design
nature: normative
---

# Template: trust-surface register

中文版本：[../zh-CN/trust-surface-register.md](../zh-CN/trust-surface-register.md)

Complete this when adding an external input, cache restore, migration import, permission
boundary, human entry, or model-output acceptance point. Embed it in the relevant Design or Decision.

```markdown
| acceptance point | input | source authority | validation | failure behavior | negative evidence | owner |
|---|---|---|---|---|---|---|
| <module:function> | <data> | <who/what may assert it> | <checks> | <reject/fallback/alert> | <test or command> | <role> |
```

Name the real authority; “validated upstream” is not a source. Validation covers type,
range, timing, identity, and freshness as applicable. Failure is observable; silent discard
is not success. Before closure, replay each negative-evidence row and confirm the owner.
