# Game Agent Framework - File Structure & Usage Guide

## 📁 File Structure

```
wordle/
├── game_agent_framework.py       # Core framework with base classes and enums
├── wordle_agent_example.py       # Wordle agent implementation
├── cluedle_agent_example.py      # Cluedle agent implementation
├── run_agent.py                  # Quick start script
├── agent_testing.py              # Testing utilities
└── AGENT_FRAMEWORK_README.md     # Complete documentation
```

## 🎯 Core Files

### 1. `game_agent_framework.py` (Core Framework)

**What it contains:**
- `BaseGameAgent` - Abstract base class for all agents
- `AgentRunner` - Manages agent lifecycle
- Enums: `GameType`, `MessageType`, `GameCommand`, `GameResult`, `AgentState`, `FeedbackType`
- Data Classes: `GameConfig`, `ParsedMessage`, `GameStats`

**Key Features:**
- ✅ WebSocket connection management
- ✅ Message parsing and routing
- ✅ Game lifecycle handling
- ✅ Statistics tracking
- ✅ Reconnection logic
- ✅ Extensible architecture

### 2. `wordle_agent_example.py` (Wordle Implementation)

**What it contains:**
- `WordleAgent` - Complete Wordle agent with AI
- OpenAI integration (simple & structured outputs)
- Feedback history tracking
- Multiple fallback strategies

**How to use:**
```python
from wordle_agent_example import WordleAgent
from game_agent_framework import GameConfig, AgentRunner

config = GameConfig(ws_url="ws://localhost:2025")
agent = WordleAgent(config, use_ai=True)
AgentRunner.run_agent(agent)
```

### 3. `cluedle_agent_example.py` (Cluedle Implementation)

**What it contains:**
- `CluedleAgent` - Clue-based word guessing agent
- `CrosswordStyleCluedleAgent` - Specialized variant
- Clue extraction and context building
- AI-powered puzzle solving

**How to use:**
```python
from cluedle_agent_example import CluedleAgent
from game_agent_framework import GameConfig, AgentRunner

config = GameConfig(ws_url="ws://localhost:2025")
agent = CluedleAgent(config, use_ai=True)
AgentRunner.run_agent(agent)
```

### 4. `run_agent.py` (Quick Start)

**What it contains:**
- Ready-to-run examples for each agent type
- Configuration templates
- Simple agent example

**How to use:**
```bash
python run_agent.py
```

### 5. `agent_testing.py` (Testing Framework)

**What it contains:**
- `AgentTester` - Comprehensive testing harness
- Mock message generation
- Unit tests for all agent capabilities
- Test result reporting

**How to use:**
```bash
python agent_testing.py
```

## 🚀 Quick Start Guide

### Option 1: Use Existing Agent

```python
# 1. Import required modules
from wordle_agent_example import WordleAgent
from game_agent_framework import GameConfig, AgentRunner

# 2. Configure connection
config = GameConfig(
    ws_url="ws://localhost:2025",
    connect_timeout=10,
    recv_timeout=2,
)

# 3. Create agent
agent = WordleAgent(config, use_ai=True)

# 4. Run agent
AgentRunner.run_agent(agent)
```

### Option 2: Create Custom Agent

```python
# 1. Import base class
from game_agent_framework import (
    BaseGameAgent, GameConfig, GameType, 
    ParsedMessage, AgentRunner
)
from typing import Optional, Dict, Any

# 2. Create your agent class
class MyAgent(BaseGameAgent):
    def __init__(self, config: GameConfig):
        super().__init__(config, GameType.CUSTOM)
    
    async def make_move(self, parsed: ParsedMessage) -> Optional[str]:
        # Your game logic here
        return "your_move"
    
    def build_response(self, parsed: ParsedMessage, move: Optional[str]) -> Optional[Dict[str, Any]]:
        # Build JSON response
        return {
            "matchId": parsed.match_id,
            "gameId": parsed.game_id,
            "otp": parsed.otp,
            "guess": move,
        }

# 3. Configure and run
config = GameConfig(ws_url="ws://localhost:2025")
agent = MyAgent(config)
AgentRunner.run_agent(agent)
```

## 📊 Framework Architecture

```
┌─────────────────────────────────────────┐
│         AgentRunner                     │
│  (Manages lifecycle & execution)        │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│       BaseGameAgent                     │
│  ┌─────────────────────────────────┐   │
│  │ Connection Management           │   │
│  │ Message Parsing & Routing       │   │
│  │ Game Lifecycle Handling         │   │
│  │ Statistics Tracking             │   │
│  │ Error Handling & Reconnection   │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Abstract Methods (implement these):   │
│  ├── make_move()                       │
│  └── build_response()                  │
│                                         │
│  Optional Hooks (override if needed):  │
│  ├── on_game_start()                   │
│  ├── on_game_result()                  │
│  ├── on_acknowledgement()              │
│  ├── on_error()                        │
│  ├── on_connected()                    │
│  └── on_disconnected()                 │
└────────────┬───────────────────────────┘
             │
             ├── WordleAgent (Example)
             ├── CluedleAgent (Example)
             └── YourCustomAgent (Your implementation)
```

## 🎨 Customization Points

### 1. Game Logic (Required)

Implement these methods in your agent:

