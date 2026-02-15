# Jarvis AI Assistant - Claude Code Instructions

## Project Overview

Jarvis is a personal AI assistant inspired by Iron Man's Jarvis, featuring voice and text interfaces with real-time streaming responses. Built with Node.js/Express backend, React frontend, and powered by Claude AI (Anthropic).

**Key Features:**
- Dual interface (voice + text)
- Real-time WebSocket communication
- Persistent conversation history (localStorage + session-based)
- Extensible plugin system
- Progressive Web App (cross-platform)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client (React)                       │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │  Chat.jsx      │  │ VoiceInterface│  │  useSocket.js   │ │
│  │  (Text UI)     │  │  (Voice UI)   │  │  (WebSocket)    │ │
│  └────────────────┘  └──────────────┘  └─────────────────┘ │
│           │                  │                    │          │
│           └──────────────────┴────────────────────┘          │
│                              │                                │
│                    localStorage (persistence)                 │
└─────────────────────────────┬───────────────────────────────┘
                              │ Socket.io
┌─────────────────────────────▼───────────────────────────────┐
│                      Server (Express)                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            WebSocket Handler (session-based)         │   │
│  └────────────┬─────────────────────────────────────────┘   │
│               │                                              │
│       ┌───────▼────────┐              ┌─────────────────┐   │
│       │ Plugin Manager │              │  Claude Agent   │   │
│       │  (Commands)    │              │  (AI Responses) │   │
│       └────────────────┘              └─────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

## Project Structure

### Backend (`/server`)

- **`server/index.js`** - Main entry point, Express + Socket.io setup
- **`server/config/index.js`** - Environment configuration
- **`server/websocket/index.js`** - WebSocket handlers, session management, message routing
- **`server/agents/claude-agent.js`** - Claude API integration (streaming + regular chat)
- **`server/integrations/plugin-manager.js`** - Plugin system core
- **`server/integrations/example-plugin.js`** - Demo plugin (time, system info)
- **`server/api/conversation.js`** - REST API for conversations (legacy, WebSocket preferred)

### Frontend (`/client`)

- **`client/src/App.jsx`** - Main app component, mode switching (text/voice)
- **`client/src/components/Chat.jsx`** - Text chat interface
- **`client/src/components/VoiceInterface.jsx`** - Voice interface with Web Speech API
- **`client/src/hooks/useSocket.js`** - WebSocket connection + localStorage persistence
- **`client/src/styles/*.css`** - Iron Man-themed styling

## Key Concepts

### 1. Session-Based Conversations

**Important:** Conversations are tied to **session IDs**, not socket IDs.

- Session ID is generated in browser on first visit: `session_${timestamp}_${random}`
- Stored in `localStorage` under key `jarvis_session_id`
- When client connects, it sends `restore-context` event with session ID + message history
- Server maintains `sessionConversations` Map keyed by session ID
- Conversations persist across page reloads and reconnections

**Server side:**
```javascript
// sessionConversations: Map<sessionId, messageArray>
// socketToSession: Map<socketId, sessionId>
```

**Client side:**
```javascript
// localStorage keys:
// - 'jarvis_session_id': unique session identifier
// - 'jarvis_conversation_history': array of messages
```

### 2. Plugin System

Plugins extend Jarvis capabilities without modifying core code.

**Plugin Structure:**
```javascript
{
  name: 'plugin-name',
  description: 'What it does',
  initialize: () => { /* setup code */ },
  commands: [
    {
      trigger: 'keyword',
      description: 'What this does',
      handler: async (message) => {
        return { message: 'response' };
      }
    }
  ]
}
```

**How it works:**
1. User sends message via WebSocket
2. Server checks `pluginManager.handleCommand(message)`
3. If trigger found → plugin handles it
4. Else → message goes to Claude AI

**Adding new plugins:**
1. Create plugin file in `server/integrations/`
2. Register in `server/index.js`: `pluginManager.registerPlugin(myPlugin)`

### 3. Real-Time Streaming

Claude responses stream in real-time using Socket.io events:

**Flow:**
```
Client                          Server
  │──── emit('chat') ────────────▶│
  │                                │ Claude API (stream)
  │◀─── emit('chat-stream') ──────│ (multiple chunks)
  │◀─── emit('chat-stream') ──────│
  │◀─── emit('chat-complete') ────│
```

**Events:**
- `chat` - Send message
- `chat-stream` - Receive response chunk
- `chat-complete` - Response finished
- `chat-error` - Error occurred
- `restore-context` - Restore session on reconnect
- `clear-conversation` - Start fresh

## Development Workflows

### Starting Development

```bash
cd /Users/vy/jarvis
npm run dev  # Starts server (3001) + client (5173/5174)
```

Runs concurrently:
- `npm run server` → nodemon server/index.js
- `npm run client` → cd client && vite

### Making Changes

**Backend changes:**
- Edit files in `server/`
- Nodemon auto-restarts on file save
- Check terminal for errors

**Frontend changes:**
- Edit files in `client/src/`
- Vite hot-reloads automatically
- Browser auto-updates

**Plugin development:**
1. Create plugin file: `server/integrations/my-plugin.js`
2. Follow template in `example-plugin.js`
3. Register in `server/index.js`
4. Test by mentioning trigger word in chat

### Testing

