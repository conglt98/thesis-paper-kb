"""
Script to check all PDF files in ./downloads and delete any that are corrupted (cannot be opened).

Usage:
    python scripts/clean_broken_pdfs.py

Requires PyPDF2. Install with:
    uv pip install PyPDF2
"""

import os
from PyPDF2 import PdfReader

DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "downloads")


def is_pdf_corrupted(filepath: str) -> bool:
    try:
        with open(filepath, "rb") as f:
            PdfReader(f)
        return False
    except Exception as e:
        print(f"[ERROR] Failed to open '{filepath}': {e}")
        return True


def main():
    deleted = []
    for filename in os.listdir(DOWNLOADS_DIR):
        if filename.lower().endswith(".pdf"):
            filepath = os.path.join(DOWNLOADS_DIR, filename)
            if is_pdf_corrupted(filepath):
                try:
                    os.remove(filepath)
                    print(f"[DELETED] Corrupted PDF removed: {filename}")
                    deleted.append(filename)
                except Exception as e:
                    print(f"[ERROR] Could not delete '{filename}': {e}")
    print(f"\nSummary: {len(deleted)} corrupted PDFs deleted.")
    if deleted:
        print("Files deleted:")
        for f in deleted:
            print(f"  - {f}")
    else:
        print("No corrupted PDFs found.")


if __name__ == "__main__":
    main()
