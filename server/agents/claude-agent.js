const Anthropic = require('@anthropic-ai/sdk');
const config = require('../config');

const client = new Anthropic({
  apiKey: config.anthropicApiKey,
});

const SYSTEM_PROMPT = `You are Jarvis, an advanced AI personal assistant inspired by the AI from Iron Man. You are:

- Highly intelligent and capable
- Helpful, efficient, and proactive
- Able to control systems, automate tasks, and provide information
- Professional yet personable
- Context-aware across conversations

You can help with:
- Answering questions and providing information
- Task automation and system control
- Scheduling and reminders
- Smart home control (when integrated)
- File and application management
- And much more

Be concise but thorough. Address the user naturally and maintain context from previous messages in the conversation.`;

class ClaudeAgent {
  async chat(messages, options = {}) {
    try {
      const response = await client.messages.create({
        model: 'claude-sonnet-4-5-20250929',
        max_tokens: options.maxTokens || 4096,
        system: SYSTEM_PROMPT,
        messages: messages,
      });

      return {
        success: true,
        content: response.content[0].text,
        usage: response.usage,
      };
    } catch (error) {
      console.error('Claude API error:', error);
      return {
        success: false,
        error: error.message,
      };
    }
  }

  async streamChat(messages, onChunk, options = {}) {
    try {
      const stream = await client.messages.create({
        model: 'claude-sonnet-4-5-20250929',
        max_tokens: options.maxTokens || 4096,
        system: SYSTEM_PROMPT,
        messages: messages,
        stream: true,
      });

      let fullText = '';
      for await (const event of stream) {
        if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
          const chunk = event.delta.text;
          fullText += chunk;
          onChunk(chunk);
        }
      }

      return {
        success: true,
        content: fullText,
      };
    } catch (error) {
      console.error('Claude streaming error:', error);
      return {
        success: false,
        error: error.message,
      };
    }
  }
}

module.exports = new ClaudeAgent();
