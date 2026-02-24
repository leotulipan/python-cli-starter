# Build: PyInstaller

## Quick Start

```bash
uv sync --group build
uv run pyinstaller --clean --onefile --name python-cli python-cli.spec
```

## Helper Scripts

Windows:

```powershell
.\scripts\build_exe.ps1
```

Linux/macOS:

```bash
./scripts/build_exe.sh
```

## Notes

- The spec file is `python-cli.spec`.
- If you add dynamic imports, add them to the spec `hiddenimports`.
- Use `--clean` for reproducible builds.
