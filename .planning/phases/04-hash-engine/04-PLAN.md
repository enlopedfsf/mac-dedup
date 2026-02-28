---
wave: 1
depends_on: []
files_modified:
  - src/mac_dedup/hash_engine.py
  - tests/test_hash_engine.py
autonomous: true
---

# Plan 01: Core Hash Engine Implementation

## Objective
Implement the core hash engine module with SHA-256 hashing and chunked file reading for memory efficiency.

## Requirements
- HASH-01: 使用 SHA-256 算法计算文件内容哈希值
- HASH-03: 高效处理大文件的哈希计算（避免内存问题）

## Context
- Located at: `src/mac_dedup/hash_engine.py`
- Must integrate with existing `scanner.py` (which yields file info dicts)
- Follow project patterns: type hints, docstrings, error handling
- Use Python's built-in `hashlib` module

## Implementation Tasks

### Task 1: Create HashEngine class with chunked reading
Create the HashEngine class at `src/mac_dedup/hash_engine.py` with:
- SHA-256 hashing using hashlib.sha256()
- Chunked reading for files > 10MB with 4MB chunk size
- Binary mode file reading for cross-platform consistency
- Internal hash cache to avoid recalculating hashes
- Type hints and comprehensive docstrings

### Task 2: Implement find_duplicates() method
Add method that:
- Accepts list of file info dicts (path, size, mtime)
- Calculates hash for each file using _calculate_hash()
- Builds hash mapping: hash -> [(filepath, mtime), ...]
- Filters to only duplicates (hashes with > 1 file)
- Handles errors gracefully (continue on missing files)

### Task 3: Add progress callback support
Implement find_duplicates_with_progress() with:
- Optional progress_callback parameter
- Calls callback with percentage (0-100) during hashing
- Matches scanner's progress bar format: [███░░] XX%

### Task 4: Add cache management
Implement clear_cache() method to clear internal hash cache for processing multiple directories.

## Verification Criteria
- [ ] HashEngine class created at `src/mac_dedup/hash_engine.py`
- [ ] _calculate_hash() implements SHA-256 with chunked reading (4MB chunks, 10MB threshold)
- [ ] find_duplicates() returns dict of hash -> [(filepath, mtime), ...]
- [ ] Only duplicates (len > 1) included in results
- [ ] clear_cache() method implemented
- [ ] All methods have type hints and docstrings
- [ ] Error handling for missing files, permissions, and I/O errors

## must_haves
1. SHA-256 algorithm used via hashlib.sha256()
2. Chunked reading for files > 10MB with 4MB chunk size
3. Binary mode file reading for cross-platform consistency
4. Hash cache to avoid recalculating hashes
5. Duplicate detection via hash mapping

## Files Modified
- src/mac_dedup/hash_engine.py (new file)

## Dependencies
None (can be implemented independently)

## Notes
- No parallel hashing in this phase (deferred to future optimization)
- Hash cache is in-memory only (persisted cache deferred to Phase 7)
- Progress callback format matches scanner's progress bar style
