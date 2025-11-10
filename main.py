import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from schema_extractor import SupabaseSchemaExtractor
from text_to_sql_engine import TextToSQLEngine
from typing import Optional

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Text-to-SQL API",
    description="API for converting natural language to SQL queries",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
SUPABASE_CONFIG = {
    "host": os.getenv("SUPABASE_HOST"),
    "database": os.getenv("SUPABASE_DB"),
    "user": os.getenv("SUPABASE_USER"),
    "password": os.getenv("SUPABASE_PASSWORD"),
    "port": os.getenv("SUPABASE_PORT"),
}

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
SCHEMA_FILE_PATH = "supabase_schema.json"

# Initialize engine
engine = None

# Request/Response models
class QueryRequest(BaseModel):
    query: str
    auto_execute: bool = False

class SQLResponse(BaseModel):
    success: bool
    sql: Optional[str] = None
    data: Optional[list] = None
    columns: list = []
    row_count: int = 0
    error: Optional[str] = None
    pending_execution: bool = False

class HealthResponse(BaseModel):
    status: str
    database_connected: bool
    schema_loaded: bool

# Initialize engine on startup
@app.on_event("startup")
async def startup_event():
    global engine
    
    print("🚀 Starting Text-to-SQL API...")
    
    # Check if schema file exists, if not extract it
    if not os.path.exists(SCHEMA_FILE_PATH):
        print("📋 Schema file not found. Extracting schema...")
        extractor = SupabaseSchemaExtractor(SUPABASE_CONFIG)
        schema = extractor.extract_complete_schema()
        if schema:
            extractor.save_schema(schema, SCHEMA_FILE_PATH)
        extractor.close()
        print("✅ Schema extracted and saved")
    
    # Initialize Text-to-SQL Engine
    try:
        engine = TextToSQLEngine(
            gemini_api_key=GEMINI_API_KEY,
            db_config=SUPABASE_CONFIG,
            schema_path=SCHEMA_FILE_PATH,
            model=MODEL
        )
        
        if not engine.connect_db():
            print("❌ Database connection failed")
            engine = None
        else:
            print("✅ Database connected successfully")
            print("✅ Text-to-SQL Engine initialized")
    except Exception as e:
        print(f"❌ Error initializing engine: {e}")
        engine = None

@app.on_event("shutdown")
async def shutdown_event():
    global engine
    if engine:
        engine.close()
        print("🔌 Database connection closed")

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health and database connection status"""
    database_connected = engine is not None and engine.conn is not None
    schema_loaded = os.path.exists(SCHEMA_FILE_PATH)
    
    return {
        "status": "healthy" if database_connected and schema_loaded else "degraded",
        "database_connected": database_connected,
        "schema_loaded": schema_loaded
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Text-to-SQL API is running",
        "version": "1.0.0",
        "endpoints": {
            "/health": "Health check",
            "/generate-sql": "Generate SQL from natural language",
            "/execute-sql": "Execute SQL query",
            "/docs": "API documentation"
        }
    }

# Generate SQL endpoint
@app.post("/generate-sql", response_model=SQLResponse)
async def generate_sql(request: QueryRequest):
    """Generate SQL query from natural language"""
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    
    try:
        result = engine.generate_sql(request.query)
        
        if not result['success']:
            return SQLResponse(
                success=False,
                error=result['error']
            )
        
        if request.auto_execute:
            # Execute the SQL
            execution_result = engine.execute_query(result['sql'])
            
            return SQLResponse(
                success=execution_result['success'],
                sql=result['sql'],
                data=execution_result['data'],
                columns=execution_result.get('columns', []),
                row_count=execution_result['row_count'],
                error=execution_result['error'],
                pending_execution=False
            )
        else:
            return SQLResponse(
                success=True,
                sql=result['sql'],
                pending_execution=True
            )
    except Exception as e:
        return SQLResponse(
            success=False,
            error=str(e)
        )

# Execute SQL endpoint
@app.post("/execute-sql", response_model=SQLResponse)
async def execute_sql(request: QueryRequest):
    """Execute a SQL query directly"""
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    
    try:
        # Validate that request.query contains SQL
        if not request.query.strip().upper().startswith('SELECT'):
            return SQLResponse(
                success=False,
                error="Only SELECT queries are allowed"
            )
        
        # Check connection before executing
        if not engine._ensure_connection():
            return SQLResponse(
                success=False,
                error="Database connection failed. Please check your database credentials."
            )
        
        execution_result = engine.execute_query(request.query)
        
        return SQLResponse(
            success=execution_result['success'],
            sql=request.query,
            data=execution_result['data'],
            columns=execution_result.get('columns', []),
            row_count=execution_result['row_count'],
            error=execution_result['error']
        )
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Execute SQL error: {error_msg}")
        return SQLResponse(
            success=False,
            error=f"Execution failed: {error_msg}"
        )

# Get schema info endpoint
@app.get("/schema-info")
async def get_schema_info():
    """Get database schema information"""
    if not os.path.exists(SCHEMA_FILE_PATH):
        raise HTTPException(status_code=404, detail="Schema file not found")
    
    import json
    with open(SCHEMA_FILE_PATH, 'r') as f:
        schema = json.load(f)
    
    return {
        "metadata": schema.get('metadata', {}),
        "tables": list(schema.get('tables', {}).keys()),
        "total_tables": len(schema.get('tables', {}))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
