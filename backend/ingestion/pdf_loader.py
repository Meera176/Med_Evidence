import re
import fitz  # PyMuPDF


def load_pdf(path: str) -> tuple[str, dict[int, int]]:
    doc = fitz.open(path)
    pages = []
    page_offsets = {}
    cursor = 0

    for i, page in enumerate(doc):
        text = page.get_text()
        page_offsets[cursor] = i + 1
        pages.append(text)
        cursor += len(text) + 1  # +1 for the space separator

    full_text = " ".join(pages)
    return full_text, page_offsets


def clean_text(text: str) -> str:
    text = re.sub(r"-\n", "", text)        # rejoin hyphenated line breaks
    text = re.sub(r"\n", " ", text)        # flatten newlines
    text = re.sub(r"\s{2,}", " ", text)    # collapse extra whitespace
    return text.strip()


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[tuple[str, int]]:
    words = text.split()
    step = chunk_size - overlap
    chunks = []
    char_cursor = 0

    for i in range(0, len(words), step):
        chunk_words = words[i : i + chunk_size]
        chunk = " ".join(chunk_words)
        chunks.append((chunk, char_cursor))
        char_cursor += len(" ".join(words[i : i + step])) + 1

    return chunks


def resolve_page(char_offset: int, page_offsets: dict[int, int]) -> int:
    page = 1
    for offset, page_num in sorted(page_offsets.items()):
        if offset <= char_offset:
            page = page_num
    return page


def process_pdf(path: str) -> list[dict]:
    full_text, page_offsets = load_pdf(path)
    full_text = clean_text(full_text)

    chunks = chunk_text(full_text)
    source = path.split("\\")[-1].split("/")[-1]

    return [
        {
            "text": chunk,
            "source": source,
            "page": resolve_page(offset, page_offsets),
        }
        for chunk, offset in chunks
    ]
