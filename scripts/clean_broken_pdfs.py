"""
Script to check all PDF files in ./downloads and delete any that are corrupted (cannot be opened) or are 5MB or larger.

Usage:
    python scripts/clean_broken_pdfs.py

Requires PyPDF2. Install with:
    uv pip install PyPDF2
"""

import os
from PyPDF2 import PdfReader

DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "downloads")

MAX_PDF_SIZE = 5 * 1024 * 1024  # 5MB in bytes


def is_pdf_corrupted(filepath: str) -> bool:
    try:
        with open(filepath, "rb") as f:
            PdfReader(f)
        return False
    except Exception as e:
        print(f"[ERROR] Failed to open '{filepath}': {e}")
        return True


def main():
    deleted_corrupted = []
    deleted_large = []
    for filename in os.listdir(DOWNLOADS_DIR):
        if filename.lower().endswith(".pdf"):
            filepath = os.path.join(DOWNLOADS_DIR, filename)
            try:
                size = os.path.getsize(filepath)
            except Exception as e:
                print(f"[ERROR] Could not get size for '{filename}': {e}")
                continue
            if size >= MAX_PDF_SIZE:
                try:
                    os.remove(filepath)
                    print(f"[DELETED] Large PDF removed (>=5MB): {filename}")
                    deleted_large.append(filename)
                except Exception as e:
                    print(f"[ERROR] Could not delete '{filename}': {e}")
                continue  # Skip corruption check if already deleted
            if is_pdf_corrupted(filepath):
                try:
                    os.remove(filepath)
                    print(f"[DELETED] Corrupted PDF removed: {filename}")
                    deleted_corrupted.append(filename)
                except Exception as e:
                    print(f"[ERROR] Could not delete '{filename}': {e}")
    print(f"\nSummary: {len(deleted_corrupted) + len(deleted_large)} PDFs deleted.")
    if deleted_large:
        print(f"Large files (>=5MB) deleted: {len(deleted_large)}")
        for f in deleted_large:
            print(f"  - {f}")
    if deleted_corrupted:
        print(f"Corrupted files deleted: {len(deleted_corrupted)}")
        for f in deleted_corrupted:
            print(f"  - {f}")
    if not deleted_corrupted and not deleted_large:
        print("No corrupted or large PDFs found.")


if __name__ == "__main__":
    main()
