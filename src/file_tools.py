
from pathlib import Path
from xml.sax.saxutils import escape

from pypdf import PdfReader
from docx import Document
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


# --------------------------------------------------
# FOLDER CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSISTANT_FILES = PROJECT_ROOT / "data" / "assistant_files"

ASSISTANT_FILES.mkdir(parents=True, exist_ok=True)

SUPPORTED_EXTENSIONS = {
    ".txt", ".md", ".pdf", ".docx"
}

MAX_READ_SIZE = 10 * 1024 * 1024
MAX_OUTPUT_LENGTH = 15000


# --------------------------------------------------
# SAFE FILE PATH
# --------------------------------------------------

def get_safe_file_path(filename):

    name = Path(filename).name

    if name != filename or name in ("", ".", ".."):
        raise ValueError("Invalid filename.")

    path = (ASSISTANT_FILES / name).resolve()

    if path.parent != ASSISTANT_FILES.resolve():
        raise ValueError("File path is outside the assistant folder.")

    return path


# --------------------------------------------------
# TOOL 1: LIST FILES
# --------------------------------------------------

def list_assistant_files():

    files = []

    for path in ASSISTANT_FILES.iterdir():

        if path.is_file():
            files.append({
                "filename": path.name,
                "extension": path.suffix.lower(),
                "size_bytes": path.stat().st_size
            })

    return {
        "success": True,
        "folder": str(ASSISTANT_FILES),
        "files": files
    }


# --------------------------------------------------
# TOOL 2: READ DOCUMENTS
# --------------------------------------------------

def read_document(filename):

    try:
        path = get_safe_file_path(filename)

        if not path.exists() or not path.is_file():
            return {
                "success": False,
                "message": "File not found."
            }

        extension = path.suffix.lower()

        if extension not in SUPPORTED_EXTENSIONS:
            return {
                "success": False,
                "message": "Unsupported document format."
            }

        if path.stat().st_size > MAX_READ_SIZE:
            return {
                "success": False,
                "message": "File exceeds the 10 MB reading limit."
            }

        if extension in (".txt", ".md"):
            content = path.read_text(
                encoding="utf-8",
                errors="replace"
            )

        elif extension == ".pdf":
            reader = PdfReader(str(path))

            if reader.is_encrypted:
                return {
                    "success": False,
                    "message": "Encrypted PDFs are not supported."
                }

            content = "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            )

        elif extension == ".docx":
            document = Document(str(path))

            content = "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
            )

        else:
            content = ""

        if not content.strip():
            return {
                "success": False,
                "message": (
                    "No readable text found. The document may "
                    "contain scanned images instead of text."
                )
            }

        original_length = len(content)

        return {
            "success": True,
            "filename": filename,
            "content": content[:MAX_OUTPUT_LENGTH],
            "truncated": original_length > MAX_OUTPUT_LENGTH,
            "original_characters": original_length
        }

    except Exception as error:
        return {
            "success": False,
            "message": str(error)
        }


# --------------------------------------------------
# TOOL 3: CREATE DOCUMENTS
# --------------------------------------------------

def create_document(filename, content):

    try:
        path = get_safe_file_path(filename)
        extension = path.suffix.lower()

        if extension not in (".txt", ".md", ".pdf", ".docx"):
            return {
                "success": False,
                "message": "Supported formats: TXT, MD, PDF and DOCX."
            }

        if not content.strip():
            return {
                "success": False,
                "message": "Document content cannot be empty."
            }

        if len(content) > 50000:
            return {
                "success": False,
                "message": "Content exceeds the 50,000 character limit."
            }

        if path.exists():
            return {
                "success": False,
                "message": (
                    "A file with this name already exists. "
                    "Choose a different filename."
                )
            }

        # TXT and Markdown
        if extension in (".txt", ".md"):

            path.write_text(content, encoding="utf-8")

        # Word document
        elif extension == ".docx":

            document = Document()

            for line in content.splitlines():
                if line.strip():
                    document.add_paragraph(line)
                else:
                    document.add_paragraph("")

            document.save(str(path))

        # PDF document
        elif extension == ".pdf":

            pdf = SimpleDocTemplate(
                str(path),
                rightMargin=0.7 * inch,
                leftMargin=0.7 * inch,
                topMargin=0.7 * inch,
                bottomMargin=0.7 * inch
            )

            styles = getSampleStyleSheet()
            story = []

            for line in content.splitlines():

                if line.strip():
                    story.append(
                        Paragraph(
                            escape(line),
                            styles["BodyText"]
                        )
                    )
                    story.append(Spacer(1, 6))

            pdf.build(story)

        return {
            "success": True,
            "message": "Document created successfully.",
            "filename": filename,
            "file_path": str(path)
        }

    except Exception as error:
        return {
            "success": False,
            "message": str(error)
        }
