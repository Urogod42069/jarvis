# 🤖 Jarvis - Personal AI Assistant

An advanced AI personal assistant inspired by Iron Man's Jarvis. Built with Node.js, React, and Claude AI, featuring both voice and text interfaces with seamless laptop-to-phone synchronization.

## ✨ Features

- 🎤 **Voice Interface**: Natural voice conversations with speech recognition and text-to-speech
- 💬 **Text Interface**: Real-time chat with streaming responses
- 🔄 **Real-time Sync**: WebSocket-based communication for instant updates across devices
- 📱 **Progressive Web App**: Install on mobile devices for native-like experience
- 🧠 **Claude AI Integration**: Powered by Claude Sonnet 4.5 for intelligent conversations
- 🎨 **Modern UI**: Sleek, Iron Man-inspired interface with animations

## 🚀 Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn
- Claude API key from Anthropic

### Installation

1. Clone the repository:
```bash
cd /Users/vy/jarvis
```

2. Install all dependencies:
```bash
npm run install-all
```

3. Set up environment variables:
```bash
cp .env.example .env
```

4. Edit `.env` and add your Claude API key:
```
ANTHROPIC_API_KEY=your_api_key_here
```

### Running the Application

Start both server and client:
```bash
npm run dev
```

This will start:
- Express server on `http://localhost:3001`
- React client on `http://localhost:5173`

Open `http://localhost:5173` in your browser to start using Jarvis!

### Mobile Access

1. Make sure your phone is on the same WiFi network as your computer
2. Find your computer's local IP address (e.g., `192.168.1.x`)
3. Open `http://YOUR_IP:5173` on your phone's browser
4. Install as PWA for the best experience

## 🏗️ Architecture

```
jarvis/
├── server/              # Express backend
│   ├── api/            # REST API routes
│   ├── websocket/      # Socket.io handlers
│   ├── agents/         # Claude AI integration
│   ├── integrations/   # Future: smart home, automation
│   └── config/         # Configuration
├── client/             # React PWA frontend
│   ├── src/
│   │   ├── components/ # UI components
│   │   ├── hooks/      # Custom React hooks
│   │   ├── services/   # API clients
│   │   └── styles/     # CSS styling
│   └── vite.config.js  # Vite + PWA config
└── shared/             # Shared utilities
```

## 🎯 Roadmap

- [ ] Task automation and system control
- [ ] Smart home integrations (lights, thermostats, etc.)
- [ ] Calendar and reminder management
- [ ] File and application control
- [ ] Plugin system for extensibility
- [ ] Multi-user support
- [ ] Conversation history persistence (PostgreSQL)
- [ ] Advanced voice customization
- [ ] Mobile native apps (React Native)

## 🔧 Tech Stack

**Backend:**
- Node.js + Express
- Socket.io for real-time communication
- Anthropic Claude API
- (Future) PostgreSQL for persistence

**Frontend:**
- React 18
- Vite for fast development
- PWA capabilities
- Web Speech API for voice
- Socket.io client

## 📝 License

MIT

## 🙏 Acknowledgments

Inspired by Jarvis from the Iron Man series.
