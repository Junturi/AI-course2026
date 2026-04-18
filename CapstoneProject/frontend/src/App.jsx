import { useState } from 'react'
import ChatInput from './components/ChatInput'
import MessageList from './components/MessageList'

const API_BASE = 'http://localhost:8000'

// Generate a session ID
const SESSION_ID =  `session-${Math.random().toString(36).slice(2, 9)}`

export default function App() {
    const [messages, setMessages] = useState([])
    const [isStreaming, setIsStreaming] = useState(false)
    const [error, setError] = useState(null)

    async function sendMessage(text) {
        if (!text.trim() || isStreaming) return

        setError(null)
        const userMessage = { role: 'user', content: text }
        const updatedMessages = [...messages, userMessage]
        setMessages(updatedMessages)
        setIsStreaming(true)

        // Pass history to backend
        // Backend converts it to Gemini format
        // History is everything before the new user message
        const history = messages

        try {
            await streamResponse(text, history, updatedMessages)
        } catch (err) {
            setError(err.message)
        } finally {
            setIsStreaming(false)
        }
    }

//-------------------------------------------------------------------------//
//  Streaming: fetch + ReadableStream                                      //
//  message         - new user text to be sent to backend                  //
//  history         - conversation history (before the new user message)   //
//  currentMessages - React message list including the new user message,   //
//                    used to append the assistant reply at correct index  //
//-------------------------------------------------------------------------//

    async function streamResponse(message, history, currentMessages) {
        const response = await fetch(`${API_BASE}/chat/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, history, session_id: SESSION_ID }),
        })

        if (!response.ok) {
            const err = await response.json()
            throw new Error(err.detail || `Server error: ${response.status}`)
        }

        // Create a new assistant message with empty content
        // Will be filled with chunks from the stream
        const assistantIndex = currentMessages.length
        setMessages([...currentMessages, { role: 'assistant', content: '' }])

        // getReader() allows us to read the response body in chunks as they arrive
        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''
        let fullText = ''

        while (true) {
            const { value, done } = await reader.read()
            if (done) break

            buffer += decoder.decode(value, { stream: true })

            // Split buffer into complete events (separated by double newlines)
            const events = buffer.split('\n\n')
            buffer = events.pop() // Last item may be incomplete, keep it in buffer

            for (const event of events) {
                if (!event.startsWith('data: ')) continue
                const data = JSON.parse(event.slice(6)) // Remove 'data: ' prefix

                // Data is either
                // { type: 'text', content: '<token(s)>' }
                // { type: 'done'}
                if (data.type === 'text') {
                    fullText += data.content

                    // Update the assistant message with the new full text
                    setMessages(prev => {
                        const updated = [...prev]
                        updated[assistantIndex] = { role: 'assistant', content: fullText }
                        return updated
                    })
                }
            }
        }
    }

    function clearChat() {
        setMessages([])
        setError(null)
    }

    return (
    <div className="app">
      <header className="header">
        <div className="header-title">
          <h1>LLM Chat Demo</h1>
          <span className="session-id">Session: {SESSION_ID}</span>
        </div>
        <div className="header-controls">
          <button onClick={clearChat} className="btn-clear" disabled={isStreaming}>
            Clear chat
          </button>
        </div>
      </header>

      <ChatInput onSend={sendMessage} disabled={isStreaming} />

      {error && <div className="error-banner">{error}</div>}

      <MessageList messages={messages} isStreaming={isStreaming} />
    </div>
  )
}
