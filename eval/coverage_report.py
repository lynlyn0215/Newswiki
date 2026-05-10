from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from service.app.context_pack import ContextPackBuilder
from service.app.repository import PublicExportRepository
from service.app.search import SearchService


def load_fixture(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


STOPWORDS = {
    "about",
    "after",
    "agent",
    "agents",
    "context",
    "newswiki",
    "product",
    "recent",
    "source",
    "source-backed",
    "sources",
    "tasks",
    "that",
    "this",
    "with",
}


def terms(value: str) -> set[str]:
    cleaned = "".join(char.lower() if char.isalnum() else " " for char in value)
    return {part for part in cleaned.split() if len(part) > 3 and part not in STOPWORDS}


def evidence_text(item: dict[str, Any]) -> str:
    evidence_fields = [
        "title",
        "summary",
        "source_claim",
        "newswiki_interpretation",
        "why_it_matters",
        "decision_impact",
        "affected_tasks",
        "data_limits",
        "key_points",
        "agent_fit",
        "install_hint",
        "source_kind",
        "source_published_at",
        "observed_at",
        "stale_after",
        "confidence",
        "source_confidence",
        "time_sensitivity",
    ]
    parts: list[str] = []
    for field in evidence_fields:
        value = item.get(field)
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(str(child) for child in value)
    return " ".join(parts)


def has_field(item: dict[str, Any], field: str) -> bool:
    value = item.get(field)
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value)
    return value is not None


def explicit_check_match(check: dict[str, Any], item: dict[str, Any]) -> bool:
    item_terms = terms(evidence_text(item))
    all_terms = set(check.get("all_terms", []))
    any_terms = set(check.get("any_terms", []))
    fields_present = check.get("fields_present", [])
    if not all_terms and not any_terms:
        return False
    if all_terms and not all_terms <= item_terms:
        return False
    if any_terms and not (any_terms & item_terms):
        return False
    if fields_present and not all(has_field(item, field) for field in fields_present):
        return False
    return bool(all_terms or any_terms or fields_present)


def expected_context_item_match(expected: str, item: dict[str, Any]) -> bool:
    expected_terms = terms(expected)
    if not expected_terms:
        return False
    item_terms = terms(evidence_text(item))
    if len(expected_terms) == 1:
        return bool(expected_terms & item_terms)
    matched = expected_terms & item_terms
    return len(matched) >= 2 or matched == expected_terms


def expected_context_coverage(expected_context: list[str], pack: dict[str, Any]) -> dict[str, bool]:
    items = [*pack["signals"], *pack["knowledge"], *pack["tools"]]
    coverage: dict[str, bool] = {}
    for expected in expected_context:
        coverage[expected] = any(expected_context_item_match(expected, item) for item in items)
    return coverage


def explicit_context_check_coverage(checks: list[dict[str, Any]], pack: dict[str, Any]) -> dict[str, bool]:
    items = [*pack["signals"], *pack["knowledge"], *pack["tools"]]
    coverage: dict[str, bool] = {}
    for check in checks:
        label = check["label"]
        coverage[label] = any(explicit_check_match(check, item) for item in items)
    return coverage


