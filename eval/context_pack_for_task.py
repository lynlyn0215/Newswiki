from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from service.app.context_pack import ContextPackBuilder
from service.app.repository import PublicExportRepository
from service.app.search import SearchService


def load_fixture(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "task" not in data:
        raise ValueError(f"{path} is missing task")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a Newswiki pre-plan context pack for an eval fixture.")
    parser.add_argument("fixture", type=Path, help="Path to eval/tasks/*.json")
    parser.add_argument("--export-dir", type=Path, default=ROOT / "examples" / "public")
    parser.add_argument("--token-budget", type=int, default=1200)
    args = parser.parse_args()

    fixture = load_fixture(args.fixture)
    repository = PublicExportRepository(args.export_dir)
    builder = ContextPackBuilder(SearchService(repository))
    pack = builder.build(
        fixture["task"],
        topic=fixture.get("topic"),
        token_budget=args.token_budget,
    )
    print(json.dumps(pack.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
