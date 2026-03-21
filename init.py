#!/usr/bin/env python3
"""Rename this scaffold from python-cli to your project name."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

NAME_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

# Files that need text replacement (relative to repo root)
TARGET_FILES = [
    "pyproject.toml",
    "src/python_cli/cli.py",
    "src/python_cli/__main__.py",
    "src/python_cli/__init__.py",
    "src/python_cli/logging.py",
    "python-cli.spec",
    "install.sh",
    "scripts/build_exe.ps1",
    "scripts/build_exe.sh",
    "docs/build.md",
    "tests/test_cli.py",
    "tests/test_config.py",
    "README.md",
]


def validate_name(name: str) -> str:
    if not NAME_RE.match(name):
        print(
            f"Error: '{name}' is not a valid project name.\n"
            "Must be lowercase letters, digits, and hyphens, starting with a letter.\n"
            "Examples: my-tool, cli-utils, awesome-app"
        )
        sys.exit(1)
    return name


def to_underscore(name: str) -> str:
    return name.replace("-", "_")


def replace_in_file(path: Path, replacements: list[tuple[str, str]], dry_run: bool) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    original = text
    for old, new in replacements:
        text = text.replace(old, new)
    if text == original:
        return False
    if not dry_run:
        path.write_text(text, encoding="utf-8")
    return True


def remove_readme_section(readme: Path, dry_run: bool) -> None:
    """Remove the 'Renaming From python-cli' section from README."""
    if not readme.exists():
        return
    text = readme.read_text(encoding="utf-8")
    # Match the section header through to the next ## heading or end of file
    pattern = r"\n## Renaming From `python-cli`\n.*?(?=\n## |\Z)"
    new_text = re.sub(pattern, "", text, flags=re.DOTALL)
    if new_text != text and not dry_run:
        readme.write_text(new_text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Rename python-cli scaffold to your project name")
    parser.add_argument("name", nargs="?", help="New project name (e.g. my-tool)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without modifying files"
    )
    args = parser.parse_args()

    name: str = args.name or input("Enter new project name (e.g. my-tool): ").strip()
    validate_name(name)

    underscore = to_underscore(name)

    replacements = [
        ("python-cli", name),
        ("python_cli", underscore),
    ]

    print(f"\nRenaming python-cli -> {name} (python_cli -> {underscore})")
    if args.dry_run:
        print("[DRY RUN] No files will be modified.\n")

    # Text replacements
    print("Text replacements:")
    for rel in TARGET_FILES:
        path = ROOT / rel
        changed = replace_in_file(path, replacements, args.dry_run)
        status = "changed" if changed else "no change"
        if not path.exists():
            status = "not found (skipped)"
        print(f"  {rel}: {status}")

    # Directory rename
    old_pkg = ROOT / "src" / "python_cli"
    new_pkg = ROOT / "src" / underscore
    if old_pkg.exists() and underscore != "python_cli":
        print(f"\nRename directory: src/python_cli -> src/{underscore}")
        if not args.dry_run:
            old_pkg.rename(new_pkg)

    # Spec file rename
    old_spec = ROOT / "python-cli.spec"
    new_spec = ROOT / f"{name}.spec"
    if old_spec.exists() and name != "python-cli":
        print(f"Rename file: python-cli.spec -> {name}.spec")
        if not args.dry_run:
            old_spec.rename(new_spec)

    # Cleanup
    print("\nCleanup:")
    walkthrough = ROOT / "walkthrough.md"
    if walkthrough.exists():
        print("  Delete walkthrough.md")
        if not args.dry_run:
            walkthrough.unlink()

    readme = ROOT / "README.md"
    print("  Remove renaming section from README.md")
    if not args.dry_run:
        remove_readme_section(readme, dry_run=False)

    init_file = ROOT / "init.py"
    print("  Delete init.py (this script)")
    if not args.dry_run:
        # Delete ourselves last
        init_file.unlink()

    if args.dry_run:
        print("\n[DRY RUN] No changes were made. Run without --dry-run to apply.")
        return

    # Run uv sync
    print("\nRunning uv sync...")
    subprocess.run(["uv", "sync", "--group", "dev"], cwd=str(ROOT), check=False)
    print(f"\nDone! Project renamed to '{name}'.")


if __name__ == "__main__":
    main()
