export default function Sidebar({ sessions, currentSessionId, onSelect, onNew }) {
    return (
        <aside className="sidebar">
            <button className="btn-new-chat" onClick={onNew}>+ New chat</button>
            <ul className="session-list">
                {sessions.map(s => (
                    <li
                        key={s.session_id}
                        className={`session-item ${s.session_id === currentSessionId ? 'active' : ''}`}
                        onClick={() => onSelect(s.session_id)}
                    >
                        <span className="session-title">{s.title}</span>
                        <span className="session-time">
                            {new Date(s.updated_at * 1000).toLocaleDateString()}
                        </span>
                    </li>
                ))}
            </ul>
        </aside>
    )
}