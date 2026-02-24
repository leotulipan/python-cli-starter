# Research: Recent Standalone Python CLI Builds

Date: 2026-02-24
Scope: `Transcribe`, `OCR`, `notion-cli` (sorted by last change in workspace)

## Directory Recency (LastWriteTime)

1. `notion-cli` — 2026-02-24 10:23:44
2. `Transcribe` — 2026-02-23 08:33:03
3. `OCR` — 2026-02-21 17:01:11

## Executive Summary

Across the three projects, the most robust patterns are:

- `pyproject.toml`-first packaging with console script entrypoints.
- Typer/Click for CLI ergonomics.
- Rich + Loguru for user-facing UX + structured logging.
- Pydantic settings for configuration (OCR, notion-cli), with `.env` helpers.
- PyInstaller for standalone binaries (Transcribe, notion-cli).

Notable gaps seen consistently:

- Some builds rely on manual PyInstaller spec files without automated build pipelines.
- Mixed dependency management patterns (Hatch + uv + ad-hoc dev groups).
- Sparse use of `py.typed` and strict typing in Transcribe (OCR and notion-cli are stronger).

## Transcribe (Audio Transcription)

### Packaging & Build

- Build system: Hatchling (`pyproject.toml`).
- CLI entrypoint: `transcribe = audio_transcribe.cli:main`.
- Standalone build: PyInstaller with two spec files:
  - `transcribe.spec` (legacy local path)
  - `transcribe-windows-amd64.spec` (current path) for Windows AMD64.
- PyInstaller config highlights:
  - `hiddenimports` for dynamic dependencies (assemblyai, groq, openai, questionary, rich, etc.).
  - Explicit `datas` inclusion for `loguru`.
  - UPX compression enabled.

### Architecture Notes

- CLI uses Click with a custom `NormalizedPath` to handle trailing quotes and slashes (PowerShell edge cases).
- Transcription pipeline:
  - Accepts file or folder input and supports globbing.
  - Checks for existing raw JSON outputs to avoid repeat API calls.
  - Can ingest API JSON directly and parse to canonical `TranscriptionResult`.
  - Handles chunking automatically when file size exceeds API limits (via `ChunkingMixin`).
- Audio optimization:
  - Uses ffmpeg via pydub and custom helpers to compress or chunk.
  - Tracks temporary intermediate files and cleans up after run.

### UX & Output

- Supports multiple outputs: text, SRT, word-level SRT, DaVinci Resolve optimized SRT.
- Adds pause markers and filler word handling for DaVinci Resolve workflows.
- Interactive setup wizard (TUI) for API keys.

### Specificities & Learnings

- Uses a “JSON-first” workflow to rehydrate transcript state.
- Word-level conversion and pause merging logic is well-encapsulated but complex; careful tests are needed.
- PyInstaller spec is handcrafted and may drift from the Python package entrypoint.

## OCR (Mistral OCR)

### Packaging & Build

- Build system: Hatchling with `pyproject.toml`.
- CLI entrypoint: `ocr = ocr.main:app` (Typer).
- `dependency-groups.dev` for dev tooling.
- No standalone PyInstaller spec present; installs as a global `uv tool`.

### Architecture Notes

- Typer app with async processing and concurrency controls.
- System-wide configuration via pydantic-settings and `.env` setup.
- Shared Mistral client instance for efficiency and consistent rate-limiting.
- Strong separation of concerns:
  - `adapters/` for API integration.
  - `services/` for filename generation, folder watching, processing queue.
  - `utils/` for caching, output, renaming, progress, locks.
  - `models/` for metadata and settings.

### UX & Output

- Intelligent filename generation:
  - First-page OCR → confidence check → full document OCR if low confidence.
  - Stores YAML frontmatter with metadata and rename history.
- Output saved to `.ocr/` subdirectory with consistent naming patterns.
- Safe rename workflow that updates both source file and OCR markdown.

### Specificities & Learnings

- Good example of “smart caching” and “confidence-based escalation.”
- Uses rename logging both in a dedicated log file and in file frontmatter.
- A clear pattern for scalable async processing with good UX feedback.

## notion-cli (Notion Ultimate Brain)

### Packaging & Build

- Build system: Hatchling (`pyproject.toml`).
- CLI entrypoint: `notion-cli = notion_cli.main_typer:app`.
- PyInstaller spec exists (`notion-cli.spec`) but is minimal:
  - `Analysis(['main.py'])` likely outdated or misaligned with `src/notion_cli/main_typer.py`.
  - No explicit hidden imports.

### Architecture Notes

- Typer-based CLI with multiple command groups (`auth`, `tasks`, `task`, `content`, `projects`).
- Logging configured via Loguru with rotating file logs in `~/.notion-cli/logs/`.
- Uses Pydantic models for tasks and content projects.
- Auth flow:
  - Encrypted token storage.
  - Login validates token and stores it securely.
  - Auth status and integration access checks are first-class commands.

### UX & Output

- Multi-format output for tasks: table, simple, json, md, todo.txt.
- Optional verbose logging for deep diagnostics.
- Comprehensive README with operational guidance.

### Specificities & Learnings

- CLI UX is polished with helpful output formats.
- Logging strategy is strong and can be reused as a scaffold template.
- PyInstaller spec likely needs alignment to the current entrypoint if standalone build is expected.

## Cross-Project Best Practices Observed

- Console scripts via `pyproject.toml`.
- Typer (and Click) for CLI ergonomics.
- Structured logging with Loguru.
- Rich for tables/progress and better UX.
- Pydantic settings with `.env` support.
- Clear separation of adapters/services/utils/models.

## Gaps and Opportunities

- Align PyInstaller specs with actual entrypoints and include `hiddenimports` consistently.
- Standardize on a single packaging + tooling approach (Hatch + uv is reasonable).
- Add `py.typed` for type completeness across all projects.
- Tighten CI and add smoke tests for executables.

## Recommendations for New Scaffold

1. `src/` layout with `pyproject.toml` and a console script entrypoint.
2. Typer + Rich for UX, Loguru for logging.
3. Pydantic settings with layered `.env` discovery (cwd + home).
4. Structured error handling with explicit exit codes.
5. Optional PyInstaller spec or build workflow template aligned to entrypoint.
6. Tests for CLI, config, and critical IO logic.

