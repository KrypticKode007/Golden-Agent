from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Any, Iterator
from pydantic import BaseModel, Field


class SpanRecord(BaseModel):
    trace_id: str
    span_name: str
    worker: str = "system"
    duration_ms: float
    status: str = "ok"
    attributes: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentTracer:
    """Black-box flight recorder logging step latency, token spend, and outcomes to JSONL."""

    def __init__(self, log_path: str | Path = ".golden_memory/traces.jsonl") -> None:
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.spans: list[SpanRecord] = []

    @contextmanager
    def span(self, trace_id: str, span_name: str, worker: str = "system", **attrs: Any) -> Iterator[dict[str, Any]]:
        t0 = time.perf_counter()
        meta: dict[str, Any] = dict(attrs)
        status = "ok"
        try:
            yield meta
        except Exception as exc:
            status = "error"
            meta["error"] = str(exc)
            raise
        finally:
            ms = round((time.perf_counter() - t0) * 1000, 2)
            rec = SpanRecord(trace_id=trace_id, span_name=span_name, worker=worker, duration_ms=ms, status=status, attributes=meta)
            self.spans.append(rec)
            dump = rec.model_dump(mode="json") if hasattr(rec, "model_dump") else json.loads(rec.json())
            with self.log_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(dump) + "\n")
