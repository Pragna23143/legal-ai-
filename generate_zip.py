"""Standalone script to bundle the entire Legal AI Demystifier project into a ZIP archive."""

from pathlib import Path
import zipfile

BASE_DIR = Path(__file__).resolve().parent
PARENT_DIR = BASE_DIR.parent
ZIP_NAME = "legal-ai-demystifier.zip"

OUTPUT_PATHS = [
    BASE_DIR / ZIP_NAME,
    PARENT_DIR / ZIP_NAME
]

IGNORE_DIRS = {
    "__pycache__",
    ".git",
    ".pytest_cache",
    ".venv",
    "venv",
    "env",
    ".system_generated",
    "uploads"
}

IGNORE_EXTENSIONS = {".pyc", ".zip", ".tar", ".gz"}


def create_project_zip():
    print(f"Packaging project from {BASE_DIR}...")
    files_added = 0

    # Write to primary zip in base dir
    primary_zip = OUTPUT_PATHS[0]
    with zipfile.ZipFile(primary_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in BASE_DIR.rglob("*"):
            # Check exclusions
            parts = file_path.relative_to(BASE_DIR).parts
            if any(part in IGNORE_DIRS for part in parts):
                continue
            if file_path.suffix in IGNORE_EXTENSIONS:
                continue

            if file_path.is_file():
                arcname = str(Path("legal-ai-demystifier") / file_path.relative_to(BASE_DIR))
                zf.write(file_path, arcname=arcname)
                files_added += 1

    print(f"Successfully packaged {files_added} files into {primary_zip} ({primary_zip.stat().st_size / 1024:.1f} KB)")

    # Copy to scratch root as well for convenience
    scratch_zip = OUTPUT_PATHS[1]
    with open(primary_zip, "rb") as src, open(scratch_zip, "wb") as dst:
        dst.write(src.read())
    print(f"Also created copy at: {scratch_zip}")


if __name__ == "__main__":
    create_project_zip()
