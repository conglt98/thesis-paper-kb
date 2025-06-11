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
    Markdown Storage Module for storing and retrieving knowledge as Markdown files.
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

    def save(
        self,
        text: str,
        team_name: str,
        feature_name: str,
        knowledge_type: str = "business",
        source_id: str = "",
    ) -> bool:
        """
        Save knowledge to a Markdown file.

        Args:
            text: The text to save
            team_name: (ignored, kept for backward compatibility)
            feature_name: The full feature path (product/project/epic/feature)
            knowledge_type: The type of knowledge (business or technical)
            source_id: The file name (ticket_id)

        Returns:
            True if the text was saved successfully, False otherwise
        """
        # Split feature_name by "/" and sanitize each part for safe directory structure
        feature_parts = [self._sanitize_name(part) for part in feature_name.split("/")]
        feature_dir = "/".join(feature_parts)

        # Validate knowledge type
        if knowledge_type not in ["business", "technical"]:
            logger.error(f"Invalid knowledge type: {knowledge_type}")
            return False

        # Create the directory structure (no team_name)
        feature_path = os.path.join(self.root_path, feature_dir)
        os.makedirs(feature_path, exist_ok=True)

        # Create the file path: [source_id].md (ticket_id.md)
        file_name = f"{source_id}.md" if source_id else f"{knowledge_type}.md"
        file_path = os.path.join(feature_path, file_name)

        try:
            # Add a header with metadata
            header = (
                f"---\n"
                f"feature: {feature_name}\n"
                f"type: {knowledge_type}\n"
                f"last_updated: {datetime.now().isoformat()}\n"
                f"---\n\n"
            )

            # Write the file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(header + text)

            logger.info(
                f"Saved {knowledge_type} knowledge for {feature_name} to {file_path}"
            )
            return True

        except Exception as e:
            error_msg = f"Error saving Markdown file: {str(e)}"
            logger.error(error_msg)
            return False

    def get(
        self, team_name: str, feature_name: str, knowledge_type: str = "business"
    ) -> str:
        """
        Get knowledge from a Markdown file.

        Args:
            team_name: The name of the team
            feature_name: The name of the feature
            knowledge_type: The type of knowledge (business or technical)

        Returns:
            The content of the Markdown file
        """
        # Sanitize team and feature names for use as directory/file names
        team_dir = self._sanitize_name(team_name)
        feature_dir = self._sanitize_name(feature_name)

        # Validate knowledge type
        if knowledge_type not in ["business", "technical"]:
            logger.error(f"Invalid knowledge type: {knowledge_type}")
            return ""

        # Create the file path
        file_path = os.path.join(
            self.root_path, team_dir, feature_dir, f"{knowledge_type}.md"
        )

        try:
            # Check if the file exists
            if not os.path.exists(file_path):
                logger.warning(f"Markdown file not found: {file_path}")
                return ""

            # Read the file
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            logger.info(
                f"Retrieved {knowledge_type} knowledge for {feature_name} (team: {team_name}) from {file_path}"
            )

            # Remove the metadata header if present
            content = re.sub(r"^---\n.*?---\n\n", "", content, flags=re.DOTALL)

            return content

        except Exception as e:
            error_msg = f"Error reading Markdown file: {str(e)}"
            logger.error(error_msg)
            return ""

    def delete(
        self, team_name: str, feature_name: str, knowledge_type: Optional[str] = None
    ) -> bool:
        """
        Delete knowledge file(s) or an entire feature directory.

        Args:
            team_name: The name of the team
            feature_name: The name of the feature
            knowledge_type: The type of knowledge (business or technical)
                            If None, delete the entire feature directory

        Returns:
            True if the deletion was successful, False otherwise
        """
        # Sanitize team and feature names for use as directory/file names
        team_dir = self._sanitize_name(team_name)
        feature_dir = self._sanitize_name(feature_name)

        # Create the feature path
        feature_path = os.path.join(self.root_path, team_dir, feature_dir)

        try:
            # Check if the feature directory exists
            if not os.path.exists(feature_path):
                logger.warning(f"Feature directory not found: {feature_path}")
                return False

            # If knowledge_type is specified, delete only that file
            if knowledge_type:
                # Validate knowledge type
                if knowledge_type not in ["business", "technical"]:
                    logger.error(f"Invalid knowledge type: {knowledge_type}")
                    return False

                # Create the file path
                file_path = os.path.join(feature_path, f"{knowledge_type}.md")

                # Check if the file exists
                if not os.path.exists(file_path):
                    logger.warning(f"Markdown file not found: {file_path}")
                    return False

                # Delete the file
                os.remove(file_path)
                logger.info(
                    f"Deleted {knowledge_type} knowledge for {feature_name} (team: {team_name})"
                )

                # Check if the feature directory is now empty and remove it if it is
                if len(os.listdir(feature_path)) == 0:
                    os.rmdir(feature_path)
                    logger.info(f"Removed empty feature directory: {feature_path}")

                    # Check if the team directory is now empty and remove it if it is
                    team_path = os.path.join(self.root_path, team_dir)
                    if len(os.listdir(team_path)) == 0:
                        os.rmdir(team_path)
                        logger.info(f"Removed empty team directory: {team_path}")
            else:
                # Delete the entire feature directory
                shutil.rmtree(feature_path)
                logger.info(
                    f"Deleted entire feature directory for {feature_name} (team: {team_name})"
                )

                # Check if the team directory is now empty and remove it if it is
                team_path = os.path.join(self.root_path, team_dir)
                if os.path.exists(team_path) and len(os.listdir(team_path)) == 0:
                    os.rmdir(team_path)
                    logger.info(f"Removed empty team directory: {team_path}")

            return True

        except Exception as e:
            error_msg = f"Error deleting Markdown file/directory: {str(e)}"
            logger.error(error_msg)
            return False

    def list_features(self, team_name: Optional[str] = None) -> List[Dict[str, str]]:
        """
        List all features or features for a specific team.

        Args:
            team_name: The name of the team (optional)

        Returns:
            A list of feature dictionaries with team, feature, and available knowledge types
        """
        features = []

        try:
            # If team_name is provided, only look in that team's directory
            if team_name:
                team_dir = self._sanitize_name(team_name)
                team_path = os.path.join(self.root_path, team_dir)

                if not os.path.exists(team_path):
                    logger.warning(f"Team directory not found: {team_path}")
                    return []

                team_dirs = [team_dir]
            else:
                # List all team directories
                team_dirs = [
                    d
                    for d in os.listdir(self.root_path)
                    if os.path.isdir(os.path.join(self.root_path, d))
                ]

            # Iterate through team directories
            for team_dir in team_dirs:
                team_path = os.path.join(self.root_path, team_dir)

                # List all feature directories in the team directory
                feature_dirs = [
                    d
                    for d in os.listdir(team_path)
                    if os.path.isdir(os.path.join(team_path, d))
                ]

                # Iterate through feature directories
                for feature_dir in feature_dirs:
                    feature_path = os.path.join(team_path, feature_dir)

                    # Check which knowledge types are available
                    knowledge_types = []
                    if os.path.exists(os.path.join(feature_path, "business.md")):
                        knowledge_types.append("business")
                    if os.path.exists(os.path.join(feature_path, "technical.md")):
                        knowledge_types.append("technical")

                    # Add the feature to the list
                    features.append(
                        {
                            "team": team_dir,
                            "feature": feature_dir,
                            "knowledge_types": knowledge_types,
                        }
                    )

            logger.info(f"Listed {len(features)} features")
            return features

        except Exception as e:
            error_msg = f"Error listing features: {str(e)}"
            logger.error(error_msg)
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
