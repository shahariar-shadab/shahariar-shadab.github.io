"""Extract text from the newest resume PDF in content/resume/.

Writes .tmp/resume.txt (one "=== page N ===" block per page) so the agent can
compare it with content/site.json. Pages with almost no text (a title/cover
page) are reported as "cover" — build_site.py drops those from the download.

Usage:  .venv/bin/python tools/extract_resume.py
"""
from pathlib import Path
import sys

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
RESUME_DIR = ROOT / "content" / "resume"
OUT = ROOT / ".tmp" / "resume.txt"

# A page with fewer characters than this is treated as a cover/title page.
COVER_PAGE_MAX_CHARS = 200


def newest_resume() -> Path:
    pdfs = sorted(RESUME_DIR.glob("*.pdf"), key=lambda p: p.stat().st_mtime)
    if not pdfs:
        sys.exit(f"No PDF found in {RESUME_DIR}")
    return pdfs[-1]


def content_pages(reader: PdfReader) -> list[int]:
    """Indexes of pages that carry real content (cover pages skipped)."""
    keep = [i for i, page in enumerate(reader.pages)
            if len((page.extract_text() or "").strip()) >= COVER_PAGE_MAX_CHARS]
    return keep or list(range(len(reader.pages)))


def main() -> None:
    pdf = newest_resume()
    reader = PdfReader(pdf)
    keep = set(content_pages(reader))

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as f:
        f.write(f"# Source: {pdf.name}\n")
        for i, page in enumerate(reader.pages):
            tag = "" if i in keep else " (cover — dropped from download)"
            f.write(f"\n=== page {i + 1}{tag} ===\n{page.extract_text() or ''}\n")

    dropped = [i + 1 for i in range(len(reader.pages)) if i not in keep]
    print(f"{pdf.name}: {len(reader.pages)} pages, cover pages dropped: {dropped or 'none'}")
    print(f"Text written to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
