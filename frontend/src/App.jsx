import { useState, useEffect, useRef } from 'react'
import Sidebar from './components/Sidebar'
import ChatArea from './components/ChatArea'
import ChatInput from './components/ChatInput'
import { apiService } from './services/api'
import './App.css'

function App() {
  const [chatSessions, setChatSessions] = useState(() => {
    const saved = localStorage.getItem('chatSessions')
    return saved ? JSON.parse(saved) : {}
  })
  
  const [currentChatId, setCurrentChatId] = useState(() => {
    const saved = localStorage.getItem('currentChatId')
    return saved || generateId()
  })
  
  const [messages, setMessages] = useState(() => {
    const saved = localStorage.getItem(`chat_${currentChatId}`)
    if (saved) {
      return JSON.parse(saved)
    }
    return [
      { role: 'assistant', content: 'Hi I am EPIC, your analyst for EPIC Toyota.' }
    ]
  })
  
  // Auto-execute is now always enabled, so we don't need this state
  
  const [apiHealth, setApiHealth] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [pendingSql, setPendingSql] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(() => {
    const saved = localStorage.getItem('sidebarOpen')
    return saved === null ? true : saved === 'true'
  })
  const messagesEndRef = useRef(null)

  // Generate unique ID
  function generateId() {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  // Save messages to localStorage
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(`chat_${currentChatId}`, JSON.stringify(messages))
    }
  }, [messages, currentChatId])

  // Save chat sessions
  useEffect(() => {
    localStorage.setItem('chatSessions', JSON.stringify(chatSessions))
  }, [chatSessions])

  // Save current chat ID
  useEffect(() => {
    localStorage.setItem('currentChatId', currentChatId)
  }, [currentChatId])

  // Save sidebar state
  useEffect(() => {
    localStorage.setItem('sidebarOpen', sidebarOpen.toString())
  }, [sidebarOpen])

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Check API health on mount
  useEffect(() => {
    checkApiHealth()
    const interval = setInterval(checkApiHealth, 30000) // Check every 30 seconds
    return () => clearInterval(interval)
  }, [])

  // Save current chat to sessions
  useEffect(() => {
    if (messages.length > 1) {
      const title = getChatTitle(messages)
      setChatSessions(prev => ({
        ...prev,
        [currentChatId]: {
          title,
          messages: [...messages],
          createdAt: new Date().toISOString()
        }
      }))
    }
  }, [messages, currentChatId])

  function getChatTitle(msgs) {
    for (const msg of msgs) {
      if (msg.role === 'user') {
        const title = msg.content.slice(0, 50)
        return title.length < msg.content.length ? title + '...' : title
      }
    }
    return 'New Chat'
  }

  async function checkApiHealth() {
    try {
      const health = await apiService.checkHealth()
      setApiHealth(health)
    } catch (error) {
      setApiHealth({ status: 'error', database_connected: false, schema_loaded: false })
    }
  }

  function createNewChat() {
    // Save current chat
    if (messages.length > 1) {
      const title = getChatTitle(messages)
      setChatSessions(prev => ({
        ...prev,
        [currentChatId]: {
          title,
          messages: [...messages],
          createdAt: new Date().toISOString()
        }
      }))
    }

    // Create new chat
    const newChatId = generateId()
    setCurrentChatId(newChatId)
    setMessages([
      { role: 'assistant', content: 'Hi I am EPIC, your analyst for EPIC Toyota.' }
    ])
    setPendingSql(null)
  }

  function loadChat(chatId) {
    if (chatId === currentChatId) return

    // Save current chat
    if (messages.length > 1) {
      const title = getChatTitle(messages)
      setChatSessions(prev => ({
        ...prev,
        [currentChatId]: {
          title,
          messages: [...messages],
          createdAt: new Date().toISOString()
        }
      }))
    }

    // Load selected chat
    setCurrentChatId(chatId)
    const chatData = chatSessions[chatId]
    if (chatData) {
      setMessages(chatData.messages)
      setPendingSql(null)
    }
  }

  function clearCurrentChat() {
    setMessages([
      { role: 'assistant', content: 'Hi I am EPIC, your analyst for EPIC Toyota.' }
    ])
    setPendingSql(null)
  }

  async function handleSendMessage(userInput) {
    if (!userInput.trim() || isLoading) return

    // Handle exit commands
    if (['cls', 'exit', 'quit', 'bye'].includes(userInput.toLowerCase())) {
      const newMessage = { role: 'user', content: userInput }
      const response = { role: 'assistant', content: 'Goodbye! Feel free to come back anytime. 👋' }
      setMessages(prev => [...prev, newMessage, response])
      return
    }

    // Add user message
    const userMessage = { role: 'user', content: userInput }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Generate SQL and execute automatically - returns natural language response
      const result = await apiService.generateSql(userInput, true)

      if (result.success) {
        // Use natural language explanation if available, otherwise fallback
        const content = result.natural_language || (
          result.row_count > 0
            ? `I found ${result.row_count} result(s) matching your query.`
            : 'I didn\'t find any results matching your query.'
        )

        setMessages(prev => [...prev, {
          role: 'assistant',
          content,
          resultData: result.data || [],
          rowCount: result.row_count || 0,
          columns: result.columns || [],
          chartConfig: result.chart_config || null
        }])
      } else {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `❌ Sorry, I encountered an error: ${result.error || 'Unknown error'}. Please try rephrasing your question.`
        }])
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `❌ Error: ${error.message || 'Failed to connect to API. Please check if the backend is running.'}`
      }])
    } finally {
      setIsLoading(false)
      setPendingSql(null)  // Always clear pending SQL since we auto-execute
    }
  }

  // Removed handleExecuteSql and handleSkipExecution - no longer needed since we auto-execute

  async function handleRetry() {
    // Find last user message
    let lastUserMessage = null
    let lastUserIndex = -1
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === 'user') {
        lastUserMessage = messages[i].content
        lastUserIndex = i
        // Remove messages after this
        setMessages(prev => prev.slice(0, i + 1))
        break
      }
    }

    if (lastUserMessage) {
      await handleSendMessage(lastUserMessage)
    }
  }

  return (
    <div className="app">
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        chatSessions={chatSessions}
        currentChatId={currentChatId}
        onNewChat={createNewChat}
        onLoadChat={loadChat}
        onClearChat={clearCurrentChat}
        onRetry={handleRetry}
        apiHealth={apiHealth}
      />
      <div className={`main-content ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <ChatArea
          messages={messages}
          isLoading={isLoading}
          pendingSql={null}
          messagesEndRef={messagesEndRef}
        />
        <ChatInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </div>
    </div>
  )
}

export default App

