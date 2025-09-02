#### Folder Structure


    velo/
    │── README.md
    │── requirements.txt
    │── .env.example              # Telegram token, DB path, model configs
    │── docker-compose.yml        # optional for local deployment
    │── Dockerfile
    │
    ├── app/                      # Main FastAPI app
    │   ├── main.py               # Entry point (FastAPI init, routes, Telegram webhook)
    │   ├── config.py             # Env config (dotenv)
    │   ├── db.py                 # DB engine + session (SQLAlchemy + SQLite)
    │   ├── schemas.py            # Pydantic models (requests/responses)
    │   ├── models.py             # SQLAlchemy ORM models (Campaigns, Tasks, Artifacts)
    │   ├── supervisor.py         # Orchestration logic
    │   ├── logger.py             # Structured JSON logging
    │   │
    │   ├── agents/               # Tool agents
    │   │   ├── __init__.py
    │   │   ├── audience_agent.py     # Audience Research (Ollama)
    │   │   ├── content_agent.py      # Content Generation (Ollama)
    │   │   ├── scheduler_agent.py    # Posting plan (Ollama)
    │   │   ├── creative_agent.py     # Image generation (Stable Diffusion API)
    │   │   ├── api_connector.py      # Mock external API integrations
    │   │   └── utils.py              # Shared helper functions
    │   │
    │   ├── telegram/             # Telegram bot interface
    │   │   ├── __init__.py
    │   │   ├── bot.py            # Bot setup, command handlers (/new_campaign, /regenerate)
    │   │   ├── handlers.py       # Message parsing, formatting campaign results
    │   │   └── keyboards.py      # Inline buttons (refine, regenerate)
    │   │
    │   └── services/             # Internal services
    │       ├── ollama_client.py  # Thin wrapper for Ollama API calls
    │       ├── sd_client.py      # Wrapper for Stable Diffusion API
    │       └── persistence.py    # Save/load campaign data (DB + filesystem)
    │
    ├── migrations/               # (Optional) Alembic migrations if DB evolves
    │
    ├── campaigns/                # Artifacts storage
    │   └── {campaign_id}/
    │       ├── results.json
    │       └── images/
    │           ├── img1.png
    │           └── img2.png
    │
    └── tests/                    # Pytest test suite
        ├── test_supervisor.py
        ├── test_agents.py
        ├── test_telegram.py
        └── test_end_to_end.py
