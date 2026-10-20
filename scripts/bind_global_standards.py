#!/usr/bin/env python3
"""Pin the two standards domains to a Git commit and expose directory symlinks."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

DOMAINS = ("skills/engineering-standards", "skills/operations-management")


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def catalog(repo: Path, ref: str) -> dict[str, str]:
    if not re.fullmatch(r"[0-9a-f]{40}", ref):
        raise ValueError("--ref must be an explicit full 40-character commit SHA")
    if git(repo, "rev-parse", f"{ref}^{{commit}}") != ref:
        raise ValueError("commit does not resolve exactly")
    entries = {}
    for line in git(repo, "ls-tree", "-r", "--name-only", ref, "--", *DOMAINS).splitlines():
        path = Path(line)
        if path.name != "SKILL.md" or len(path.parts) != 4:
            continue
        name = path.parent.name
        content = git(repo, "show", f"{ref}:{line}")
        match = re.search(r"^name:\s*['\"]?([a-z0-9-]+)['\"]?\s*$", content, re.M)
        if not match or match.group(1) != name or name in entries:
            raise ValueError(f"missing, mismatched or duplicate skill name: {line}")
        entries[name] = str(path.parent)
    if not entries or not all(any(p.startswith(d + "/") for p in entries.values()) for d in DOMAINS):
        raise ValueError("both standards domains must contain skills")
    return entries


def read_state(state: Path) -> dict:
    path = state / "lock.json"
    return json.loads(path.read_text()) if path.exists() else {}


def symlink_atomic(link: Path, target: Path) -> None:
    fd, temporary = tempfile.mkstemp(prefix=".standards-", dir=link.parent)
    os.close(fd)
    os.unlink(temporary)
    try:
        os.symlink(target, temporary, target_is_directory=True)
        os.replace(temporary, link)
    finally:
        if os.path.lexists(temporary):
            os.unlink(temporary)


def check_install(state: Path) -> dict:
    lock = read_state(state)
    if not lock:
        raise ValueError("no installed standards lock")
    snapshot = Path(lock["snapshot"]).resolve()
    if git(snapshot, "rev-parse", "HEAD") != lock["commit"]:
        raise ValueError("snapshot commit drift")
    if git(snapshot, "status", "--porcelain", "--untracked-files=all", "--", *DOMAINS):
        raise ValueError("installed standards snapshot has local changes")
    if not (state / "current").is_symlink() or (state / "current").resolve() != snapshot:
        raise ValueError("active version pointer drift")
    for name, entry in lock["skills"].items():
        link = Path(lock["dest"]) / name
        if not link.is_symlink() or os.readlink(link) != entry["link_target"]:
            raise ValueError(f"global skill link drift: {name}")
        if not (link / "SKILL.md").is_file():
            raise ValueError(f"broken global skill: {name}")
    return {"commit": lock["commit"], "skills": len(lock["skills"]), "status": "verified"}


def bind(repo: Path, ref: str, dest: Path, state: Path, apply: bool) -> dict:
    entries = catalog(repo, ref)
    previous = read_state(state)
    if previous and (previous["dest"] != str(dest) or previous["repository"] != str(repo)):
        raise ValueError("existing lock belongs to another repository or destination")
    old = previous.get("skills", {})
    if os.path.lexists(state / "current") and not (state / "current").is_symlink():
        raise ValueError("active pointer is an unmanaged directory")
    # Preflight every existing link before changing any global skill.
    for name in set(entries) | set(old):
        link = dest / name
        if os.path.lexists(link):
            if not link.is_symlink() or name not in old or os.readlink(link) != old[name]["link_target"]:
                raise ValueError(f"refusing to overwrite unmanaged skill: {link}")
    if previous:
        check_install(state)
    result = {"commit": ref, "skills": len(entries), "dest": str(dest), "apply": apply}
    if not apply:
        return result
    dest.mkdir(parents=True, exist_ok=True)
    state.mkdir(parents=True, exist_ok=True)
    guard = state / "install.lock"
    fd = os.open(guard, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    try:
        # Another installer may have completed between preview and lock acquisition.
        if read_state(state) != previous:
            raise ValueError("installation changed during preflight; preview again")
        snapshot = state / "versions" / ref
        snapshot.parent.mkdir(exist_ok=True)
        if snapshot.exists():
            if git(snapshot, "rev-parse", "HEAD") != ref or git(snapshot, "status", "--porcelain", "--untracked-files=all"):
                raise ValueError("existing snapshot is modified or has the wrong commit")
        else:
            subprocess.run(["git", "-C", str(repo), "worktree", "add", "--detach", str(snapshot), ref], check=True, stdout=subprocess.DEVNULL)
        active = state / "current"
        links = {name: {"path": path, "link_target": str(active / path)} for name, path in entries.items()}
        # Existing skills retain the old pointer while new links are prepared.
        for name, entry in links.items():
            if name not in old or entry["link_target"] != old[name]["link_target"]:
                symlink_atomic(dest / name, Path(entry["link_target"]))
        symlink_atomic(active, snapshot)
        for name in set(old) - set(entries):
            (dest / name).unlink()  # Only exact, previously owned symlinks passed preflight.
        if previous:
            history = state / "history"
            history.mkdir(exist_ok=True)
            (history / f"{previous['commit']}.json").write_text(json.dumps(previous, indent=2) + "\n")
        lock = {"schema_version": 1, "repository": str(repo), "commit": ref, "snapshot": str(snapshot), "dest": str(dest), "skills": links}
        temporary = state / "lock.json.next"
        temporary.write_text(json.dumps(lock, indent=2) + "\n")
        temporary.replace(state / "lock.json")
        return check_install(state)
    finally:
        guard.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--ref", help="full immutable commit SHA; never a moving branch")
    parser.add_argument("--dest", type=Path, default=Path.home() / ".agents/skills")
    parser.add_argument("--state", type=Path, default=Path.home() / ".agents/skill-sources/xworkspace-core-skills")
    parser.add_argument("--apply", action="store_true", help="apply; otherwise preview only")
    parser.add_argument("--check", action="store_true", help="verify installed commit, content and links")
    args = parser.parse_args()
    try:
        if args.check:
            if args.apply or args.ref:
                raise ValueError("--check cannot be combined with --ref or --apply")
            result = check_install(args.state.resolve())
        else:
            if not args.ref:
                raise ValueError("--ref is required")
            result = bind(args.repo.resolve(), args.ref, args.dest.resolve(), args.state.resolve(), args.apply)
        print(json.dumps(result, ensure_ascii=False))
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"error: {exc}\n")


if __name__ == "__main__":
    main()
