from __future__ import annotations

import fnmatch
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCAFFOLD_DIST_NAME = "python-cli"
SCAFFOLD_MODULE_NAME = "python_cli"
SCAFFOLD_DESCRIPTION = "Generic best-practice Python CLI scaffold"
SCAFFOLD_AUTHOR = "Your Name"
SCAFFOLD_EMAIL = "you@example.com"

EXCLUDED_DIR_NAMES = {
    ".claude",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
}
EXCLUDED_FILE_NAMES = {
    "desktop.ini",
    "uv.lock",
}
EXCLUDED_PATTERNS = {
    "*.egg-info",
    "*.pyc",
    "*.pyo",
}
SETUP_FILES = {
    "init.py",
    "initial_setup.py",
    "initial_setup.sh",
    "initial_setup.ps1",
    "initial_setup.bat",
}
OPTIONAL_DOC_PATHS = {
    "docs",
    "research.md",
    "walkthrough.md",
}


def main() -> int:
    source_dir = Path(__file__).resolve().parent
    print("Initial Python CLI scaffold setup")
    print(f"Source: {source_dir}")
    print()

    target_dir = ask_path("Target directory").expanduser().resolve()
    if target_dir == source_dir:
        print("Target directory must be different from the scaffold directory.", file=sys.stderr)
        return 1
    if target_dir.exists() and any(target_dir.iterdir()) and not ask_yes_no(
        "Target directory is not empty. Continue",
        default=False,
    ):
        print("Aborted.")
        return 1

    guessed_name = slugify_dist_name(target_dir.name) or "my-tool"
    dist_name = ask_value("Project distribution name", guessed_name, normalize=slugify_dist_name)
    module_name = ask_value(
        "Python import package",
        dist_name.replace("-", "_"),
        normalize=python_identifier,
    )
    command_name = ask_value(
        "CLI command name",
        default_command_name(dist_name),
        normalize=slugify_dist_name,
    )
    display_name = ask_value("Display name", default_display_name(dist_name))
    description = ask_value("Project description", f"{dist_name} CLI")
    author_name = ask_value("Author name", git_config(source_dir, "user.name") or SCAFFOLD_AUTHOR)
    author_email = ask_value("Author email", git_config(source_dir, "user.email") or SCAFFOLD_EMAIL)
    repo_url = ask_value("Repository URL (leave blank to skip)", "")
    copy_docs = ask_yes_no("Copy docs/research files too", default=False)

    replacements = build_replacements(
        dist_name=dist_name,
        module_name=module_name,
        command_name=command_name,
        display_name=display_name,
        description=description,
        author_name=author_name,
        author_email=author_email,
        repo_url=repo_url,
    )

    copy_scaffold(
        source_dir=source_dir,
        target_dir=target_dir,
        replacements=replacements,
        dist_name=dist_name,
        module_name=module_name,
        copy_docs=copy_docs,
    )
    remove_readme_section(target_dir / "README.md")
    remove_install_warning(target_dir / "install.sh")
    initialize_git_repo(target_dir)

    print()
    print(f"Created scaffold in: {target_dir}")
    print("Next steps:")
    print(f"  cd {target_dir}")
    print("  uv sync --group dev")
    print("  uv run pytest")
    print(f"  uv run {command_name} --help")
    return 0


def ask_path(prompt: str) -> Path:
    while True:
        raw = input(f"{prompt}: ").strip().strip('"')
        if raw:
            return Path(raw)
        print("Please enter a target directory.")


def ask_value(prompt: str, default: str, normalize=None) -> str:
    while True:
        suffix = f" [{default}]" if default else ""
        raw = input(f"{prompt}{suffix}: ").strip()
        value = raw or default
        if normalize:
            value = normalize(value)
        if value or default == "":
            return value
        print("Please enter a value.")


def ask_yes_no(prompt: str, *, default: bool) -> bool:
    suffix = "Y/n" if default else "y/N"
    while True:
        raw = input(f"{prompt}? [{suffix}]: ").strip().lower()
        if not raw:
            return default
        if raw in {"y", "yes"}:
            return True
        if raw in {"n", "no"}:
            return False
        print("Please answer yes or no.")


def git_config(cwd: Path, key: str) -> str:
    try:
        result = subprocess.run(
            ["git", "config", key],
            capture_output=True,
            text=True,
            cwd=str(cwd),
            check=False,
        )
    except Exception:
        return ""
    return result.stdout.strip()


def slugify_dist_name(value: str) -> str:
    value = value.strip().lower().replace("_", "-")
    value = re.sub(r"[^a-z0-9.-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-.")
    if value and not value[0].isalpha():
        value = f"cli-{value}"
    return value


def title_from_slug(value: str) -> str:
    return " ".join(part.capitalize() for part in re.split(r"[-_\s]+", value) if part)


def default_command_name(dist_name: str) -> str:
    if dist_name.endswith("-cli") and len(dist_name) > 4:
        return dist_name[:-4]
    return dist_name


def default_display_name(dist_name: str) -> str:
    if dist_name.endswith("-cli"):
        base = dist_name[:-4]
        return f"{title_from_slug(base)} CLI" if base else "CLI"
    return title_from_slug(dist_name)


