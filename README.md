# VERA – Voice-Enabled AI Virtual Assistant

<p align="center">
  <strong>A voice-enabled AI assistant powered by Speech Recognition, Machine Learning, and Large Language Models.</strong>
</p>

<p align="center">
  <em>Speak naturally. Get things done.</em>
</p>

---
<p align="center">
  <img width="315" height="142" alt="image" src="https://github.com/user-attachments/assets/ea448c68-8308-4b84-a527-e2a3a03ec17e" />
</p>


## Overview

**VERA** is an AI-powered virtual assistant designed to understand voice and text commands, process natural-language requests, and perform useful tasks through an interactive web interface.

The project combines local speech recognition, machine-learning-based intent classification, an LLM-powered agent, and task-specific tools to create an extensible personal assistant.

VERA allows users to interact through their browser microphone or text input. It can transcribe speech, identify user intent, respond conversationally, and execute supported actions such as managing notes, checking the date and time, searching the web, and working with documents.

The application is built using Python and Flask, with SQLite for data storage and Groq for LLM-powered responses.

## Live Demo

**Live Application:** https://vera-ai-njh2.onrender.com/

> Note: The hosted application is under active development. Some features, particularly cloud-based speech transcription, may require further deployment optimization.

---

## Key Features

### 1. Voice Interaction

- Record audio directly through the browser microphone.
- Capture audio using JavaScript MediaRecorder.
- Upload recorded audio to the Flask backend.
- Convert speech into text using Faster-Whisper.
- Display the recognized transcript for further processing.

### 2. Speech Recognition

VERA uses **Faster-Whisper** for speech-to-text conversion.

Current configuration:

- Model: `base`
- Device: CPU
- Compute type: `int8`
- Language detection: Automatic

The model is initialized lazily to avoid loading it unnecessarily when the application starts.

### 3. Intent Classification

VERA includes a machine-learning-based intent classification system to identify what the user wants to do.

Examples of supported intent categories include:

- Greeting
- Goodbye
- Date and time queries
- Note-related commands
- Reminder-related commands

The intent classifier helps route straightforward commands to the appropriate application logic.

### 4. AI-Powered Agent

VERA integrates the Groq API to generate conversational responses and handle requests that require more flexible natural-language understanding.

The agent can:

- Understand natural-language instructions.
- Select appropriate tools for supported tasks.
- Process tool results.
- Generate responses based on the results.
- Maintain conversation context using stored conversation messages.

The agent uses a tool-calling workflow to connect the LLM with application functionality.

### 5. Notes and Reminders

VERA includes SQLite-backed functionality for managing personal information.

Supported functionality includes:

- Creating notes.
- Listing saved notes.
- Reading supported note content.
- Creating reminders.
- Storing application data persistently within the configured database.

### 6. Web Search

VERA integrates Tavily for web search.

This allows the assistant to retrieve information from the web and use search results when responding to user requests.

### 7. YouTube Integration

VERA includes browser automation functionality for YouTube-related tasks.

The integration uses Playwright to support:

- Searching YouTube.
- Retrieving relevant video information.
- Opening selected video links.

### 8. Document Management

VERA includes document-handling utilities for working with supported file formats.

Supported formats:

| Format | Functionality |
|---|---|
| TXT | Read and create text files |
| Markdown | Read and create Markdown files |
| PDF | Extract text from PDF documents |
| DOCX | Read Word documents |

Document processing uses libraries such as PyPDF and python-docx.

### 9. Conversation History

VERA includes a conversation-history interface backed by SQLite.

It supports:

- Starting a new conversation.
- Saving conversation messages.
- Retrieving previous conversations.
- Displaying conversation history in the interface.

### 10. Web-Based Interface

The frontend is built using HTML, CSS, and JavaScript.

It provides:

- Voice recording controls.
- Text-based interaction.
- Conversation display.
- Conversation history.
- New conversation functionality.
- A responsive assistant interface.

---

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python 3.11 |
| Backend | Flask |
| Frontend | HTML, CSS, JavaScript |
| Speech Recognition | Faster-Whisper |
| Machine Learning | Scikit-learn, Joblib |
| LLM Integration | Groq API |
| Search Integration | Tavily API |
| Browser Automation | Playwright |
| Database | SQLite |
| PDF Processing | PyPDF, ReportLab |
| Word Documents | python-docx |
| Deployment | Render |
| Version Control | Git, GitHub |

---

## System Architecture

VERA follows a modular architecture in which each component handles a specific responsibility.

