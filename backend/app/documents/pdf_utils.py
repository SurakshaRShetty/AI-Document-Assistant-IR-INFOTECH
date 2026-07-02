from pypdf import PdfReader


def extract_text_from_pdf(file_path: str) -> str:
    """Kept for backward compatibility: full document text, no page info."""
    pages = extract_pages_from_pdf(file_path)
    return "\n".join(pages)


def extract_pages_from_pdf(file_path: str) -> list[str]:
    """Returns a list of page texts, index 0 = page 1."""
    reader = PdfReader(file_path)

    pages = []
    for page in reader.pages:
        page_text = page.extract_text()
        pages.append(page_text or "")

    return pages
