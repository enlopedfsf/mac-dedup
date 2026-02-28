"""CLI interface for mac-dedup."""

import click


@click.group()
@click.version_option(version="0.1.0", prog_name="mac-dedup")
def main() -> None:
    """mac-dedup: Fast duplicate file finder for macOS."""
    pass


@main.command()
@click.argument("directory", type=click.Path(exists=True))
def scan(directory: str) -> None:
    """Scan directory for duplicate files."""
    click.echo(f"Scanning {directory} for duplicates...")


@main.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, help="Show what would be deleted without deleting")
def clean(directory: str, dry_run: bool) -> None:
    """Remove duplicate files from directory."""
    if dry_run:
        click.echo(f"Dry run: Would clean {directory}")
    else:
        click.echo(f"Cleaning {directory}...")


@main.command()
@click.argument("directory", type=click.Path(exists=True))
def report(directory: str) -> None:
    """Generate report of duplicate files."""
    click.echo(f"Generating report for {directory}...")
