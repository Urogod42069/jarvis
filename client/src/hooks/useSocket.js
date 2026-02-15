import { useState, useEffect, useCallback, useRef } from 'react';
import { io } from 'socket.io-client';

const SOCKET_URL = 'http://localhost:3001';
const STORAGE_KEY = 'jarvis_conversation_history';
const SESSION_ID_KEY = 'jarvis_session_id';

// Generate or retrieve session ID
function getSessionId() {
  let sessionId = localStorage.getItem(SESSION_ID_KEY);
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem(SESSION_ID_KEY, sessionId);
  }
  return sessionId;
}

// Load conversation history from localStorage
function loadConversationHistory() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : [];
  } catch (error) {
    console.error('Failed to load conversation history:', error);
    return [];
  }
}

// Save conversation history to localStorage
function saveConversationHistory(messages) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  } catch (error) {
    console.error('Failed to save conversation history:', error);
  }
}

export function useSocket() {
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState(loadConversationHistory());
  const [isStreaming, setIsStreaming] = useState(false);
  const socketRef = useRef(null);
  const currentMessageRef = useRef('');
  const sessionIdRef = useRef(getSessionId());

  useEffect(() => {
    // Initialize socket connection
    socketRef.current = io(SOCKET_URL);

    socketRef.current.on('connect', () => {
      console.log('Connected to Jarvis server');
      setConnected(true);

      // Send conversation history to server for context
      const history = loadConversationHistory();
      if (history.length > 0) {
        socketRef.current.emit('restore-context', {
          sessionId: sessionIdRef.current,
          history: history,
        });
      }
    });

    socketRef.current.on('disconnect', () => {
      console.log('Disconnected from Jarvis server');
      setConnected(false);
    });

    socketRef.current.on('chat-stream', (data) => {
      setIsStreaming(true);
      currentMessageRef.current += data.chunk;

      // Update the last message in real-time
      setMessages((prev) => {
        const updated = [...prev];
        if (updated.length > 0 && updated[updated.length - 1].role === 'assistant') {
          updated[updated.length - 1].content = currentMessageRef.current;
        } else {
          updated.push({
            role: 'assistant',
            content: currentMessageRef.current,
            timestamp: Date.now(),
          });
        }
        saveConversationHistory(updated);
        return updated;
      });
    });

    socketRef.current.on('chat-complete', () => {
      setIsStreaming(false);
      currentMessageRef.current = '';
      // Save final state
      setMessages((prev) => {
        saveConversationHistory(prev);
        return prev;
      });
    });

    socketRef.current.on('chat-error', (data) => {
      console.error('Chat error:', data.error);
      setIsStreaming(false);
      currentMessageRef.current = '';
    });

    socketRef.current.on('conversation-cleared', () => {
      setMessages([]);
      localStorage.removeItem(STORAGE_KEY);
    });

    return () => {
      socketRef.current?.disconnect();
    };
  }, []);

  const sendMessage = useCallback((content) => {
    if (!socketRef.current || !content.trim()) return;

    // Add user message
    const userMessage = {
      role: 'user',
      content: content.trim(),
      timestamp: Date.now(),
    };
    setMessages((prev) => {
      const updated = [...prev, userMessage];
      saveConversationHistory(updated);
      return updated;
    });

    // Send to server
    socketRef.current.emit('chat', {
      message: content.trim(),
      conversationId: sessionIdRef.current,
    });
  }, []);

  const clearConversation = useCallback(() => {
    if (!socketRef.current) return;
    socketRef.current.emit('clear-conversation');
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
    // Generate new session ID
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem(SESSION_ID_KEY, newSessionId);
    sessionIdRef.current = newSessionId;
  }, []);

  return {
    connected,
    messages,
    sendMessage,
    isStreaming,
    clearConversation,
  };
}
