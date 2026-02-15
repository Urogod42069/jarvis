const claudeAgent = require('../agents/claude-agent');
const pluginManager = require('../integrations/plugin-manager');

// Store active conversations per session ID (not socket ID)
// This allows conversations to persist across reconnections
const sessionConversations = new Map();
const socketToSession = new Map();

function initializeWebSocket(io) {
  io.on('connection', (socket) => {
    console.log('Client connected:', socket.id);

    // Handle context restoration from previous session
    socket.on('restore-context', (data) => {
      const { sessionId, history } = data;
      console.log(`Restoring context for session: ${sessionId} (${history.length} messages)`);

      socketToSession.set(socket.id, sessionId);

      // Only restore if we don't already have this session's history
      if (!sessionConversations.has(sessionId)) {
        sessionConversations.set(sessionId, history || []);
      }
    });

    // Handle chat messages with streaming
    socket.on('chat', async (data) => {
      const { message, conversationId } = data;

      // Use session ID if available, otherwise fall back to socket ID
      const sessionId = conversationId || socketToSession.get(socket.id) || socket.id;
      socketToSession.set(socket.id, sessionId);

      // Get or create conversation history for this session
      if (!sessionConversations.has(sessionId)) {
        sessionConversations.set(sessionId, []);
      }
      const history = sessionConversations.get(sessionId);

      // Add user message
      history.push({
        role: 'user',
        content: message,
      });

      // Check if message contains a plugin command
      const commandResult = await pluginManager.handleCommand(message);

      if (commandResult && commandResult.success) {
        // Command was handled by plugin
        const response = commandResult.result.message || JSON.stringify(commandResult.result, null, 2);

        history.push({
          role: 'assistant',
          content: response,
        });

        socket.emit('chat-stream', { chunk: response, messageId: Date.now() });
        socket.emit('chat-complete', {
          response,
          conversationId,
          handledBy: 'plugin',
        });
      } else {
        // No command found, use Claude AI
        let fullResponse = '';
        const result = await claudeAgent.streamChat(
          history,
          (chunk) => {
            fullResponse += chunk;
            socket.emit('chat-stream', { chunk, messageId: Date.now() });
          }
        );

        if (result.success) {
          // Add assistant response to history
          history.push({
            role: 'assistant',
            content: fullResponse,
          });

          // Keep history manageable
          if (history.length > 20) {
            history.splice(0, history.length - 20);
          }

          socket.emit('chat-complete', {
            response: fullResponse,
            conversationId,
            handledBy: 'claude',
          });
        } else {
          socket.emit('chat-error', { error: result.error });
        }
      }
    });

    // Clear conversation
    socket.on('clear-conversation', () => {
      const sessionId = socketToSession.get(socket.id);
      if (sessionId) {
        sessionConversations.delete(sessionId);
      }
      socket.emit('conversation-cleared');
    });

    socket.on('disconnect', () => {
      console.log('Client disconnected:', socket.id);
      // Don't delete the session conversation - it should persist
      // Only clean up the socket-to-session mapping
      socketToSession.delete(socket.id);
    });
  });
}

module.exports = { initializeWebSocket };