**Manual testing checklist:**
- [ ] Text chat works (type message → get response)
- [ ] Voice works (click mic → speak → hear response)
- [ ] Reload persists conversation
- [ ] Clear button resets conversation
- [ ] Plugin commands work ("what time is it?")
- [ ] Connection status shows correctly
- [ ] Mobile responsive (resize browser)

### Debugging

**Backend:**
```bash
# Check server logs in terminal
# Look for:
# - "Client connected: <socketId>"
# - "Restoring context for session: <sessionId>"
# - Plugin command matches
# - Claude API errors
```

**Frontend:**
```bash
# Browser console (F12)
# Look for:
# - "Connected to Jarvis server"
# - WebSocket events
# - localStorage contents: localStorage.getItem('jarvis_conversation_history')
```

**Common issues:**
- Port conflicts → Kill process on 3001/5173: `lsof -ti:3001 | xargs kill -9`
- CORS errors → Check `server/index.js` CORS config includes your port
- Lost context → Check localStorage in browser DevTools
- Voice not working → Use Chrome/Edge, check mic permissions

## Code Conventions

### Backend

- Use `const` for requires and non-reassigned variables
- Use async/await for asynchronous operations
- Export modules with `module.exports`
- Error handling: try-catch in async functions
- Logging: `console.log()` for important events

### Frontend

- Functional components with hooks (no class components)
- Use `useCallback` for event handlers to prevent re-renders
- CSS modules or separate CSS files (no inline styles for large blocks)
- State management: useState for local, useRef for non-reactive values

### Naming Conventions

- **Files:** kebab-case (`claude-agent.js`, `use-socket.js`)
- **Components:** PascalCase (`Chat.jsx`, `VoiceInterface.jsx`)
- **Functions:** camelCase (`sendMessage`, `handleCommand`)
- **Constants:** UPPER_SNAKE_CASE (`SOCKET_URL`, `STORAGE_KEY`)

## Environment Variables

Located in `/Users/vy/jarvis/.env`:

```bash
PORT=3001                          # Server port
ANTHROPIC_API_KEY=sk-ant-api03-... # Claude API key
NODE_ENV=development               # Environment
```

**Never commit `.env` to git** - it's in `.gitignore`

## Common Tasks

### Change AI Model

Edit `server/agents/claude-agent.js`:
```javascript
model: 'claude-sonnet-4-5-20250929',  // Change to opus/haiku
```

### Modify System Prompt

Edit `SYSTEM_PROMPT` in `server/agents/claude-agent.js`

### Add New API Endpoint

1. Create route in `server/api/` or add to existing file
2. Register in `server/index.js`: `app.use('/api/route', router)`

### Change UI Theme

Edit CSS variables in `client/src/styles/index.css`:
```css
:root {
  --accent-blue: #00d4ff;
  --accent-purple: #9d4edd;
  /* ... */
}
```

### Add Voice Commands

Create plugin with voice-specific triggers:
```javascript
{
  trigger: 'jarvis',
  handler: async (message) => {
    // Extract command after "jarvis"
    // Execute action
  }
}
```

## Important Notes

### Security Considerations

- **API Key Protection:** Never expose ANTHROPIC_API_KEY in client code
- **Input Validation:** Sanitize user inputs before processing (especially for system commands)
- **CORS:** Currently allows all localhost ports for dev - restrict in production
- **Rate Limiting:** Not implemented - add before public deployment

### Performance

- **Conversation History:** Limited to last 20 messages to prevent memory bloat
- **localStorage:** Has 5-10MB limit - conversations may fill up over time
- **WebSocket:** More efficient than polling for real-time updates

### Future Enhancements (TODO)

- [ ] Database persistence (PostgreSQL/SQLite) instead of in-memory
- [ ] User authentication system
- [ ] Conversation search/export
- [ ] Multi-device sync (same user, multiple browsers)
- [ ] Voice customization (pitch, rate, voice selection)
- [ ] Smart home integrations
- [ ] Task automation framework
- [ ] Mobile native apps (React Native)

## Plugin Ideas

Suggested plugins to build:

1. **Weather** - Integrate OpenWeather API
2. **Calendar** - Google Calendar integration
3. **Email** - Gmail API for reading/sending emails
4. **File System** - Safe file operations (read, list, search)
5. **Music Control** - Spotify/Apple Music integration
6. **Reminders** - Set and manage reminders
7. **News** - Fetch latest news from RSS/APIs
8. **Smart Home** - HomeKit, Hue, Nest integration
9. **Screenshot** - Take and analyze screenshots
10. **Code Runner** - Execute safe code snippets

## Deployment Considerations

**Not production-ready yet.** Before deploying:

1. Add authentication (JWT, OAuth)
2. Implement rate limiting
3. Set up proper database (PostgreSQL)
4. Use environment-specific configs
5. Add HTTPS/SSL
6. Implement logging (Winston, Morgan)
7. Add monitoring (error tracking)
8. Secure WebSocket connections (wss://)
9. Add input validation/sanitization
10. Implement proper CORS policies

## Getting Help

- **Documentation:** See README.md, QUICKSTART.md, PLUGIN_GUIDE.md
- **Issues:** Check console logs (server terminal + browser console)
- **API Docs:** https://docs.anthropic.com/claude/reference/
- **Socket.io Docs:** https://socket.io/docs/v4/

## Version History

- **v1.0.0** (Feb 2026) - Initial release with voice, text, plugins, persistence

---

**Remember:** This is a personal assistant that handles sensitive conversations. Always prioritize user privacy and data security.
