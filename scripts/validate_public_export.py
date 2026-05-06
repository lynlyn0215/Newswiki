from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXPECTED_FILES = {
    "signals.example.json": "signals",
    "knowledge_pages.example.json": "knowledge_pages",
    "tool_cards.example.json": "tool_cards",
    "briefs.example.json": "briefs",
    "topics.example.json": "topics",
    "signals.json": "signals",
    "knowledge_pages.json": "knowledge_pages",
    "tool_cards.json": "tool_cards",
    "briefs.json": "briefs",
    "topics.json": "topics",
}

REQUIRED_FIELDS = {
    "id",
    "title",
    "summary",
    "source_urls",
    "topics",
    "updated_at",
    "freshness",
    "confidence",
    "public_safe",
}

VALID_FRESHNESS = {"live", "daily", "weekly", "archival"}
VALID_CONFIDENCE = {"low", "medium", "high"}

FORBIDDEN_FIELD_NAMES = {
    "body",
    "content",
    "raw_content",
    "full_text",
    "fulltext",
    "article_body",
    "private_notes",
    "internal_notes",
    "local_path",
    "local_paths",
    "notebook_state",
    "session_state",
    "api_key",
    "token",
    "password",
    "secret",
    "credential",
    "credentials",
}

PRIVATE_PATH_MARKERS = [
    "C:" + "\\Users" + "\\",
    "C:" + "/Users" + "/",
    "/Users/",
    "/home/",
]

PRIVATE_RUNTIME_MARKERS = [
    "chrome" + "-profile",
    "session" + ".json",
    "pipeline" + "_raw.json",
    "pipeline" + "_processed.json",
    "collector" + "_report.json",
    "pipeline" + "-to-wiki-state.json",
    ".notebook" + "lm",
]

SECRET_VALUE_RE = re.compile(
    r"(?i)(api[_-]?key|token|secret|password|credential)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}"
)


@dataclass
class ValidationError:
    file: str
    path: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"file": self.file, "path": self.path, "message": self.message}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def json_path(parent: str, key: str | int) -> str:
    if isinstance(key, int):
        return f"{parent}[{key}]"
    if not parent:
        return key
    return f"{parent}.{key}"


def is_public_url(value: str) -> bool:
    return value.startswith("https://") or value.startswith("http://")


def validate_string(value: str, *, file_name: str, path: str, errors: list[ValidationError]) -> None:
    for marker in PRIVATE_PATH_MARKERS:
        if marker in value:
            errors.append(ValidationError(file_name, path, "contains a local absolute path marker"))
    for marker in PRIVATE_RUNTIME_MARKERS:
        if marker.lower() in value.lower():
            errors.append(ValidationError(file_name, path, "contains a private runtime marker"))
    if SECRET_VALUE_RE.search(value):
        errors.append(ValidationError(file_name, path, "contains a secret-like assignment"))


def walk_forbidden(value: Any, *, file_name: str, path: str, errors: list[ValidationError]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = json_path(path, key)
            if key.lower() in FORBIDDEN_FIELD_NAMES:
                errors.append(ValidationError(file_name, child_path, "uses a forbidden field name"))
            walk_forbidden(child, file_name=file_name, path=child_path, errors=errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk_forbidden(child, file_name=file_name, path=json_path(path, index), errors=errors)
    elif isinstance(value, str):
        validate_string(value, file_name=file_name, path=path, errors=errors)


def validate_common_item(item: Any, *, file_name: str, collection: str, index: int, errors: list[ValidationError]) -> None:
    path = f"{collection}[{index}]"
    if not isinstance(item, dict):
        errors.append(ValidationError(file_name, path, "item must be an object"))
        return

    missing = sorted(REQUIRED_FIELDS - set(item))
    if missing:
        errors.append(ValidationError(file_name, path, f"missing required fields: {', '.join(missing)}"))

    if item.get("public_safe") is not True:
        errors.append(ValidationError(file_name, json_path(path, "public_safe"), "public_safe must be true"))

    source_urls = item.get("source_urls")
    if not isinstance(source_urls, list) or not source_urls:
        errors.append(ValidationError(file_name, json_path(path, "source_urls"), "source_urls must be a non-empty array"))
    else:
        for url_index, url in enumerate(source_urls):
            url_path = json_path(json_path(path, "source_urls"), url_index)
            if not isinstance(url, str) or not is_public_url(url):
                errors.append(ValidationError(file_name, url_path, "source URL must be http(s)"))

    topics = item.get("topics")
    if not isinstance(topics, list) or not topics or not all(isinstance(topic, str) and topic for topic in topics):
        errors.append(ValidationError(file_name, json_path(path, "topics"), "topics must be a non-empty string array"))

    if item.get("freshness") not in VALID_FRESHNESS:
        errors.append(ValidationError(file_name, json_path(path, "freshness"), "freshness has an invalid value"))

    if item.get("confidence") not in VALID_CONFIDENCE:
        errors.append(ValidationError(file_name, json_path(path, "confidence"), "confidence has an invalid value"))

    for field in ["id", "title", "summary", "updated_at"]:
        if field in item and (not isinstance(item[field], str) or not item[field].strip()):
            errors.append(ValidationError(file_name, json_path(path, field), f"{field} must be a non-empty string"))

    walk_forbidden(item, file_name=file_name, path=path, errors=errors)


def expected_collection_for(path: Path, data: Any) -> str | None:
    if path.name in EXPECTED_FILES:
        return EXPECTED_FILES[path.name]
    if isinstance(data, dict):
        matches = [key for key in EXPECTED_FILES.values() if key in data]
        if len(matches) == 1:
            return matches[0]
    return None


def validate_file(path: Path, root: Path) -> dict[str, Any]:
    rel = str(path.relative_to(root))
    errors: list[ValidationError] = []
    try:
        data = load_json(path)
    except json.JSONDecodeError as exc:
        return {"file": rel, "ok": False, "count": 0, "errors": [{"file": rel, "path": "$", "message": str(exc)}]}

    collection = expected_collection_for(path, data)
    if collection is None:
        errors.append(ValidationError(rel, "$", "cannot determine export collection"))
        return {"file": rel, "ok": False, "count": 0, "errors": [error.to_dict() for error in errors]}

    items = data.get(collection) if isinstance(data, dict) else None
    if not isinstance(items, list):
        errors.append(ValidationError(rel, collection, "collection must be an array"))
        items = []

    for index, item in enumerate(items):
        validate_common_item(item, file_name=rel, collection=collection, index=index, errors=errors)

    return {
        "file": rel,
        "collection": collection,
        "ok": not errors,
        "count": len(items),
        "errors": [error.to_dict() for error in errors],
    }


def find_json_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(file for file in path.rglob("*.json") if file.is_file())


def validate(path: Path) -> dict[str, Any]:
    root = path if path.is_dir() else path.parent
    files = find_json_files(path)
    file_reports = [validate_file(file, root) for file in files]
    errors = [error for report in file_reports for error in report["errors"]]
    return {
        "ok": not errors,
        "root": str(root),
        "files": file_reports,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Newswiki public-safe export JSON.")
    parser.add_argument("path", nargs="?", default="examples/public")
    args = parser.parse_args()

    report = validate(Path(args.path))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
