# Game Agent Framework

> ⚠️ **Beta Version** - This framework is currently in beta. APIs and features may change.

A modular, extensible Python framework for building AI-powered game agents that connect to game servers via WebSocket. Currently supports Wordle and other word/puzzle games.

## 📚 Documentation

- **[Agent Framework Guide](AGENT_FRAMEWORK_README.md)** - Complete framework documentation, architecture, and examples
- **[Visual Reference](VISUAL_REFERENCE.md)** - Diagrams showing message flow, state machines, and component interactions

## 🚀 Quick Start

### Requirements
- Python 3.12.6
- [uv](https://github.com/astral-sh/uv) package manager installed
- OpenAI API key with access to GPT-5/GPT-4 series models
  - Get your key: [Creating OpenAI API Key](https://spl.solitontech.ai/docs/setup-tools/creating-openai-api-key/)

### Setup

1. **Install Dependencies**
   ```bash
   uv sync
   ```
   This creates a virtual environment under `.venv` and installs all dependencies from `pyproject.toml`.

2. **Configure OpenAI API Key**
   
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_open_ai_api_key
   ```

3. **Run the Wordle Agent**
   ```bash
   uv run .\agents\wordle_agent_example.py
   ```

## 🎯 Features

- **Modular Architecture** - Base class handles connection, messaging, and lifecycle
- **Easy Extension** - Create new agents by implementing just 2 methods
- **AI Integration** - Built-in OpenAI support with structured outputs
- **Rich State Management** - Comprehensive enums for game states and commands
- **Statistics Tracking** - Automatic performance metrics and win rates
- **Auto-Reconnection** - Configurable retry logic for robust connections

## 📖 Learn More

- **Framework Details** - See [AGENT_FRAMEWORK_README.md](AGENT_FRAMEWORK_README.md) for:
  - Architecture overview
  - Creating custom agents
  - Configuration options
  - Advanced usage patterns
  - Code examples

- **Visual Guides** - See [VISUAL_REFERENCE.md](VISUAL_REFERENCE.md) for:
  - Message flow diagrams
  - Class hierarchy
  - State machine visualization
  - Data flow charts
  - Implementation checklist

- **OpenAI Resources** - [OpenAI Bytes](https://spl.solitontech.ai/docs/learning/openai-bytes) for platform capabilities and model guidance