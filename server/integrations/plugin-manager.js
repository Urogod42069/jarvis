/**
 * Plugin Manager - Extensible system for adding capabilities to Jarvis
 *
 * Plugins can add:
 * - Custom commands
 * - System integrations
 * - External API connections
 * - Automation workflows
 */

class PluginManager {
  constructor() {
    this.plugins = new Map();
    this.commandHandlers = new Map();
  }

  /**
   * Register a new plugin
   * @param {Object} plugin - Plugin configuration
   * @param {string} plugin.name - Plugin name
   * @param {string} plugin.description - Plugin description
   * @param {Function} plugin.initialize - Initialization function
   * @param {Array} plugin.commands - Array of command definitions
   */
  registerPlugin(plugin) {
    if (this.plugins.has(plugin.name)) {
      throw new Error(`Plugin ${plugin.name} is already registered`);
    }

    // Initialize the plugin
    if (plugin.initialize) {
      plugin.initialize();
    }

    // Register commands
    if (plugin.commands) {
      plugin.commands.forEach(cmd => {
        this.commandHandlers.set(cmd.trigger, cmd.handler);
      });
    }

    this.plugins.set(plugin.name, plugin);
    console.log(`✓ Plugin registered: ${plugin.name}`);
  }

  /**
   * Check if a message contains a command and execute it
   * @param {string} message - User message
   * @returns {Object|null} Command result or null if no command found
   */
  async handleCommand(message) {
    // Check for command patterns (e.g., /weather, @system)
    for (const [trigger, handler] of this.commandHandlers) {
      if (message.toLowerCase().includes(trigger.toLowerCase())) {
        try {
          const result = await handler(message);
          return {
            success: true,
            result,
            handledBy: trigger,
          };
        } catch (error) {
          return {
            success: false,
            error: error.message,
            handledBy: trigger,
          };
        }
      }
    }

    return null;
  }

  /**
   * Get list of all registered plugins
   */
  listPlugins() {
    return Array.from(this.plugins.values()).map(p => ({
      name: p.name,
      description: p.description,
      commands: p.commands?.map(c => c.trigger) || [],
    }));
  }

  /**
   * Unregister a plugin
   */
  unregisterPlugin(name) {
    const plugin = this.plugins.get(name);
    if (!plugin) return false;

    // Remove command handlers
    if (plugin.commands) {
      plugin.commands.forEach(cmd => {
        this.commandHandlers.delete(cmd.trigger);
      });
    }

    this.plugins.delete(name);
    console.log(`✓ Plugin unregistered: ${name}`);
    return true;
  }
}

module.exports = new PluginManager();
