#!/usr/bin/env python3
"""Install the self-contained long-horizon-agents skill into a local discovery directory."""

from __future__ import annotations

import argparse
from pathlib import Path
import stat
import sys


SKILL_NAME = "long-horizon-agents"


class InstallError(Exception):
    """An installation conflict that needs an explicit user choice."""


def _info(path: Path):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & reparse:
        raise InstallError(f"Link or junction at {path}. Use a real directory/file path.")
    return info


def _directory(path: Path) -> None:
    for parent in (*reversed(path.parents), path):
        info = _info(parent)
        if info is not None and not stat.S_ISDIR(info.st_mode):
            raise InstallError(f"Expected a directory: {parent}. Move the conflicting entry first.")


def _source_files(source: Path) -> list[Path]:
    _directory(source)
    required = ["SKILL.md", "scripts/init_project.py"]
    required.extend(f"assets/templates/project/{name}.md"
                    for name in ("MISSION", "PLAN", "CURRENT", "DECISIONS", "HISTORY", "TASK"))
    required.append("assets/templates/project/agent.config.example.toml")
    required.extend(f"assets/roles/{name}.md" for name in ("planner", "executor"))
    required.extend(f"assets/adapters/codex/{name}.md"
                    for name in ("setup", "planner-wake", "executor-wake"))
    for relative in required:
        path = source / relative
        info = _info(path)
        if info is None or not stat.S_ISREG(info.st_mode):
            raise InstallError(f"Incomplete skill bundle: missing regular file {path}. Restore the repository bundle first.")

    files: list[Path] = []
    for path in sorted(source.rglob("*")):
        if "__pycache__" in path.relative_to(source).parts:
            continue
        info = _info(path)
        if stat.S_ISREG(info.st_mode):
            files.append(path)
        elif not stat.S_ISDIR(info.st_mode):
            raise InstallError(f"Unsupported entry in skill bundle: {path}.")
    return files


def install(skills_dir: Path, dry_run: bool = False,
            source_root: Path | None = None) -> list[str]:
    """Plan all files before making an additive installation; preserve local edits."""
    source = (Path(__file__).resolve().parents[1] / "skills" / SKILL_NAME
              if source_root is None else Path(source_root).absolute())
    files = _source_files(source)
    destination = Path(skills_dir).absolute() / SKILL_NAME
    _directory(destination)
    writes: list[tuple[Path, bytes]] = []
    outcomes: list[str] = []
    for path in files:
        relative = path.relative_to(source)
        target = destination / relative
        _directory(target.parent)
        content = path.read_bytes()
        info = _info(target)
        if info is not None:
            if not stat.S_ISREG(info.st_mode) or target.read_bytes() != content:
                raise InstallError(
                    f"Existing skill differs at {target}. Your files were preserved. "
                    "Choose a different --skills-dir, or back up and remove the existing skill directory before reinstalling."
                )
            outcomes.append(f"SKIPPED {relative.as_posix()}")
        else:
            writes.append((target, content))
            outcomes.append(f"CREATED {relative.as_posix()}")

    if not dry_run:
        for target, content in writes:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as handle:
                handle.write(content)
    return outcomes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-dir", type=Path, default=Path.home() / ".agents" / "skills",
                        help="Skill discovery directory (default: ~/.agents/skills)")
    parser.add_argument("--dry-run", action="store_true", help="Show planned results without writing")
    args = parser.parse_args(argv)
    try:
        outcomes = install(args.skills_dir, args.dry_run)
    except (InstallError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.dry_run:
        print("DRY RUN: planned results; no files changed")
    print("\n".join(outcomes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
