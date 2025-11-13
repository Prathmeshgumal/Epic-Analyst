# ===========================
# TEXT-TO-SQL ENGINE CLASS
# ===========================

import psycopg2
import json
import re
import pandas as pd
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from datetime import datetime

class TextToSQLEngine:
    def __init__(self, gemini_api_key: str, db_config: Dict, schema_path: str, model: str = "gemini-2.0-flash-exp"):
        """Initialize the Text-to-SQL engine"""
        self.db_config = db_config
        self.conn = None
        self.cursor = None
        self.model_name = model

        # Initialize Gemini
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel(model)

        # Load schema
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)

        print("✅ Text-to-SQL Engine initialized!")
        print(f"📊 Loaded schema with {self.schema['metadata']['total_tables']} tables")

    def connect_db(self):
        """Connect to Supabase database"""
        try:
            # Close any existing cursor first
            if self.cursor:
                try:
                    self.cursor.close()
                except:
                    pass
                self.cursor = None
            
            # Close any existing connection
            if self.conn:
                try:
                    self.conn.close()
                except:
                    pass
                self.conn = None
            
            # Create new connection
            self.conn = psycopg2.connect(
                host=self.db_config['host'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                port=self.db_config['port'],
                connect_timeout=10,
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=5
            )
            
            # Create new cursor
            self.cursor = self.conn.cursor()
            
            print("✅ Connected to Supabase!")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            self.cursor = None
            self.conn = None
            return False

    def generate_schema_context(self, relevant_tables: Optional[List[str]] = None) -> str:
        """Generate schema context for the prompt"""
        if relevant_tables is None:
            relevant_tables = list(self.schema['tables'].keys())

        context = "# DATABASE SCHEMA\n\n"

        for table_name in relevant_tables:
            if table_name not in self.schema['tables']:
                continue

            table_info = self.schema['tables'][table_name]
            context += f"## Table: {table_name}\n"
            context += f"Row count: {table_info['row_count']}\n\n"

            # Columns
            context += "### Columns:\n"
            for col in table_info['columns']:
                pk = " (PRIMARY KEY)" if col['name'] in table_info['primary_keys'] else ""
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                context += f"- {col['name']}: {col['type']} {nullable}{pk}\n"

            # Foreign Keys
            if table_info['foreign_keys']:
                context += "\n### Foreign Keys:\n"
                for fk in table_info['foreign_keys']:
                    context += f"- {fk['column']} → {fk['references_table']}.{fk['references_column']}\n"

            # Sample Data
            if table_info['sample_data']:
                context += "\n### Sample Data (first 3 rows):\n"
                sample_df = pd.DataFrame(table_info['sample_data'][:3])
                context += sample_df.to_string(index=False) + "\n"

            context += "\n" + "-" * 80 + "\n\n"

        return context

    def identify_relevant_tables(self, user_query: str) -> List[str]:
        """Identify which tables are relevant to the user's query"""
        user_query_lower = user_query.lower()
        relevant_tables = []

        # Keywords mapping to tables
        table_keywords = {
            'lead_master': ['lead', 'customer', 'mobile', 'phone', 'source', 'cre', 'follow'],
            'ps_followup_master': ['followup', 'follow-up', 'follow up', 'ps', 'pre-sales', 'presales'],
            'qualified_leads': ['qualified', 'qualify'],
            'booking_and_retail_master': ['booking', 'retail', 'booked', 'retailed'],
            'trade_in_master': ['trade', 'trade-in', 'exchange'],
            'users': ['user', 'employee', 'staff', 'cre', 'sales'],
            'duplicate_leads': ['duplicate', 'duplicates'],
            'source_subsource_mapping': ['source', 'subsource', 'sub-source']
        }

        for table, keywords in table_keywords.items():
            if any(keyword in user_query_lower for keyword in keywords):
                relevant_tables.append(table)

        # If no specific tables identified, use main tables
        if not relevant_tables:
            relevant_tables = ['lead_master', 'ps_followup_master', 'qualified_leads', 'users']

        return relevant_tables


    def create_prompt(self, user_query: str) -> str:
        """Create prompt for the model"""
        relevant_tables = self.identify_relevant_tables(user_query)
        schema_context = self.generate_schema_context(relevant_tables)

        # Load Important Rules JSON
        with open("rules.json", "r", encoding="utf-8") as f:
            rules_data = json.load(f)
        rules_list = rules_data.get("important_rules", [])
        rules_text = "\n".join([f"{i+1}. {rule}" for i, rule in enumerate(rules_list)])

        # Load Business Context JSON
        with open("business_context.json", "r", encoding="utf-8") as f:
            business_context = json.load(f)

        # Convert nested business context to readable formatted text
        business_context_text = json.dumps(business_context, indent=2, ensure_ascii=False)

        # Build final prompt
        prompt = f"""You are an expert SQL query generator for a CRM system database.
        Your task is to convert natural language questions into valid PostgreSQL SQL queries.

        {schema_context}

        ## IMPORTANT RULES:
        {rules_text}

        ## BUSINESS CONTEXT:
        {business_context_text}

        ## USER QUERY:
        {user_query}

        ## YOUR RESPONSE:
        Generate ONLY the SQL query without any explanations, code blocks, or formatting.
        Just the raw SQL query.
        """
        return prompt

    def generate_sql(self, user_query: str) -> Dict[str, Any]:
        """Generate SQL query from natural language using Gemini"""
        try:
            print(f"\n🔍 Processing query: '{user_query}'")

            # Create prompt
            prompt = self.create_prompt(user_query)

            # Generate SQL using Gemini
            print("🤖 Asking Gemini to generate SQL...")
            response = self.model.generate_content(prompt)
            sql_query = response.text.strip()

            # Clean up the SQL query
            sql_query = self.clean_sql_query(sql_query)

            print(f"✅ Generated SQL:\n{sql_query}\n")

            return {
                'success': True,
                'sql': sql_query,
                'error': None
            }
        except Exception as e:
            return {
                'success': False,
                'sql': None,
                'error': str(e)
            }

    def determine_chart_type(self, user_query: str, data: List[Dict], columns: List[str]) -> Dict[str, Any]:
        """Determine if data should be visualized and what chart type to use"""
        try:
            if not data or len(data) == 0:
                return {'should_visualize': False}
            
            # Check if query suggests visualization
            query_lower = user_query.lower()
            visualization_keywords = ['chart', 'graph', 'plot', 'visualize', 'show', 'display', 'compare', 'trend', 'over time', 'distribution', 'percentage', 'ratio', 'breakdown', 'analysis']
            should_visualize = any(keyword in query_lower for keyword in visualization_keywords)
            
            # Analyze data structure to determine chart type
            numeric_columns = []
            categorical_columns = []
            date_columns = []
            
            for col in columns:
                # Check first few rows to determine column type
                sample_values = [str(row.get(col, '')) for row in data[:10] if col in row]
                if not sample_values:
                    continue
                
                # Try to detect numeric columns
                try:
                    float(sample_values[0])
                    numeric_columns.append(col)
                    continue
                except:
                    pass
                
                # Try to detect date columns
                if any(char in str(sample_values[0]) for char in ['-', '/', '202', '201', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']):
                    date_columns.append(col)
                    continue
                
                # Otherwise categorical
                categorical_columns.append(col)
            
            # Determine chart type based on data structure
            chart_config = {'should_visualize': False, 'chart_type': None, 'x_axis': None, 'y_axis': None}
            
            # Auto-visualize if we have:
            # - Explicit visualization keywords in query, OR
            # - Multiple numeric columns (aggregations, counts, etc.), OR
            # - Time-series data (date columns), OR
            # - Comparative data (multiple categories with values)
            has_numeric_data = len(numeric_columns) > 0
            has_time_series = len(date_columns) > 0
            has_categories = len(categorical_columns) > 0
            has_multiple_values = len(data) >= 3
            
            if not should_visualize:
                # Auto-visualize if data structure suggests it
                should_visualize = (
                    (has_numeric_data and has_categories and len(data) >= 2) or  # Categories with numbers
                    (has_numeric_data and has_time_series and len(data) >= 3) or  # Time series
                    (has_numeric_data and len(data) >= 5)  # Numeric data with enough points
                )
            
            if not should_visualize:
                return chart_config
            
            # Use LLM to determine best chart type
            chart_prompt = f"""You are a data visualization expert. Analyze the following query and data structure:

User Query: "{user_query}"

Data Structure:
- Total rows: {len(data)}
- Columns: {', '.join(columns)}
- Numeric columns: {', '.join(numeric_columns) if numeric_columns else 'None'}
- Categorical columns: {', '.join(categorical_columns) if categorical_columns else 'None'}
- Date columns: {', '.join(date_columns) if date_columns else 'None'}

Sample data (first 3 rows):
{json.dumps(data[:3], indent=2, default=str)}

Determine if this data should be visualized and what type of chart would be most appropriate.
Response format (JSON only):
{{
    "should_visualize": true/false,
    "chart_type": "bar" | "line" | "pie" | "area" | "scatter" | null,
    "x_axis": "column_name" | null,
    "y_axis": "column_name" | null,
    "explanation": "brief explanation of why this chart type"
}}

Chart types:
- bar: For comparing categories
- line: For trends over time
- pie: For showing proportions/percentages (max 10 categories)
- area: For cumulative values over time
- scatter: For relationships between two numeric variables

Return ONLY valid JSON, no other text.
"""
            
            print("📊 Determining chart type...")
            response = self.model.generate_content(chart_prompt)
            response_text = response.text.strip()
            
            # Clean up response (remove markdown code blocks if present)
            response_text = re.sub(r'^```json\s*', '', response_text, flags=re.MULTILINE)
            response_text = re.sub(r'^```\s*', '', response_text, flags=re.MULTILINE)
            response_text = re.sub(r'```$', '', response_text, flags=re.MULTILINE)
            response_text = response_text.strip()
            
            chart_config = json.loads(response_text)
            return chart_config
            
        except Exception as e:
            print(f"⚠️ Chart determination failed: {e}")
            return {'should_visualize': False}

    def generate_natural_language_response(self, user_query: str, sql_query: str, execution_result: Dict[str, Any], chart_config: Optional[Dict[str, Any]] = None) -> str:
        """Generate natural language explanation from query results"""
        try:
            row_count = execution_result.get('row_count', 0)
            data = execution_result.get('data', [])
            columns = execution_result.get('columns', [])
            
            if not execution_result['success']:
                return f"I encountered an error while processing your query: {execution_result.get('error', 'Unknown error')}. Please try rephrasing your question."
            
            if row_count == 0:
                return f"I searched for '{user_query}' but didn't find any matching results in the database. Please try adjusting your query or check if the data exists."
            
            # Prepare a summary of the data for the LLM
            data_summary = ""
            if data and len(data) > 0:
                # Take first few rows as sample
                sample_size = min(5, len(data))
                sample_data = data[:sample_size]
                
                data_summary = f"\n\nHere's a sample of the results ({sample_size} of {row_count} total rows):\n"
                for i, row in enumerate(sample_data, 1):
                    data_summary += f"\nRow {i}:\n"
                    for col, val in row.items():
                        data_summary += f"  {col}: {val}\n"
                
                if len(data) > sample_size:
                    data_summary += f"\n... and {len(data) - sample_size} more rows.\n"
            
            # Add chart information if applicable
            chart_info = ""
            if chart_config and chart_config.get('should_visualize'):
                chart_type = chart_config.get('chart_type', 'chart')
                chart_info = f"\n\nI've created a {chart_type} chart to help visualize this data. "
            
            # Create prompt for natural language response
            explanation_prompt = f"""You are a helpful data analyst assistant. A user asked: "{user_query}"

You executed a SQL query and got the following results:
- Total rows found: {row_count}
- Columns: {', '.join(columns)}

{data_summary}
{chart_info}

Provide a natural, conversational response explaining what you found. Be helpful and concise. 
Don't mention SQL queries or technical details. Just explain the results in plain language as if you're a helpful assistant.
If there are specific insights or patterns in the data, mention them naturally.
If a chart was created, briefly explain what the chart shows.
"""
            
            print("🤖 Generating natural language response...")
            response = self.model.generate_content(explanation_prompt)
            explanation = response.text.strip()
            
            return explanation
        except Exception as e:
            # Fallback to simple explanation
            row_count = execution_result.get('row_count', 0)
            if row_count > 0:
                return f"I found {row_count} result(s) matching your query. Here are the details:"
            else:
                return "I didn't find any results matching your query."

    def clean_sql_query(self, sql: str) -> str:
        """Clean and validate SQL query"""
        # Remove markdown code blocks if present
        sql = re.sub(r'^```sql\s*', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'^```\s*', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'```$', '', sql, flags=re.MULTILINE)

        # Remove extra whitespace
        sql = sql.strip()

        # Ensure it ends with semicolon
        if not sql.endswith(';'):
            sql += ';'

        return sql

    def validate_sql(self, sql: str) -> Dict[str, Any]:
        """Validate SQL query for safety"""
        sql_upper = sql.upper()

        # Check for dangerous operations
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE', 'GRANT', 'REVOKE']

        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return {
                    'valid': False,
                    'error': f"Query contains forbidden operation: {keyword}"
                }

        # Must be a SELECT query
        if not sql_upper.strip().startswith('SELECT'):
            return {
                'valid': False,
                'error': "Only SELECT queries are allowed"
            }

        return {'valid': True, 'error': None}

    def _ensure_connection(self):
        """Ensure database connection is active"""
        try:
            # Check if we have a valid connection and cursor
            if self.conn is None or self.conn.closed:
                print("⚠️ Connection is closed. Reconnecting...")
                return self.connect_db()
            
            # Check cursor validity
            if self.cursor is None or self.cursor.closed:
                print("⚠️ Cursor is closed. Creating new cursor...")
                self.cursor = self.conn.cursor()
            
            # Test the connection with a simple query
            self.cursor.execute("SELECT 1")
            self.cursor.fetchone()
            
            return True
        except Exception as e:
            print(f"⚠️ Connection test failed: {e}. Reconnecting...")
            # Close existing connections
            if self.cursor:
                try:
                    self.cursor.close()
                except:
                    pass
            if self.conn:
                try:
                    self.conn.close()
                except:
                    pass
            
            self.cursor = None
            self.conn = None
            
            return self.connect_db()

    def execute_query(self, sql: str) -> Dict[str, Any]:
        """Execute SQL query and return results"""
        try:
            # Ensure we have a valid connection
            if not self._ensure_connection():
                return {
                    'success': False,
                    'data': None,
                    'error': "Failed to establish database connection",
                    'row_count': 0
                }
            
            # Validate query
            validation = self.validate_sql(sql)
            if not validation['valid']:
                return {
                    'success': False,
                    'data': None,
                    'error': validation['error'],
                    'row_count': 0
                }

            # Execute query
            print("⚡ Executing query...")
            
            try:
                self.cursor.execute(sql)
            except (psycopg2.OperationalError, psycopg2.InterfaceError, psycopg2.InternalError) as e:
                # Connection error, try to reconnect and retry
                print(f"⚠️ Connection error: {e}. Attempting to reconnect...")
                
                # Close existing connections
                if self.cursor:
                    try:
                        self.cursor.close()
                    except:
                        pass
                if self.conn:
                    try:
                        self.conn.close()
                    except:
                        pass
                
                self.cursor = None
                self.conn = None
                
                # Reconnect
                if not self._ensure_connection():
                    return {
                        'success': False,
                        'data': None,
                        'error': f"Failed to reconnect to database: {str(e)}",
                        'row_count': 0
                    }
                
                # Retry the query
                try:
                    self.cursor.execute(sql)
                except Exception as retry_error:
                    return {
                        'success': False,
                        'data': None,
                        'error': f"Query execution failed after reconnect: {str(retry_error)}",
                        'row_count': 0
                    }

            # Fetch results
            columns = [desc[0] for desc in self.cursor.description]
            rows = self.cursor.fetchall()

            # Convert to list of dictionaries
            data = []
            for row in rows:
                data.append(dict(zip(columns, row)))

            print(f"✅ Query executed successfully! Retrieved {len(data)} rows.\n")

            return {
                'success': True,
                'data': data,
                'columns': columns,
                'error': None,
                'row_count': len(data)
            }
        except psycopg2.Error as e:
            error_msg = str(e)
            print(f"❌ PostgreSQL error: {error_msg}")
            return {
                'success': False,
                'data': None,
                'error': f"Database error: {error_msg}",
                'row_count': 0
            }
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Query execution failed: {error_msg}")
            return {
                'success': False,
                'data': None,
                'error': error_msg,
                'row_count': 0
            }

    def query(self, user_query: str, auto_execute: bool = False) -> Dict[str, Any]:
        # Generate SQL
        sql_result = self.generate_sql(user_query)

        if not sql_result['success']:
            return {
                'success': False,
                'sql': None,
                'data': None,
                'error': f"SQL generation failed: {sql_result['error']}"
            }

        # If not auto-execute, return SQL without executing
        if not auto_execute:
            return {
                'success': True,
                'sql': sql_result['sql'],
                'data': None,
                'columns': [],
                'row_count': 0,
                'error': None,
                'pending_execution': True
            }

        # Execute SQL
        execution_result = self.execute_query(sql_result['sql'])

        return {
            'success': execution_result['success'],
            'sql': sql_result['sql'],
            'data': execution_result['data'],
            'columns': execution_result.get('columns', []),
            'row_count': execution_result['row_count'],
            'error': execution_result['error'],
            'pending_execution': False
        }

    def display_results(self, result: Dict[str, Any]):
        """Display query results in a nice format"""
        print("=" * 80)
        print("QUERY RESULTS")
        print("=" * 80)

        if not result['success']:
            print(f"❌ Error: {result['error']}")
            return

        print(f"\n📊 SQL Query:\n{result['sql']}\n")
        print(f"📈 Rows returned: {result['row_count']}\n")

        if result['row_count'] > 0:
            # Display as DataFrame
            df = pd.DataFrame(result['data'])
            print(df.to_string(index=False))
        else:
            print("No results found.")

        print("\n" + "=" * 80)

    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔌 Connection closed")