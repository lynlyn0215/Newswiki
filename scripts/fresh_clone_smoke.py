from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_TESTS = [
    "tests.test_public_export_schema",
    "service.tests.test_health",
    "service.tests.test_search",
    "service.tests.test_context_pack",
    "service.tests.test_routes",
    "service.tests.test_mcp_contract",
]


def run(command: list[str], *, cwd: Path, name: str, report: dict[str, Any]) -> None:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    detail = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
    ok = completed.returncode == 0
    report["steps"].append({"name": name, "ok": ok, "detail": detail})
    if not ok:
        report["ok"] = False
        raise RuntimeError(f"{name} failed with exit code {completed.returncode}")


def clone_source(source: str, destination: Path, report: dict[str, Any]) -> None:
    source_path = Path(source).expanduser()
    clone_source_value = str(source_path.resolve()) if source_path.exists() else source
    run(["git", "clone", clone_source_value, str(destination)], cwd=destination.parent, name="clone repository", report=report)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fresh-clone smoke test for Newswiki.")
    parser.add_argument(
        "--source",
        default="https://github.com/lynlyn0215/Newswiki.git",
        help="Git URL or local repository path to clone.",
    )
    parser.add_argument("--workdir", help="Directory for the temporary clone. Defaults to a temp directory.")
    parser.add_argument("--target", help="Private instance target. Defaults to a temp directory.")
    parser.add_argument("--skip-install", action="store_true")
    parser.add_argument("--keep", action="store_true", help="Keep temp clone and private target after the run.")
    args = parser.parse_args()

    temp_root = Path(args.workdir).expanduser().resolve() if args.workdir else Path(tempfile.mkdtemp(prefix="newswiki-fresh-"))
    temp_root.mkdir(parents=True, exist_ok=True)
    clone_dir = temp_root / "Newswiki"
    target = Path(args.target).expanduser().resolve() if args.target else temp_root / "Newswiki-private"
    report: dict[str, Any] = {
        "ok": True,
        "source": args.source,
        "clone": str(clone_dir),
        "private_instance": str(target),
        "steps": [],
    }

    try:
        clone_source(args.source, clone_dir, report)
        if not args.skip_install:
            run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=clone_dir, name="install dependencies", report=report)
        else:
            report["steps"].append({"name": "install dependencies", "ok": True, "detail": "skipped"})

        run([sys.executable, "-m", "json.tool", "newswiki.setup.json"], cwd=clone_dir, name="validate setup manifest", report=report)
        run([sys.executable, "scripts/validate_public_export.py", "examples/public"], cwd=clone_dir, name="validate public export", report=report)
        run([sys.executable, "scripts/privacy_scan.py"], cwd=clone_dir, name="privacy scan", report=report)
        run(
            [sys.executable, "scripts/smoke_mcp_client.py", "--api-key", "local-key", "--export-dir", "examples/public"],
            cwd=clone_dir,
            name="hosted MCP smoke",
            report=report,
        )
        run(
            [sys.executable, "scripts/agent_setup_newswiki.py", "--target", str(target), "--skip-install"],
            cwd=clone_dir,
            name="agent-native setup smoke",
            report=report,
        )
        run([sys.executable, "-m", "unittest", *DEFAULT_TESTS], cwd=clone_dir, name="service tests", report=report)
    except Exception as exc:
        if report["ok"]:
            report["ok"] = False
            report["steps"].append({"name": "fresh clone smoke failed", "ok": False, "detail": str(exc)})
    finally:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if not args.keep and not args.workdir:
            shutil.rmtree(temp_root, ignore_errors=True)

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
