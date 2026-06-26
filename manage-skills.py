#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_MANIFEST = ROOT / "skills-manifest.json"


@dataclass(frozen=True)
class Skill:
    name: str
    type: str
    required: bool
    source: str = ""
    directory: str = ""
    repo: str = ""
    path: str = ""
    ref: str = "main"
    description: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Skill":
        return cls(
            name=str(data["name"]),
            type=str(data["type"]),
            required=bool(data.get("required", False)),
            source=str(data.get("source", "")),
            directory=str(data.get("directory", "")),
            repo=str(data.get("repo", "")),
            path=str(data.get("path", "")),
            ref=str(data.get("ref", "main")),
            description=str(data.get("description", "")),
        )


def load_manifest(path: Path) -> list[Skill]:
    data = json.loads(path.read_text(encoding="utf-8"))
    skills = data.get("skills")
    if not isinstance(skills, list):
        raise ValueError(f"{path} must contain a 'skills' list")
    return [Skill.from_dict(item) for item in skills]


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def skills_dir() -> Path:
    return codex_home() / "skills"


def skill_dir_name(name: str) -> str:
    return name.split(":", 1)[-1]


def installed_path(skill: Skill, dest: Path) -> Path:
    return dest / skill_dir_name(skill.name)


def plugin_cache_dir(dest: Path) -> Path:
    return dest.parent / "plugins" / "cache"


def has_skill_md(path: Path) -> bool:
    return (path / "SKILL.md").is_file()


def find_skill_in_tree(root: Path, directory: str) -> bool:
    if not root.exists() or not directory:
        return False
    for skill_md in root.rglob("SKILL.md"):
        if skill_md.parent.name == directory:
            return True
    return False


def is_installed(skill: Skill, dest: Path) -> bool:
    if skill.type in {"local", "github", "manual"}:
        return has_skill_md(installed_path(skill, dest))
    if skill.type == "builtin":
        return has_skill_md(dest / ".system" / skill_dir_name(skill.name))
    if skill.type == "plugin":
        return find_skill_in_tree(plugin_cache_dir(dest), skill.directory or skill_dir_name(skill.name))
    return has_skill_md(installed_path(skill, dest))


def local_skill_path(skill: Skill) -> Path:
    return ROOT / skill_dir_name(skill.name)


def install_local(skill: Skill, dest: Path, dry_run: bool) -> None:
    source = local_skill_path(skill)
    if not (source / "SKILL.md").is_file():
        raise FileNotFoundError(f"local skill source missing: {source}")

    target = installed_path(skill, dest)
    if dry_run:
        print(f"Would install {skill.name} -> {target}")
        return

    dest.mkdir(parents=True, exist_ok=True)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    print(f"Installed {skill.name} -> {target}")


def github_url(skill: Skill) -> str:
    if not skill.repo or not skill.path:
        raise ValueError(f"github skill {skill.name} requires repo and path")
    return f"https://github.com/{skill.repo}.git"


def install_github(skill: Skill, dest: Path, dry_run: bool) -> None:
    install_github_many([skill], dest, dry_run)


def install_github_many(skills: list[Skill], dest: Path, dry_run: bool) -> None:
    if not skills:
        return

    repo = skills[0].repo
    ref = skills[0].ref
    if any(skill.repo != repo or skill.ref != ref for skill in skills):
        raise ValueError("github batch requires all skills to share repo and ref")

    for skill in skills:
        if not skill.repo or not skill.path:
            raise ValueError(f"github skill {skill.name} requires repo and path")

    if dry_run:
        for skill in skills:
            target = installed_path(skill, dest)
            print(f"Would install {skill.name} from {skill.repo}:{skill.path} -> {target}")
        return

    dest.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="codex-skill-") as tmp:
        checkout = Path(tmp) / "repo"
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--filter=blob:none",
                "--sparse",
                "--branch",
                ref,
                github_url(skills[0]),
                str(checkout),
            ],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(checkout), "sparse-checkout", "set", *[skill.path for skill in skills]],
            check=True,
        )
        for skill in skills:
            source = checkout / skill.path
            if not (source / "SKILL.md").is_file():
                raise FileNotFoundError(f"github skill source missing SKILL.md: {source}")
            target = installed_path(skill, dest)
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source, target)
            print(f"Installed {skill.name} -> {target}")


def github_batch_key(skill: Skill) -> tuple[str, str]:
    return (skill.repo, skill.ref)


def install_github_batches(skills: list[Skill], dest: Path, dry_run: bool) -> None:
    batches: dict[tuple[str, str], list[Skill]] = {}
    for skill in skills:
        batches.setdefault(github_batch_key(skill), []).append(skill)
    for batch in batches.values():
        install_github_many(batch, dest, dry_run)


def can_install(skill: Skill) -> bool:
    return skill.type in {"local", "github"}


def print_table(skills: list[Skill], dest: Path) -> None:
    for skill in skills:
        status = "installed" if is_installed(skill, dest) else "missing"
        required = "required" if skill.required else "optional"
        print(f"{status:9} {required:8} {skill.type:7} {skill.name}")


def doctor(skills: list[Skill], dest: Path) -> int:
    missing_required = False
    print_table(skills, dest)
    print()

    for skill in skills:
        if is_installed(skill, dest):
            continue
        if skill.required:
            missing_required = True
        if can_install(skill):
            print(f"installable missing: {skill.name}")
        elif skill.type == "plugin":
            print(f"plugin missing: {skill.name} ({skill.source or 'install matching plugin/runtime'})")
        elif skill.type == "builtin":
            print(f"builtin missing: {skill.name} (check Codex version/system skills)")
        else:
            print(f"manual missing: {skill.name} ({skill.description or 'manual setup required'})")

    return 1 if missing_required else 0


def install_missing(skills: list[Skill], dest: Path, dry_run: bool) -> int:
    skipped = []
    github = []
    for skill in skills:
        if is_installed(skill, dest):
            continue
        if skill.type == "local":
            install_local(skill, dest, dry_run)
        elif skill.type == "github":
            github.append(skill)
        else:
            skipped.append(skill)

    install_github_batches(github, dest, dry_run)

    for skill in skipped:
        print(f"Skipped {skill.name}: {skill.type} skills must be provided by Codex, plugins, or manual setup.")

    if not dry_run:
        print("Restart Codex to pick up new skills.")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Manage Codex skills from skills-manifest.json.")
    parser.add_argument("command", choices=["list", "doctor", "install-missing"])
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="Path to skills manifest JSON.")
    parser.add_argument("--dest", default=str(skills_dir()), help="Destination skills directory.")
    parser.add_argument("--dry-run", action="store_true", help="Show install actions without writing files.")
    args = parser.parse_args(argv)

    manifest = Path(args.manifest).expanduser().resolve()
    dest = Path(args.dest).expanduser().resolve()
    skills = load_manifest(manifest)

    if args.command == "list":
        print_table(skills, dest)
        return 0
    if args.command == "doctor":
        return doctor(skills, dest)
    if args.command == "install-missing":
        return install_missing(skills, dest, args.dry_run)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
