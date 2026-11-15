import ast, math, re
from collections import Counter
from pathlib import Path
from pydantic import BaseModel, Field


class CodeChunk(BaseModel):
    chunk_id: str
    file_path: str
    symbol_name: str
    kind: str
    start_line: int
    end_line: int
    content: str
    tokens: list[str] = Field(default_factory=list)


class SearchHit(BaseModel):
    chunk: CodeChunk
    score: float


def _tok(text: str) -> list[str]:
    spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    return [t for t in re.split(r"[^a-zA-Z0-9]+", spaced.lower()) if len(t) > 1]


class HybridCodeIndex:
    def __init__(self) -> None:
        self.chunks: list[CodeChunk] = []
        self._df: Counter[str] = Counter()
        self._avg_dl: float = 1.0

    def chunk_python_source(self, file_path: str, source: str) -> list[CodeChunk]:
        lines = source.splitlines()
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return self.chunk_text_document(file_path, source)
        out = [
            CodeChunk(
                chunk_id=f"{file_path}:{n.name}:{n.lineno}", file_path=file_path,
                symbol_name=n.name, kind="class" if isinstance(n, ast.ClassDef) else "function",
                start_line=n.lineno, end_line=getattr(n, "end_lineno", n.lineno),
                content="\n".join(lines[n.lineno - 1 : getattr(n, "end_lineno", n.lineno)]),
                tokens=_tok(f"{n.name} " + "\n".join(lines[n.lineno - 1 : getattr(n, "end_lineno", n.lineno)])),
            )
            for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        ]
        return out or self.chunk_text_document(file_path, source)

    def chunk_text_document(self, file_path: str, text: str, max_lines: int = 40) -> list[CodeChunk]:
        lines = text.splitlines()
        return [
            CodeChunk(
                chunk_id=f"{file_path}:doc:{i + 1}", file_path=file_path, symbol_name=f"sec_{i + 1}",
                kind="document", start_line=i + 1, end_line=min(len(lines), i + max_lines),
                content="\n".join(lines[i : i + max_lines]), tokens=_tok("\n".join(lines[i : i + max_lines])),
            )
            for i in range(0, max(1, len(lines)), max_lines) if "\n".join(lines[i : i + max_lines]).strip()
        ]


    def chunk_polyglot_source(self, file_path: str, source: str) -> list[CodeChunk]:
        """Extract functions, classes, structs, and interfaces across JS/TS, Go, Rust, C/C++, Java, and Shell."""
        lines = source.splitlines()
        patterns = [
            ("class", re.compile(r"^\s*(?:pub\s+|export\s+)?(?:abstract\s+)?(?:class|struct|interface|enum|trait)\s+([A-Za-z_][A-Za-z0-9_]*)")),
            ("class", re.compile(r"^\s*type\s+([A-Za-z_][A-Za-z0-9_]*)\s+(?:struct|interface)\b")),
            ("function", re.compile(r"^\s*(?:pub(?:\([^)]*\))?\s+|export\s+)?(?:async\s+)?(?:function|def|fn|func)\s+(?:\([^)]*\)\s*)?([A-Za-z_][A-Za-z0-9_]*)")),
            ("function", re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>")),
        ]
        hits: list[tuple[int, str, str]] = []
        for idx, line in enumerate(lines, start=1):
            for kind, pat in patterns:
                m = pat.match(line)
                if m:
                    hits.append((idx, kind, m.group(1)))
                    break
        if not hits:
            return self.chunk_text_document(file_path, source)
        chunks: list[CodeChunk] = []
        for i, (start_ln, kind, sym) in enumerate(hits):
            end_ln = hits[i + 1][0] - 1 if i + 1 < len(hits) else len(lines)
            end_ln = min(end_ln, start_ln + 60)
            snippet = "\n".join(lines[start_ln - 1 : end_ln])
            chunks.append(
                CodeChunk(
                    chunk_id=f"{file_path}:{sym}:{start_ln}",
                    file_path=file_path,
                    symbol_name=sym,
                    kind=kind,
                    start_line=start_ln,
                    end_line=end_ln,
                    content=snippet,
                    tokens=_tok(f"{sym} {snippet}"),
                )
            )
        return chunks

    def index_directory(self, root: str | Path, exts: tuple[str, ...] = (".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".c", ".cpp", ".sh", ".md", ".yaml", ".toml")) -> int:
        root_p, skip = Path(root), {".git", "__pycache__", ".venv", "venv", ".pytest_cache"}
        self.chunks.clear()
        for p in root_p.rglob("*"):
            if not p.is_file() or any(s in skip for s in p.parts) or p.suffix.lower() not in exts:
                continue
            txt = p.read_text(encoding="utf-8", errors="ignore")
            rel = str(p.relative_to(root_p))
            self.chunks.extend(self.chunk_python_source(rel, txt) if p.suffix == ".py" else self.chunk_text_document(rel, txt))
        self._df.clear()
        for ch in self.chunks:
            self._df.update(set(ch.tokens))
        self._avg_dl = sum(len(c.tokens) for c in self.chunks) / max(1, len(self.chunks))
        return len(self.chunks)

    def search(self, query: str, top_k: int = 5) -> list[SearchHit]:
        q = _tok(query)
        if not q or not self.chunks:
            return []
        n, hits = len(self.chunks), []
        for ch in self.chunks:
            tf, dl = Counter(ch.tokens), len(ch.tokens)
            bm25 = sum(
                math.log(1 + (n - self._df[t] + 0.5) / (self._df[t] + 0.5))
                * ((tf[t] * 2.5) / (tf[t] + 1.5 * (0.25 + 0.75 * dl / self._avg_dl)))
                for t in q if t in tf
            )
            cov = sum(1 for t in set(q) if t in tf) / len(set(q))
            if (score := round(bm25 + 0.5 * cov, 4)) > 0:
                hits.append(SearchHit(chunk=ch, score=score))
        return sorted(hits, key=lambda h: h.score, reverse=True)[:top_k]
