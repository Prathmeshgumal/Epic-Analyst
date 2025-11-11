# EPIC CRM · Text2SQL Assistant

AI-assisted analytics for the EPIC Automotive CRM. This project lets business users ask questions in plain English and receive the exact SQL needed to explore their data, plus instant visual answers when it is safe to execute the query.

## Why It Matters

- **Bridge the gap:** Empower non-technical teammates to explore CRM insights without writing SQL.
- **Stay safe:** The engine validates every query, allowing only read-only `SELECT` statements.
- **Stay fast:** Streamlit provides a responsive chat interface backed by a FastAPI-powered inference layer and Gemini 2.0 models.
- **Stay contextual:** Business rules, schema metadata, and sample rows keep the model grounded in EPIC Toyota’s domain.

## Quick Start

- **Python 3.11+**
- **PostgreSQL (Supabase) connection** with read-only credentials
- **Google Gemini API key** with access to `gemini-2.0-flash-exp`

```bash
git clone <your fork or repo>
cd text2sql
python -m venv venv
venv\Scripts\activate        # PowerShell (Windows)
pip install -r requirements.txt
```

Create a `.env` file in the repo root:

```env
SUPABASE_HOST=your-db.supabase.co
SUPABASE_DB=epic_crm
SUPABASE_USER=readonly_user
SUPABASE_PASSWORD=super_secure_password
SUPABASE_PORT=5432
GEMINI_API_KEY=your_google_gemini_key
GEMINI_MODEL=gemini-2.0-flash-exp
```

Start both services in separate terminals:

```bash
# Backend (FastAPI)
python main.py

# Frontend (Streamlit)
streamlit run app.py
```

Visit `http://localhost:8501` to start chatting with the assistant. API docs live at `http://localhost:8000/docs`.

## Architecture at a Glance

- **Streamlit UI (`app.py`)**  
  WhatsApp-inspired chat interface, session history, quick actions, result tables.

- **FastAPI backend (`main.py`)**  
  REST endpoints for health checks, SQL generation, execution, and schema inspection.

- **Text-to-SQL engine (`text_to_sql_engine.py`)**  
  Gemini prompt engineering, query validation, retrying connections, safe execution.

- **Schema extractor (`schema_extractor.py`)**  
  Builds `supabase_schema.json` with table metadata, keys, indexes, and sample rows.

```text
User → Streamlit (chat UI) → FastAPI → Gemini + Supabase
            ↑───────────── chat history, result tables ────────────↑
```

## Key Features

- **Conversational SQL**: Gemini-driven NLU translates natural questions to SQL with business context baked in.
- **Dual execution modes**: Auto-run trusted queries or require manual confirmation.
- **Schema awareness**: Dynamic prompts include relevant tables, joins, and sample data pulled from Supabase.
- **Safety rails**: Hard blocks on mutating commands, connection retries, and error surfacing.
- **Persistent insights**: Chat sessions are tracked with friendly titles for easy recall during an analysis session.

## Repository Map

```text
app.py                   # Streamlit frontend
main.py                  # FastAPI application entrypoint
text_to_sql_engine.py    # Gemini-powered SQL generator and executor
schema_extractor.py      # Supabase schema crawler
business_context.json    # Domain facts for EPIC Toyota
rules.json               # Guardrails the LLM must follow
supabase_schema.json     # Generated schema snapshot
requirements.txt         # Shared dependencies (frontend + backend)
requirements-backend.txt # Backend-only minimal set (optional)
```

## Backend API

- `GET /health` – engine status, schema availability, DB connectivity  
- `GET /schema-info` – summary of discovered tables and metadata  
- `POST /generate-sql` – payload `{ "query": "How many leads..." , "auto_execute": false }`  
- `POST /execute-sql` – run a validated `SELECT` statement ({ "query": "SELECT ..." })

When `auto_execute=true`, the backend immediately runs the generated SQL and returns `columns`, `data`, and `row_count`.

## Customising the Assistant

- Update `business_context.json` to teach the model new domain abbreviations or KPIs.
- Extend `rules.json` with additional do/don't instructions or default filters.
- Regenerate the schema snapshot by deleting `supabase_schema.json`; the backend rebuilds it on the next start.

## Troubleshooting

- **API says “Engine not initialized”**: double-check `.env` credentials, ensure Supabase allows inbound traffic from your IP, then restart the backend.
- **Gemini auth errors**: confirm the API key and model name, ensure your Google Cloud project has Gemini enabled.
- **Frontend shows “Not Connected”**: backend may be offline; run `python main.py` and refresh Streamlit.
- **Slow responses**: schema prompts can be large; trim seldom-used tables or sample data in `schema_extractor.py` if necessary.

## Contributing

1. Fork and branch (`git checkout -b feature/awesome-insight`)
2. Keep changes focused; add/update tests or sample prompts if applicable
3. Verify formatting and linting
4. Open a pull request describing the change and manual test steps

## License

Internal project for the EPIC Automotive CRM team. Seek approval before sharing outside the organisation.
