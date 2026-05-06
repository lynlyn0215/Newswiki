from __future__ import annotations

import re

from service.app.models import PublicItem
from service.app.repository import PublicExportRepository


def tokenize(query: str) -> list[str]:
    return [term.lower() for term in re.findall(r"[a-zA-Z0-9_-]{2,}", query)]


def score_item(item: PublicItem, terms: list[str]) -> int:
    haystack = " ".join(
        [
            item.title,
            item.summary,
            " ".join(item.topics),
            " ".join(str(value) for value in item.extra.values()),
        ]
    ).lower()
    return sum(haystack.count(term) for term in terms)


class SearchService:
    def __init__(self, repository: PublicExportRepository) -> None:
        self.repository = repository

    def search(self, collection: str, query: str, *, topic: str | None = None, limit: int = 10) -> list[PublicItem]:
        terms = tokenize(query)
        items = self.repository.load_collection(collection)
        if topic:
            items = [item for item in items if topic in item.topics]
        if not terms:
            return items[:limit]
        scored = [(score_item(item, terms), item) for item in items]
        matched = [(score, item) for score, item in scored if score > 0]
        matched.sort(key=lambda pair: (pair[0], pair[1].updated_at), reverse=True)
        return [item for _, item in matched[:limit]]

    def latest_signals(self, *, topic: str | None = None, limit: int = 10) -> list[PublicItem]:
        items = self.repository.load_collection("signals")
        if topic:
            items = [item for item in items if topic in item.topics]
        items.sort(key=lambda item: item.updated_at, reverse=True)
        return items[:limit]
