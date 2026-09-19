"""Read the flat string-valued YAML frontmatter used by the lab corpus."""

import json
import re
from pathlib import Path

from .models import Document


def load_document(path: str | Path) -> Document:
    path = Path(path)
    text = path.read_text(encoding="utf-8-sig")
    metadata = {"source": str(path), "extension": path.suffix.lower()}
    if text.startswith("---\n"):
        header, separator, text = text[4:].partition("\n---\n")
        if not separator:
            raise ValueError(f"Unclosed frontmatter: {path}")
        for line in header.splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            key, colon, value = line.partition(":")
            if not colon or not re.fullmatch(r"[a-z][a-z0-9_]*", key):
                raise ValueError(f"Expected flat YAML metadata in {path}: {line}")
            value = value.strip()
            if value.startswith('"'):
                value = json.loads(value)
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1].replace("''", "'")
            else:
                value = value.split(" #", 1)[0].strip()
                if value.startswith(("[", "{", "|", ">", "&", "*", "!")):
                    raise ValueError(f"Only scalar string metadata is supported: {path}")
            metadata[key] = value
    return Document(id=metadata.get("doc_id", path.stem), content=text.strip(), metadata=metadata)
