# Chargeback MVP Backend

## Architecture

This backend follows Domain-Driven Design (DDD) principles with clean architecture layers:

### Layer Structure

```
src/
├── domain/              # Core business logic (pure Python)
│   ├── entities/        # Business entities (Dispute, User, etc.)
│   ├── services/        # Domain services
│   └── repositories/    # Repository interfaces (abstract)
│
├── application/         # Use cases / Application services
│   ├── use_cases/       # Business use cases
│   └── events/          # Domain events
│
├── infrastructure/      # External dependencies
│   ├── database/        # PostgreSQL, SQLAlchemy models
│   ├── stripe/          # Stripe API client
│   ├── llm/             # LLM providers (Groq, OpenAI, Ollama)
│   └── queue/           # Redis queue for async tasks
│
├── agents/              # AI Agents (LangGraph)
│   ├── orchestrator.py  # Main workflow
│   ├── prompts.py       # Agent prompts
│   └── state.py         # Workflow state
│
└── api/                 # HTTP interface (FastAPI)
    └── routes/          # API endpoints
```

## Configuration

### LLM Provider

Configured via `.env`:
```bash
LLM_PROVIDER=groq  # Options: groq, openai, ollama
```

**Groq** (recommended for MVP):
- FREE
- Fast inference
- llama-3.1-70b model
- Already configured with your key

**OpenAI**:
- Paid (but cheap with gpt-4o-mini)
- $0.001 per dispute
- High quality

**Ollama**:
- Completely FREE
- Runs locally
- Need to start with: `docker-compose --profile local-llm up -d ollama`

### LangSmith Tracing

Add your LangSmith API key to `.env`:
```bash
LANGCHAIN_API_KEY=your_key_here
```

View traces at: https://smith.langchain.com

## Development

### Install Dependencies Locally (Optional)
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Run Tests (Coming Soon)
```bash
pytest
```

### Code Style
- Follow PEP 8
- Use type hints
- Docstrings for all public functions
- Keep functions small and focused

## API Endpoints

### Health & Testing
- `GET /health` - Health check
- `GET /test/llm` - Test LLM connection
- `GET /docs` - API documentation

### Coming Next
- `POST /webhooks/stripe` - Stripe webhook handler
- `GET /api/disputes` - List disputes
- `GET /api/disputes/{id}` - Get dispute details
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login
- `GET /api/metrics` - Dashboard metrics

## Database Schema

### Users
- id (UUID, PK)
- email (unique)
- password_hash
- stripe_account_id
- stripe_access_token
- created_at, updated_at

### Disputes
- id (UUID, PK)
- user_id (FK → users)
- stripe_dispute_id (unique)
- stripe_charge_id
- amount_cents, currency
- reason, status
- deadline
- metadata, evidence, decision_data, submission_data, outcome_data (JSON)
- created_at, updated_at

## Current Status

✅ **Implemented:**
- Domain entities (Dispute, User, Evidence, Decision)
- Repository interfaces
- PostgreSQL models and repositories
- Multi-provider LLM client (Groq, OpenAI, Ollama)
- Configuration management
- FastAPI app with health check
- Docker setup

⏭️ **Next Steps:**
- Stripe webhook endpoint
- Agent workflow (LangGraph)
- Authentication (JWT)
- Use cases (ProcessDispute, etc.)
- API routes for disputes and metrics

## Dependencies

**Core:**
- FastAPI - Web framework
- SQLAlchemy - ORM
- Alembic - Migrations
- Pydantic - Validation

**AI/LLM:**
- LangChain - LLM abstraction
- LangGraph - Agent orchestration
- LangSmith - Tracing
- langchain-groq - Groq provider
- langchain-openai - OpenAI provider

**External Services:**
- Stripe - Payment processing
- Redis - Task queue
- PostgreSQL - Database

## Environment Variables

See `.env.example` for all configuration options.

Required:
- `DATABASE_URL`
- `REDIS_URL`
- `LLM_PROVIDER`
- `GROQ_API_KEY` (or OPENAI_API_KEY or OLLAMA_BASE_URL)
- `JWT_SECRET`

Optional:
- `LANGCHAIN_API_KEY` (for LangSmith tracing)
- `STRIPE_API_KEY` (for Stripe integration)
- `STRIPE_WEBHOOK_SECRET` (for webhook verification)

## Notes

- All timestamps are UTC
- Money is stored as cents (integers) to avoid float precision issues
- Disputes are immutable once submitted
- Agents run asynchronously via Redis queue
- LangSmith tracing is enabled by default for debugging
