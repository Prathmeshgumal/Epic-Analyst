import axios from 'axios'

// Use proxy in development, direct URL in production
const API_BASE_URL = import.meta.env.MODE === 'development' 
  ? '/api'  // Proxy via Vite dev server
  : (import.meta.env.VITE_API_URL || 'http://localhost:8000')

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const apiService = {
  async checkHealth() {
    const response = await api.get('/health')
    return response.data
  },

  async generateSql(query, autoExecute = true) {
    // Always auto-execute now
    const response = await api.post('/generate-sql', {
      query,
      auto_execute: true,
    })
    return response.data
  },

  async executeSql(sql) {
    const response = await api.post('/execute-sql', {
      query: sql,
      auto_execute: false,
    })
    return response.data
  },

  async getSchemaInfo() {
    const response = await api.get('/schema-info')
    return response.data
  },
}

