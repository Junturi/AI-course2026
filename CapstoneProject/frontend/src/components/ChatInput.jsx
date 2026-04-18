import { useState } from 'react'

export default function ChatInput({ onSend, disabled }) {
    const [text, setText] = useState('')

    function handleKeyDown(e) {
        // Enter key sends the message, Shift+Enter creates a new line
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            submit()
        }
    }

    function submit() {
        if (!text.trim() || disabled) return
        onSend(text.trim())
        setText('')
    }

    return (
        <div className="input-area">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Message Gemini…"
        disabled={disabled}
        rows={2}
        autoFocus
      />
      <button onClick={submit} disabled={disabled || !text.trim()} className="btn-send">
        {disabled ? 'Waiting…' : 'Send'}
      </button>
    </div>
  )
}