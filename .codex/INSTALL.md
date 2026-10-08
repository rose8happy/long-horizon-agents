# Install Long Horizon Agents for Codex

This document is intended for an agent asked to install the harness. Complete the local installation yourself, then report the installed path and how to invoke it. The skill contains its initializer, role instructions, templates, and recovery protocol; it does not depend on this clone after installation.

## Install

1. Use an existing checkout of `https://github.com/rose8happy/long-horizon-agents` when available. Otherwise clone it into a separate tool directory, such as `~/long-horizon-agents`. Preserve an existing directory with that name; inspect it instead of overwriting it.
2. From the framework checkout run:

   ```sh
   python scripts/install_skill.py
   ```

   This installs `long-horizon-agents` into `~/.agents/skills`, a native Codex discovery location. It needs Python 3.10+ and uses only the standard library. On Windows use `py -3` if `python` is unavailable. No symlink, administrator privilege, API key, model call, or scheduled task is required.

   For a project-scoped installation, run instead:

   ```sh
   python scripts/install_skill.py --skills-dir <project>/.agents/skills
   ```

   Avoid installing the same skill both globally and within the same project. An identical installation is reused; a conflicting installation is preserved and reported for an intentional merge. `--dry-run` previews the copy.
3. Check that the destination has `long-horizon-agents/SKILL.md`, `assets/`, `references/`, and `scripts/init_project.py`. Codex detects skill changes automatically; if it does not appear, restart the client or start a new session.
4. Invoke `$long-horizon-agents`. For the current session, if native discovery has not refreshed, read the installed `SKILL.md` directly and follow it for the requested project. Report that fallback accurately rather than claiming the skill appeared in the selector.

If the user's request also includes adopting a project, continue with the skill's project setup and the first authorized delivery. If the request was only installation, stop after verifying installation; do not bootstrap unrelated projects or alter running tasks.

## Reuse

The user can give a new agent this single instruction:

> Fetch and follow https://raw.githubusercontent.com/rose8happy/long-horizon-agents/main/.codex/INSTALL.md, then use the harness for this project.

After adoption, the project's `AGENTS.md` loads the harness and its mapped documents for later work. A simple resume request is:

> Use $long-horizon-agents as the executor and continue the current authorized work.

Native skill discovery selects relevant workflow instructions; it does not start a persistent process. The host supplies models, role chats, permissions and scheduled wakes.