def source_quality_issues(pack: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for signal in pack["signals"]:
        for field in ["why_it_matters", "affected_tasks", "decision_impact", "last_verified_at", "stale_after", "entities", "source_confidence", "time_sensitivity", "data_limits"]:
            if field not in signal:
                issues.append(f"{signal['id']} missing {field}")
    for item in [*pack["knowledge"], *pack["tools"]]:
        if not item.get("source_urls"):
            issues.append(f"{item['id']} missing source_urls")
    return issues


def source_url_issues(pack: dict[str, Any], *, timeout: float) -> list[str]:
    issues: list[str] = []
    seen: set[str] = set()
    for item in [*pack["signals"], *pack["knowledge"], *pack["tools"]]:
        for url in item.get("source_urls", []):
            if url in seen:
                continue
            seen.add(url)
            request = Request(url, method="HEAD", headers={"User-Agent": "NewswikiEval/0.1"})
            try:
                with urlopen(request, timeout=timeout) as response:
                    if response.status >= 400:
                        issues.append(f"{item['id']} source_url {url} returned HTTP {response.status}")
            except HTTPError as exc:
                if exc.code in {403, 405}:
                    try:
                        fallback = Request(url, headers={"User-Agent": "NewswikiEval/0.1"})
                        with urlopen(fallback, timeout=timeout) as response:
                            if response.status >= 400:
                                issues.append(f"{item['id']} source_url {url} returned HTTP {response.status}")
                    except HTTPError as fallback_exc:
                        issues.append(f"{item['id']} source_url {url} returned HTTP {fallback_exc.code}")
                    except URLError as fallback_exc:
                        issues.append(f"{item['id']} source_url {url} failed: {fallback_exc.reason}")
                    except TimeoutError:
                        issues.append(f"{item['id']} source_url {url} timed out")
                else:
                    issues.append(f"{item['id']} source_url {url} returned HTTP {exc.code}")
            except URLError as exc:
                issues.append(f"{item['id']} source_url {url} failed: {exc.reason}")
            except TimeoutError:
                issues.append(f"{item['id']} source_url {url} timed out")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Newswiki context coverage across eval fixtures.")
    parser.add_argument("--tasks-dir", type=Path, default=ROOT / "eval" / "tasks")
    parser.add_argument("--export-dir", type=Path, default=ROOT / "examples" / "public")
    parser.add_argument("--check-source-urls", action="store_true", help="Also make network HEAD requests for cited source URLs.")
    parser.add_argument("--source-url-timeout", type=float, default=5.0)
    args = parser.parse_args()

    builder = ContextPackBuilder(SearchService(PublicExportRepository(args.export_dir)))
    rows: list[dict[str, Any]] = []
    for fixture_path in sorted(args.tasks_dir.glob("*.json")):
        fixture = load_fixture(fixture_path)
        pack = builder.build(fixture["task"], topic=fixture.get("topic")).to_dict()
        external_decision = pack["retrieval_decision"]["external_signals"]
        if fixture.get("expected_context_checks"):
            expected_coverage = explicit_context_check_coverage(fixture["expected_context_checks"], pack)
        else:
            expected_coverage = expected_context_coverage(fixture.get("expected_context", []), pack)
        missing_expected = [key for key, covered in expected_coverage.items() if not covered]
        quality_issues = source_quality_issues(pack)
        url_issues = source_url_issues(pack, timeout=args.source_url_timeout) if args.check_source_urls else []
        rows.append(
            {
                "id": fixture["id"],
                "topic": fixture.get("topic", ""),
                "expected_fresh": bool(fixture.get("needs_fresh_facts")),
                "detected_fresh": pack["needs_fresh_facts"],
                "external_status": external_decision["status"],
                "topic_matched": external_decision["topic_matched"],
                "fallback_used": external_decision["fallback_used"],
                "signals": len(pack["signals"]),
                "knowledge": len(pack["knowledge"]),
                "tools": len(pack["tools"]),
                "sources": len(pack["sources"]),
                "confidence": pack["confidence"],
                "expected_context_coverage": expected_coverage,
                "missing_expected_context": missing_expected,
                "source_quality_issues": quality_issues,
                "source_url_issues": url_issues,
            }
        )

    mismatches = [
        row["id"]
        for row in rows
        if row["expected_fresh"] != row["detected_fresh"]
    ]
    low_coverage = [
        row["id"]
        for row in rows
        if row["signals"] == 0 or row["sources"] == 0
    ]
    fallback_coverage = [row["id"] for row in rows if row["fallback_used"]]
    missing_expected_context = [row["id"] for row in rows if row["missing_expected_context"]]
    source_quality_failures = [row["id"] for row in rows if row["source_quality_issues"]]
    source_url_failures = [row["id"] for row in rows if row["source_url_issues"]]
    ok = not mismatches and not low_coverage and not fallback_coverage and not missing_expected_context and not source_quality_failures and not source_url_failures
    print(
        json.dumps(
            {
                "ok": ok,
                "freshness_mismatches": mismatches,
                "low_coverage": low_coverage,
                "fallback_coverage": fallback_coverage,
                "missing_expected_context": missing_expected_context,
                "source_quality_failures": source_quality_failures,
                "source_url_failures": source_url_failures,
                "tasks": rows,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
