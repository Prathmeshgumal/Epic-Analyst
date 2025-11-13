import { useState, useRef, useEffect } from 'react'
import { Send, Mic, Volume2 } from 'lucide-react'
import './ChatInput.css'

function ChatInput({ onSendMessage, isLoading }) {
  const [input, setInput] = useState('')
  const textareaRef = useRef(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [input])

  function handleSubmit(e) {
    e.preventDefault()
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim())
      setInput('')
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="chat-input-container">
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <div className="input-wrapper">
          <button type="button" className="mic-button" title="Voice input">
            <Mic size={18} />
          </button>
          <textarea
            ref={textareaRef}
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything"
            rows={1}
            disabled={isLoading}
          />
          <button
            type="submit"
            className="send-button"
            disabled={!input.trim() || isLoading}
          >
            <Send size={18} />
          </button>
          <button type="button" className="waveform-button" title="Voice input">
            <Volume2 size={18} />
          </button>
        </div>
      </form>
      
      <div className="chat-disclaimer">
        EPIC can make mistakes. Check important info.
      </div>
    </div>
  )
}

export default ChatInput

