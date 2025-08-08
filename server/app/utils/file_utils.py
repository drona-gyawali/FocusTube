import csv
import io
import re
from typing import List

import PyPDF2
from openpyxl import load_workbook


def _extract_links_from_text(text: str) -> List[str]:
    """Extracts all URLs from plain text."""
    url_pattern = r"https?://[^\s]+"
    return re.findall(url_pattern, text)


def extract_file_link(file_bytes: bytes, filename: str) -> List[str]:
    """
    Detect file type by extension and extract URLs.
    Supports .txt, .csv, .xlsx, .pdf
    """
    filename = filename.lower()

    if filename.endswith(".txt"):
        text = file_bytes.decode("utf-8", errors="ignore")
        return _extract_links_from_text(text)

    elif filename.endswith(".csv"):
        text = file_bytes.decode("utf-8", errors="ignore")
        reader = csv.reader(io.StringIO(text))
        links = []
        for row in reader:
            for cell in row:
                links.extend(_extract_links_from_text(cell))
        return links

    elif filename.endswith(".xlsx"):
        workbook = load_workbook(io.BytesIO(file_bytes), read_only=True)
        links = []
        for sheet in workbook.worksheets:
            for row in sheet.iter_rows(values_only=True):
                for cell in row:
                    if cell:
                        links.extend(_extract_links_from_text(str(cell)))
        return links

    elif filename.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        links = []
        for page in pdf_reader.pages:
            text = page.extract_text() or ""
            links.extend(_extract_links_from_text(text))
        return links

    else:
        raise ValueError("Unsupported file type. Supported: .txt, .csv, .xlsx, .pdf")
