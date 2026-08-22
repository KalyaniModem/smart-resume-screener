import os
import re
import uuid
from pathlib import Path
from backend.config import settings
from backend.utils.logging_config import logger

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal security vulnerabilities."""
    # Remove directory path components
    basename = Path(filename).name
    # Keep only safe alphanumeric characters, underscores, hyphens, and dots
    clean_name = re.sub(r'[^a-zA-Z0-9_\.-]', '_', basename)
    return clean_name or "resume_file"

def save_uploaded_file(file_bytes: bytes, original_filename: str) -> Path:
    """Safely write uploaded file bytes to local storage with a unique prefix."""
    clean_name = sanitize_filename(original_filename)
    unique_filename = f"{uuid.uuid4().hex[:8]}_{clean_name}"
    target_path = settings.UPLOAD_DIR / unique_filename

    with open(target_path, "wb") as f:
        f.write(file_bytes)

    logger.info(f"Saved uploaded file to {target_path}")
    return target_path
