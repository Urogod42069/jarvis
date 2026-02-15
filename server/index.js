const express = require('express');
const { createServer } = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const config = require('./config');
const conversationRouter = require('./api/conversation');
const { initializeWebSocket } = require('./websocket');
const pluginManager = require('./integrations/plugin-manager');
const examplePlugin = require('./integrations/example-plugin');

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: ['http://localhost:5173', 'http://localhost:5174'],
    methods: ['GET', 'POST']
  }
});

// Middleware
app.use(cors());
app.use(express.json());

// API Routes
app.use('/api/conversation', conversationRouter);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', message: 'Jarvis is online' });
});

// Register plugins
pluginManager.registerPlugin(examplePlugin);

// WebSocket initialization
initializeWebSocket(io);

httpServer.listen(config.port, () => {
  console.log(`🤖 Jarvis server running on port ${config.port}`);
  console.log(`📦 Loaded ${pluginManager.listPlugins().length} plugin(s)`);
});
