---
locale: zh-CN
purpose: 把采用 GMGN 前已有的跨 Milestone 需求存量一次性分配到新里程碑。
upstream: [ROADMAP skill](../../../roadmap/SKILL.md)
downstream: none
status: approved
type: research
nature: descriptive
---

# 模板：分配账本（仅存量迁移）

English: [../en/allocation-ledger.md](../en/allocation-ledger.md)

新项目不用本模板。只有采用 GMGN 前已有跨 Milestone 需求池时使用，分完即归档；新增想法走 ROADMAP 的 TODO。

```markdown
| legacy id | source | summary | target milestone | target requirement | rationale | status |
|---|---|---|---|---|---|---|
| L-1 | <path:line> | <原意> | M1 | R1 or pending | <为什么> | allocated |
```

表尾核对总数：源存量 = 已分配 + 明确拒绝 + 待裁决。任何一项不得静默消失。