def python_identifier(value: str) -> str:
    value = value.strip().lower().replace("-", "_")
    value = re.sub(r"\W+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    if value and value[0].isdigit():
        value = f"_{value}"
    return value if value.isidentifier() else ""


def build_replacements(
    *,
    dist_name: str,
    module_name: str,
    command_name: str,
    display_name: str,
    description: str,
    author_name: str,
    author_email: str,
    repo_url: str,
) -> list[tuple[str, str]]:
    replacements = [
        ('python-cli = "python_cli.cli:app"', f'{command_name} = "{module_name}.cli:app"'),
        ("uv run python-cli --help", f"uv run {command_name} --help"),
        ("python-cli --version", f"{command_name} --version"),
        ("# Python CLI Scaffold", f"# {display_name}"),
        (
            "A modern, batteries-included scaffold for building robust Python CLI tools.",
            description,
        ),
        ("Generic Python CLI scaffold", description),
        (SCAFFOLD_DESCRIPTION, description),
        (SCAFFOLD_AUTHOR, author_name),
        (SCAFFOLD_EMAIL, author_email),
        (SCAFFOLD_DIST_NAME, dist_name),
        (SCAFFOLD_MODULE_NAME, module_name),
    ]
    if repo_url:
        replacements.extend(
            [
                ("https://example.com/issues", f"{repo_url}/issues"),
                ("https://example.com/repo", repo_url),
                ("https://example.com", repo_url),
            ]
        )
    return replacements


def copy_scaffold(
    *,
    source_dir: Path,
    target_dir: Path,
    replacements: list[tuple[str, str]],
    dist_name: str,
    module_name: str,
    copy_docs: bool,
) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    for path in source_dir.rglob("*"):
        if path == target_dir or target_dir in path.parents:
            continue
        relative = path.relative_to(source_dir)
        if should_skip(relative, path, copy_docs=copy_docs):
            continue

        rewritten_relative = rewrite_relative_path(relative, dist_name, module_name)
        destination = target_dir / rewritten_relative
        if path.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        if is_text_file(path):
            text = path.read_text(encoding="utf-8")
            for old, new in replacements:
                if old:
                    text = text.replace(old, new)
            destination.write_text(text, encoding="utf-8", newline="")
        else:
            shutil.copy2(path, destination)


def should_skip(relative: Path, path: Path, *, copy_docs: bool) -> bool:
    parts = set(relative.parts)
    if parts & EXCLUDED_DIR_NAMES:
        return True
    if path.name in EXCLUDED_FILE_NAMES or path.name in SETUP_FILES:
        return True
    if any(
        fnmatch.fnmatch(part, pattern)
        for part in relative.parts
        for pattern in EXCLUDED_PATTERNS
    ):
        return True
    return not copy_docs and relative.parts and relative.parts[0] in OPTIONAL_DOC_PATHS


def rewrite_relative_path(relative: Path, dist_name: str, module_name: str) -> Path:
    parts = []
    for part in relative.parts:
        if part == SCAFFOLD_MODULE_NAME:
            parts.append(module_name)
        elif part == f"{SCAFFOLD_DIST_NAME}.spec":
            parts.append(f"{dist_name}.spec")
        else:
            parts.append(part)
    return Path(*parts)


def is_text_file(path: Path) -> bool:
    text_suffixes = {
        ".cfg",
        ".ini",
        ".md",
        ".ps1",
        ".py",
        ".sh",
        ".spec",
        ".toml",
        ".txt",
        ".yaml",
        ".yml",
    }
    if path.suffix.lower() in text_suffixes:
        return True
    try:
        path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    return True


def remove_readme_section(readme: Path) -> None:
    if not readme.exists():
        return
    text = readme.read_text(encoding="utf-8")
    patterns = [
        r"\n## Start a New Project From This Template\n.*?(?=\n## |\Z)",
        r"\n## Renaming From `python-cli`\n.*?(?=\n## |\Z)",
    ]
    new_text = text
    for pattern in patterns:
        new_text = re.sub(pattern, "", new_text, flags=re.DOTALL)
    if new_text != text:
        readme.write_text(new_text, encoding="utf-8", newline="")


def remove_install_warning(install_script: Path) -> None:
    if not install_script.exists():
        return
    text = install_script.read_text(encoding="utf-8")
    pattern = (
        r"\n# Warn if the project hasn't been renamed yet\n"
        r"if grep -q '\^name = \".*?\"' pyproject\.toml 2>/dev/null; then\n"
        r".*?fi\n"
    )
    new_text = re.sub(pattern, "\n", text, flags=re.DOTALL)
    if new_text != text:
        install_script.write_text(new_text, encoding="utf-8", newline="")


def initialize_git_repo(target_dir: Path) -> None:
    try:
        subprocess.run(
            ["git", "init"], cwd=str(target_dir), capture_output=True, check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  git init failed or git is not available; skipping repo setup.")
        return

    gitignore_path = target_dir / ".gitignore"
    if gitignore_path.exists():
        content = gitignore_path.read_text(encoding="utf-8")
        if ".worktree/" not in content:
            content = content.rstrip("\n") + "\n\n# Git worktree checkout directory\n.worktree/\n"
            gitignore_path.write_text(content, encoding="utf-8", newline="")

    (target_dir / ".worktree").mkdir(exist_ok=True)

    try:
        subprocess.run(
            ["git", "add", "-A"], cwd=str(target_dir), capture_output=True, check=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit from python-cli scaffold"],
            cwd=str(target_dir),
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  git commit failed; repo is initialized but has no initial commit.")


if __name__ == "__main__":
    raise SystemExit(main())
