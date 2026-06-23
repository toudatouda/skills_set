import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "manage-skills.py"


def run_manage(tmp_path, manifest):
    manifest_path = tmp_path / "skills-manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    dest = tmp_path / "codex" / "skills"
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "install-missing",
            "--manifest",
            str(manifest_path),
            "--dest",
            str(dest),
        ],
        text=True,
        capture_output=True,
        check=False,
    ), dest


def test_installs_local_skills_and_skips_plugin(tmp_path):
    manifest = {
        "skills": [
            {"name": "orchestrator-workers", "type": "local", "required": True},
            {"name": "pdf:pdf", "type": "plugin", "required": False, "source": "runtime"},
        ]
    }

    result, dest = run_manage(tmp_path, manifest)

    assert result.returncode == 0, result.stderr
    assert (dest / "orchestrator-workers" / "SKILL.md").is_file()
    assert not (dest / "pdf" / "SKILL.md").exists()
    assert "Skipped pdf:pdf" in result.stdout


def test_detects_builtin_and_plugin_locations(tmp_path):
    dest = tmp_path / "codex" / "skills"
    builtin = dest / ".system" / "skill-installer"
    plugin = tmp_path / "codex" / "plugins" / "cache" / "vendor" / "pkg" / "1.0" / "skills" / "control-chrome"
    builtin.mkdir(parents=True)
    plugin.mkdir(parents=True)
    (builtin / "SKILL.md").write_text("---\nname: skill-installer\n---\n", encoding="utf-8")
    (plugin / "SKILL.md").write_text("---\nname: control-chrome\n---\n", encoding="utf-8")

    manifest = {
        "skills": [
            {"name": "skill-installer", "type": "builtin", "required": True},
            {
                "name": "chrome:control-chrome",
                "type": "plugin",
                "required": False,
                "directory": "control-chrome",
            },
        ]
    }
    manifest_path = tmp_path / "skills-manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "list",
            "--manifest",
            str(manifest_path),
            "--dest",
            str(dest),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "installed required builtin skill-installer" in result.stdout
    assert "installed optional plugin  chrome:control-chrome" in result.stdout


def test_doctor_reports_missing_required_with_failure_exit(tmp_path):
    manifest = {
        "skills": [
            {"name": "missing-local", "type": "local", "required": True},
            {"name": "browser:control-in-app-browser", "type": "plugin", "required": False},
        ]
    }
    manifest_path = tmp_path / "skills-manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "doctor",
            "--manifest",
            str(manifest_path),
            "--dest",
            str(tmp_path / "skills"),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "installable missing: missing-local" in result.stdout
    assert "plugin missing: browser:control-in-app-browser" in result.stdout
