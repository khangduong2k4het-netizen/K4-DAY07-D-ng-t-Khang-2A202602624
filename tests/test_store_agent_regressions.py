from src import Document, EmbeddingStore, KnowledgeBaseAgent


def test_delete_all_chunks_preserves_explicit_parent_and_infers_suffix():
    store = EmbeddingStore(embedding_fn=lambda _: [1.0])
    store.add_documents([
        Document("alias#0", "a", {"doc_id": "file"}),
        Document("file#1", "b", {}),
        Document("other#0", "c", {}),
    ])
    assert store.delete_document("file")
    assert [r["id"] for r in store.search("q")] == ["other#0"]
    assert not store.delete_document("file")


def test_metadata_isolated_from_caller_and_search_results():
    store = EmbeddingStore(embedding_fn=lambda _: [1.0])
    metadata = {"tags": ["original"]}
    store.add_documents([Document("file", "text", metadata)])
    metadata["tags"].append("changed")
    result = store.search("q")[0]
    assert result["metadata"]["tags"] == ["original"]
    assert "embedding" not in result
    result["metadata"]["tags"].clear()
    assert store.search("q")[0]["metadata"]["tags"] == ["original"]


def test_filter_before_top_k_and_no_filter_equivalence():
    vectors = {"q": [1.0, 0.0], "staff": [1.0, 0.0], "student": [0.0, 1.0]}
    store = EmbeddingStore(embedding_fn=vectors.__getitem__)
    store.add_documents([Document("a", "staff", {"audience": "staff"}), Document("b", "student", {"audience": "student"})])
    assert store.search("q", 1)[0]["id"] == "a"
    assert store.search_with_filter("q", 1, {"audience": "student"})[0]["id"] == "b"
    assert store.search("q") == store.search_with_filter("q", 5, {}) == store.search_with_filter("q", 5, None)


def test_empty_store_does_not_call_embedder_or_llm():
    def unexpected(_):
        raise AssertionError("Unnecessary call")
    store = EmbeddingStore(embedding_fn=unexpected)
    assert KnowledgeBaseAgent(store, unexpected).answer("Question")


def test_agent_prompt_has_traceable_chunks_and_grounding():
    store = EmbeddingStore(embedding_fn=lambda _: [1.0])
    store.add_documents([Document("file#0", "Evidence text", {"source": "data/file.md"}), Document("file#1", "More evidence", {"source_url": "https://example.edu/policy"})])
    prompts = []
    def llm(prompt):
        prompts.append(prompt)
        return "Answer [1]"
    assert KnowledgeBaseAgent(store, llm).answer("Question", 2) == "Answer [1]"
    prompt = prompts[0]
    assert "[1] Source: data/file.md" in prompt
    assert "[2] Source: https://example.edu/policy" in prompt
    assert "Document: file; Chunk: file#0" in prompt
    assert "using only the provided context" in prompt
    assert "information was not found" in prompt
    assert "Question" in prompt and "Evidence text" in prompt
