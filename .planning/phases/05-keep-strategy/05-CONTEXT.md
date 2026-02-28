# Phase 5: Keep Strategy - Context

**Gathered:** 2026-03-01
**Status:** Ready for planning

## Phase Boundary

根据修改时间决定保留哪个重复文件（保留最新的），并明确标识哪些文件将被删除。

## Implementation Decisions

### 保留规则
- 对于相同哈希的文件组，保留 `mtime`（修改时间）最新的文件
- `mtime` 相同时保留 `path` 较短的文件（更一致的路径）
- 保留的文件标记为 `keep`，其他标记为 `delete`

### 输出数据结构
- 返回 `Group` 类：包含 hash、keep_file、delete_files
- `Group` 包含方法：`get_keep_file()`, `get_delete_files()`

### Claude's Discretion
- 冲突处理：mtime 相同时的选择逻辑
- 删除前确认：是否需要用户确认（但需求中已明确按时间保留）

---

*Phase: 05-keep-strategy*
*Context gathered: 2026-03-01*
