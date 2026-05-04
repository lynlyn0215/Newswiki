from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TEXT_EXTENSIONS = {
    ".md",
    ".py",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".txt",
    ".ps1",
    ".sql",
}

DENY_PATH_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    ".next",
    "dist",
    "build",
}

PATTERNS = {
    "private_windows_path": re.compile(r"C:\\Users\\(?!YOUR_USER|example)", re.IGNORECASE),
    "local_desktop_path": re.compile(r"C:/Users/(?!YOUR_USER|example)", re.IGNORECASE),
    "secret_assignment": re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}"),
    "private_runtime_file": re.compile(
        r"(?i)(session\.json|chrome-profile|pipeline_raw\.json|pipeline_processed\.json|collector_report\.json|pipeline-to-wiki-state\.json)"
    ),
}


def should_scan(path: Path) -> bool:
    if any(part in DENY_PATH_PARTS for part in path.parts):
        return False
    if path.name == "privacy_scan.py":
        return False
    return path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS


def main() -> int:
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        if not should_scan(path):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = path.relative_to(ROOT)
        for name, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                line = text.splitlines()[line_no - 1].lower()
                if "never commit" in line or "do not commit" in line:
                    continue
                findings.append(f"{rel}:{line_no}: {name}")

    if findings:
        print("Privacy scan failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print("Privacy scan passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