```text
                  USER
                    |
                    v
          Web-Based Interface
           HTML / CSS / JS
                    |
          +---------+---------+
          |                   |
          v                   v
      Voice Input          Text Input
          |                   |
          v                   |
     MediaRecorder             |
          |                   |
          v                   |
      Flask Backend <---------+
          |
          v
     Speech-to-Text
     Faster-Whisper
          |
          v
    Recognized Text
          |
          v
    Intent Detection
          |
          v
    AI Agent / Router
          |
          +-------------------------+
          |           |             |
          v           v             v
       Groq LLM    Local Tools    External APIs
                     |             |
                 +---+---+       +--+------+
                 |       |       |         |
                Notes  Files   Tavily   YouTube
                 |       |       |         |
                 +-------+-------+---------+
                          |
                          v
                    SQLite Database
                          |
                          v
                  Assistant Response
                          |
                          v
                     Web Interface
```

---

## Project Structure

```text
VERA/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
├── .python-version
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── app.js
│
├── src/
│   ├── agent.py
│   ├── groq_client.py
│   ├── train_intent.py
│   ├── browser_tools.py
│   ├── file_tools.py
│   └── web_tools.py
│
├── data/
│   ├── intents.json
│   ├── vera.db
│   ├── uploads/
│   └── assistant_files/
│
├── models/
│   └── intent_classifier.joblib
│
└── README.md
```

### Folder Description

| File / Folder | Purpose |
|---|---|
| `app.py` | Main Flask application and API routes |
| `src/agent.py` | AI agent, tool execution, and conversation management |
| `src/groq_client.py` | Groq API client configuration |
| `src/train_intent.py` | Intent classifier training |
| `src/browser_tools.py` | YouTube-related browser functionality |
| `src/file_tools.py` | Document reading and creation |
| `src/web_tools.py` | Web search and webpage processing |
| `templates/` | HTML templates |
| `static/css/` | Application styling |
| `static/js/` | Frontend interactions and voice recording |
| `data/` | Database, uploads, and assistant files |
| `models/` | Saved machine-learning models |

---

## Installation and Setup

### Prerequisites

Make sure the following are installed:

- Python 3.11
- Git
- Visual Studio Code (recommended)
- A Groq API key
- A Tavily API key

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/VERA-AI-Assistant.git

cd VERA-AI-Assistant
```

Replace `YOUR_USERNAME` with the GitHub account or organization that owns the repository.

### 2. Create a Virtual Environment

```bash
python -m venv freya_env
```

Activate it on Windows:

```bash
freya_env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b

TAVILY_API_KEY=your_tavily_api_key

SECRET_KEY=your_secure_random_secret
```

Replace the placeholder values with your actual API keys and a secure secret key.

**Important:** Never upload `.env` to GitHub or expose API keys in frontend JavaScript.

### 5. Run the Application

```bash
python app.py
```

Open the application in your browser:

```text
http://127.0.0.1:5000
```

The first speech-recognition request may take additional time because the Whisper model needs to be initialized and downloaded if it is not already cached.

---

## Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | API key used for Groq LLM requests |
| `GROQ_MODEL` | Model identifier used by the Groq client |
| `TAVILY_API_KEY` | API key used for web search |
| `SECRET_KEY` | Flask application secret key |

Keep all credentials private and configure them through environment variables.

---

## API Endpoints

The Flask backend exposes endpoints for frontend communication.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Loads the VERA interface |
| POST | `/api/upload-audio` | Uploads recorded audio |
| POST | `/api/transcribe` | Converts uploaded audio into text |
| POST | `/api/intent` | Identifies the user's intent |
| POST | `/api/execute` | Processes and executes a user request |
| GET | `/api/conversations` | Retrieves conversation history |
| GET | `/api/conversations/<id>` | Retrieves a conversation |
| GET | `/api/health` | Checks application health |

These endpoints are handled by the Flask application.

---

## Machine Learning Workflow

VERA combines traditional machine learning with LLM-based processing.

### Intent Classification Pipeline

```text
User Command
     |
     v
Text Preprocessing
     |
     v
Feature Extraction
     |
     v
Intent Classifier
     |
     v
Predicted Intent
     |
     v