```python
async def make_move(self, parsed: ParsedMessage) -> Optional[str]:
    """Generate your next move based on game state"""
    pass

def build_response(self, parsed: ParsedMessage, move: Optional[str]) -> Optional[Dict[str, Any]]:
    """Build the JSON response to send to server"""
    pass
```

### 2. Lifecycle Hooks (Optional)

Override these for custom behavior:

```python
def on_game_start(self, parsed: ParsedMessage):
    """Called when game starts"""
    pass

def on_game_result(self, parsed: ParsedMessage):
    """Called when game ends"""
    pass
```

### 3. Message Parsing (Optional)

Extend parsing for custom message formats:

```python
def parse_message(self, msg: str) -> Optional[ParsedMessage]:
    """Custom message parsing logic"""
    parsed = super().parse_message(msg)
    # Add custom fields
    return parsed
```

## 📋 Enums Reference

### GameType
- `WORDLE` - Word guessing with position feedback
- `CLUEDLE` - Clue-based word guessing
- `CUSTOM` - Your custom game type

### MessageType
- `GAME_START` - Game initialization
- `GAME_RESULT` - Game completion
- `COMMAND` - Server command (requires response)
- `ACKNOWLEDGEMENT` - Server acknowledgement
- `ERROR` - Error message
- `UNKNOWN` - Unrecognized message

### GameCommand
- `GUESS` - Make a guess
- `SOLVE` - Solve the puzzle
- `HINT` - Request a hint
- `UNKNOWN` - Unrecognized command

### GameResult
- `WIN` - Player won
- `LOSS` - Player lost
- `TIMEOUT` - Game timed out
- `ERROR` - Error occurred
- `ABANDONED` - Game abandoned
- `UNKNOWN` - Unrecognized result

### AgentState
- `IDLE` - Not connected
- `CONNECTING` - Establishing connection
- `CONNECTED` - Connection established
- `PLAYING` - Game in progress
- `GAME_OVER` - Game completed
- `DISCONNECTED` - Connection closed
- `ERROR` - Error state

### FeedbackType (Wordle)
- `CORRECT` - Letter in correct position (green)
- `PRESENT` - Letter in word, wrong position (yellow)
- `ABSENT` - Letter not in word (gray)

## 🔧 Configuration Options

### GameConfig

```python
config = GameConfig(
    ws_url="ws://localhost:2025",        # Required: Server URL
    connect_timeout=10,                   # Connection timeout (seconds)
    recv_timeout=2,                       # Message receive timeout
    keep_alive=True,                      # Keep connection alive
    max_reconnect_attempts=3,             # Reconnection attempts
    reconnect_delay=5,                    # Delay between retries
)
```

### Agent-Specific Configuration

Each agent can have additional configuration:

```python
# Wordle Agent
agent = WordleAgent(
    config=config,
    ai_model="gpt-5-nano",              # OpenAI model
    use_structured_output=True,           # Structured JSON
    use_ai=True,                          # Enable AI
)

# Cluedle Agent
agent = CluedleAgent(
    config=config,
    ai_model="gpt-5-nano",
    use_ai=True,
)
```

## 📈 Statistics & Monitoring

Access statistics through `agent.stats`:

```python
agent.stats.games_played        # Total games played
agent.stats.games_won          # Total wins
agent.stats.games_lost         # Total losses
agent.stats.total_guesses      # Total guesses made
agent.stats.current_game_guesses  # Guesses in current game
agent.stats.start_time         # Game start timestamp
agent.stats.end_time           # Game end timestamp
```

Calculate metrics:

```python
win_rate = agent.stats.games_won / agent.stats.games_played * 100
avg_guesses = agent.stats.total_guesses / agent.stats.games_played
```

## 🧪 Testing Your Agent

Use the testing framework:

```python
from agent_testing import AgentTester

tester = AgentTester(your_agent)
results = await tester.run_all_tests()
```

Tests include:
- ✅ Game start handling
- ✅ Guess generation
- ✅ Response building
- ✅ Win/loss handling
- ✅ Feedback parsing
- ✅ Multi-guess sequences

## 🎯 Best Practices

1. **Always handle None returns** in `make_move()`
2. **Validate required fields** in `build_response()`
3. **Use lifecycle hooks** for state management
4. **Log important events** using `self.log()`
5. **Test your agent** before connecting to live server
6. **Handle AI failures** with fallback strategies
7. **Track game state** for context-aware decisions
8. **Monitor statistics** to improve performance

## 🚨 Common Issues & Solutions

### Issue: AI not working
**Solution:** Check `OPENAI_API_KEY` in `.env` file

### Issue: Connection fails
**Solution:** Verify `ws_url` and server status

### Issue: No moves generated
**Solution:** Check `make_move()` implementation and fallback logic

### Issue: Invalid responses
**Solution:** Validate all required fields in `build_response()`

### Issue: Stats not updating
**Solution:** Ensure lifecycle methods are called properly

## 📚 Additional Resources

- **Framework Documentation**: `AGENT_FRAMEWORK_README.md`
- **Example Implementations**: `wordle_agent_example.py`, `cluedle_agent_example.py`
- **Testing Guide**: `agent_testing.py`
- **Quick Start**: `run_agent.py`

---

**Ready to build your agent? Start with `run_agent.py` or create a new agent class!** 🚀
