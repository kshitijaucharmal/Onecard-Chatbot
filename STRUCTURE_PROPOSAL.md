# Proposed Project Structure

## Current Structure (Issues)
```
FPL/
├── backend.py          # AI backend (mixed concerns)
├── mock_apis.py        # Mock API server
├── setup_database.py   # DB setup
├── requirements.txt
├── onecard-bot/        # Frontend
└── *.db files          # Databases in root
```

**Problems:**
- All backend files in root directory
- Databases scattered in root
- No clear separation of concerns
- Hard to scale or add new features

## Proposed Structure

```
FPL/
├── README.md
├── .env.example
├── .gitignore
│
├── backend/                    # Backend application
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration management
│   │
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   └── chat.py             # Chat endpoint
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── agent.py            # AI agent setup
│   │   ├── knowledge_base.py   # RAG service
│   │   └── tools/              # Agent tools
│   │       ├── __init__.py
│   │       ├── account_tools.py
│   │       ├── card_tools.py
│   │       ├── billing_tools.py
│   │       └── transaction_tools.py
│   │
│   └── models/                 # Data models
│       ├── __init__.py
│       └── schemas.py          # Pydantic models
│
├── mock_api/                   # Mock banking API
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── database.py              # DB setup & models
│   ├── api/                     # API routes
│   │   ├── __init__.py
│   │   ├── account.py
│   │   ├── card.py
│   │   ├── billing.py
│   │   ├── transactions.py
│   │   └── collections.py
│   └── seed.py                  # Database seeding
│
├── frontend/                    # React frontend (renamed from onecard-bot)
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   ├── services/
│   │   └── utils/
│   └── public/
│
├── data/                        # Data files (databases, etc.)
│   ├── .gitignore              # Ignore .db files
│   ├── onecard.db
│   └── rag_knowledge.db
│
├── logs/                        # Application logs
│   └── .gitignore
│
├── scripts/                     # Utility scripts
│   ├── start.sh
│   ├── start.py
│   └── setup.sh                # Initial setup script
│
├── docker/                      # Docker-related files
│   ├── Dockerfile.backend
│   ├── Dockerfile.mock
│   └── docker-compose.yml
│
├── requirements.txt             # Python dependencies
├── Makefile
└── .env.example
```

## Benefits of New Structure

1. **Clear Separation**: Backend, mock API, and frontend are clearly separated
2. **Scalability**: Easy to add new features in organized modules
3. **Maintainability**: Related code is grouped together
4. **Professional**: Follows Python/React best practices
5. **Data Organization**: All databases in one place
6. **Scripts**: Utility scripts in dedicated folder

## Migration Steps

1. Create new directory structure
2. Move files to appropriate locations
3. Update imports in all files
4. Update paths in configuration
5. Test all services still work
6. Update README with new structure

## Alternative: Keep Current Structure (Simpler)

If you prefer to keep it simple, at minimum:

```
FPL/
├── backend/          # Move backend.py here
├── mock_api/         # Move mock_apis.py here  
├── frontend/         # Rename onecard-bot
├── data/             # Move all .db files
├── scripts/          # Move start scripts
└── logs/             # Create logs directory
```

This is a lighter refactor but still improves organization.

