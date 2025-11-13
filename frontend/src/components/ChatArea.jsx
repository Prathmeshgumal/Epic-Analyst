import { useEffect, useRef } from 'react'
import ChatMessage from './ChatMessage'
import './ChatArea.css'

function ChatArea({ messages, isLoading, pendingSql, messagesEndRef }) {
  const chatContainerRef = useRef(null)

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
    }
  }, [messages, isLoading])

  return (
    <div className="chat-area">
      <div className="chat-header-bar">
        <div className="chat-header-content">
          <div className="chat-header-title">
            <span>EPIC</span>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <button className="share-btn">Share</button>
        </div>
      </div>
      
      <div className="chat-container" ref={chatContainerRef}>
        <div className="messages-container">
          {messages.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))}
          
          {isLoading && (
            <div className="loading-message">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>
    </div>
  )
}

export default ChatArea

