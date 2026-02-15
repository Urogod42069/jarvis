# Jarvis Plugin Development Guide

This guide explains how to extend Jarvis with custom plugins.

## What are Plugins?

Plugins allow you to add custom capabilities to Jarvis, such as:
- System automation (file operations, process management)
- External API integrations (weather, news, calendar)
- Smart home control (lights, thermostats, locks)
- Custom commands and workflows
- Database integrations
- And much more!

## Creating a Plugin

### 1. Basic Plugin Structure

Create a new file in `server/integrations/your-plugin-name.js`:

```javascript
const myPlugin = {
  name: 'my-plugin',
  description: 'Description of what this plugin does',

  // Optional: Initialize when plugin is loaded
  initialize() {
    // Setup code here
    console.log('My plugin initialized');
  },

  // Define commands this plugin handles
  commands: [
    {
      trigger: 'command keyword',
      description: 'What this command does',
      handler: async (message) => {
        // Your command logic here
        return {
          type: 'response-type',
          data: 'your data',
          message: 'Human-readable response',
        };
      },
    },
  ],
};

module.exports = myPlugin;
```

### 2. Register Your Plugin

In `server/index.js`, add:

```javascript
const pluginManager = require('./integrations/plugin-manager');
const myPlugin = require('./integrations/your-plugin-name');

// Register the plugin
pluginManager.registerPlugin(myPlugin);
```

### 3. Using Commands in Conversation

Once registered, Jarvis will automatically detect and execute your commands when users mention the trigger keyword in conversation.

## Example Plugins

### Weather Plugin

```javascript
const weatherPlugin = {
  name: 'weather',
  description: 'Get weather information',

  commands: [
    {
      trigger: 'weather',
      handler: async (message) => {
        // Extract location from message
        const location = extractLocation(message) || 'current location';

        // Call weather API
        const weather = await fetchWeather(location);

        return {
          type: 'weather',
          location: location,
          temp: weather.temp,
          conditions: weather.conditions,
          message: `The weather in ${location} is ${weather.temp}°F and ${weather.conditions}`,
        };
      },
    },
  ],
};
```

### Smart Home Plugin

```javascript
const smartHomePlugin = {
  name: 'smart-home',
  description: 'Control smart home devices',

  initialize() {
    // Connect to smart home hub
    this.hub = new SmartHomeHub();
  },

  commands: [
    {
      trigger: 'lights',
      handler: async (message) => {
        if (message.includes('on')) {
          await this.hub.turnLightsOn();
          return { message: 'Lights turned on' };
        } else if (message.includes('off')) {
          await this.hub.turnLightsOff();
          return { message: 'Lights turned off' };
        }
      },
    },
  ],
};
```

### File System Plugin

```javascript
const fs = require('fs').promises;

const filePlugin = {
  name: 'file-system',
  description: 'File operations',

  commands: [
    {
      trigger: 'list files',
      handler: async (message) => {
        const path = extractPath(message) || './';
        const files = await fs.readdir(path);

        return {
          type: 'file-list',
          path: path,
          files: files,
          message: `Found ${files.length} files in ${path}`,
        };
      },
    },
  ],
};
```

## Advanced Features

### Accessing Plugin Manager

```javascript
const pluginManager = require('./integrations/plugin-manager');

// List all plugins
const plugins = pluginManager.listPlugins();

// Unregister a plugin
pluginManager.unregisterPlugin('plugin-name');
```

### Error Handling

Always wrap your handler logic in try-catch:

```javascript
handler: async (message) => {
  try {
    // Your logic
    return { success: true, data: result };
  } catch (error) {
    console.error('Plugin error:', error);
    return {
      success: false,
      error: error.message,
      message: 'Something went wrong',
    };
  }
}
```

### Integration with Claude AI

Plugins work alongside Claude AI. When a command is detected, the plugin handles it first. Otherwise, the message goes to Claude for natural language processing.

## Best Practices

1. **Keep triggers specific**: Use unique trigger words to avoid conflicts
2. **Return structured data**: Always return an object with `type` and `message`
3. **Handle errors gracefully**: Don't let plugin errors crash Jarvis
4. **Document your plugins**: Add clear descriptions and usage examples
5. **Test thoroughly**: Test with various message formats
6. **Security**: Validate inputs and don't expose sensitive operations
7. **Async operations**: Use async/await for API calls and I/O

## Next Steps

1. Study the example plugin in `server/integrations/example-plugin.js`
2. Create your first plugin
3. Register it in `server/index.js`
4. Test it by mentioning the trigger in conversation
5. Share your plugins with the community!

## Plugin Ideas

- 📧 Email integration
- 📅 Calendar management
- 🎵 Music control (Spotify, Apple Music)
- 💾 Database queries
- 🌐 Web scraping
- 🔔 Notifications and alerts
- 📊 Data visualization
- 🤖 IoT device control
- 📝 Note-taking and wiki
- 🎮 Game servers management

Happy coding! 🚀
