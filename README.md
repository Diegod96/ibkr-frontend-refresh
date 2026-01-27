# IBKR Frontend Refresh

A modern portfolio management interface for Interactive Brokers. Organize your investments with pies and slices, set up auto-invest, and build positions with smart triggers.

## Features

- **Pie & Slice Structure**: Organize your portfolio into themed pies (e.g., "Semiconductors", "Big Tech") with weighted slices for individual holdings
- **Auto-Invest**: Automatically allocate deposits across your portfolio based on target weights
- **Position Building**: Build positions gradually using time-based, price-based, or technical triggers

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14 + TypeScript + Tailwind CSS |
| Backend | Python 3.11 + FastAPI |
| Database | PostgreSQL (Supabase) |
| Auth | Supabase Auth |
| Broker API | IBKR Web API |

## Project Structure

```
.
├── frontend/                # Next.js frontend application
│   ├── src/
│   │   ├── app/            # App Router pages
│   │   ├── components/     # React components
│   │   ├── lib/            # Utilities and helpers
│   │   └── types/          # TypeScript type definitions
│   └── ...
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration and database
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   └── tests/              # Backend tests
├── supabase/
│   └── migrations/         # Database migrations
├── docs/                    # Documentation
├── .github/
│   └── workflows/          # CI/CD pipelines
├── docker-compose.yml       # Full stack Docker setup
└── docker-compose.dev.yml   # Database-only for development
```

## Getting Started

### Prerequisites

- Node.js 20+
- Python 3.11+
- Docker and Docker Compose
- Git

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/Diegod96/ibkr-frontend-refresh.git
   cd ibkr-frontend-refresh
   ```

2. **Start all services**
   ```bash
   docker compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api
   - API Docs: http://localhost:8000/api/docs

### Development Setup (Recommended)

For local development with hot-reloading:

1. **Start the database**
   ```bash
   docker compose -f docker-compose.dev.yml up -d
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   cp .env.example .env
   # Edit .env with your configuration
   uvicorn app.main:app --reload
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   cp .env.example .env.local
   # Edit .env.local with your configuration
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api
   - API Docs: http://localhost:8000/api/docs

## Database Schema

The application uses the following main tables:

| Table | Description |
|-------|-------------|
| `users` | User accounts linked to Supabase Auth |
| `portfolios` | User portfolios (e.g., Roth IRA, Brokerage) |
| `pies` | Themed groupings of assets within a portfolio |
| `slices` | Individual holdings within a pie |
| `build_rules` | Rules for position building triggers |
| `deposits` | Cash deposits into portfolios |
| `transactions` | Trade execution history |

### Weight Constraints

- Pie weights within a portfolio must sum to 100%
- Slice weights within a pie must sum to 100%

## API Endpoints

### Health Check
- `GET /api/health` - Basic health check
- `GET /api/health/ready` - Readiness check with database connectivity
- `GET /api/health/live` - Liveness check

### Coming Soon (Phase 2+)
- Authentication endpoints
- Portfolio CRUD operations
- Pie/Slice management
- Auto-invest configuration
- Transaction history

## Development

### Running Tests

**Backend:**
```bash
cd backend
pytest
```

**Frontend:**
```bash
cd frontend
npm test
```

### Linting

**Backend:**
```bash
cd backend
ruff check .
black --check .
```

**Frontend:**
```bash
cd frontend
npm run lint
npm run format:check
npm run type-check
```

## CI/CD

The project uses GitHub Actions for continuous integration:

- **Lint**: Code style checks (Ruff, Black, ESLint, Prettier)
- **Test**: Unit and integration tests with coverage
- **Build**: Docker image builds

All checks must pass before merging PRs.

## Contributing

1. Create a feature branch from `develop`
2. Make your changes following the coding standards
3. Write tests for new functionality
4. Submit a PR against `develop`

See [plans/plan-part4-git-strategy.md](plans/plan-part4-git-strategy.md) for detailed git workflow.

## License

MIT
