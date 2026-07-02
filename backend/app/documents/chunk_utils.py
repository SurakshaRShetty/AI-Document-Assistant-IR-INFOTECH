def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    """Kept for backward compatibility (no page tracking)."""
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

    return chunks


def chunk_pages(pages: list[str], chunk_size: int = 1000, overlap: int = 200):
    """
    Chunks page-by-page so every chunk keeps its source page number.
    Returns a list of dicts: {chunk_index, page_number, text}
    """
    chunks = []
    chunk_index = 0

    for page_number, page_text in enumerate(pages, start=1):
        if not page_text.strip():
            continue

        start = 0
        while start < len(page_text):
            end = start + chunk_size
            piece = page_text[start:end]

            if piece.strip():
                chunks.append({
                    "chunk_index": chunk_index,
                    "page_number": page_number,
                    "text": piece,
                })
                chunk_index += 1

            start = end - overlap

    return chunks
