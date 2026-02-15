/**
 * Example Plugin - Time and Weather Commands
 *
 * This demonstrates how to create a plugin for Jarvis.
 * You can copy this template to create your own plugins.
 */

const examplePlugin = {
  name: 'example',
  description: 'Example plugin with time and system info commands',

  // Called when plugin is registered
  initialize() {
    console.log('Example plugin initialized');
  },

  // Define commands this plugin handles
  commands: [
    {
      trigger: 'time',
      description: 'Get current time',
      handler: async (message) => {
        const now = new Date();
        return {
          type: 'time',
          time: now.toLocaleTimeString(),
          date: now.toLocaleDateString(),
          message: `The current time is ${now.toLocaleTimeString()}`,
        };
      },
    },
    {
      trigger: 'system info',
      description: 'Get system information',
      handler: async (message) => {
        const os = require('os');
        return {
          type: 'system',
          platform: os.platform(),
          arch: os.arch(),
          cpus: os.cpus().length,
          totalMem: (os.totalmem() / 1024 / 1024 / 1024).toFixed(2) + ' GB',
          freeMem: (os.freemem() / 1024 / 1024 / 1024).toFixed(2) + ' GB',
          uptime: (os.uptime() / 3600).toFixed(2) + ' hours',
        };
      },
    },
  ],
};

module.exports = examplePlugin;
