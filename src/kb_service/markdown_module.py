"""
Markdown Storage Module for the AI-Powered Knowledge Base System.

This module provides functionality for storing and retrieving knowledge as Markdown files.
"""

import os
import re
import shutil
from typing import Dict, List, Optional
from datetime import datetime

from src.core.config import MARKDOWN_ROOT_PATH
from src.core.logger import logger


class MarkdownModule:
    """
    Markdown Storage Module for storing and retrieving scientific paper knowledge as Markdown files.
    """

    def __init__(self, root_path: Optional[str] = None):
        """
        Initialize the Markdown Storage Module.

        Args:
            root_path: The root path for storing Markdown files
        """
        self.root_path = root_path or MARKDOWN_ROOT_PATH

        # Create the root directory if it doesn't exist
        os.makedirs(self.root_path, exist_ok=True)

        logger.info(
            f"Initialized Markdown Storage Module with root path: {self.root_path}"
        )

    def save(self, text: str, paper_title: str, doi: str = "") -> bool:
        """
        Save scientific paper knowledge to a Markdown file.

        Args:
            text: The text to save
            paper_title: The title of the scientific paper
            doi: The DOI of the paper (optional, used for filename if provided)

        Returns:
            True if the text was saved successfully, False otherwise
        """
        # Sanitize paper title for directory structure
        paper_dir = self._sanitize_name(paper_title)
        paper_path = os.path.join(self.root_path, paper_dir)
        os.makedirs(paper_path, exist_ok=True)
        # Use DOI as filename if provided, else use 'paper.md'
        file_name = f"{self._sanitize_name(doi)}.md" if doi else "paper.md"
        file_path = os.path.join(paper_path, file_name)
        try:
            header = (
                f"---\n"
                f"title: {paper_title}\n"
                f"doi: {doi}\n"
                f"last_updated: {datetime.now().isoformat()}\n"
                f"---\n\n"
            )
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(header + text)
            logger.info(
                f"Saved scientific paper knowledge for '{paper_title}' to {file_path}"
            )
            return True
        except Exception as e:
            logger.error(f"Error saving Markdown file: {str(e)}")
            return False

    def get_paper(self, paper_title: str, doi: str = "") -> str:
        """
        Get a scientific paper from a Markdown file.

        Args:
            paper_title: The title of the scientific paper
            doi: The DOI of the paper (optional)

        Returns:
            The content of the Markdown file
        """
        paper_dir = self._sanitize_name(paper_title)
        paper_path = os.path.join(self.root_path, paper_dir)
        file_name = f"{self._sanitize_name(doi)}.md" if doi else "paper.md"
        file_path = os.path.join(paper_path, file_name)
        try:
            if not os.path.exists(file_path):
                logger.warning(f"Markdown file not found: {file_path}")
                return ""
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            logger.info(
                f"Retrieved scientific paper '{paper_title}' (DOI: {doi}) from {file_path}"
            )
            content = re.sub(r"^---\n.*?---\n\n", "", content, flags=re.DOTALL)
            return content
        except Exception as e:
            error_msg = f"Error reading Markdown file: {str(e)}"
            logger.error(error_msg)
            return ""

    def delete(self, paper_title: str, doi: str = "") -> bool:
        """
        Delete a scientific paper knowledge file or directory.

        Args:
            paper_title: The title of the scientific paper
            doi: The DOI of the paper (optional)

        Returns:
            True if the deletion was successful, False otherwise
        """
        paper_dir = self._sanitize_name(paper_title)
        paper_path = os.path.join(self.root_path, paper_dir)
        if doi:
            file_name = f"{self._sanitize_name(doi)}.md"
            file_path = os.path.join(paper_path, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file {file_path}")
                if len(os.listdir(paper_path)) == 0:
                    os.rmdir(paper_path)
                    logger.info(f"Removed empty paper directory: {paper_path}")
                return True
            else:
                logger.warning(f"Markdown file not found: {file_path}")
                return False
        else:
            if os.path.exists(paper_path):
                shutil.rmtree(paper_path)
                logger.info(f"Deleted paper directory: {paper_path}")
                return True
            else:
                logger.warning(f"Paper directory not found: {paper_path}")
                return False

    def list_papers(self) -> list:
        """
        List all scientific papers stored in the Markdown module.

        Returns:
            A list of paper titles (directory names)
        """
        try:
            papers = [
                d
                for d in os.listdir(self.root_path)
                if os.path.isdir(os.path.join(self.root_path, d))
            ]
            logger.info(f"Listed {len(papers)} scientific papers")
            return papers
        except Exception as e:
            logger.error(f"Error listing papers: {str(e)}")
            return []

    def _sanitize_name(self, name: str) -> str:
        """
        Sanitize a name for use as a directory or file name.

        Args:
            name: The name to sanitize

        Returns:
            The sanitized name
        """
        # Replace spaces and special characters with underscores
        sanitized = re.sub(r"[^\w\s-]", "", name).strip().lower()
        sanitized = re.sub(r"[-\s]+", "_", sanitized)
        return sanitized
