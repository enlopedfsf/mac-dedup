---
phase: 05-keep-strategy
plan: 01
type: tdd
wave: 1
depends_on: []
files_modified: [src/mac_dedup/keep_strategy.py, tests/test_keep_strategy.py, src/mac_dedup/__init__.py]
autonomous: true
requirements: [KEEP-01, KEEP-02]
user_setup: []

must_haves:
  truths:
    - Duplicate file groups are sorted by modification time (newest first)
    - When modification times are equal, file with shorter path is kept
    - Group objects clearly identify which file to keep and which to delete
    - get_keep_file() returns file path marked for preservation
    - get_delete_files() returns all other file paths in group
  artifacts:
    - KeepStrategy class in src/mac_dedup/keep_strategy.py
    - Group dataclass with hash, keep_file, delete_files fields
    - Full test coverage in tests/test_keep_strategy.py
  key_links:
    - HashEngine.find_duplicates() output -> KeepStrategy.analyze_groups() input
    - KeepStrategy output -> Safe Deletion Phase (Phase 6) input
---

<objective>
Create Keep Strategy module that intelligently determines which duplicate file to keep based on modification time and path length, with clear identification of keep/delete files.

Purpose: Implement core decision logic for duplicate file management. After Phase 4 identifies duplicates via hashing, Phase 5 must decide which version to preserve. This enables deletion phase (Phase 6) to execute safely.

Output: KeepStrategy class with Group dataclass, providing clear API for duplicate file decision making.
</objective>

<execution_context>
@/Users/apple/.claude/get-shit-done/workflows/execute-plan.md
@/Users/apple/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/phases/05-keep-strategy/05-CONTEXT.md

# Input Interface from Phase 4 (HashEngine)

From src/mac_dedup/hash_engine.py:

```python
def find_duplicates(
    self, file_infos: List[Dict[str, object]]
) -> Dict[str, List[Tuple[str, float]]]:
    """Returns dict mapping hash to list of (filepath, mtime) tuples.
    Only includes hashes with multiple files (duplicates).
    """
```

Input format example:
```python
{
    "abc123": [
        ("/Users/apple/old/file.txt", 1700000000.0),
        ("/Users/apple/new/file.txt", 1700001000.0),
        ("/var/backup/file.txt", 1699999000.0),
    ]
}
```

# Existing Code Style

From src/mac_dedup/file_type.py:
- Uses dataclasses/typing for type safety
- Docstrings with Args, Returns, Raises sections
- No external logging (TODO in hash_engine.py for Phase 6)
- Clear separation of concerns

From src/mac_dedup/hash_engine.py:
- Input validation at start of methods
- Type hints throughout
- Exception handling with meaningful messages
- Dictionary-based data structures for efficiency
</context>

<tasks>

