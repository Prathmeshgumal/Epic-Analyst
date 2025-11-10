import streamlit as st
import requests
import pandas as pd
import uuid
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="EPIC CRM - Chat with PG",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS for WhatsApp-style chat
st.markdown("""
    <style>
    /* Center the main content area like WhatsApp */
    .main .block-container {
        max-width: 750px;
        padding: 2rem;
        margin: 0 auto;
        padding-top: 2rem;
    }
    
    /* Center the page content */
    section[data-testid="stMain"] {
        padding: 1rem;
    }
    
    /* Hide Streamlit branding for cleaner look */
    #MainMenu {visibility: visible;}
    footer {visibility: visible;}
    header {visibility: visible;}
    
    /* Button styling */
    .stButton>button {
        font-size: 16px;
        padding: 0.5rem;
        border-radius: 5px;
    }
    
    /* Title centering */
    h1 {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* Make chat messages feel more like WhatsApp */
    .stChatMessage {
        padding: 0.5rem 0;
    }
    
    /* Custom chat message styling */
    .user-message {
        background-color: #dcf8c6;
        padding: 10px 15px;
        border-radius: 10px;
        margin: 5px 0;
        margin-left: auto;
        margin-right: 0;
        max-width: 80%;
        text-align: right;
    }
    
    .assistant-message {
        background-color: #ffffff;
        padding: 10px 15px;
        border-radius: 10px;
        margin: 5px 0;
        margin-left: 0;
        margin-right: auto;
        max-width: 80%;
        border: 1px solid #e5e5e5;
    }
    
    /* Center the chat input */
    .stChatInput {
        max-width: 750px;
        margin: 0 auto;
    }
    
    /* Ensure chat input area is centered */
    div[data-testid="stChatInput"] {
        max-width: 750px;
        margin: 0 auto;
    }
    
    /* Center all table text */
    .stDataFrame table {
        width: 80%;
    }
    
    .stDataFrame table th,
    .stDataFrame table td {
        text-align: center !important;
    }
    
    /* Also center data in Streamlit's data table */
    table {
        text-align: center;
    }
    
    table th,
    table td {
        text-align: center !important;
    }
    
    /* Center pandas DataFrame output */
    div[data-testid="stDataFrame"] table th,
    div[data-testid="stDataFrame"] table td {
        text-align: center !important;
    }
    
    /* Style the sidebar */
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    /* Chat history button styling */
    .element-container button {
        text-align: left !important;
    }
    
    /* Active chat indicator */
    button[kind="secondary"]:has-text("🔵") {
        background-color: #f0f2f6;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for chat history
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())

# Get current chat messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi I am EPIC, your analyst for EPIC Toyota."}
    ]

if "current_sql" not in st.session_state:
    st.session_state.current_sql = None

if "waiting_for_response" not in st.session_state:
    st.session_state.waiting_for_response = False

if "auto_execute" not in st.session_state:
    st.session_state.auto_execute = False

# Helper functions
def check_api_health():
    """Check if API is running and healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def generate_sql(query):
    """Generate SQL from natural language query"""
    try:
        payload = {"query": query, "auto_execute": False}
        response = requests.post(
            f"{API_BASE_URL}/generate-sql",
            json=payload,
            timeout=60
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_sql(sql):
    """Execute SQL query"""
    try:
        payload = {"query": sql, "auto_execute": False}
        response = requests.post(
            f"{API_BASE_URL}/execute-sql",
            json=payload,
            timeout=60
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_chat_title(messages):
    """Generate a title from the first user message"""
    for msg in messages:
        if msg["role"] == "user":
            title = msg["content"][:50]
            if len(msg["content"]) > 50:
                title += "..."
            return title
    return "New Chat"

def get_all_user_messages(messages):
    """Extract all user messages to generate title"""
    user_msgs = []
    for msg in messages:
        if msg["role"] == "user":
            user_msgs.append(msg["content"])
    return user_msgs

# Sidebar with chat history
with st.sidebar:
    st.title("🤖 EPIC")
    
    # New Chat button
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        # Save current chat before switching
        if len(st.session_state.messages) > 1:
            title = get_chat_title(st.session_state.messages)
            st.session_state.chat_sessions[st.session_state.current_chat_id] = {
                "title": title,
                "messages": st.session_state.messages.copy(),
                "created_at": datetime.now().isoformat()
            }
        
        # Create new chat
        new_chat_id = str(uuid.uuid4())
        st.session_state.current_chat_id = new_chat_id
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi I am EPIC, your analyst for EPIC Toyota."}
        ]
        st.session_state.current_sql = None
        st.session_state.waiting_for_response = False
        st.rerun()
    
    st.markdown("---")
    
    # Chat History Section
    if st.session_state.chat_sessions:
        st.subheader("📋 Chat History")
        
        # Save current chat to history if it has conversations
        if len(st.session_state.messages) > 1:
            title = get_chat_title(st.session_state.messages)
            st.session_state.chat_sessions[st.session_state.current_chat_id] = {
                "title": title,
                "messages": st.session_state.messages.copy(),
                "created_at": datetime.now().isoformat()
            }
        
        # Display all chats
        for chat_id, chat_data in sorted(st.session_state.chat_sessions.items(), 
                                         key=lambda x: x[1]['created_at'], 
                                         reverse=True):
            is_active = chat_id == st.session_state.current_chat_id
            button_label = f"{'🔵' if is_active else '⚪'} {chat_data['title']}"
            
            if st.button(button_label, key=f"chat_{chat_id}", use_container_width=True):
                if not is_active:
                    # Save current chat
                    if len(st.session_state.messages) > 1:
                        current_title = get_chat_title(st.session_state.messages)
                        st.session_state.chat_sessions[st.session_state.current_chat_id] = {
                            "title": current_title,
                            "messages": st.session_state.messages.copy(),
                            "created_at": datetime.now().isoformat()
                        }
                    
                    # Load selected chat
                    st.session_state.current_chat_id = chat_id
                    st.session_state.messages = chat_data['messages'].copy()
                    st.session_state.current_sql = None
                    st.session_state.waiting_for_response = False
                    st.rerun()
    
    st.markdown("---")
    
    # Controls section
    st.subheader("⚙️ Controls")
    
    # Auto-execute toggle
    auto_execute = st.toggle(
        "🚀 Auto-Execute Queries",
        value=st.session_state.auto_execute,
        help="When ON: Queries execute automatically. When OFF: Ask for permission first."
    )
    st.session_state.auto_execute = auto_execute
    
    st.markdown("---")
    
    api_status = check_api_health()
    
    if api_status:
        st.success("✅ Connected")
    else:
        st.error("❌ Not Connected")
        st.info("Run: `python main.py`")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Current", use_container_width=True):
            st.session_state.messages = [
                {"role": "assistant", "content": "Hi I am EPIC, your analyst for EPIC Toyota."}
            ]
            st.session_state.current_sql = None
            st.session_state.waiting_for_response = False
            st.rerun()
    
    with col2:
        if st.button("🔁 Retry", use_container_width=True):
            # Retry the last user query if available
            if len(st.session_state.messages) > 1:
                # Find the last user message
                for i in range(len(st.session_state.messages) - 1, -1, -1):
                    if st.session_state.messages[i]["role"] == "user":
                        last_query = st.session_state.messages[i]["content"]
                        # Remove messages after this query
                        st.session_state.messages = st.session_state.messages[:i+1]
                        
                        # Regenerate SQL
                        with st.spinner("🤖 PG is reanalyzing your question..."):
                            result = generate_sql(last_query)
                        
                        if result.get('success'):
                            sql_query = result.get('sql')
                            st.session_state.current_sql = sql_query
                            
                            # Check if auto-execute is enabled
                            if st.session_state.auto_execute:
                                # Auto-execute the query - don't show SQL, go straight to results
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": "Analyzing your question and executing query..."
                                })
                                
                                # Execute the query automatically
                                with st.spinner("Executing query..."):
                                    exec_result = execute_sql(sql_query)
                                
                                # Update chat in history
                                title = get_chat_title(st.session_state.messages)
                                st.session_state.chat_sessions[st.session_state.current_chat_id] = {
                                    "title": title,
                                    "messages": st.session_state.messages.copy(),
                                    "created_at": datetime.now().isoformat()
                                }
                                
                                if exec_result.get('success'):
                                    row_count = exec_result.get('row_count', 0)
                                    data = exec_result.get('data', [])
                                    
                                    if row_count > 0:
                                        st.session_state.messages.append({
                                            "role": "assistant",
                                            "content": f"✅ Query executed successfully! Found {row_count} rows.",
                                            "result_data": data,
                                            "row_count": row_count
                                        })
                                    else:
                                        st.session_state.messages.append({
                                            "role": "assistant",
                                            "content": "✅ Query executed successfully! No results found.",
                                        })
                                else:
                                    st.session_state.messages.append({
                                        "role": "assistant",
                                        "content": f"❌ Error: {exec_result.get('error', 'Unknown error')}",
                                    })
                                
                                # Update chat in history after execution
                                title = get_chat_title(st.session_state.messages)
                                st.session_state.chat_sessions[st.session_state.current_chat_id] = {
                                    "title": title,
                                    "messages": st.session_state.messages.copy(),
                                    "created_at": datetime.now().isoformat()
                                }
                                
                                st.session_state.waiting_for_response = False
                                st.session_state.current_sql = None
                            else:
                                # Ask for permission
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": "I've generated the SQL query for your question. Would you like me to execute it?",
                                    "sql": sql_query
                                })
                                
                                st.session_state.waiting_for_response = True
                                
                                # Update chat in history
                                title = get_chat_title(st.session_state.messages)
                                st.session_state.chat_sessions[st.session_state.current_chat_id] = {
                                    "title": title,
                                    "messages": st.session_state.messages.copy(),
                                    "created_at": datetime.now().isoformat()
                                }
                        else:
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": f"❌ Sorry, I encountered an error: {result.get('error', 'Unknown error')}. Please try rephrasing your question.",
                            })
                            
                            # Update chat in history
                            title = get_chat_title(st.session_state.messages)
                            st.session_state.chat_sessions[st.session_state.current_chat_id] = {
                                "title": title,
                                "messages": st.session_state.messages.copy(),
                                "created_at": datetime.now().isoformat()
                            }
                        
                        st.rerun()
                        break

