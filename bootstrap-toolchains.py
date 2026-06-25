#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_MANIFEST = ROOT / "toolchains.json"


def load_manifest(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    tools = data.get("tools", [])
    if not isinstance(tools, list):
        raise ValueError("toolchains.json must contain a tools list")
    return tools


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def check_command(command: list[str]) -> bool:
    if not command or not command_exists(command[0]):
        return False
    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    return result.returncode == 0


def check_paths(paths: list[str]) -> bool:
    return bool(paths) and all(Path(path).expanduser().exists() for path in paths)


def is_installed(tool: dict[str, Any]) -> bool:
    checks = []
    command = tool.get("check")
    if isinstance(command, list):
        checks.append(check_command([str(part) for part in command]))
    paths = tool.get("check_paths")
    if isinstance(paths, list):
        checks.append(check_paths([str(path) for path in paths]))
    return any(checks)


def package_spec(install: dict[str, Any]) -> str:
    package = str(install["package"])
    version = install.get("version")
    return f"{package}@{version}" if version else package


def install_tool(tool: dict[str, Any], dry_run: bool) -> None:
    install = tool.get("install", {})
    install_type = install.get("type")
    name = tool["name"]
    if install_type == "npm-global":
        spec = package_spec(install)
        command = ["npm", "install", "-g", spec]
        registry = install.get("registry")
        if registry:
            command.extend(["--registry", str(registry)])
        if dry_run:
            print(f"Would install {name}: {' '.join(command)}")
            return
        subprocess.run(command, check=True)
        print(f"Installed {name}: {spec}")
        return
    if install_type == "codex-plugin":
        source = str(install["marketplace_source"])
        plugin = str(install["plugin"])
        marketplace = str(install.get("marketplace", ""))
        add_marketplace = ["codex", "plugin", "marketplace", "add", source]
        add_plugin = ["codex", "plugin", "add", f"{plugin}@{marketplace}" if marketplace else plugin]
        if dry_run:
            print(f"Would install {name}: {' '.join(add_marketplace)}")
            print(f"Would install {name}: {' '.join(add_plugin)}")
            return
        subprocess.run(add_marketplace, check=True)
        subprocess.run(add_plugin, check=True)
        print(f"Installed {name}: {plugin}{'@' + marketplace if marketplace else ''}")
        return
    print(f"Manual setup required for {name}: {install.get('summary', tool.get('notes', 'see toolchains.json'))}")


def doctor(tools: list[dict[str, Any]]) -> int:
    missing_required = False
    for tool in tools:
        installed = is_installed(tool)
        status = "installed" if installed else "missing"
        required = "required" if tool.get("required") else "optional"
        print(f"{status:9} {required:8} {tool.get('platform', 'any'):10} {tool['name']}")
        if not installed and tool.get("required"):
            missing_required = True
    return 1 if missing_required else 0


def install_missing(tools: list[dict[str, Any]], dry_run: bool) -> int:
    for tool in tools:
        if is_installed(tool):
            continue
        install_tool(tool, dry_run)
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Bootstrap non-skill Codex toolchains for a new environment.")
    parser.add_argument("command", choices=["doctor", "install", "install-missing"])
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    tools = load_manifest(Path(args.manifest).expanduser().resolve())
    if args.command == "doctor":
        return doctor(tools)
    if args.command in {"install", "install-missing"}:
        return install_missing(tools, args.dry_run)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))