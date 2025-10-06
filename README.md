# LLM Chat Application with Agent System

A full-stack application that combines a React frontend with a Python backend, utilizing Llama as the language model and supporting agent-based interactions. The application is designed to be extensible, supporting RAG (Retrieval-Augmented Generation) capabilities and custom tool integration.

## Features

- 🤖 Llama-based LLM integration
- 💬 Real-time chat interface
- 🔧 Extensible agent system
- 🎯 Custom tool integration support
- 🔄 RAG-ready architecture
- ⚡ Fast API backend
- 🎨 Modern React frontend with TypeScript

## Prerequisites

- Node.js >=20.19.0
- Python >=3.8
- Git (for version control)

## Quick Start

1. Clone the repository:
```bash
git clone [your-repo-url]
cd LLMandAgent
```

2. Set up the Python virtual environment:
```bash
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Unix or MacOS:
source .venv/bin/activate
```

3. Install dependencies:
```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..

# Install root project dependencies
npm install
```

4. Download the LLM model:
- Download the `llama-2-7b.Q4_K_M.gguf` model
- Place it in the `backend/models` directory

5. Start the application:
```bash
npm run dev
```

This will start both the frontend and backend servers concurrently:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Project Structure

```
LLMandAgent/
├── frontend/                # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── Chat.tsx   # Main chat interface
│   │   │   └── ui/        # UI components
│   │   ├── App.tsx        # Root component
│   │   └── main.tsx       # Entry point
│   ├── package.json
│   └── vite.config.ts
├── backend/                # Python FastAPI backend
│   ├── main.py            # API server
│   ├── agents/            # Agent system
│   ├── tools/             # Custom tools
│   ├── models/            # LLM models
│   └── requirements.txt
└── package.json           # Root package.json for concurrent running
```

## Development

### Frontend Development

The frontend is built with:
- React with TypeScript
- Vite for build tooling
- Chakra UI for components
- Axios for API communication

To run the frontend separately:
```bash
npm run frontend
```

### Backend Development

The backend uses:
- FastAPI for the web framework
- Llama.cpp for the language model
- LangChain for the agent framework

To run the backend separately:
```bash
npm run backend
```

### Adding New Tools

1. Create a new tool in `backend/tools/`:
```python
from langchain.tools import BaseTool

class YourNewTool(BaseTool):
    name = "tool_name"
    description = "Tool description"

    def _run(self, query: str) -> str:
        # Implementation
        pass
```

2. Register the tool in `tools/base_tools.py`

### Adding RAG Capabilities

The backend is set up to support RAG through:
- ChromaDB for vector storage
- LangChain for document processing
- Custom document loaders

## API Documentation

### Chat Endpoint

```http
POST /api/chat
Content-Type: application/json

{
  "text": "Your message",
  "parameters": {},
  "use_agent": false
}
```

### Health Check

```http
GET /api/health
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your chosen license]

## Acknowledgments

- [Llama](https://github.com/facebookresearch/llama) for the language model
- [LangChain](https://github.com/hwchase17/langchain) for the agent framework
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework