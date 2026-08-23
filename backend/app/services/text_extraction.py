"""
Text extraction — pulls plain text (with page numbers where applicable)
out of an uploaded file's raw bytes, based on content_type.

Returns a list of (text, page_number) tuples so the chunker can preserve
page provenance for PDFs. For formats without a page concept (DOCX, TXT,
CSV), page_number is always None.
"""

import csv
import io

import pypdf
from docx import Document as DocxDocument

from app.models.document import Document


class UnsupportedContentTypeError(Exception):
    pass


def extract_text(document: Document, file_bytes: bytes) -> list[tuple[str, int | None]]:
    """
    Dispatches to the right extractor based on document.content_type.
    Returns a list of (text_segment, page_number) tuples.
    """
    content_type = document.content_type

    if content_type == "application/pdf":
        return _extract_pdf(file_bytes)

    if content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return _extract_docx(file_bytes)

    if content_type == "text/plain":
        return _extract_txt(file_bytes)

    if content_type == "text/csv":
        return _extract_csv(file_bytes)

    # XLSX intentionally not handled yet — raise so the pipeline marks
    # the document FAILED with a clear reason rather than silently
    # skipping it. Revisit if XLSX Q&A becomes a requirement.
    raise UnsupportedContentTypeError(
        f"No text extractor implemented for content_type='{content_type}'"
    )


def _extract_pdf(file_bytes: bytes) -> list[tuple[str, int | None]]:
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    segments = []
    for page_index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            segments.append((text, page_index + 1))
    return segments


def _extract_docx(file_bytes: bytes) -> list[tuple[str, int | None]]:
    doc = DocxDocument(io.BytesIO(file_bytes))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    full_text = "\n".join(paragraphs)
    return [(full_text, None)] if full_text else []


def _extract_txt(file_bytes: bytes) -> list[tuple[str, int | None]]:
    text = file_bytes.decode("utf-8", errors="ignore").strip()
    return [(text, None)] if text else []


def _extract_csv(file_bytes: bytes) -> list[tuple[str, int | None]]:
    text_io = io.StringIO(file_bytes.decode("utf-8", errors="ignore"))
    reader = csv.reader(text_io)
    rows = [", ".join(row) for row in reader]
    full_text = "\n".join(rows).strip()
    return [(full_text, None)] if full_text else []
