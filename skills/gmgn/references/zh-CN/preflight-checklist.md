---
locale: zh-CN
purpose: 在真实环境运行或依据运行结果做决策前检查对象、环境、装置、判据与运行管理。
upstream: [GMGN §8](../../../../GMGN.zh-CN.md)
downstream: none
status: approved
type: design
nature: normative
---

# 上机前核对单

English: [../en/preflight-checklist.md](../en/preflight-checklist.md)

对每问写 `answer | evidence | owner | unresolved`，不能只打勾。

1. **问题**：本次运行唯一要回答什么？什么输出不支持该结论？
2. **环境实体性**：版本、配置、数据、权限、依赖和硬件真实状态与假设一致吗？
3. **表征—实体对齐**：每个“已修复/已选择/已部署”能指到真实落点吗？
4. **装置忠实性**：测试、采样、时钟、mock、日志和判定脚本自身被校准或用已知样本验证了吗？
5. **判据完备性**：成功、失败、超时、数据缺失和中途中断能自动判死吗？
6. **无人值守韧性**：挂起、静默失败、资源耗尽时如何报警、恢复和保留证据？
7. **工作区与锁**：`git rev-parse --show-toplevel` 是否等于当前派发的绝对 `worktree_path`；
   `workspace_mode`、`branch_ref` 是否准确；本 lane 的 `write_set`、`conflict_domains`、
   `runtime_locks` 是否与所有 active lane 兼容？

未解决 blocker 不得启动；非 blocker 必须写 owner 和跟进点。
