# Phase 4: Hash Engine - Context

**Gathered:** 2026-03-01
**Status:** Ready for planning

<domain>
## Phase Boundary

使用 SHA-256 算法计算文件内容哈希值，通过哈希值识别重复文件。需要高效处理大文件以避免内存问题。
</domain>

<decisions>
## Implementation Decisions

### 分块哈希策略
- 对于大于 10MB 的文件使用分块读取哈希
- 块大小：4MB（在内存安全范围内）
- 顺序读取块并更新哈希值，避免全文件加载

### 哈希算法
- 使用 Python 内置 `hashlib.sha256()`
- 二进制模式读取文件，确保跨平台一致性

### 重复检测
- 使用字典映射：hash → list[filepath, mtime]
- 每次哈希计算后立即检查是否存在重复

### 进度显示
- 显示当前正在哈希的文件名和进度百分比
- 格式与扫描器保持一致：`[███░░] XX%`

### Claude's Discretion
- 分块阈值选择：10MB vs 50MB vs 100MB
- 哈希缓存：是否需要内存缓存哈希值以加速重复检测
- 并行哈希计算：是否使用多线程加速

</decisions>

<specifics>
## Specific Ideas

- Existing code: CLI in src/mac_dedup/cli.py, Scanner in src/mac_dedup/scanner.py, FileType in src/mac_dedup/file_type.py
- Click library already available in pyproject.toml
- Project follows type hints, docstrings, and error handling patterns

</specifics>

<deferred>
## Deferred Ideas

- 并行哈希计算（多线程优化）
- 持久化哈希缓存（Phase 7）
- 增量哈希计算（仅哈希新文件）

</deferred>

---
*Phase: 04-hash-engine*
*Context gathered: 2026-03-01*
