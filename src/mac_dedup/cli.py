"""CLI interface for mac-dedup."""

import json
from pathlib import Path
from typing import List, Optional, cast

import click

from mac_dedup.file_type import FileType, get_supported_extensions
from mac_dedup.scanner import DirectoryScanner
from mac_dedup.hash_engine import HashEngine
from mac_dedup.keep_strategy import KeepStrategy
from mac_dedup.deleter import Deleter


@click.group()
@click.version_option(version="0.1.0", prog_name="mac-dedup")
def main() -> None:
    """mac-dedup: Fast duplicate file finder for macOS."""
    pass


def parse_file_types(file_types_str: Optional[str]) -> Optional[List[FileType]]:
    """Parse comma-separated file type string to FileType enum list."""
    if not file_types_str:
        return None

    types_map = {
        "text": FileType.TEXT,
        "audio": FileType.AUDIO,
        "video": FileType.VIDEO,
        "archive": FileType.ARCHIVE,
    }

    result: List[FileType] = []
    for name in file_types_str.split(","):
        name = name.strip().lower()
        if name in types_map:
            result.append(types_map[name])
        else:
            raise click.BadParameter(
                f"Invalid file type: {name}. Valid types: {', '.join(types_map.keys())}"
            )

    return result if result else None


@main.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option(
    "--file-types",
    "-t",
    type=str,
    help="Filter by file type (comma-separated: text,audio,video,archive)",
)
@click.option(
    "--exclude",
    "-e",
    multiple=True,
    help="Exclude directory patterns (can be used multiple times)",
)
@click.option(
    "--include-defaults/--no-include-defaults",
    default=True,
    help="Include default exclude patterns (.git, node_modules, etc.)",
)
def scan(
    directory: str,
    file_types: Optional[str],
    exclude: tuple,
    include_defaults: bool,
) -> None:
    """Scan directory for duplicate files."""
    types = parse_file_types(file_types)
    exclude_dirs = list(exclude) if exclude else None

    scanner = DirectoryScanner(
        directory,
        file_types=types,
        exclude_dirs=exclude_dirs,
        use_default_excludes=include_defaults,
    )

    # Scan and collect file info
    file_infos = list(scanner.scan())

    if not file_infos:
        click.echo("No files found matching criteria.")
        return

    # Group by size for efficient hashing
    size_groups: dict[int, List[dict]] = {}
    for info in file_infos:
        size = cast(int, info["size"])
        if size not in size_groups:
            size_groups[size] = []
        size_groups[size].append(info)

    # Only hash groups with multiple files
    potential_dupes = [g for g in size_groups.values() if len(g) > 1]

    if not potential_dupes:
        click.echo(f"Scanned {len(file_infos)} files.")
        click.echo("No duplicates found.")
        return

    # Hash potential duplicates
    click.echo(f"\nFound {len(potential_dupes)} potential duplicate group(s).")
    click.echo("Hashing files...\n")

    hash_engine = HashEngine()
    duplicate_groups: dict[str, List[dict]] = {}

    for group in potential_dupes:
        for info in group:
            file_hash = hash_engine._calculate_hash(cast(str, info["path"]))
            if file_hash not in duplicate_groups:
                duplicate_groups[file_hash] = []
            duplicate_groups[file_hash].append(info)

    # Filter to actual duplicates
    actual_dups = {h: g for h, g in duplicate_groups.items() if len(g) > 1}

    if not actual_dups:
        click.echo(f"Scanned {len(file_infos)} files.")
        click.echo(f"No duplicates found among {len(potential_dupes)} same-size groups.")
        return

    click.echo(f"Found {len(actual_dups)} duplicate group(s):\n")

    for hash_val, files in actual_dups.items():
        click.echo(f"  Hash: {hash_val[:16]}...")
        for f in files:
            size_mb = f["size"] / (1024 * 1024)
            click.echo(f"    - {f['path']} ({size_mb:.2f} MB)")
        click.echo()


