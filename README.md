# Jarvis

Personal AI assistant powered by Claude. CLI-first, extensible via a plugin tool system.

## Setup

```bash
cd /Users/vy/jarvis
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Configure
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Usage

```bash
jarvis
# or
python -m jarvis
```

### Commands

| Command    | Description              |
|------------|--------------------------|
| `/quit`    | Exit the session         |
| `/history` | List past conversations  |

## Adding Tools

Create a new file in `jarvis/tools/` that subclasses `Tool`:

```python
from jarvis.tools.base import Tool

class MyTool(Tool):
    @property
    def name(self) -> str:
        return "my_tool"

    @property
    def description(self) -> str:
        return "What it does."

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "arg": {"type": "string", "description": "..."},
            },
            "required": ["arg"],
        }

    @property
    def requires_confirmation(self) -> bool:
        return True  # prompt user before executing

    def execute(self, *, arg: str) -> str:
        return "result"
```

Tools are auto-discovered — just drop the file in and restart.

## Architecture

```
jarvis/
├── __main__.py       # CLI entry point
├── agent.py          # Core loop: API calls, tool routing
├── config.py         # Env-based configuration
├── database.py       # SQLite conversation history
├── models.py         # Data models (Message, ToolCall, ToolResult)
└── tools/
    ├── __init__.py   # Auto-discovery registry
    ├── base.py       # Abstract Tool base class
    └── read_file.py  # Example: read local files
```