# Main interface - Centered title
st.title("🤖  Chat with EPIC")

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message("assistant", avatar="🤖"):
            st.write(message["content"])
            
            # Show SQL if available (only when auto-execute is OFF, messages with auto-execute don't have "sql" field)
            if "sql" in message:
                st.code(message["sql"], language="sql")
            
            # Show results if available
            if "result_data" in message:
                df = pd.DataFrame(message["result_data"])
                # Center align the dataframe
                st.dataframe(df.style.set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center')]},
                    {'selector': 'td', 'props': [('text-align', 'center')]}
                ]), use_container_width=True, hide_index=True)
                st.caption(f"Total rows: {message.get('row_count', 0)}")
    else:
        st.chat_message("user").write(message["content"])

# Handle SQL execution prompt
if st.session_state.waiting_for_response and st.session_state.current_sql:
    st.markdown("---")
    st.markdown("**Would you like to execute this query?**")
    
    col1, col2 = st.columns(2, gap="small")
    
    with col1:
        if st.button("✅ Yes, Execute", use_container_width=True, type="primary"):
            with st.spinner("Executing query..."):
                result = execute_sql(st.session_state.current_sql)
            
            if result.get('success'):
                row_count = result.get('row_count', 0)
                data = result.get('data', [])
                
                if row_count > 0:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"✅ Query executed successfully! Found {row_count} rows.",
                        "result_data": data,
                        "row_count": row_count
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "✅ Query executed successfully! No results found.",
                    })
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"❌ Error: {result.get('error', 'Unknown error')}",
                })
            
            # Update chat in history
            title = get_chat_title(st.session_state.messages)
            st.session_state.chat_sessions[st.session_state.current_chat_id] = {
                "title": title,
                "messages": st.session_state.messages.copy(),
                "created_at": datetime.now().isoformat()
            }
            
            st.session_state.waiting_for_response = False
            st.session_state.current_sql = None
            st.rerun()
    
    with col2:
        if st.button("❌ No, Skip", use_container_width=True):
            st.session_state.messages.append({
                "role": "assistant",
                "content": "No problem! Feel free to ask me anything else about your data.",
            })
            
            # Update chat in history
            title = get_chat_title(st.session_state.messages)
            st.session_state.chat_sessions[st.session_state.current_chat_id] = {
                "title": title,
                "messages": st.session_state.messages.copy(),
                "created_at": datetime.now().isoformat()
            }
            
            st.session_state.waiting_for_response = False
            st.session_state.current_sql = None
            st.rerun()

