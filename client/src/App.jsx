import { useState, useEffect } from 'react';
import Chat from './components/Chat';
import VoiceInterface from './components/VoiceInterface';
import { useSocket } from './hooks/useSocket';
import './styles/App.css';

function App() {
  const [mode, setMode] = useState('text'); // 'text' or 'voice'
  const { connected, messages, sendMessage, isStreaming, clearConversation } = useSocket();

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1 className="logo">
            <span className="logo-icon">⚡</span>
            JARVIS
          </h1>
          <div className="connection-status">
            <span className={`status-dot ${connected ? 'connected' : 'disconnected'}`}></span>
            {connected ? 'Online' : 'Offline'}
          </div>
        </div>
        <div className="mode-toggle">
          <button
            className={`mode-btn ${mode === 'text' ? 'active' : ''}`}
            onClick={() => setMode('text')}
          >
            💬 Text
          </button>
          <button
            className={`mode-btn ${mode === 'voice' ? 'active' : ''}`}
            onClick={() => setMode('voice')}
          >
            🎤 Voice
          </button>
        </div>
      </header>

      <main className="app-main">
        {mode === 'text' ? (
          <Chat
            messages={messages}
            onSendMessage={sendMessage}
            isStreaming={isStreaming}
            onClear={clearConversation}
          />
        ) : (
          <VoiceInterface
            messages={messages}
            onSendMessage={sendMessage}
            isStreaming={isStreaming}
          />
        )}
      </main>
    </div>
  );
}

export default App;
