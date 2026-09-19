from __future__ import annotations

import json
from pathlib import Path

from src.chunking import FixedSizeChunker
from src.document_io import load_document
from src.embeddings import _mock_embed
from src.models import Document
from src.store import EmbeddingStore


def load_scholarship_chunks(base_dir: str | Path = "data/scholarships") -> list[Document]:
    base = Path(base_dir)
    chunker = FixedSizeChunker(chunk_size=500, overlap=60)
    docs: list[Document] = []

    for path in sorted(base.glob("*.md")):
        document = load_document(path)
        full_metadata = dict(document.metadata)
        full_metadata["doc_id"] = document.id
        chunks = chunker.chunk(document.content)
        for index, chunk in enumerate(chunks):
            chunk_metadata = dict(full_metadata)
            docs.append(
                Document(
                    id=f"{document.id}#{index}",
                    content=chunk.strip(),
                    metadata=chunk_metadata,
                )
            )
    return docs


def benchmark() -> str:
    queries = json.loads(Path("report/scholarship_queries.json").read_text(encoding="utf-8"))
    store = EmbeddingStore(collection_name="scholarship_benchmark", embedding_fn=_mock_embed)
    store.add_documents(load_scholarship_chunks())

    lines: list[str] = []
    lines.append("Scholarship Benchmark Report")
    lines.append(f"Collection size: {store.get_collection_size()}")
    lines.append(f"Embedding backend: mock embeddings fallback (MD5-based, semantic noise expected)")
    lines.append("")

    for query in queries:
        with_filter = store.search_with_filter(
            query["question"],
            top_k=3,
            metadata_filter=query.get("metadata_filter"),
        )
        without_filter = store.search(query["question"], top_k=3)

        lines.append(f"Query: {query['id']} - {query['question']}")
        lines.append(f"Gold answer: {query['gold_answer']}")
        lines.append(f"Expected doc ids: {query['expected_doc_ids']}")
        lines.append(f"Filter: {query.get('metadata_filter')}")

        lines.append("  WITH FILTER")
        for pos, item in enumerate(with_filter, start=1):
            lines.append(
                f"    {pos}. score={item['score']:.4f} doc_id={item['metadata'].get('doc_id')} "
                f"chunk={item['id']}"
            )

        lines.append("  WITHOUT FILTER")
        for pos, item in enumerate(without_filter, start=1):
            lines.append(
                f"    {pos}. score={item['score']:.4f} doc_id={item['metadata'].get('doc_id')} "
                f"chunk={item['id']}"
            )
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    print(benchmark())
