const express = require('express');
const router = express.Router();
const claudeAgent = require('../agents/claude-agent');

// Store conversations in memory (replace with DB later)
const conversations = new Map();

router.post('/send', async (req, res) => {
  try {
    const { message, conversationId = 'default', userId = 'user' } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Get or create conversation history
    if (!conversations.has(conversationId)) {
      conversations.set(conversationId, []);
    }
    const history = conversations.get(conversationId);

    // Add user message to history
    history.push({
      role: 'user',
      content: message,
    });

    // Get response from Claude
    const response = await claudeAgent.chat(history);

    if (!response.success) {
      return res.status(500).json({ error: response.error });
    }

    // Add assistant response to history
    history.push({
      role: 'assistant',
      content: response.content,
    });

    // Keep history manageable (last 20 messages)
    if (history.length > 20) {
      history.splice(0, history.length - 20);
    }

    res.json({
      response: response.content,
      conversationId,
      usage: response.usage,
    });
  } catch (error) {
    console.error('Conversation error:', error);
    res.status(500).json({ error: error.message });
  }
});

router.get('/history/:conversationId', (req, res) => {
  const { conversationId } = req.params;
  const history = conversations.get(conversationId) || [];
  res.json({ history });
});

router.delete('/history/:conversationId', (req, res) => {
  const { conversationId } = req.params;
  conversations.delete(conversationId);
  res.json({ message: 'Conversation cleared' });
});

module.exports = router;
