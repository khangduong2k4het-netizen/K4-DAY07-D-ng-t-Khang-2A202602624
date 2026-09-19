import pytest

from src.document_io import load_document


def test_frontmatter_is_metadata_not_retrieval_content(tmp_path):
    path = tmp_path / "scholarship.md"
    path.write_text('---\ndoc_id: "stable-id"\naudience: student\nlanguage: vi\n---\n\n# Học bổng\n\nĐiều kiện: 15 tín chỉ.\n', encoding="utf-8")
    doc = load_document(path)
    assert doc.id == "stable-id"
    assert doc.metadata["audience"] == "student"
    assert doc.content == "# Học bổng\n\nĐiều kiện: 15 tín chỉ."


def test_plain_document_still_loads(tmp_path):
    path = tmp_path / "plain.txt"
    path.write_text("Plain content", encoding="utf-8")
    doc = load_document(path)
    assert doc.id == "plain"
    assert doc.content == "Plain content"


def test_broken_frontmatter_fails_explicitly(tmp_path):
    path = tmp_path / "broken.md"
    path.write_text('---\naudience: student\n', encoding="utf-8")
    with pytest.raises(ValueError, match="Unclosed"):
        load_document(path)
