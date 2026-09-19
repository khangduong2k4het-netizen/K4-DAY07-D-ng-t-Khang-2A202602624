"""Validate collection integrity and gold-answer evidence, without a model/API."""
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.document_io import load_document


def main():
    root = Path("data/scholarships")
    sources = list(csv.DictReader((root / "sources.csv").open(encoding="utf-8")))
    inputs = list(csv.DictReader(Path("data/urls.csv").open(encoding="utf-8")))
    docs = {p.stem: load_document(p) for p in root.glob("*.md")}
    assert 5 <= len(docs) <= 10
    assert len(sources) == len(docs) == len(inputs)
    assert {r["doc_id"] for r in sources} == set(docs) == {r["doc_id"] for r in inputs}
    by_id = {r["doc_id"]: r for r in inputs}
    for row in sources:
        doc = docs[row["doc_id"]]
        assert doc.id == row["doc_id"]
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", doc.id)
        assert Path(row["file_path"]).resolve() == (root / f"{doc.id}.md").resolve()
        for key in ("doc_id", "title", "source_url", "retrieved_at", "document_version", "license_or_permission"):
            assert row[key] and row[key] == doc.metadata[key], (doc.id, key)
        for key, value in by_id[doc.id].items():
            assert doc.metadata["source_url" if key == "url" else key] == value
        date.fromisoformat(doc.metadata["retrieved_at"])
        assert doc.metadata["audience"] in {"student", "faculty", "staff", "all"}
        assert doc.metadata["language"] == "vi"
        assert doc.metadata["source_url"].startswith("https://dsa.ueh.edu.vn/")
        assert len(doc.content) > 80 and "\n## " in doc.content
        for noise in ("doc_id:", "Chuyển đến nội dung", "Danh Mục Tin", "jojobet", "casibom", "Search for:", "- - ", "\ufffd"):
            assert noise not in doc.content, (doc.id, noise)
    assert {d.metadata["audience"] for d in docs.values()} == {"student", "staff"}
    queries = json.loads(Path("report/scholarship_queries.json").read_text(encoding="utf-8"))
    assert len(queries) == 5
    for query in queries:
        eligible = {key for key, doc in docs.items() if all(doc.metadata.get(k) == v for k, v in query["metadata_filter"].items())}
        assert set(query["expected_doc_ids"]) <= eligible
        assert not (set(query.get("excluded_doc_ids", [])) & eligible)
        for item in query["evidence"]:
            assert item["quote"] in docs[item["doc_id"]].content, (query["id"], item)
        print(f"{query['id']}: evidence and audience filter verified")
    print(f"PASS: {len(docs)} documents, {len({r['source_url'] for r in sources})} sources, 2 audiences, 5 grounded queries")
    print("This validates corpus evidence, not embedding retrieval quality.")


if __name__ == "__main__":
    main()
