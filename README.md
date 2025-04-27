# TAMMA Backend

A FastAPI-based backend for the TAMMA AI chat application, which provides APIs for chat interactions, session management, and AI content generation.

## Features

- Chat API with both synchronous and streaming responses
- Chat history management
- Session management
- AI content generation using OpenAI
- Supabase integration for data storage

## Project Structure

```
infuse-ai-tamma-be/
├── .env                    # Environment variables configuration
├── .git/                   # Git repository
├── .gitignore              # Git ignore file
├── app/                    # Application code
│   ├── __pycache__/        # Python cache directory
│   ├── config.py           # Configuration settings
│   ├── deps.py             # Dependency injection
│   ├── main.py             # Main application entry point
│   ├── supabase.py         # Supabase client configuration
│   ├── models/             # Data models
│   ├── routers/            # API route definitions
│   │   ├── chat.py         # Chat API endpoints
│   │   ├── chat_history.py # Chat history API endpoints
│   │   ├── chat_stream.py  # Streaming chat API endpoints
│   │   ├── generator.py    # Content generation endpoints
│   │   └── session.py      # Session management endpoints
│   └── services/           # Business logic services
│       └── feature_builder.py # Feature building service
└── venv/                   # Python virtual environment
```

## Getting Started

### Prerequisites

- Python 3.8+
- Supabase account
- OpenAI API key

### Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/infuse-ai-tamma-be.git
   cd infuse-ai-tamma-be
   ```

2. Create a virtual environment and activate it:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   ```

### Running the Application

Start the FastAPI server:

```
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Endpoints

- `/api/chat` - Chat with AI
- `/api/chat/stream` - Stream chat responses
- `/api/chat/history` - Manage chat history
- `/api/session` - Manage user sessions
- `/api/generate` - Generate AI content

## Development

Access the API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
