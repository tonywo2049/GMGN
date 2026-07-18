---
locale: zh-CN
purpose: 在设计时登记每个输入受理点信任的来源、校验、失败行为和证据。
upstream: [GMGN §8](../../../../GMGN.zh-CN.md)
downstream: [关账前核对单](pre-close-checklist.md)
status: approved
type: design
nature: normative
---

# 模板：信任面登记表

English: [../en/trust-surface-register.md](../en/trust-surface-register.md)

在新增外部输入、缓存恢复、迁移导入、权限边界、人工录入或模型输出受理点时填写，并嵌入对应 Design/Decision。

```markdown
| acceptance point | input | source authority | validation | failure behavior | negative evidence | owner |
|---|---|---|---|---|---|---|
| <module:function> | <data> | <who/what may assert it> | <checks> | <reject/fallback/alert> | <test or command> | <role> |
```

来源写真实权威，不写“上游已校验”。校验要说明类型、范围、时序、身份与新鲜度。失败行为必须可观察；
不能把静默吞掉当成功。关账前逐行重放负向证据并确认 owner 仍有效。
