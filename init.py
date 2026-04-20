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


def git_config(key: str) -> str:
    try:
        result = subprocess.run(
            ["git", "config", key], capture_output=True, text=True, cwd=str(ROOT), check=False
        )
        return result.stdout.strip()
    except Exception:
        return ""


def prompt(label: str, default: str) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or default


def replace_in_file(path: Path, replacements: list[tuple[str, str]], dry_run: bool) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    original = text
    for old, new in replacements:
        if old:
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
    pattern = r"\n## Renaming From `python-cli`\n.*?(?=\n## |\Z)"
    new_text = re.sub(pattern, "", text, flags=re.DOTALL)
    if new_text != text and not dry_run:
        readme.write_text(new_text, encoding="utf-8")


def build_replacements(
    name: str, underscore: str, description: str, author_name: str, author_email: str, repo_url: str
) -> list[tuple[str, str]]:
    replacements = [
        ("python-cli", name),
        ("python_cli", underscore),
        ("Generic best-practice Python CLI scaffold", description),
        ("Your Name", author_name),
        ("you@example.com", author_email),
    ]
    if repo_url:
        replacements += [
            ("https://example.com/issues", f"{repo_url}/issues"),
            ("https://example.com/repo", repo_url),
            ("https://example.com", repo_url),
        ]
    return replacements


def apply_text_replacements(replacements: list[tuple[str, str]], dry_run: bool) -> None:
    print("Text replacements:")
    for rel in TARGET_FILES:
        path = ROOT / rel
        changed = replace_in_file(path, replacements, dry_run)
        status = "changed" if changed else "no change"
        if not path.exists():
            status = "not found (skipped)"
        print(f"  {rel}: {status}")


def apply_renames(name: str, underscore: str, dry_run: bool) -> None:
    old_pkg = ROOT / "src" / "python_cli"
    new_pkg = ROOT / "src" / underscore
    if old_pkg.exists() and underscore != "python_cli":
        print(f"\nRename directory: src/python_cli -> src/{underscore}")
        if not dry_run:
            old_pkg.rename(new_pkg)

    old_spec = ROOT / "python-cli.spec"
    new_spec = ROOT / f"{name}.spec"
    if old_spec.exists() and name != "python-cli":
        print(f"Rename file: python-cli.spec -> {name}.spec")
        if not dry_run:
            old_spec.rename(new_spec)


def cleanup(dry_run: bool) -> None:
    print("\nCleanup:")
    walkthrough = ROOT / "walkthrough.md"
    if walkthrough.exists():
        print("  Delete walkthrough.md")
        if not dry_run:
            walkthrough.unlink()

    print("  Remove renaming section from README.md")
    if not dry_run:
        remove_readme_section(ROOT / "README.md", dry_run=False)


def post_rename(name: str, commit: bool) -> None:
    print("\nRunning uv sync...")
    subprocess.run(["uv", "sync", "--group", "dev"], cwd=str(ROOT), check=False)

    git_dir = ROOT / ".git"
    if not git_dir.exists():
        print("\nInitializing git repository...")
        subprocess.run(["git", "init"], cwd=str(ROOT), check=False)

    if commit:
        print("Creating initial commit...")
        subprocess.run(["git", "add", "-A"], cwd=str(ROOT), check=False)
        subprocess.run(
            ["git", "commit", "-m", f"chore: rename scaffold to {name}"],
            cwd=str(ROOT),
            check=False,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Rename python-cli scaffold to your project name")
    parser.add_argument("name", nargs="?", help="New project name (e.g. my-tool)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without modifying files"
    )
    parser.add_argument(
        "--commit", action="store_true", help="Create an initial git commit after rename"
    )
    args = parser.parse_args()

    name: str = args.name or input("Enter new project name (e.g. my-tool): ").strip()
    validate_name(name)
    underscore = to_underscore(name)

    description = prompt("Project description", f"{name} CLI")
    author_name = prompt("Author name", git_config("user.name"))
    author_email = prompt("Author email", git_config("user.email"))
    repo_url = prompt("Repository URL (leave blank to skip)", "")

    replacements = build_replacements(
        name, underscore, description, author_name, author_email, repo_url
    )

    print(f"\nRenaming python-cli -> {name} (python_cli -> {underscore})")
    if args.dry_run:
        print("[DRY RUN] No files will be modified.\n")

    apply_text_replacements(replacements, args.dry_run)
    apply_renames(name, underscore, args.dry_run)
    cleanup(args.dry_run)

    if args.dry_run:
        print("\n[DRY RUN] No changes were made. Run without --dry-run to apply.")
        return

    post_rename(name, args.commit)
    (ROOT / "init.py").unlink()
    print(f"\nDone! Project renamed to '{name}'.")


if __name__ == "__main__":
    main()
