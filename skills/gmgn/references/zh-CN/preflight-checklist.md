---
locale: zh-CN
purpose: 在真实执行前检查问题、环境、判据、工作区与证据。
upstream: [GMGN](../../../../GMGN.zh-CN.md)
downstream: none
status: approved
type: design
nature: normative
---

# 上机前核对单

English: [../en/preflight-checklist.md](../en/preflight-checklist.md)

每个未解决项都要写证据和 owner，只打勾不算证据。

1. **问题**：本次运行只回答什么？哪些输出不支持该结论？
2. **环境**：版本、配置、数据、权限、依赖和硬件是否符合 Card 假设？
3. **测量**：测试、时钟、mock、日志、fixture 和判定脚本对本问题是否可信？
4. **结果分类**：成功、失败、超时、数据缺失和中断能否明确分类？
5. **工作区**：仓库根和 HEAD 是否匹配已准备 brief；允许写入范围是否明确？
6. **并发**：本任务是否只有一个 writer；是否与已声明的共享资源约束发生碰撞？
7. **证据落点**：命令、结果、限制和副作用将记录到单卡 Log 的哪里？

未解决 blocker 不得启动。非阻塞跟进项必须有 owner 和落点。
