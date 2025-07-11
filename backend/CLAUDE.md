# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Start the FastAPI server with uv (IMPORTANT!)
uv run python main.py
# Server runs on http://0.0.0.0:8000 with auto-reload enabled

# Alternative: Using uvicorn directly
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Important Note:** The server MUST be run with `uv run` to access all dependencies correctly, especially Redis and other services.

### Testing
```bash
# Run all tests
python run_tests.py

# Run specific test suites
python run_tests.py --memory    # AI Memory tests only
python run_tests.py --agents    # Agent tests only
python run_tests.py --verbose   # Verbose output

# Run individual test files
python -m unittest tests.test_ai_memory -v
python -m unittest tests.unit_testing -v
```

### Dependencies
```bash
# Install dependencies (using uv package manager)
uv sync

# Alternative with pip
pip install -r requirements.txt
```

## Architecture Overview

This is a multi-agent AI system built with FastAPI that provides text-to-SQL capabilities and conversation management.

### Core Components

1. **FastAPI Application** (`main.py`)
   - Main entry point with basic chat endpoint
   - Pydantic v2 models for request/response validation
   - Custom error handling for validation errors

2. **Multi-Agent System** (`my_agents/`)
   - **Base Agent Pattern**: All agents inherit from `BaseAgent` with consistent `process()` method
   - **Agent Communication**: Shared context and caching between agents
   - **Specialized Agents**:
     - `QueryUnderstandingAgent`: Analyzes user questions
     - `SchemaExplorerAgent`: Explores database schema
     - `SqlGeneratorAgent`: Generates SQL queries
     - `ExecutionValidatorAgent`: Validates SQL syntax/logic
     - `ExplanationAgent`: Explains SQL queries
     - `ResponseFormatterAgent`: Formats final responses
     - `RouterAgent`: Orchestrates the complete workflow

3. **Services Layer**
   - `AIMemoryService`: Redis-based conversation history storage
   - `ConversationHistoryService`: Session management
   - `SemanticCacheService`: Query result caching

4. **API Routes** (`my_agents/routes/`)
   - Individual agent endpoints for testing
   - Complete text-to-SQL workflow endpoint

### Key Patterns

- **Agent Base Class**: All agents extend `BaseAgent` with standard `process()` method
- **Context Passing**: Agents share session and cache context via `AgentContext`
- **Error Handling**: Comprehensive logging and exception handling throughout
- **Async Processing**: All agent operations are asynchronous
- **Caching Strategy**: Semantic caching for expensive operations

### Configuration

Environment variables are managed through `.env` file:
- Database connections (MySQL)
- Vector database (Qdrant)
- OpenAI API configuration
- Redis connection details

### Testing Strategy

- **Unit Tests**: Individual agent and service testing with mocked dependencies
- **Integration Tests**: Complete workflow testing
- **Edge Case Testing**: Unicode, large data, error conditions
- **Mock Strategy**: Redis and external APIs are mocked for testing

## Important Notes

- The system uses two agent implementations: `my_agents/agents/` (newer) and `my_agents/sql_agents/` (alternative)
- Redis is required for conversation history and caching
- All agents support session-based conversation tracking
- The router agent coordinates the complete text-to-SQL pipeline
- Tests use `fakeredis` to avoid requiring a real Redis instance