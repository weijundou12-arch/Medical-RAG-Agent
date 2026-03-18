from __future__ import annotations

from pathlib import Path
from pypdf import PdfReader


def parse_pdf(file_path: str | Path) -> str:
    reader = PdfReader(str(file_path))
    pages: list[str] = []
    for idx, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(f"[Page {idx}]\n{text}")
    return "\n\n".join(pages)
