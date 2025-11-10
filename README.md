# EPIC CRM - Text to SQL System

A powerful natural language to SQL query system for EPIC CRM using Google Gemini AI, FastAPI, and Streamlit.

## Features

- 🤖 **Natural Language Processing**: Convert plain English questions into SQL queries
- 🔄 **Interactive Chat**: Streamlit-based UI for easy conversation
- 🚀 **FastAPI Backend**: RESTful API for SQL generation
- 📊 **Real-time Execution**: Generate and execute SQL queries instantly
- 🔍 **Schema Intelligence**: Automatic schema understanding and extraction
- 🛡️ **Security**: Only SELECT queries allowed, preventing data modifications

## Project Structure

```
text2sql/
├── main.py                  # FastAPI backend server
├── app.py                   # Streamlit frontend application
├── text_to_sql_engine.py    # Core SQL generation engine
├── schema_extractor.py      # Database schema extraction
├── business_context.json    # Business domain knowledge
├── rules.json              # SQL generation rules
├── supabase_schema.json    # Extracted database schema
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Installation

### 1. Clone and Setup

```bash
cd text2sql
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
SUPABASE_HOST=your_supabase_host
SUPABASE_DB=your_database_name
SUPABASE_USER=your_username
SUPABASE_PASSWORD=your_password
SUPABASE_PORT=5432
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash-exp
```

## Usage

### Method 1: FastAPI Backend + Streamlit Frontend (Recommended)

#### Step 1: Start the FastAPI Backend

```bash
python main.py
```

Or with custom host/port:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

#### Step 2: Start the Streamlit Frontend

Open a new terminal:

```bash
streamlit run app.py
```

The UI will be available at: `http://localhost:8501`

### Method 2: Direct API Testing

You can test the API directly using curl or any HTTP client:

```bash
curl -X POST "http://localhost:8000/generate-sql" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me all leads from the last 7 days", "auto_execute": true}'
```

## API Endpoints

### Health Check
```
GET /health
```
Returns API and database connection status.

### Generate SQL
```
POST /generate-sql
Body: {"query": "your question", "auto_execute": false}
```
Generates SQL from natural language query.

### Execute SQL
```
POST /execute-sql
Body: {"query": "SELECT * FROM table"}
```
Executes a SQL query directly.

### Schema Info
```
GET /schema-info
```
Returns database schema information.

## Example Queries

### Lead Analysis
- "Show me all leads from Google source"
- "How many leads were created in the last 7 days?"
- "Display leads with status 'Qualified'"

### Performance Metrics
- "What is the conversion rate by source?"
- "Show me team performance this month"
- "Which leads are pending follow-up?"

### Customer Analysis
- "List all customers interested in Fortuner"
- "Show me trade-in details from last month"
- "Display qualified leads by branch"

## Architecture

```
┌─────────────────────────────────────────────┐
│         Streamlit Frontend (app.py)         │
│  • User Interface                            │
│  • Chat History                               │
│  • Query Input/Output                         │
└─────────────────┬───────────────────────────┘
                  │ HTTP Requests
                  ▼
┌─────────────────────────────────────────────┐
│      FastAPI Backend (main.py)               │
│  • REST API Endpoints                        │
│  • Request Validation                         │
│  • CORS Handling                              │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│    Text-to-SQL Engine (text_to_sql_engine.py) │
│  • Gemini AI Integration                      │
│  • SQL Generation                             │
│  • Query Execution                            │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│         PostgreSQL Database                   │
│  • EPIC CRM Data                              │
└─────────────────────────────────────────────┘
```

## Features Explained

### Security
- Only SELECT queries are allowed
- Automatic validation of dangerous operations
- API-level security checks

### Intelligence
- Context-aware SQL generation
- Business rules integration
- Schema-aware joins and filters
- Automatic LIMIT on large queries

### User Experience
- Real-time chat interface
- Query history preservation
- Error handling and feedback
- Quick action buttons

## Troubleshooting

### API Not Available
- Ensure FastAPI server is running: `python main.py`
- Check if port 8000 is available
- Verify `.env` configuration

### Database Connection Failed
- Verify Supabase credentials in `.env`
- Check database host accessibility
- Ensure schema file exists: `supabase_schema.json`

### Gemini API Errors
- Verify `GEMINI_API_KEY` in `.env`
- Check API quota and limits
- Ensure model name is correct

## Development

### Adding New Features
1. Update `text_to_sql_engine.py` for logic changes
2. Update `main.py` for API endpoints
3. Update `app.py` for UI changes

### Testing
```bash
# Test API endpoints
curl http://localhost:8000/health

# Test SQL generation
curl -X POST http://localhost:8000/generate-sql \
  -H "Content-Type: application/json" \
  -d '{"query": "test query"}'
```

## License

This project is developed for EPIC CRM - Automotive Dealership Management System.

## Support

For issues and questions, please contact the development team.

