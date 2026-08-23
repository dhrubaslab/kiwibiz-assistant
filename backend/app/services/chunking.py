"""
Chunking — splits extracted text segments into overlapping windows sized
for embedding. Character-based (not token-based) for simplicity; a rough
CHUNK_SIZE of 1000 chars with 150 char overlap works well as a starting
point for text-embedding-3-small and keeps answers groundable without
losing too much surrounding context at chunk boundaries.
"""

from dataclasses import dataclass

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


@dataclass
class Chunk:
    text: str
    page_number: int | None


def chunk_segments(segments: list[tuple[str, int | None]]) -> list[Chunk]:
    """
    Takes the (text, page_number) segments from text_extraction and produces
    a flat list of Chunk objects ready for embedding. Each segment (e.g. a
    PDF page) is chunked independently, so page_number stays accurate.
    """
    chunks: list[Chunk] = []

    for text, page_number in segments:
        if len(text) <= CHUNK_SIZE:
            chunks.append(Chunk(text=text, page_number=page_number))
            continue

        start = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            piece = text[start:end].strip()
            if piece:
                chunks.append(Chunk(text=piece, page_number=page_number))
            if end >= len(text):
                break
            start = end - CHUNK_OVERLAP

    return chunks
