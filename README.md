# Speech-to-Document (S2D)

Real-time speech-to-text webapp that uses OpenAI Whisper for transcription and an LLM to populate a structured process document.

## Features

- **Real-time Transcription**: Uses OpenAI Whisper API for accurate speech-to-text (~3-5 second latency)
- **Intelligent Document Updates**: LLM processes transcription and updates structured document via JSON Patch (RFC 6902)
- **Overlapping Context**: Consecutive transcriptions overlap to help LLM understand corrections ("actually, change that to...")
- **JSON Patch Support**: Supports add, replace, and remove operations for precise document updates
- **WebSocket Communication**: Real-time bidirectional communication between frontend and backend
- **Immediate Processing**: LLM processes new transcription as soon as it arrives (no artificial delays)

## Architecture

### Tech Stack

**Backend:**
- Python 3.10+
- FastAPI for REST API and WebSocket
- OpenAI API (Whisper for transcription, configurable LLM for processing)
- Pydantic for data validation
- JSON Patch (RFC 6902) for document updates

**Frontend:** (To be implemented)
- React 18
- Vite
- fast-json-patch
- Tailwind CSS

### Project Structure

```
s2d/
├── core/                          # Pure Python business logic (testable independently)
│   ├── templates.py              # Document schema (PROCESS_TEMPLATE)
│   ├── transcription_buffer.py   # Overlapping window extraction
│   ├── patch_generator.py        # JSON Patch validation/application
│   └── prompt_builder.py         # LLM prompt construction
├── backend/                       # FastAPI backend
│   ├── main.py                   # FastAPI app entry point
│   ├── config.py                 # Configuration management
│   ├── api/
│   │   ├── routes.py            # HTTP REST endpoints
│   │   └── websocket.py         # WebSocket handler
│   ├── services/
│   │   ├── transcription_service.py  # Whisper API integration
│   │   ├── llm_service.py           # LLM integration
│   │   └── session_manager.py       # Session state management
│   └── models/
│       ├── session.py           # Session data model
│       └── message.py           # WebSocket message models
├── tests/                         # Test suite
│   ├── test_transcription_buffer.py
│   └── test_patch_generator.py
├── .env.example                   # Environment variables template
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Setup

### Prerequisites

- Python 3.10 or higher
- OpenAI API key with access to Whisper and the configured LLM model

### Installation

1. **Clone the repository** (or navigate to the project directory)

```bash
cd /home/eric/work/s2d
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

```bash
cp .env.example ~/.env.s2d
```

Edit `~/.env.s2d` and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Running the Backend

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **REST API**: http://localhost:8000
- **WebSocket**: ws://localhost:8000/ws
- **API Docs**: http://localhost:8000/docs (Swagger UI)

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=backend tests/

# Run specific test file
pytest tests/test_transcription_buffer.py -v
```

## API Documentation

### WebSocket Endpoint

**Endpoint**: `ws://localhost:8000/ws`

**Client → Server Messages:**

1. Audio Chunk:
```json
{
  "type": "audio_chunk",
  "data": "base64_encoded_audio_data",
  "format": "webm"
}
```

2. Stop Recording:
```json
{
  "type": "stop_recording"
}
```

**Server → Client Messages:**

1. Transcription:
```json
{
  "type": "transcription",
  "text": "transcribed text",
  "timestamp": 1234567890.123
}
```

2. Document Patch:
```json
{
  "type": "document_patch",
  "patch": [
    {"op": "add", "path": "/actors/-", "value": "Sales Team"},
    {"op": "replace", "path": "/process_name", "value": "Customer Onboarding"}
  ]
}
```

3. Status:
```json
{
  "type": "status",
  "status": "processing|idle|error",
  "message": "Status message"
}
```

4. Error:
```json
{
  "type": "error",
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

### REST API Endpoints

**GET /**
- Root endpoint with API information

**GET /health**
- Health check

**GET /api/sessions**
- List all sessions

**POST /api/sessions**
- Create a new session

**GET /api/sessions/{session_id}**
- Get session details

**DELETE /api/sessions/{session_id}**
- Delete a session

**POST /api/sessions/{session_id}/export**
- Export session document (JSON format)

## Document Schema (PROCESS_TEMPLATE)

The document follows this structure:

- **process_name** (string): Short, descriptive process name
- **process_goal** (string): Primary objective of the process
- **scope** (object):
  - **start_trigger** (string): What initiates the process
  - **end_condition** (string): What marks completion
  - **in_scope** (array): What's included
  - **out_of_scope** (array): What's excluded
- **actors** (array): People/roles involved
- **systems** (array): Tools/platforms used
- **main_flow** (array): Sequential steps with id, description, actor, system
- **exceptions** (array): Error cases with condition and action
- **metrics** (array): KPIs with name and description
- **open_questions** (array): Uncertainties or questions

## How It Works

### Data Flow

```
1. User speaks → Browser captures audio (MediaRecorder)
2. Audio sent to backend via WebSocket (3-second chunks)
3. Backend transcribes with Whisper API
4. Transcription sent to client immediately
5. Transcription added to buffer (overlapping window)
6. LLM processes transcription tail + current document
7. LLM returns JSON Patch operations
8. Patches applied to document
9. Patches sent to client
10. Client applies patches to UI
```

### Key Design Decisions

1. **Immediate LLM Processing**: No artificial delays - LLM processes as soon as new transcription arrives
2. **Overlapping Context**: 250-word windows with overlap help LLM understand corrections
3. **JSON Patch Updates**: RFC 6902 patches enable precise updates (add/replace/remove)
4. **Context in Messages**: Current document passed in user message to LLM, not in system prompt
5. **Graceful Degradation**: If LLM fails, transcription still works

## Testing the Backend

### Manual WebSocket Testing

You can test the WebSocket endpoint using Python:

```python
import asyncio
import websockets
import json
import base64

