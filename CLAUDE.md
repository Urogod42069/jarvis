# Jarvis — Project Context

## What This Is
Personal AI assistant CLI powered by Claude (Anthropic API). Python backend with plugin-based tool architecture.

## Current Phase: v0.1 — Foundation

### Architecture
- **CLI entry**: `jarvis/__main__.py` — Rich-based REPL
- **Agent core**: `jarvis/agent.py` — conversation loop, tool execution, action proposals
- **Config**: `jarvis/config.py` — env vars via python-dotenv
- **Database**: `jarvis/database.py` — SQLite conversation history (`~/.jarvis/conversations.db`)
- **Models**: `jarvis/models.py` — Message, ToolCall, ToolResult dataclasses
- **Tool system**: `jarvis/tools/` — auto-discovered plugins
  - `base.py` — abstract Tool base class (name, description, parameters, requires_confirmation, execute)
  - `read_file.py` — example tool: read local files (256KB limit, UTF-8 only)

### Key Design Decisions
- Tools use Anthropic's native tool_use / function calling API
- Tools auto-register via `pkgutil.iter_modules` discovery — drop a file in `tools/`, restart, done
- `requires_confirmation` property on tools triggers action-proposal flow (y/n in terminal)
- Conversation history persisted in SQLite so future sessions can resume context
- No hardcoded secrets — everything via `.env`

### Dependencies
- `anthropic` — Claude API client
- `python-dotenv` — env file loading
- `rich` — terminal UI (panels, markdown rendering, status spinners)

## Completed
- [x] Project structure and pyproject.toml
- [x] Configuration from environment variables
- [x] SQLite conversation persistence (conversations + messages tables)
- [x] Abstract Tool base class with standard interface
- [x] Auto-discovery tool registry
- [x] Example tool: read_file (with size limit and confirmation)
- [x] Agent core: API loop with tool execution
- [x] Action proposal system (y/n confirmation before tool execution)
- [x] CLI REPL with Rich formatting
- [x] README with setup instructions and tool authoring guide

## Next Steps
- [ ] Set up venv and verify `pip install -e .` works end to end
- [ ] Test a real conversation with the Anthropic API
- [ ] Add `/resume` command to continue a previous conversation
- [ ] Add a second tool (e.g., `run_shell_command` with confirmation)
- [ ] Add streaming support for long responses
- [ ] Consider web/API interface as alternative to CLI
