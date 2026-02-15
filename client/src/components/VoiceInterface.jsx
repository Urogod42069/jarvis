import { useState, useEffect, useRef } from 'react';
import '../styles/VoiceInterface.css';

function VoiceInterface({ messages, onSendMessage, isStreaming }) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);
  const recognitionRef = useRef(null);
  const synthRef = useRef(window.speechSynthesis);

  useEffect(() => {
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;

      recognitionRef.current.onresult = (event) => {
        const current = event.resultIndex;
        const transcriptText = event.results[current][0].transcript;
        setTranscript(transcriptText);

        if (event.results[current].isFinal) {
          onSendMessage(transcriptText);
          setTranscript('');
          setIsListening(false);
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [onSendMessage]);

  // Auto-speak Jarvis responses
  useEffect(() => {
    if (messages.length === 0) return;
    const lastMessage = messages[messages.length - 1];

    if (lastMessage.role === 'assistant' && !isStreaming) {
      speakText(lastMessage.content);
    }
  }, [messages, isStreaming]);

  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in your browser');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      // Stop any ongoing speech
      synthRef.current.cancel();
      setIsSpeaking(false);

      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const speakText = (text) => {
    if (!('speechSynthesis' in window)) return;

    // Cancel any ongoing speech
    synthRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.1;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    synthRef.current.speak(utterance);
  };

  const stopSpeaking = () => {
    synthRef.current.cancel();
    setIsSpeaking(false);
  };

  const lastAssistantMessage = messages
    .slice()
    .reverse()
    .find((m) => m.role === 'assistant');

  return (
    <div className="voice-interface">
      <div className="voice-visualizer">
        <div className={`voice-orb ${isListening ? 'listening' : ''} ${isSpeaking ? 'speaking' : ''}`}>
          <div className="orb-inner"></div>
          <div className="orb-pulse"></div>
        </div>
      </div>

      <div className="voice-status">
        {isListening && (
          <div className="status-message listening">
            🎤 Listening...
            {transcript && <div className="transcript-preview">{transcript}</div>}
          </div>
        )}
        {isStreaming && !isListening && (
          <div className="status-message thinking">
            ⚡ Processing...
          </div>
        )}
        {isSpeaking && !isListening && !isStreaming && (
          <div className="status-message speaking">
            🔊 Speaking...
          </div>
        )}
        {!isListening && !isStreaming && !isSpeaking && (
          <div className="status-message idle">
            Ready to assist
          </div>
        )}
      </div>

      {lastAssistantMessage && (
        <div className="last-response">
          <div className="response-label">Last response:</div>
          <div className="response-text">{lastAssistantMessage.content}</div>
        </div>
      )}

      <div className="voice-controls">
        <button
          className={`voice-btn ${isListening ? 'active' : ''}`}
          onClick={toggleListening}
          disabled={isStreaming}
        >
          {isListening ? '🎤 Stop' : '🎤 Talk to Jarvis'}
        </button>
        {isSpeaking && (
          <button className="mute-btn" onClick={stopSpeaking}>
            🔇 Mute
          </button>
        )}
      </div>
    </div>
  );
}

export default VoiceInterface;
