#!/usr/bin/env python3
"""Add the long-horizon agent documents to a project without replacing files."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import stat
import sys


START = b"<!-- long-horizon-agents:start -->"
END = b"<!-- long-horizon-agents:end -->"


class InitError(Exception):
    """An installation conflict that the user can resolve."""


@dataclass
class Write:
    path: Path
    content: bytes
    append: bool = False


def _lstat(path: Path):
    try:
        return path.lstat()
    except FileNotFoundError:
        return None


def _reject_link(path: Path, info) -> None:
    # Windows junctions are reparse points, even on Python versions without
    # Path.is_junction(). Reject links entirely instead of resolving them.
    reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & reparse:
        raise InitError(f"Unsafe link or junction: {path}. Use a real directory/file path.")


def _check_directories(path: Path) -> None:
    for directory in (*reversed(path.parents), path):
        info = _lstat(directory)
        if info is not None:
            _reject_link(directory, info)
            if not stat.S_ISDIR(info.st_mode):
                raise InitError(f"Expected a directory: {directory}. Move the conflicting file first.")


def _existing_file(path: Path) -> bool:
    _check_directories(path.parent)
    info = _lstat(path)
    if info is None:
        return False
    _reject_link(path, info)
    if not stat.S_ISREG(info.st_mode):
        raise InitError(f"Expected a regular file: {path}. Move the conflicting entry first.")
    return True


def _sources():
    for name in ("MISSION", "PLAN", "CURRENT", "DECISIONS", "HISTORY"):
        yield f"templates/project/{name}.md", f"docs/agent/{name}.md"
    yield "templates/project/TASK.md", "docs/agent/templates/TASK.md"
    yield "templates/project/agent.config.example.toml", ".agent/agent.config.example.toml"
    for name in ("planner", "executor"):
        yield f"roles/{name}.md", f".agent/roles/{name}.md"
    for name in ("setup", "planner-wake", "executor-wake"):
        yield f"adapters/codex/{name}.md", f".agent/codex/{name}.md"


def initialize(target: Path, name: str | None = None, dry_run: bool = False,
               source_root: Path | None = None) -> list[str]:
    """Preflight and apply an additive installation; return readable outcomes."""
    target = Path(target).absolute()
    source_root = Path(source_root) if source_root is not None else Path(__file__).resolve().parent.parent / "assets"
    name = target.name if name is None else name
    _check_directories(target)
    writes: list[Write] = []
    outcomes: list[str] = []

    def plan_file(relative: str, content=None, source: str | None = None) -> None:
        destination = target / relative
        if _existing_file(destination):
            outcomes.append(f"SKIPPED {relative}")
            return
        if content is None:
            source_path = source_root / source
            if not source_path.is_file():
                raise InitError(f"Missing source template: {source_path}. Restore the template before initializing.")
            content = source_path.read_text(encoding="utf-8")
        replacement = json.dumps(name, ensure_ascii=False)[1:-1] if relative.endswith(".toml") else name
        content = content.replace("{{PROJECT_NAME}}", replacement)
        writes.append(Write(destination, content.encode("utf-8")))
        outcomes.append(f"CREATED {relative}")

    for source, destination in _sources():
        plan_file(destination, source=source)

    plan_file("docs/agent/README.md", """# Agent documents for {{PROJECT_NAME}}

Start with [MISSION.md](MISSION.md), then [PLAN.md](PLAN.md) and
[CURRENT.md](CURRENT.md). Record decisions in [DECISIONS.md](DECISIONS.md)
and completed work in [HISTORY.md](HISTORY.md).

Use [templates/TASK.md](templates/TASK.md) for a task contract. Read the
[planner role](../../.agent/roles/planner.md) and
[executor role](../../.agent/roles/executor.md). Review the
[example configuration](../../.agent/agent.config.example.toml) and follow
the [Codex setup guide](../../.agent/codex/setup.md) before configuring a runtime.
""")

    agents_path = target / "AGENTS.md"
    agents_exists = _existing_file(agents_path)
    existing = agents_path.read_bytes() if agents_exists else b""
    starts, ends = existing.count(START), existing.count(END)
    if starts or ends:
        if starts != 1 or ends != 1 or existing.index(START) >= existing.index(END):
            raise InitError(
                f"Malformed long-horizon-agents markers in {agents_path}. "
                "Keep exactly one start marker followed by one end marker, or remove both markers."
            )
        outcomes.append("SKIPPED AGENTS.md (instruction block)")
    else:
        block = b"""<!-- long-horizon-agents:start -->
## Long-horizon agent workflow

For long-running work, invoke $long-horizon-agents when that skill is
available. Read [docs/agent/README.md](docs/agent/README.md) and the durable
project documents it links. If the skill is unavailable, these local
documents and roles provide the workflow. Follow the
[planner](.agent/roles/planner.md) or [executor](.agent/roles/executor.md)
role matching your assigned function. Review [.agent/agent.config.example.toml](.agent/agent.config.example.toml),
and use [.agent/codex/setup.md](.agent/codex/setup.md) for Codex setup.
<!-- long-horizon-agents:end -->
"""
        separator = b"" if not existing else (b"\n" if existing.endswith(b"\n") else b"\n\n")
        writes.append(Write(agents_path, separator + block, append=agents_exists))
        outcomes.append("CREATED AGENTS.md (instruction block)")

    # No writes or directory creation occur until every destination and every
    # needed source has passed preflight. I/O failures still report normally.
    if not dry_run:
        for write in writes:
            write.path.parent.mkdir(parents=True, exist_ok=True)
            with write.path.open("ab" if write.append else "xb") as handle:
                handle.write(write.content)
    return outcomes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, type=Path, help="Project directory to initialize")
    parser.add_argument("--name", help="Project name (defaults to the target directory name)")
    parser.add_argument("--dry-run", action="store_true", help="Show the planned installation without writing")
    args = parser.parse_args(argv)
    try:
        outcomes = initialize(args.target, args.name, args.dry_run)
    except (InitError, OSError, UnicodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.dry_run:
        print("DRY RUN: planned results; no files changed")
    print("\n".join(outcomes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
