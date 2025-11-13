import { useState } from 'react'
import { Menu, X, Plus, Search, LibraryBig, Sparkles, FolderOpen } from 'lucide-react'
import './Sidebar.css'

function Sidebar({
  isOpen,
  onToggle,
  chatSessions,
  currentChatId,
  onNewChat,
  onLoadChat,
  onClearChat,
  onRetry,
  apiHealth
}) {
  const sortedSessions = Object.entries(chatSessions).sort(
    (a, b) => new Date(b[1].createdAt) - new Date(a[1].createdAt)
  )

  return (
    <>
      <div className={`sidebar-overlay ${isOpen ? 'open' : ''}`} onClick={onToggle} />
      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">EPIC</div>
          <button className="toggle-btn" onClick={onToggle}>
            {isOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        <div className="sidebar-content">
          <button className="new-chat-btn" onClick={onNewChat}>
            <Plus size={16} />
            <span>New chat</span>
          </button>

          <nav className="sidebar-nav">
            <button className="nav-item">
              <Search size={16} />
              <span>Search chats</span>
            </button>
            <button className="nav-item">
              <LibraryBig size={16} />
              <span>Library</span>
            </button>
            <button className="nav-item">
              <Sparkles size={16} />
              <span>GPTs</span>
            </button>
            <button className="nav-item">
              <FolderOpen size={16} />
              <span>Projects</span>
            </button>
          </nav>

          {sortedSessions.length > 0 && (
            <div className="chat-history">
              <h3 className="chats-header">Chats</h3>
              <div className="chat-list">
                {sortedSessions.map(([chatId, chatData]) => (
                  <button
                    key={chatId}
                    className={`chat-item ${chatId === currentChatId ? 'active' : ''}`}
                    onClick={() => onLoadChat(chatId)}
                  >
                    <span className="chat-title">{chatData.title}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="api-status">
            {apiHealth ? (
              apiHealth.database_connected && apiHealth.schema_loaded ? (
                <div className="status-item success">
                  <span>✅ Connected</span>
                </div>
              ) : (
                <div className="status-item error">
                  <span>❌ Not Connected</span>
                </div>
              )
            ) : (
              <div className="status-item loading">
                <span>Checking...</span>
              </div>
            )}
          </div>
        </div>

        <div className="sidebar-footer">
          <div className="user-profile">
            <div className="user-avatar">EP</div>
            <div className="user-info">
              <div className="user-name">User</div>
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}

export default Sidebar