@main.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option(
    "--file-types",
    "-t",
    type=str,
    help="Filter by file type (comma-separated: text,audio,video,archive)",
)
@click.option(
    "--exclude",
    "-e",
    multiple=True,
    help="Exclude directory patterns (can be used multiple times)",
)
@click.option(
    "--dry-run",
    "-n",
    is_flag=True,
    help="Preview deletions without actually deleting",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompt (use with caution, has no effect with --dry-run)",
)
def clean(
    directory: str,
    file_types: Optional[str],
    exclude: tuple,
    dry_run: bool,
    yes: bool,
) -> None:
    """Remove duplicate files, keeping one copy per group."""
    types = parse_file_types(file_types)
    exclude_dirs = list(exclude) if exclude else None

    click.echo(f"Scanning: {directory}")
    if dry_run:
        click.echo("DRY RUN mode - no files will be deleted\n")

    scanner = DirectoryScanner(
        directory,
        file_types=types,
        exclude_dirs=exclude_dirs,
        use_default_excludes=True,
    )

    file_infos = list(scanner.scan())
    if not file_infos:
        click.echo("No files found.")
        return

    # Find duplicates using HashEngine
    hash_engine = HashEngine()
    duplicates = hash_engine.find_duplicates(file_infos)

    if not duplicates:
        click.echo("No duplicates found.")
        return

    # Apply keep strategy
    strategy = KeepStrategy()
    groups = strategy.analyze_groups(duplicates)

    total_delete = 0
    total_size = 0

    click.echo(f"Found {len(groups)} duplicate group(s):\n")

    for group in groups:
        delete_files = group.get_delete_files()
        keep_file = group.get_keep_file()

        if delete_files:
            total_delete += len(delete_files)

            # Calculate size of files to delete
            for info in file_infos:
                if info["path"] in delete_files:
                    total_size += cast(int, info["size"])

            click.echo(f"  Hash: {group.hash[:16]}...")
            click.echo(f"    Keep: {keep_file}")
            for df in delete_files:
                click.echo(f"    Delete: {df}")
            click.echo()

    if total_delete == 0:
        click.echo("No files marked for deletion.")
        return

    total_size_mb = total_size / (1024 * 1024)
    click.echo(f"\nTotal: Would delete {total_delete} file(s) ({total_size_mb:.2f} MB)")

    if dry_run:
        click.echo("Dry run mode - no files were deleted.")
        return

    # Confirm deletion (skip if --yes flag is set)
    if not yes:
        click.confirm("\nDelete these files?", abort=True)

    # Execute deletion
    deleter = Deleter(dry_run=False)

    success, failures, _ = deleter.delete_groups(groups)

    click.echo(f"\nDeleted: {success} file(s)")
    if failures:
        click.echo(f"Failed: {failures} file(s)")


@main.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option(
    "--file-types",
    "-t",
    type=str,
    help="Filter by file type (comma-separated: text,audio,video,archive)",
)
@click.option(
    "--exclude",
    "-e",
    multiple=True,
    help="Exclude directory patterns (can be used multiple times)",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "csv", "json"]),
    default="table",
    help="Output format",
)
def report(
    directory: str,
    file_types: Optional[str],
    exclude: tuple,
    format: str,
) -> None:
    """Generate a report of duplicate files."""
    types = parse_file_types(file_types)
    exclude_dirs = list(exclude) if exclude else None

    scanner = DirectoryScanner(
        directory,
        file_types=types,
        exclude_dirs=exclude_dirs,
        use_default_excludes=True,
    )

    file_infos = list(scanner.scan())
    if not file_infos:
        click.echo("No files found.")
        return

    # Find duplicates using HashEngine
    hash_engine = HashEngine()
    duplicates = hash_engine.find_duplicates(file_infos)

    if not duplicates:
        click.echo("No duplicates found.")
        return

    # Generate report based on format
    if format == "table":
        click.echo("=" * 70)
        click.echo("Scan Summary")
        click.echo("=" * 70)
        click.echo(f"Total files scanned: {len(file_infos)}")
        click.echo(f"Duplicate groups: {len(duplicates)}")

        total_wasted = 0
        total_dupes = 0

        for files in duplicates.values():
            # Count extras (all but first)
            extras = len(files) - 1
            total_dupes += extras
            # Get size from file_infos (convert from tuple back to info)
            # files are tuples of (path, mtime)
            # Find matching file_info for size
            for path, _ in files:
                for info in file_infos:
                    if info["path"] == path:
                        if total_wasted == 0:  # Only count first file size per group
                            total_wasted += extras * cast(int, info["size"])
                        break

        # Calculate correctly: total_dupe_files - number_of_groups
        total_dupe_files = sum(len(f) for f in duplicates.values()) - len(duplicates)

        # Recalculate wasted space correctly
        total_wasted = 0
        for files in duplicates.values():
            extras = len(files) - 1
            if extras > 0:
                # Find file size from original file_infos
                path = files[0][0]  # First file path
                for info in file_infos:
                    if info["path"] == path:
                        total_wasted += extras * cast(int, info["size"])
                        break

        wasted_mb = total_wasted / (1024 * 1024)
        click.echo(f"Duplicate files: {total_dupe_files}")
        click.echo(f"Wasted space: {wasted_mb:.2f} MB")
        click.echo()

    elif format == "csv":
        click.echo("Group,Hash,Size,Files")
        for hash_val, files in duplicates.items():
            paths = "|".join(f[0] for f in files)
            # Get size from file_infos
            size = 0
            path = files[0][0]
            for info in file_infos:
                if info["path"] == path:
                    size = cast(int, info["size"])
                    break
            click.echo(f"{hash_val[:16]},{hash_val},{size},{paths}")

    elif format == "json":
        report_data = {
            "summary": {
                "total_files": len(file_infos),
                "duplicate_groups": len(duplicates),
            },
            "groups": [
                {
                    "hash": hash_val,
                    "size": next(
                        (info["size"] for info in file_infos if info["path"] == files[0][0]), 0
                    ),
                    "count": len(files),
                    "files": [f[0] for f in files],
                }
                for hash_val, files in duplicates.items()
            ],
        }
        click.echo(json.dumps(report_data, indent=2))
