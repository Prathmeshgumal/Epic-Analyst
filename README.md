# EPIC CRM - Text to SQL Chatbot

A modern React-based chatbot application that converts natural language queries to SQL for EPIC CRM system.

## Features

- 🤖 Modern chatbot interface with React
- 💬 WhatsApp-style chat UI
- 📊 Interactive data tables with sorting and pagination
- 💾 Chat history and session management
- ⚡ Auto-execute queries option
- 🔄 Retry and clear chat functionality
- 📱 Responsive design for mobile and desktop

## Project Structure

```
text2sql/
├── frontend/          # React frontend application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API service layer
│   │   └── App.jsx       # Main app component
│   ├── package.json
│   └── vite.config.js
├── backend/           # FastAPI backend (or root)
│   ├── main.py        # FastAPI server
│   ├── static/        # Built React app (generated)
│   └── ...
└── requirements.txt
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your database credentials:
```
SUPABASE_HOST=your_host
SUPABASE_DB=your_database
SUPABASE_USER=your_user
SUPABASE_PASSWORD=your_password
SUPABASE_PORT=5432
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash-exp
```

3. Run the backend server:
```bash
python main.py
```

The backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. For development, run the dev server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000` with hot-reload enabled.

4. For production, build the React app:
```bash
npm run build
```

This will build the React app into `backend/static` directory, which the FastAPI server will serve.

## Running the Application

### Development Mode

1. Start the backend server:
```bash
python main.py
```

2. In a separate terminal, start the frontend dev server:
```bash
cd frontend
npm run dev
```

Visit `http://localhost:3000` in your browser.

### Production Mode

1. Build the React frontend:
```bash
cd frontend
npm run build
```

2. Start the backend server (it will serve the built React app):
```bash
python main.py
```

Visit `http://localhost:8000` in your browser.

## API Endpoints

- `GET /health` - Health check
- `POST /generate-sql` - Generate SQL from natural language
- `POST /execute-sql` - Execute SQL query
- `GET /schema-info` - Get database schema information

## Technologies Used

### Frontend
- React 18
- Vite
- Axios
- Lucide React (icons)
- Modern CSS with CSS Variables

### Backend
- FastAPI
- PostgreSQL (via Supabase)
- Google Gemini AI
- Psycopg2

## Features Overview

### Chat Interface
- Modern, WhatsApp-inspired design
- Real-time message display
- Typing indicators
- Message animations

### Data Visualization
- Sortable data tables
- Pagination for large datasets
- Responsive table design
- SQL query preview

### Session Management
- Multiple chat sessions
- Chat history persistence
- Auto-save functionality
- Session switching

### Query Controls
- Auto-execute toggle
- Manual SQL execution approval
- Retry last query
- Clear current chat

## Environment Variables

Create a `.env` file in the root directory:

```env
SUPABASE_HOST=your_supabase_host
SUPABASE_DB=your_database_name
SUPABASE_USER=your_username
SUPABASE_PASSWORD=your_password
SUPABASE_PORT=5432
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash-exp
```

## Troubleshooting

1. **Frontend not loading**: Make sure you've built the React app with `npm run build`
2. **API connection error**: Verify the backend is running on port 8000
3. **Database connection failed**: Check your `.env` file credentials
4. **CORS errors**: The backend CORS is configured to allow all origins in development

## License

MIT
