import { CheckCircle, XCircle } from 'lucide-react'
import './SqlExecutionPrompt.css'

function SqlExecutionPrompt({ sql, onExecute, onSkip }) {
  return (
    <div className="sql-execution-prompt">
      <div className="prompt-content">
        <p className="prompt-question">Would you like to execute this query?</p>
        <div className="sql-preview">
          <pre><code>{sql}</code></pre>
        </div>
        <div className="prompt-actions">
          <button className="btn-execute" onClick={() => onExecute(sql)}>
            <CheckCircle size={18} />
            Yes, Execute
          </button>
          <button className="btn-skip" onClick={onSkip}>
            <XCircle size={18} />
            No, Skip
          </button>
        </div>
      </div>
    </div>
  )
}

export default SqlExecutionPrompt

