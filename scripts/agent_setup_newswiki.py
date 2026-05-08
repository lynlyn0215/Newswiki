from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]


class SetupReport:
    def __init__(self, target: Path) -> None:
        self.data: dict[str, Any] = {
            "ok": True,
            "repo": str(REPO),
            "private_instance": str(target),
            "steps": [],
        }

    def add(self, name: str, ok: bool, detail: str = "") -> None:
        self.data["steps"].append({"name": name, "ok": ok, "detail": detail})
        if not ok:
            self.data["ok"] = False


def run_command(name: str, command: list[str], report: SetupReport, *, cwd: Path = REPO) -> None:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    detail = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
    if completed.returncode != 0:
        report.add(name, False, detail)
        raise RuntimeError(f"{name} failed with exit code {completed.returncode}")
    report.add(name, True, detail)


def copy_tree_contents(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        return
    for item in source.iterdir():
        target = destination / item.name
        if item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def initialize_private_instance(target: Path) -> None:
    dirs = [
        "data/news",
        "inbox",
        "logs",
        "outputs",
        "reports",
        "state",
        "wiki",
        "raw",
        "reviews",
        "config",
        "agents",
    ]
    for directory in dirs:
        (target / directory).mkdir(parents=True, exist_ok=True)

    copy_tree_contents(REPO / "templates/wiki/wiki", target / "wiki")
    shutil.copy2(REPO / "templates/wiki/AGENTS.md", target / "AGENTS.md")
    copy_tree_contents(REPO / "templates/config", target / "config")
    shutil.copy2(REPO / "templates/agents/startup-protocol.md", target / "agents/startup-protocol.md")
    shutil.copy2(REPO / "examples/capabilities.example.json", target / "capabilities.json")
    copy_tree_contents(REPO / "examples/news", target / "data/news")

    readme = f"""# Private Newswiki Instance

This directory is private by default.

Start:

1. Edit config/sources.example.yaml.
2. Edit config/pipeline.example.yaml.
3. Refresh capabilities when your local tools change:
   python "{REPO / 'scripts/build_capabilities.py'}" --output "{target / 'capabilities.json'}"
4. Configure the Newswiki MCP/input layers from config/mcp.example.toml.
5. Ask your agent to follow AGENTS.md and prefer get_context_for_task when available.
"""
    (target / "README.md").write_text(readme, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent-native cross-platform Newswiki bootstrap.")
    parser.add_argument("--target", required=True)
    parser.add_argument("--skip-install", action="store_true")
    parser.add_argument("--skip-capability-scan", action="store_true")
    parser.add_argument("--skip-hosted-smoke", action="store_true")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    report = SetupReport(target)

    try:
        if args.skip_install:
            report.add("install dependencies", True, "skipped")
        else:
            run_command("install dependencies", [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], report)

        initialize_private_instance(target)
        report.add("initialize private instance", True, f"Created private Newswiki instance at {target}")

        if args.skip_capability_scan:
            report.add("build capability catalog", True, "skipped")
        else:
            run_command(
                "build capability catalog",
                [
                    sys.executable,
                    str(REPO / "scripts/build_capabilities.py"),
                    "--output",
                    str(target / "capabilities.json"),
                ],
                report,
            )

        run_command(
            "validate public export examples",
            [sys.executable, str(REPO / "scripts/validate_public_export.py"), str(REPO / "examples/public")],
            report,
        )
        run_command("privacy scan public template", [sys.executable, str(REPO / "scripts/privacy_scan.py")], report)

        if args.skip_hosted_smoke:
            report.add("hosted MCP smoke", True, "skipped")
        else:
            run_command(
                "hosted MCP smoke",
                [
                    sys.executable,
                    str(REPO / "scripts/smoke_mcp_client.py"),
                    "--api-key",
                    "local-key",
                    "--export-dir",
                    str(REPO / "examples/public"),
                ],
                report,
            )
    except Exception as exc:
        if report.data["ok"]:
            report.add("setup failed", False, str(exc))
    finally:
        report_path = target / "setup-report.json"
        report_path.write_text(json.dumps(report.data, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Newswiki agent setup complete." if report.data["ok"] else "Newswiki agent setup failed.")
    print(f"Private instance: {target}")
    print(f"Setup report: {target / 'setup-report.json'}")
    return 0 if report.data["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
