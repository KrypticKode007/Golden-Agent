import operator
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4
from pydantic import BaseModel, Field


class Episode(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:8])
    category: str
    summary: str
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EpisodicMemoryStore:
    def __init__(self, storage_path: str | Path = ".golden_memory/episodes.json") -> None:
        self.path = Path(storage_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        loader = getattr(Episode, "model_validate", None) or Episode.parse_obj
        self._items: list[Episode] = [loader(x) for x in json.loads(self.path.read_text())] if self.path.exists() else []

    def remember(self, category: str, summary: str, tags: list[str] | None = None) -> Episode:
        ep = Episode(category=category, summary=summary, tags=tags or [])
        self._items.append(ep)
        dump = [e.model_dump(mode="json") if hasattr(e, "model_dump") else json.loads(e.json()) for e in self._items]
        self.path.write_text(json.dumps(dump, indent=2))
        return ep

    def recall(self, query: str, limit: int = 5) -> list[Episode]:
        terms = {w.lower() for w in query.split() if len(w) > 2}
        if not terms:
            return self._items[-limit:]
        scored = [(sum(1 for t in terms if t in f"{e.category} {e.summary} {' '.join(e.tags)}".lower()), e) for e in self._items]
        return [e for s, e in sorted(scored, key=operator.itemgetter(0), reverse=True) if s > 0][:limit]
