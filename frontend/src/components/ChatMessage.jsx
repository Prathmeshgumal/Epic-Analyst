import DataTable from './DataTable'
import Chart from './Chart'
import './ChatMessage.css'

function ChatMessage({ message }) {
  const isUser = message.role === 'user'
  const isAssistant = message.role === 'assistant'

  return (
    <div className={`message ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-avatar">
        {isUser ? (
          <div className="user-avatar-initial">U</div>
        ) : (
          <div className="bot-avatar-initial">E</div>
        )}
      </div>
      <div className="message-content">
        <div className="message-text">
          {message.content.split('\n').map((line, i) => (
            <p key={i}>{line}</p>
          ))}
        </div>
        
        {/* Display chart if available */}
        {message.chartConfig && message.chartConfig.should_visualize && message.resultData && (
          <Chart
            data={message.resultData}
            chartConfig={message.chartConfig}
          />
        )}
        
        {/* Display data table */}
        {message.resultData && message.resultData.length > 0 && (
          <DataTable
            data={message.resultData}
            columns={message.columns}
            rowCount={message.rowCount}
          />
        )}
      </div>
    </div>
  )
}

export default ChatMessage