<task type="auto">
  <name>Task 1: Write failing tests for KeepStrategy</name>
  <files>tests/test_keep_strategy.py</files>
  <behavior>
    Test 1: Basic keep decision - newest mtime wins
    Test 2: Tiebreaker - shorter path wins when mtime equal
    Test 3: Single duplicate pair - correct identification
    Test 4: Multiple files in group - correct keep/delete split
    Test 5: Empty input - returns empty list
    Test 6: Non-duplicate groups are filtered out
    Test 7: Group.get_keep_file() returns correct path
    Test 8: Group.get_delete_files() returns all except keep
    Test 9: Path comparison is case-sensitive on macOS
    Test 10: Mtime comparison uses float precision
  </behavior>
  <action>
    Create tests/test_keep_strategy.py with the following test cases:

    1. test_keep_newest_mtime():
       Input: Group with 3 files, mtime 1000, 2000, 1500
       Expected: File with mtime 2000 is kept

    2. test_tiebreaker_shorter_path():
       Input: Group with 2 files, same mtime, paths "/a/long/path.txt" and "/short.txt"
       Expected: "/short.txt" is kept (shorter path)

    3. test_single_duplicate_pair():
       Input: Two identical files
       Expected: One keep, one delete

    4. test_multiple_duplicates():
       Input: Hash map with multiple duplicate groups
       Expected: Each group has correct keep/delete assignment

    5. test_empty_input():
       Input: Empty hash map
       Expected: Empty Group list

    6. test_group_get_keep_file():
       Input: Group with keep_file set
       Expected: Returns keep_file attribute

    7. test_group_get_delete_files():
       Input: Group with multiple delete files
       Expected: Returns list of all delete files

    8. test_mtime_float_precision():
       Input: Files with mtime 1700000000.123456 and 1700000000.123457
       Expected: Higher precision mtime wins

    Use pytest fixtures for test data. All tests should FAIL initially.
  </action>
  <verify>
    <automated>cd /Users/apple/Project/mac-dedup && python -m pytest tests/test_keep_strategy.py -v</automated>
  </verify>
  <done>
    All 10 test cases written and failing (RED state)
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Implement Group dataclass</name>
  <files>src/mac_dedup/keep_strategy.py</files>
  <behavior>
    - Group has hash attribute (str)
    - Group has keep_file attribute (str)
    - Group has delete_files attribute (List[str])
    - get_keep_file() returns keep_file
    - get_delete_files() returns delete_files
  </behavior>
  <action>
    Create src/mac_dedup/keep_strategy.py with:

    1. Import dataclass and typing
    2. Define Group dataclass:
       - hash: str (the SHA-256 hash value)
       - keep_file: str (absolute path to keep)
       - delete_files: List[str] (absolute paths to delete)
    3. Implement get_keep_file() method
    4. Implement get_delete_files() method

    No keep/delete logic in this task - just the data structure.
    Make Group a proper dataclass with type hints.
  </action>
  <verify>
    <automated>cd /Users/apple/Project/mac-dedup && python -m pytest tests/test_keep_strategy.py::test_group_get_keep_file tests/test_keep_strategy.py::test_group_get_delete_files -v</automated>
  </verify>
  <done>
    Group dataclass created, getter methods pass tests
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Implement KeepStrategy class with mtime sorting</name>
  <files>src/mac_dedup/keep_strategy.py</files>
  <behavior>
    - analyze_groups() receives hash map from HashEngine
    - For each hash, sort files by mtime (descending)
    - Newest file marked as keep
    - All other files marked as delete
    - Returns List[Group] objects
  </behavior>
  <action>
    Add KeepStrategy class to keep_strategy.py:

    1. Define KeepStrategy class with __init__()
    2. Implement analyze_groups() method:
       - Input: Dict[str, List[Tuple[str, float]]] from HashEngine
       - For each hash in the dict:
         * Sort file list by mtime descending
         * First file (newest) becomes keep_file
         * Remaining files become delete_files
         * Create Group object
       - Return List[Group]

    Use Python's sorted() with key lambda for mtime sorting.
    Handle empty input gracefully.
  </action>
  <verify>
    <automated>cd /Users/apple/Project/mac-dedup && python -m pytest tests/test_keep_strategy.py::test_keep_newest_mtime tests/test_keep_strategy.py::test_single_duplicate_pair tests/test_keep_strategy.py::test_multiple_duplicates tests/test_keep_strategy.py::test_empty_input -v</automated>
  </verify>
  <done>
    KeepStrategy.analyze_groups() correctly identifies newest files to keep
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 4: Implement path length tiebreaker</name>
  <files>src/mac_dedup/keep_strategy.py</files>
  <behavior>
    - When mtime values are equal, sort by path length
    - Shorter path is preferred for keeping
    - Maintain existing mtime-based sorting as primary criteria
  </behavior>
  <action>
    Modify sorting logic in analyze_groups():

    1. Change sort key to be tuple: (-mtime, len(path))
       - Negative mtime for descending order
       - len(path) for ascending order (shorter first)
    2. This ensures:
       - Different mtime: newest wins
       - Same mtime: shorter path wins

    Example: sorted(files, key=lambda x: (-x[1], len(x[0])))
  </action>
  <verify>
    <automated>cd /Users/apple/Project/mac-dedup && python -m pytest tests/test_keep_strategy.py::test_tiebreaker_shorter_path -v</automated>
  </verify>
  <done>
    Path length tiebreaker works correctly when mtime equal
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 5: Export KeepStrategy and update __init__.py</name>
  <files>src/mac_dedup/__init__.py, src/mac_dedup/keep_strategy.py</files>
  <behavior>
    - KeepStrategy class exported from mac_dedup module
    - Group dataclass exported from mac_dedup module
    - Module has proper docstring
  </behavior>
  <action>
    1. Add docstring to keep_strategy.py describing module purpose
    2. Update src/mac_dedup/__init__.py:
       - Import KeepStrategy from .keep_strategy
       - Import Group from .keep_strategy
       - Add to __all__ list

    Follow existing export pattern from file_type.py
  </action>
  <verify>
    <automated>cd /Users/apple/Project/mac-dedup && python -c "from mac_dedup import KeepStrategy, Group; print('Exports OK')" && python -m pytest tests/test_keep_strategy.py -v</automated>
  </verify>
  <done>
    KeepStrategy and Group properly exported, all tests pass
  </done>
</task>

</tasks>

<verification>
1. Test coverage: Run pytest with coverage to ensure >= 80%
2. Type checking: Run mypy on keep_strategy.py
3. Integration: Verify KeepStrategy accepts HashEngine output format
4. Edge cases: Test with empty input, single file, mtime ties, path ties
</verification>

<success_criteria>
- [ ] All tests pass (pytest tests/test_keep_strategy.py)
- [ ] Coverage >= 80% for keep_strategy.py
- [ ] mypy passes with no errors
- [ ] KEEP-01: Duplicates sorted by mtime (newest kept)
- [ ] KEEP-02: Clear keep/delete identification via Group API
- [ ] KeepStrategy exported from mac_dedup module
- [ ] Code follows existing project patterns (docstrings, type hints)
</success_criteria>

<output>
After completion, create `.planning/phases/05-keep-strategy/05-SUMMARY.md` using the summary template
</output>
