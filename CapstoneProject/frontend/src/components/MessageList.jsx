export default function MessageList({ messages, isStreaming }) {
    if (messages.length === 0) {
        return (
      <div className="messages empty">
        <p className="empty-hint">
          Ask anything. Gemini is here to help!
        </p>
      </div>
    )
  }

    return (
        <div className="messages">
      {messages.map((msg, i) => {

        return (
          <div key={i} className={`message ${msg.role}`}>
            <div className="message-label">
              {msg.role === 'user' ? 'You' : 'Gemini'}
            </div>
            <div className="message-content">
              {msg.content || <span className="thinking">thinking…</span>}
            </div>
          </div>
        )
      })}
    </div>
  )
}
