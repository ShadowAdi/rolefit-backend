import re
from typing import Optional, List
from datetime import datetime
from pydantic import ValidationError, field_validator, BaseModel


class PublicationValidator(BaseModel):
    """Validators for Publication model"""

    @staticmethod
    def validate_title(v: str) -> str:
        """Validate publication title"""
        if not v or not v.strip():
            raise ValueError("Publication title cannot be empty")

        if len(v) < 3:
            raise ValueError("Publication title must be at least 3 characters long")

        if len(v) > 500:
            raise ValueError("Publication title must not exceed 500 characters")

        return v.strip()

    @staticmethod
    def validate_publisher(v: str) -> str:
        """Validate publisher name"""
        if not v or not v.strip():
            raise ValueError("Publisher name cannot be empty")

        if len(v) < 2:
            raise ValueError("Publisher name must be at least 2 characters long")

        if len(v) > 255:
            raise ValueError("Publisher name must not exceed 255 characters")

        return v.strip()

    @staticmethod
    def validate_publication_date(v: datetime) -> datetime:
        """Validate publication date"""
        if not isinstance(v, datetime):
            raise ValueError("Publication date must be a datetime object")

        # Publication date should not be in the future
        if v > datetime.now():
            raise ValueError("Publication date cannot be in the future")

        return v

    @staticmethod
    def validate_authors(v: List[str]) -> List[str]:
        """Validate authors list"""
        if not isinstance(v, list):
            raise ValueError("Authors must be a list")

        if len(v) == 0:
            raise ValueError("At least one author is required")

        if len(v) > 100:
            raise ValueError("Cannot exceed 100 authors")

        validated_authors = []
        for author in v:
            if not isinstance(author, str):
                raise ValueError("Each author must be a string")

            author = author.strip()
            if not author:
                raise ValueError("Author names cannot be empty")

            if len(author) < 2:
                raise ValueError(
                    f"Author name '{author}' must be at least 2 characters long"
                )

            if len(author) > 255:
                raise ValueError(
                    f"Author name '{author}' must not exceed 255 characters"
                )

            # Allow letters, spaces, hyphens, and apostrophes
            if not re.match(r"^[a-zA-Z\s\-'.]+$", author):
                raise ValueError(
                    f"Author name '{author}' contains invalid characters. Use letters, spaces, hyphens, and apostrophes."
                )

            validated_authors.append(author)

        # Check for duplicates
        if len(validated_authors) != len(set(validated_authors)):
            raise ValueError("Duplicate author names detected")

        return validated_authors

    @staticmethod
    def validate_description(v: Optional[str]) -> Optional[str]:
        """Validate publication description"""
        if v is None:
            return None

        if not v.strip():
            return None

        if len(v) < 10:
            raise ValueError("Description must be at least 10 characters long")

        if len(v) > 2000:
            raise ValueError("Description must not exceed 2000 characters")

        return v.strip()

    @staticmethod
    def validate_url(v: Optional[str]) -> Optional[str]:
        """Validate publication URL"""
        if v is None:
            return None

        if not v.strip():
            return None

        v = v.strip()

        if len(v) > 2000:
            raise ValueError("URL must not exceed 2000 characters")

        # Validate URL format
        url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"

        if not re.match(url_pattern, v):
            raise ValueError(f"Invalid URL format: {v}")

        return v

    @staticmethod
    def validate_author_in_profile(
        authors: List[str], profile_full_name: Optional[str] = None
    ) -> List[str]:
        """Validate that at least one author is the profile owner (optional validation)"""
        # This is optional - implement if needed to ensure profile owner is listed as author
        if profile_full_name and profile_full_name not in authors:
            # Could warn but not fail - uncomment if strict validation needed
            # raise ValueError(f"Profile owner '{profile_full_name}' should be listed as an author")
            pass

        return authors