async def test_websocket():
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        # Send a test audio chunk (empty for testing)
        message = {
            "type": "audio_chunk",
            "data": base64.b64encode(b"fake audio").decode(),
            "format": "webm"
        }
        await websocket.send(json.dumps(message))

        # Receive responses
        for _ in range(3):
            response = await websocket.recv()
            print(f"Received: {response}")

asyncio.run(test_websocket())
```

### Testing with cURL

```bash
# Health check
curl http://localhost:8000/health

# Create session
curl -X POST http://localhost:8000/api/sessions

# List sessions
curl http://localhost:8000/api/sessions

# Get session details
curl http://localhost:8000/api/sessions/{session_id}
```

## Development

### Code Quality

The codebase follows these principles:

- **Separation of Concerns**: Core logic in `core/`, completely independent of FastAPI
- **Type Hints**: Full type annotations for better IDE support and error detection
- **Comprehensive Tests**: 49 tests covering core functionality
- **Logging**: Structured logging throughout the application
- **Error Handling**: Graceful degradation when APIs fail

### Adding New Features

1. **Core Logic**: Add to `core/` directory (must be framework-independent)
2. **Services**: Add to `backend/services/` (can use FastAPI/async)
3. **Models**: Add to `backend/models/` (use Pydantic)
4. **API Endpoints**: Add to `backend/api/routes.py` or `websocket.py`
5. **Tests**: Add to `tests/` directory

## Troubleshooting

### "OPENAI_API_KEY must be set"

Make sure you've created a `~/.env.s2d` file (copy from `.env.example`) and added your OpenAI API key.

### "Module not found" errors

Make sure you've activated the virtual environment and installed dependencies:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### WebSocket connection fails

- Check that the backend is running on port 8000
- Check firewall settings
- Try accessing http://localhost:8000/health to verify the server is running

### Transcription is slow

- Whisper API typically takes 3-5 seconds per audio chunk
- Check your internet connection
- Check OpenAI API status

### LLM not generating patches

- Check logs for errors: `uvicorn backend.main:app --log-level=debug`
- Verify your OpenAI API key has access to the configured model (check `config.yaml`)
- Check API rate limits

## Configuration

The application uses a two-file configuration approach:

### 1. Secrets (`~/.env.s2d`)

Secrets and API keys are stored in `~/.env.s2d` (not tracked in git):

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional
ASSEMBLYAI_API_KEY=your-key
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=your-key
LIVEKIT_API_SECRET=your-secret
```

Create this file by copying [.env.example](.env.example):
```bash
cp .env.example ~/.env.s2d
```

### 2. Regular Parameters (`config.yaml`)

Regular configuration parameters are in [config.yaml](config.yaml) (tracked in git):

```yaml
whisper_model: "whisper-1"
gpt_model: "gpt-4o"
audio_chunk_duration: 3
transcription_window_size: 250
patch_history_count: 5
host: "localhost"
port: 8000
frontend_url: "http://localhost:5173"
session_timeout_minutes: 60
max_sessions: 100
verbose_llm_logging: false
```

### Override Priority

Configuration values can be overridden with this priority (highest to lowest):
1. Environment variables
2. `~/.env.s2d` file
3. `config.yaml` file
4. Default values

Example: To override the port, set the environment variable:
```bash
PORT=9000 uvicorn backend.main:app
```

## Future Enhancements

### v2 Features (Planned)

- React frontend with beautiful document UI
- User edit conflict detection and resolution
- Voice commands ("delete last step", "change that to...")
- Export to PDF/Markdown/DOCX
- Multi-language support
- Custom document templates
- Collaborative editing
- Version history and undo/redo

## License

[Add your license here]

## Contributing

[Add contributing guidelines here]

## Support

For issues, questions, or feature requests, please [contact information or issue tracker URL].
