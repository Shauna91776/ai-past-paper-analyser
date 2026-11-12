
import pdfplumber


def extract_text_from_pdf(pdf_path: str) -> dict:
    """
    Extract text from every page of a PDF document.
    Returns the total page count and extracted text per page.
    """

    pages = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""

            pages.append({
                "page_number": page_number,
                "text": text
            })

    return {
        "total_pages": len(pages),
        "pages": pages
    }