# Chat input
user_input = st.chat_input("Type your question here...")

if user_input:
    # Handle exit commands
    if user_input.lower() in ['cls', 'exit', 'quit', 'bye']:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Goodbye! Feel free to come back anytime. 👋"
        })
        st.rerun()
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Save chat to history with title generated from first user message
    if len(st.session_state.messages) == 2:  # Only assistant greeting + this first user message
        title = get_chat_title(st.session_state.messages)
        st.session_state.chat_sessions[st.session_state.current_chat_id] = {
            "title": title,
            "messages": st.session_state.messages.copy(),
            "created_at": datetime.now().isoformat()
        }
    
    # Generate SQL
    with st.spinner("🤖 PG is analyzing your question..."):
        result = generate_sql(user_input)
    
    if result.get('success'):
        sql_query = result.get('sql')
        st.session_state.current_sql = sql_query
        
        # Check if auto-execute is enabled
        if st.session_state.auto_execute:
            # Auto-execute the query - don't show SQL, go straight to results
            # Just show a loading message
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Analyzing your question and executing query..."
            })
            
            # Execute the query automatically
            with st.spinner("Executing query..."):
                exec_result = execute_sql(sql_query)
            
            # Update chat in history
            title = get_chat_title(st.session_state.messages)
            st.session_state.chat_sessions[st.session_state.current_chat_id] = {
                "title": title,
                "messages": st.session_state.messages.copy(),
                "created_at": datetime.now().isoformat()
            }
            
            if exec_result.get('success'):
                row_count = exec_result.get('row_count', 0)
                data = exec_result.get('data', [])
                
                if row_count > 0:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"✅ Query executed successfully! Found {row_count} rows.",
                        "result_data": data,
                        "row_count": row_count
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "✅ Query executed successfully! No results found.",
                    })
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"❌ Error: {exec_result.get('error', 'Unknown error')}",
                })
            
            # Update chat in history after execution
            title = get_chat_title(st.session_state.messages)
            st.session_state.chat_sessions[st.session_state.current_chat_id] = {
                "title": title,
                "messages": st.session_state.messages.copy(),
                "created_at": datetime.now().isoformat()
            }
            
            st.session_state.waiting_for_response = False
            st.session_state.current_sql = None
        else:
            # Ask for permission
            st.session_state.messages.append({
                "role": "assistant",
                "content": "I've generated the SQL query for your question. Would you like me to execute it?",
                "sql": sql_query
            })
            
            st.session_state.waiting_for_response = True
            
            # Update chat in history
            title = get_chat_title(st.session_state.messages)
            st.session_state.chat_sessions[st.session_state.current_chat_id] = {
                "title": title,
                "messages": st.session_state.messages.copy(),
                "created_at": datetime.now().isoformat()
            }
    else:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"❌ Sorry, I encountered an error: {result.get('error', 'Unknown error')}. Please try rephrasing your question.",
        })
        
        # Update chat in history
        title = get_chat_title(st.session_state.messages)
        st.session_state.chat_sessions[st.session_state.current_chat_id] = {
            "title": title,
            "messages": st.session_state.messages.copy(),
            "created_at": datetime.now().isoformat()
        }
    
    st.rerun()

# Footer
st.markdown("---")
with st.expander("📋 Example Questions"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **Leads:**
        - Show all leads from Google
        - How many leads last week?
        - Leads with status Qualified
        """)
    with col2:
        st.markdown("""
        **Performance:**
        - Conversion rate by source
        - Team performance this month
        - Pending follow-ups
        """)
    with col3:
        st.markdown("""
        **Customers:**
        - Customers interested in Fortuner
        - Trade-in details last month
        - Qualified leads by branch
        """)
st.caption("💡 Type your question or 'cls' to clear chat")
