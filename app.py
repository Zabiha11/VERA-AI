import joblib
from pathlib import Path
from uuid import UUID, uuid4
from threading import Lock
import sqlite3
from flask import Flask, render_template, jsonify, request
from werkzeug.exceptions import RequestEntityTooLarge
from faster_whisper import WhisperModel
from datetime import datetime 
import re
from src.agent import (
    run_agent,
    save_conversation_turn,
    get_conversation_history,
    CONVERSATION_DB
)
import traceback

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
DB_PATH = BASE_DIR / "data" / "vera.db"

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        connection.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                due_at TEXT,
                created_at TEXT NOT NULL,
                completed INTEGER DEFAULT 0
            )
        """)
        connection.commit()
    finally:
        connection.close()

def extract_note_content(text):
    patterns = [
        r"^(?:vera[, ]+)?(?:please\s+)?save\s+(?:a\s+)?note(?:\s+that|\s+about)?\s*",
        r"^(?:vera[, ]+)?(?:please\s+)?make\s+(?:a\s+)?note(?:\s+that|\s+about)?\s*",
        r"^(?:vera[, ]+)?(?:please\s+)?write\s+(?:a\s+)?note(?:\s+that|\s+about)?\s*",
        r"^(?:vera[, ]+)?(?:please\s+)?remember\s+that\s*"
    ]

    for pattern in patterns:
        match = re.match(pattern, text.strip(), flags=re.IGNORECASE)

        if match:
            return text.strip()[match.end():].strip(" .,!؟")

    return ""

def extract_reminder_content(text):
    patterns = [
        r"^(?:vera[, ]+)?(?:please\s+)?remind me to\s+",
        r"^(?:vera[, ]+)?(?:please\s+)?set (?:a )?reminder to\s+",
        r"^(?:vera[, ]+)?(?:please\s+)?create (?:a )?reminder to\s+"
    ]

    for pattern in patterns:
        match = re.match(pattern, text.strip(), flags=re.IGNORECASE)

        if match:
            return text.strip()[match.end():].strip(" .,!؟")

    return ""

def extract_note_number(text):
    text = text.lower().strip()

    number_words = {
        "first": 1,
        "one": 1,
        "second": 2,
        "two": 2,
        "third": 3,
        "three": 3,
        "fourth": 4,
        "four": 4,
        "fifth": 5,
        "five": 5,
        "sixth": 6,
        "six": 6,
        "seventh": 7,
        "seven": 7,
        "eighth": 8,
        "eight": 8,
        "ninth": 9,
        "nine": 9,
        "tenth": 10,
        "ten": 10
    }

    match = re.search(
        r"\b(?:note\s+)?(?:number|no\.?)\s*(\d+)\b",
        text
    )

    if match:
        return int(match.group(1))

    for word, number in number_words.items():
        if re.search(rf"\b{word}\b", text):
            return number

    return None

init_db()

app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Load the model only when transcription is first requested.
whisper_model = None
model_lock = Lock()
transcription_lock = Lock()

ALLOWED_TYPES = {
    "audio/webm": ".webm",
    "audio/mp4": ".mp4",
    "application/octet-stream": ".bin",
}

INTENT_MODEL_PATH = BASE_DIR / "models" / "intent_classifier.joblib"

intent_model = None
intent_model_lock = Lock()


def get_intent_model():
    global intent_model

    if intent_model is None:
        with intent_model_lock:
            if intent_model is None:
                if not INTENT_MODEL_PATH.is_file():
                    raise FileNotFoundError(
                        "Intent model not found. "
                        "Run python src/train_intent.py first."
                    )

                intent_model = joblib.load(INTENT_MODEL_PATH)

    return intent_model


def get_whisper_model():
    global whisper_model

    if whisper_model is None:
        with model_lock:
            if whisper_model is None:
                whisper_model = WhisperModel(
                    "base",
                    device="cpu",
                    compute_type="int8",
                )

    return whisper_model


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/health")
def health_check():
    return jsonify({"app": "VERA", "status": "running"})


@app.route("/api/upload-audio", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file was provided."}), 400

    audio = request.files["audio"]

    if not audio.filename:
        return jsonify({"error": "The audio filename is missing."}), 400

    content_type = audio.mimetype.lower()
    extension = ALLOWED_TYPES.get(content_type)

    if extension is None:
        return jsonify({
            "error": f"Unsupported audio type: {content_type}"
        }), 415

    filename = f"{uuid4().hex}{extension}"
    destination = UPLOAD_DIR / filename
    audio.save(destination)

    size_bytes = destination.stat().st_size

    if size_bytes == 0:
        destination.unlink(missing_ok=True)
        return jsonify({"error": "The uploaded audio file is empty."}), 400

    return jsonify({
        "message": "Audio uploaded successfully.",
        "filename": filename,
        "size_bytes": size_bytes,
        "content_type": content_type,
    }), 200


@app.route("/api/transcribe", methods=["POST"])
def transcribe_audio():
    data = request.get_json(silent=True) or {}
    filename = data.get("filename")

    if not isinstance(filename, str) or not filename:
        return jsonify({
            "error": "Provide the filename returned by the upload endpoint."
        }), 400

    # Accept only a filename, never a client-supplied path.
    if Path(filename).name != filename:
        return jsonify({"error": "Invalid filename."}), 400

    if Path(filename).suffix.lower() not in {".webm", ".mp4", ".bin"}:
        return jsonify({"error": "Unsupported audio file extension."}), 415

    audio_path = UPLOAD_DIR / filename

    if not audio_path.is_file():
        return jsonify({
            "error": "Recording not found. Upload the audio again."
        }), 404

    if audio_path.stat().st_size == 0:
        return jsonify({"error": "The audio file is empty."}), 400

    try:
        # Avoid multiple simultaneous transcriptions in this first version.
        with transcription_lock:
            model = get_whisper_model()

            segments, info = model.transcribe(
                str(audio_path),
                language="en",
                beam_size=3,
                vad_filter=True,
            )

            # Transcription starts when the generator is consumed.
            segments = list(segments)

        transcript = " ".join(
            segment.text.strip()
            for segment in segments
            if segment.text.strip()
        ).strip()

        if not transcript:
            return jsonify({
                "error": (
                    "No speech was detected. Try recording again "
                    "in a quiet environment."
                )
            }), 422

        return jsonify({
            "filename": filename,
            "text": transcript,
            "language": info.language,
            "language_probability": round(
                info.language_probability, 3
            ),
            "duration_seconds": round(info.duration, 2),
        }), 200

    except Exception:
        app.logger.exception("VERA transcription failed")
        return jsonify({
            "error": (
                "Transcription failed. Check the audio format, "
                "model download, and Flask terminal for details."
            )
        }), 500


def detect_rule_intent(text):
    text = " ".join(text.lower().strip().split())

    # Check specific requests before general greetings
    if any(phrase in text for phrase in [
        "current time", "what time", "time is it",
        "tell me the time", "time right now", "time now"
    ]):
        return "get_time"

    if any(phrase in text for phrase in [
        "today's date", "current date", "what date",
        "what day is it", "tell me the date"
    ]):
        return "get_date"

    if any(phrase in text for phrase in [
        "show my notes", "list my notes",
        "view my notes", "display my notes"
    ]):
        return "list_notes"

    if any(phrase in text for phrase in [
        "show my reminders", "list my reminders",
        "view my reminders"
    ]):
        return "list_reminders"

    if any(phrase in text for phrase in [
        "set a reminder", "remind me", "create a reminder"
    ]):
        return "set_reminder"

    if any(phrase in text for phrase in [
        "save a note", "save note", "make a note",
        "remember that", "write a note"
    ]):
        return "save_note"

    if any(phrase in text for phrase in [
        "goodbye", "see you later", "bye vera", "exit vera"
    ]):
        return "goodbye"

    # Only classify a simple greeting as a greeting.
    greetings = {
        "hello", "hi", "hey", "hello vera",
        "hi vera", "hey vera", "good morning",
        "good afternoon", "good evening"
    }

    if text in greetings:
        return "greeting"
    
    if any(phrase in text for phrase in [
        "delete note", "delete my note",
        "remove note", "remove my note",
        "erase note", "erase my note"
    ]):
        return "delete_note"

    return None


@app.route("/api/intent", methods=["POST"])
def classify_intent():
    data = request.get_json(silent=True) or {}
    text = data.get("text")

    if not isinstance(text, str) or not text.strip():
        return jsonify({
            "error": "Provide some text for intent classification."
        }), 400

    text = text.strip()

    if len(text) > 1000:
        return jsonify({
            "error": "Text is too long. Please use a shorter request."
        }), 400

    rule_intent = detect_rule_intent(text)

    if rule_intent:
        return jsonify({
            "intent": rule_intent,
            "confidence": 1.0,
            "needs_clarification": False,
            "method": "rule"
        }), 200

    # Route unknown requests to the Groq AI agent
    return jsonify({
        "text": text,
        "intent": "ai_agent",
        "confidence": None,
        "needs_clarification": False,
        "method": "agent",
        "message": "VERA will process this request using its AI agent."
    }), 200


@app.route("/api/execute", methods=["POST"])
def execute_action():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")

    if not isinstance(text, str) or not text.strip():
        return jsonify({
            "error": "Please provide some text."
        }), 400

    text = text.strip()

    if len(text) > 1000:
        return jsonify({
            "error": "Text is too long."
        }), 400
    # Get or create a conversation ID
    conversation_id = data.get("conversation_id")

    try:
        conversation_id = str(UUID(str(conversation_id))) if conversation_id else str(uuid4())
    except ValueError:
        return jsonify({"error": "Invalid conversation ID."}), 400
    
    # Step 1: Check known rule-based commands
    intent = detect_rule_intent(text)

    # Step 2: Send all other requests to Groq
    if intent is None:
        try:
            result = run_agent(
                text,
                conversation_id=conversation_id
            )

            return jsonify({
                "success": True,
                "intent": "ai_agent",
                "response": result,
                "conversation_id": conversation_id
            }), 200

        # except Exception as e:
        #     print("Agent error:", str(e))
        #     return jsonify({
        #         "success": False,
        #         "error": "VERA could not process this request.",
        #         "conversation_id": conversation_id
        #     }), 500
        
        except Exception as e:
            print("\n========== VERA AGENT ERROR ==========")
            traceback.print_exc()
            print("======================================\n")

            return jsonify({
                "success": False,
                "error": str(e),
                "conversation_id": conversation_id
            }), 500

    # Step 3: Execute existing basic commands

    if intent == "save_note":
        note_content = extract_note_content(text)

        if not note_content:
            message = "What would you like me to save?"
        else:
            connection = sqlite3.connect(DB_PATH)

            try:
                connection.execute(
                    "INSERT INTO notes (content, created_at) VALUES (?, ?)",
                    (
                        note_content,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                )
                connection.commit()
            finally:
                connection.close()

            message = f"I have saved your note: {note_content}"

    elif intent == "list_notes":
        connection = sqlite3.connect(DB_PATH)

        try:
            rows = connection.execute(
                """
                SELECT content, created_at
                FROM notes
                ORDER BY id DESC
                LIMIT 20
                """
            ).fetchall()
        finally:
            connection.close()

        if not rows:
            message = "You don't have any saved notes yet."
        else:
            message = "Here are your saved notes:\n"

            for index, (content, created_at) in enumerate(rows, start=1):
                message += f"\n{index}. {content} (Saved: {created_at})"

    elif intent == "set_reminder":
        reminder_content = extract_reminder_content(text)

        if not reminder_content:
            message = "What would you like me to remind you about?"
        else:
            connection = sqlite3.connect(DB_PATH)

            try:
                connection.execute(
                    """
                    INSERT INTO reminders
                    (content, due_at, created_at)
                    VALUES (?, ?, ?)
                    """,
                    (
                        reminder_content,
                        None,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                )
                connection.commit()
            finally:
                connection.close()

            message = f"I have saved your reminder: {reminder_content}"

    elif intent == "list_reminders":
        connection = sqlite3.connect(DB_PATH)

        try:
            rows = connection.execute(
                """
                SELECT id, content, created_at
                FROM reminders
                WHERE completed = 0
                ORDER BY id DESC
                """
            ).fetchall()
        finally:
            connection.close()

        if not rows:
            message = "You don't have any pending reminders."
        else:
            message = "Here are your pending reminders:\n"

            for index, (reminder_id, content, created_at) in enumerate(rows, start=1):
                message += f"\n{index}. {content} (Created: {created_at})"

    elif intent == "get_time":
        current_time = datetime.now().strftime("%I:%M %p")
        message = f"The current time is {current_time}."

    elif intent == "get_date":
        current_date = datetime.now().strftime("%A, %d %B %Y")
        message = f"Today's date is {current_date}."

    elif intent == "greeting":
        message = "Hello! I'm Vera. How can I help you?"

    elif intent == "goodbye":
        message = "Goodbye! Have a great day."

    elif intent == "delete_note":
        message = (
            "Note deletion is not implemented yet. "
            "I can help you add this capability."
        )

    else:
        message = "I couldn't identify a supported command."

    # Save rule-based interactions in conversation history
    save_conversation_turn(
        conversation_id,
        text,
        message
    )

    return jsonify({
        "success": True,
        "intent": intent,
        "message": message,
        "conversation_id": conversation_id
    }), 200
    
# --------------------------------------------------
# CONVERSATION HISTORY API
# --------------------------------------------------

@app.route("/api/conversations", methods=["GET"])
def get_conversations():

    import sqlite3

    with sqlite3.connect(CONVERSATION_DB) as connection:
        rows = connection.execute("""
            SELECT id, title, created_at, updated_at
            FROM conversations
            ORDER BY updated_at DESC
        """).fetchall()

    conversations = [
        {
            "id": row[0],
            "title": row[1],
            "created_at": row[2],
            "updated_at": row[3]
        }
        for row in rows
    ]

    return jsonify({
        "success": True,
        "conversations": conversations
    })


@app.route("/api/conversations/<conversation_id>", methods=["GET"])
def load_conversation(conversation_id):

    import sqlite3

    with sqlite3.connect(CONVERSATION_DB) as connection:
        conversation = connection.execute("""
            SELECT id, title
            FROM conversations
            WHERE id = ?
        """, (conversation_id,)).fetchone()

    if not conversation:
        return jsonify({
            "success": False,
            "error": "Conversation not found."
        }), 404

    history = get_conversation_history(conversation_id)

    return jsonify({
        "success": True,
        "conversation_id": conversation_id,
        "title": conversation[1],
        "messages": history
    })

@app.errorhandler(RequestEntityTooLarge)
def handle_large_upload(error):
    return jsonify({
        "error": "Recording is too large. Please record a shorter clip."
    }), 413

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
    
    app.config.from_object("config.Config")