Task Execution
```

The classifier is trained using the project's intent dataset and saved as a Joblib model.

The trained model is stored in:

```text
models/intent_classifier.joblib
```

The intent examples are maintained in:

```text
data/intents.json
```

### LLM Processing

For requests that require flexible language understanding, VERA uses the Groq API.

The agent can select from registered tools, execute supported operations, and use the results to generate a response.

---

## Database

VERA uses SQLite for local data storage.

The database file is:

```text
data/vera.db
```

The application uses database tables for functionality such as:

- Notes
- Reminders
- Conversations
- Conversation messages
- User memory

The database is initialized by the application and agent modules.

> Deployment note: SQLite files and uploaded files stored on a free Render instance may not persist across restarts or redeployments. Persistent storage or an external database is needed for reliable production data retention.

---

## Deployment

VERA is configured for deployment on **Render**.

### Build Command

```bash
pip install -r requirements.txt && playwright install chromium
```

### Start Command

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

### Deployment Steps

1. Push the project to a GitHub repository.
2. Create a new Web Service on Render.
3. Connect the GitHub repository.
4. Select the Python runtime.
5. Configure the build and start commands.
6. Add the required environment variables.
7. Deploy the application.
8. Open the generated public URL.

**Deployment considerations:**

- The Whisper model requires additional memory and initialization time.
- Free hosting instances may spin down after inactivity.
- Local filesystem storage on free instances is temporary.
- Browser automation and speech recognition may need additional hosting resources.
- API usage limits and service availability depend on the external providers.

---

## Security and Privacy Considerations

VERA is an actively developed project. Before using it as a public production service, the following protections should be implemented and verified:

- Isolate each visitor's conversations, notes, reminders, and files.
- Implement secure guest sessions and session expiration.
- Validate uploaded audio and document files.
- Add request rate limiting to protect API usage.
- Restrict access to conversation records by session ownership.
- Avoid exposing API keys or internal error details.
- Configure secure cookies and HTTPS.
- Define data retention and deletion policies.

Do not assume that public guest access automatically provides private, isolated user sessions. These protections must be implemented in the backend.

---

## Current Development Status

| Component | Status |
|---|---|
| Flask backend | Implemented |
| Web interface | Implemented |
| Browser microphone recording | Implemented |
| Audio upload | Implemented |
| Faster-Whisper transcription | Working locally; cloud deployment under validation |
| Intent classification | Implemented; further improvement needed |
| Groq LLM integration | Implemented |
| AI agent and tool calling | Implemented |
| Notes functionality | Implemented |
| Reminder functionality | Implemented |
| SQLite conversation storage | Implemented |
| Conversation history interface | Implemented |
| Web search integration | Implemented |
| YouTube tools | Implemented |
| Document processing | Implemented |
| Public deployment | Deployed on Render; ongoing testing |
| Guest session isolation | Planned |
| Production-grade rate limiting | Planned |

---

## Future Enhancements

VERA is designed to grow into a more capable personal AI assistant.

Potential improvements include:

- Secure temporary guest sessions.
- User-specific storage and conversation isolation.
- Improved intent classification accuracy.
- More reliable speech recognition on cloud hosting.
- Voice responses using text-to-speech.
- Better conversational memory.
- More advanced reminder management.
- Improved document understanding.
- Additional integrations and custom tools.
- Better error handling and monitoring.
- Persistent cloud database and file storage.
- Improved mobile responsiveness.

---

## Challenges and Learning Outcomes

Building VERA involves combining several different areas of software development and artificial intelligence.

Key learning areas include:

- Integrating speech recognition into a web application.
- Building REST APIs using Flask.
- Training and integrating machine-learning models.
- Connecting LLMs with external tools.
- Managing conversation context.
- Working with SQLite databases.
- Automating browser-based tasks using Playwright.
- Integrating external APIs.
- Deploying Python applications using Gunicorn and Render.
- Debugging resource and dependency issues in cloud environments.

---

## Contributing

Contributions, suggestions, and improvements are welcome.

To contribute:

1. Fork the repository.
2. Create a new feature branch.
3. Make your changes.
4. Test the functionality.
5. Submit a pull request with a clear description.

---

## Acknowledgements

VERA is built using several open-source technologies and external services, including:

- [Flask](https://flask.palletsprojects.com/)
- [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper)
- [Groq](https://groq.com/)
- [Tavily](https://tavily.com/)
- [Scikit-learn](https://scikit-learn.org/)
- [Playwright](https://playwright.dev/)
- [SQLite](https://www.sqlite.org/)

---

## License

A license has not yet been specified for this repository.

Add a `LICENSE` file before allowing others to reuse, modify, or distribute the project.

---

<p align="center">
  <strong>VERA – Your Voice. Your Assistant. Your AI.</strong>
</p>
