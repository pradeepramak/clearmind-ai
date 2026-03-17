# ClearMind AI - Copilot Instructions

## Project Overview
ClearMind AI is a Flask-based document analysis application that uses Google's Gemini API to analyze PDFs and images, with follow-up conversation capabilities. The app processes documents, stores analysis results in memory, and enables multi-turn Q&A sessions.

## Architecture

### Core Components
- **Backend**: Flask application (`app.py`) with three main routes (`/`, `/upload`, `/ask`)
- **Frontend**: Jinja2 templates with vanilla JavaScript (no build tools)
- **Document Processing**: 
  - PDFs via `pdfplumber` (text extraction)
  - Images via PIL (direct Gemini multimodal input)
- **AI Integration**: Google Gemini 2.5-Flash API via `google.generativeai`

### Data Flow
1. User uploads file → `/upload` route
2. Flask extracts text (PDFs) or passes image directly to Gemini
3. Gemini analyzes with structured prompt → stores in global `analysis_result`
4. Results rendered in `result.html` with chat interface
5. User asks questions → `/ask` route appends to `chat_history` and re-renders

### Critical Design Patterns
- **Global State Storage**: Uses module-level variables (`document_context`, `analysis_result`, `chat_history`) rather than database - intentional for single-session simplicity
- **Stateless Rendering**: Each response re-renders the entire result page with current state
- **Prompt Engineering Over Logic**: All document understanding happens via Gemini's system prompt, not Python logic

## Developer Workflows

### Running the Application
```bash
python app.py
# Server runs on http://localhost:5000 with debug=True enabled
```

### File Upload Requirements
- **Supported formats**: `.pdf`, `.png`, `.jpg`, `.jpeg`, `.txt`, `.docx` (HTML accepts these; backend validates in code)
- **Backend handling**: Only PDF and image handling implemented; other formats currently unsupported (missing implementation)

### Testing Changes
- Test PDF parsing: Use multi-page PDFs to verify `pdfplumber` text extraction
- Test image analysis: Try various image types and complexities with Gemini
- Test chat: Multiple Q&A rounds to verify `chat_history` appending logic

## Project-Specific Conventions

### Prompt Structure
All Gemini prompts follow this pattern:
```python
prompt = """
System instruction or role definition.
Structured output format (Document Type, Summary, Key Details).
Context or instructions about the document.
"""
```
Never omit the structured output section - Gemini's responses depend on it.

### Frontend Conventions
- Drag-and-drop file upload in `index.html`
- Chat bubbles styled with `.user-msg` (green, right-aligned) and `.ai-msg` (gray, left-aligned)
- No validation library - all file type validation in HTML `accept` attribute and backend code
- No CSS framework - inline styles in `<style>` tags

### State Management
- Always reinitialize `chat_history` on new document upload (`document_context = ""; chat_history = []`)
- Global variables reset because multi-user sessions aren't supported
- The `/ask` route receives question via form data, not JSON

## Integration Points & Dependencies

### External Dependencies
- `flask`: Web framework
- `pdfplumber`: PDF text extraction
- `pillow` (PIL): Image handling
- `google-generativeai`: Gemini API client
- **API Key**: Hardcoded in `app.py` line 6 (⚠️ insecure - should move to env vars)

### Gemini Integration Details
- **Model**: `models/gemini-2.5-flash` (not configurable)
- **Input**: Text prompts for PDFs; `[prompt, image]` list for images
- **Output**: `.text` property on response object
- **No streaming**: Waits for full response before rendering

## Common Pitfalls & Workarounds
- **Missing file type support**: `.txt` and `.docx` in HTML accept but not handled in Python - will error
- **Session loss on restart**: No persistence; data lost when Flask restarts
- **Prompt injection**: `chat_history` and `document_context` included raw in prompts - user input could manipulate Gemini
- **Large PDFs**: Full text concatenated into memory - very large documents may fail

## File Structure Reference
- [app.py](../app.py) - Core Flask app with all routes and Gemini integration
- [templates/index.html](../templates/index.html) - File upload UI with drag-and-drop
- [templates/result.html](../templates/result.html) - Analysis display and chat interface
