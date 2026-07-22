---
locale: en
purpose: Check the question, environment, criteria, workspace, and evidence before real execution.
upstream: [GMGN](../../../../GMGN.md)
downstream: none
status: approved
type: design
nature: normative
---

# Preflight checklist

中文版本：[../zh-CN/preflight-checklist.md](../zh-CN/preflight-checklist.md)

For each unresolved item record its evidence and owner; a checkbox alone is not evidence.

1. **Question** — What one question does this run answer, and what output would not support
   that conclusion?
2. **Environment** — Do versions, configuration, data, permissions, dependencies, and hardware
   match the Card assumptions?
3. **Measurement** — Are tests, clocks, mocks, logs, fixtures, and judgment scripts trustworthy
   for this question?
4. **Outcomes** — Can success, failure, timeout, missing data, and interruption be classified?
5. **Workspace** — Does the repository root and HEAD match the prepared brief, and is the
   allowed write scope explicit?
6. **Concurrency** — Does this task have one writer, with no collision against any declared
   shared-resource constraint?
7. **Evidence destination** — Where will commands, results, limitations, and side effects be
   recorded in the card Log?

Do not start with an unresolved blocker. Give each non-blocking follow-up an owner and point.
