---
locale: en
purpose: Provide an append-only decision template that fixes rulings, rationale, conditions, and downstream propagation.
upstream: [GMGN §2](../../../../GMGN.md)
downstream: none
status: approved
type: decision
nature: normative
---

# Template: decision log

中文版本：[../zh-CN/decision-log.md](../zh-CN/decision-log.md)

```markdown
---
locale: en
purpose: Record authoritative decisions and propagation for <scope>.
upstream: [<trigger material>](<path>)
downstream: [<changed authority>](<path>)
status: approved
type: decision
nature: normative
---

# <scope> Decision Log

## D1 — <one-line subject>
- Trigger: <problem and version anchor>
- Decision: <what is explicitly adopted or rejected>
- Rationale: <evidence and trade-off>
- Conditions: <conditions or none>
- Propagation: <files, sections, IDs, states>
- Owner: <decision maker>
- Version anchor: <commit/hash>
```

Append `D2`; do not rewrite `D1`. To supersede a decision, cite the old ID in a new entry
and add a superseded pointer to the old entry.
