---
locale: zh-CN
purpose: 提供只追加的决议记录模板，固定裁决、理由、条件与下游传导。
upstream: [GMGN §2](../../../../GMGN.zh-CN.md)
downstream: none
status: approved
type: decision
nature: normative
---

# 模板：决议记录

English: [../en/decision-log.md](../en/decision-log.md)

```markdown
---
locale: zh-CN
purpose: 记录 <范围> 的权威裁决及传导。
upstream: [<触发材料>](<path>)
downstream: [<被修改的权威文档>](<path>)
status: approved
type: decision
nature: normative
---

# <范围> Decision Log

## D1 — <一句话主题>
- Trigger: <问题与版本锚>
- Decision: <明确采用/拒绝什么>
- Rationale: <证据与权衡>
- Conditions: <附带条件或 none>
- Propagation: <文件、节、ID、状态>
- Owner: <裁决者>
- Version anchor: <commit/hash>
```

后续裁决新增 `D2`，不改写 `D1`；推翻旧裁决时在新条目引用旧 ID，并在旧条目加 superseded 指针。
