# Jarvis iOS App

SwiftUI-based iPhone client for Jarvis AI assistant.

## Prerequisites

- Xcode 15+ (iOS 17 SDK)
- Jarvis Python backend running with the API server

## Setup

### 1. Start the Jarvis API server

From the project root:

```bash
pip install -e .
jarvis-api
```

The API server starts on `http://localhost:8000` by default.
Set `JARVIS_API_PORT` to use a different port.

### 2. Create the Xcode project

1. Open Xcode → **File → New → Project**
2. Select **iOS → App**
3. Product Name: `Jarvis`
4. Interface: **SwiftUI**, Language: **Swift**
5. Save to a temporary location
6. Delete the generated Swift files from the new project
7. Drag the contents of `ios/Jarvis/` into the Xcode project navigator
8. Ensure all `.swift` files are added to the target

**Or** open the pre-generated `Jarvis.xcodeproj` if available.

### 3. Configure networking

- **Simulator**: Works with `http://localhost:8000` out of the box
- **Physical device**: Open Settings in the app and enter your Mac's LAN IP
  (e.g., `http://192.168.1.42:8000`)

The `Info.plist` already allows local networking (ATS exception).

## Architecture

```
Jarvis/
├── JarvisApp.swift              # App entry point
├── Models/
│   ├── Conversation.swift       # Conversation data model
│   ├── Message.swift            # Message data model
│   └── ChatRequest.swift        # API request/response types
├── Services/
│   ├── JarvisAPIClient.swift    # HTTP client for Jarvis API
│   └── ChatViewModel.swift      # Main ViewModel (ObservableObject)
├── Views/
│   ├── ConversationListView.swift  # Conversation list (home screen)
│   ├── ChatView.swift           # Chat interface with messages
│   ├── MessageBubble.swift      # Individual message bubble
│   └── SettingsView.swift       # Server URL configuration
└── Assets.xcassets/             # App icons and colors
```

## API Endpoints Used

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/conversations` | List conversations |
| POST | `/api/conversations` | Create new conversation |
| GET | `/api/conversations/{id}/messages` | Get messages |
| POST | `/api/conversations/{id}/chat` | Send message (supports SSE streaming) |
| POST | `/api/chat` | One-shot chat (creates conversation automatically) |
