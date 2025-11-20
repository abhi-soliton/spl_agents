# 🎮 Game Agent Framework - Quick Reference Card

## 📁 Complete File Structure

```
wordle/
│
├── 📦 CORE FRAMEWORK
│   └── game_agent_framework.py         (520 lines)
│       ├── BaseGameAgent               (abstract base class)
│       ├── AgentRunner                 (lifecycle manager)
│       ├── Enums                       (6 types)
│       │   ├── GameType
│       │   ├── MessageType
│       │   ├── GameCommand
│       │   ├── GameResult
│       │   ├── AgentState
│       │   └── FeedbackType
│       └── Data Classes                (3 types)
│           ├── GameConfig
│           ├── ParsedMessage
│           └── GameStats
│
├── 🎯 AGENT IMPLEMENTATIONS
│   ├── wordle_agent_example.py         (240 lines)
│   │   └── WordleAgent
│   │       ├── OpenAI integration
│   │       ├── Structured outputs
│   │       └── Multiple strategies
│   │
│   └── cluedle_agent_example.py        (200 lines)
│       ├── CluedleAgent
│       └── CrosswordStyleCluedleAgent
│
├── 🚀 QUICK START
│   └── run_agent.py                    (Ready to run)
│       ├── Wordle agent example
│       ├── Cluedle agent example
│       └── Simple agent template
│
├── 🧪 TESTING
│   └── agent_testing.py                (300 lines)
│       ├── AgentTester
│       ├── MockMessage
│       └── 7 comprehensive tests
│
└── 📚 DOCUMENTATION
    ├── AGENT_FRAMEWORK_README.md       (Full API reference)
    ├── FRAMEWORK_GUIDE.md              (Usage guide)
    ├── VISUAL_REFERENCE.md             (Diagrams)
    └── PACKAGE_SUMMARY.md              (This file)
```

## ⚡ Quick Start Commands

```bash
# Run Wordle agent immediately
python run_agent.py

# Test without connecting to server
python agent_testing.py

# Run custom agent
python -c "from wordle_agent_example import WordleAgent; from game_agent_framework import GameConfig, AgentRunner; agent = WordleAgent(GameConfig(ws_url='ws://localhost:2025')); AgentRunner.run_agent(agent)"
```

## 📖 Code Snippets

### Minimal Agent (10 lines)

```python
from game_agent_framework import BaseGameAgent, GameConfig, GameType, ParsedMessage, AgentRunner

class MinimalAgent(BaseGameAgent):
    def __init__(self, config): super().__init__(config, GameType.WORDLE)
    
    async def make_move(self, parsed): return "hello"[:parsed.word_length or 5]
    
    def build_response(self, parsed, move):
        return {"matchId": parsed.match_id, "gameId": parsed.game_id, "otp": parsed.otp, "guess": move} if move else None

AgentRunner.run_agent(MinimalAgent(GameConfig(ws_url="ws://localhost:2025")))
```

### Complete Agent Template

```python
from game_agent_framework import BaseGameAgent, GameConfig, GameType, ParsedMessage, AgentRunner
from typing import Optional, Dict, Any

class MyAgent(BaseGameAgent):
    def __init__(self, config: GameConfig):
        super().__init__(config, GameType.CUSTOM)
        # Your initialization here
    
    async def make_move(self, parsed: ParsedMessage) -> Optional[str]:
        """Generate next move based on game state"""
        # Your logic here
        return "your_move"
    
    def build_response(self, parsed: ParsedMessage, move: Optional[str]) -> Optional[Dict[str, Any]]:
        """Build JSON response for server"""
        if not move:
            return None
        return {
            "matchId": parsed.match_id,
            "gameId": parsed.game_id,
            "otp": parsed.otp,
            "guess": move,
        }
    
    # Optional: Override lifecycle hooks
    def on_game_start(self, parsed: ParsedMessage):
        """Called when game starts"""
        self.log(f"Game starting with {parsed.word_length} letters")
    
    def on_game_result(self, parsed: ParsedMessage):
        """Called when game ends"""
        self.log(f"Game ended: {parsed.result.value if parsed.result else 'unknown'}")

# Run it
config = GameConfig(ws_url="ws://localhost:2025")
agent = MyAgent(config)
AgentRunner.run_agent(agent)
```

## 🎯 Common Patterns

### Pattern 1: AI with Fallback

```python
async def make_move(self, parsed: ParsedMessage) -> Optional[str]:
    # Try AI first
    ai_guess = await self._try_ai(parsed)
    if ai_guess:
        return ai_guess
    
    # Fallback to heuristic
    return self._fallback_strategy(parsed)
```

### Pattern 2: State Tracking

```python
def __init__(self, config: GameConfig):
    super().__init__(config, GameType.WORDLE)
    self.guess_history = []
    self.feedback_history = []

async def make_move(self, parsed: ParsedMessage) -> Optional[str]:
    # Use history for context
    guess = self._generate_smart_guess(self.guess_history, self.feedback_history)
    self.guess_history.append(guess)
    self.feedback_history.append(parsed.last_result)
    return guess
```

### Pattern 3: Multi-Strategy

```python
async def make_move(self, parsed: ParsedMessage) -> Optional[str]:
    strategies = [
        self._ai_strategy,
        self._wordlist_strategy,
        self._heuristic_strategy,
        self._alphabet_fallback,
    ]
    
    for strategy in strategies:
        move = await strategy(parsed)
        if move:
            return move
    
    return None
```

## 📊 API Quick Reference

### GameConfig

```python
config = GameConfig(
    ws_url="ws://localhost:2025",        # Required
    connect_timeout=10,                   # seconds
    recv_timeout=2,                       # seconds
    keep_alive=True,                      # bool
    max_reconnect_attempts=3,             # int
    reconnect_delay=5,                    # seconds
)
```

### ParsedMessage Fields

```python
parsed.type              # MessageType enum
parsed.command           # GameCommand enum
parsed.match_id          # str
parsed.game_id           # str
parsed.otp               # str
parsed.word_length       # int
parsed.max_attempts      # int
parsed.last_guess        # str
parsed.last_result       # List[str]
parsed.current_attempt   # int
parsed.result            # GameResult enum
parsed.word              # str
parsed.metadata          # dict (full message)
```

### GameStats Properties

```python
agent.stats.games_played
agent.stats.games_won
agent.stats.games_lost
agent.stats.total_guesses
agent.stats.current_game_guesses
agent.stats.start_time
agent.stats.end_time
```

### Logging

```python
self.log("Message", "🎯")        # Custom log
self.ts()                        # Get timestamp string
```

## 🎨 Enum Values

```python
# GameType
GameType.WORDLE
GameType.CLUEDLE
GameType.CUSTOM

# MessageType
MessageType.GAME_START
MessageType.GAME_RESULT
MessageType.COMMAND
MessageType.ACKNOWLEDGEMENT
MessageType.ERROR
MessageType.UNKNOWN

# GameCommand
GameCommand.GUESS
GameCommand.SOLVE
GameCommand.HINT
GameCommand.UNKNOWN

# GameResult
GameResult.WIN
GameResult.LOSS
GameResult.TIMEOUT
GameResult.ERROR
GameResult.ABANDONED
GameResult.UNKNOWN

# AgentState
AgentState.IDLE
AgentState.CONNECTING
AgentState.CONNECTED
AgentState.PLAYING
AgentState.GAME_OVER
AgentState.DISCONNECTED
AgentState.ERROR

# FeedbackType
FeedbackType.CORRECT    # green/right position
FeedbackType.PRESENT    # yellow/wrong position
FeedbackType.ABSENT     # gray/not in word
```

## 🔧 Lifecycle Hooks

```python
def on_game_start(self, parsed: ParsedMessage):
    """Game initialization - reset state"""
    pass

def on_game_result(self, parsed: ParsedMessage):
    """Game completion - analyze results"""
    pass

def on_acknowledgement(self, parsed: ParsedMessage):
    """Server acknowledged your move"""
    pass

def on_error(self, parsed: ParsedMessage):
    """Server sent error message"""
    pass

def on_connected(self):
    """WebSocket connection established"""
    pass

def on_disconnected(self):
    """WebSocket connection closed"""
    pass
```

## 🧪 Testing

```python
from agent_testing import AgentTester

# Create agent
agent = MyAgent(config)

# Run all tests
tester = AgentTester(agent)
results = await tester.run_all_tests()

# Run specific test
await tester.test_make_guess()
await tester.test_feedback_parsing()
```

## 📈 Calculating Metrics

```python
# Win rate
win_rate = (agent.stats.games_won / agent.stats.games_played) * 100

# Average guesses
avg_guesses = agent.stats.total_guesses / agent.stats.games_played

# Game duration
duration = (agent.stats.end_time - agent.stats.start_time).total_seconds()
```

## 🚨 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| AI not working | Check `OPENAI_API_KEY` in `.env` |
| Connection fails | Verify `ws_url` and server status |
| No moves generated | Check `make_move()` returns non-None |
| Invalid responses | Validate required fields in `build_response()` |
| Stats not updating | Ensure lifecycle hooks are called |
| Reconnection issues | Adjust `max_reconnect_attempts` and `reconnect_delay` |

## 📚 Documentation Map

```
Start Here → FRAMEWORK_GUIDE.md
             │
             ├─► Quick Start
             ├─► Creating Agents
             └─► Configuration
             
Reference → AGENT_FRAMEWORK_README.md
            │
            ├─► Full API
            ├─► Examples
            └─► Best Practices

Visual Aid → VISUAL_REFERENCE.md
             │
             ├─► Message Flow
             ├─► State Machine
             └─► Class Hierarchy

Code → wordle_agent_example.py
       │
       ├─► Complete implementation
       ├─► OpenAI integration
       └─► Multiple strategies
```

## 🎯 Implementation Checklist

### Basic Agent (5 minutes)
- [ ] Import `BaseGameAgent`, `GameConfig`, `GameType`
- [ ] Create class inheriting from `BaseGameAgent`
- [ ] Implement `make_move()`
- [ ] Implement `build_response()`
- [ ] Run with `AgentRunner.run_agent()`

### Production Agent (30 minutes)
- [ ] Add error handling
- [ ] Add fallback strategies
- [ ] Implement lifecycle hooks
- [ ] Add logging
- [ ] Track game state
- [ ] Write tests

### Advanced Agent (2+ hours)
- [ ] Integrate AI/ML
- [ ] Multiple strategies
- [ ] Context-aware decisions
- [ ] Performance optimization
- [ ] Comprehensive testing
- [ ] Documentation

## 🏆 Feature Comparison

| Feature | Minimal Agent | Example Agent | Your Custom Agent |
|---------|--------------|---------------|-------------------|
| Lines of code | ~10 | ~240 | Your choice |
| AI integration | ❌ | ✅ | 🔧 Optional |
| Multiple strategies | ❌ | ✅ | 🔧 Optional |
| State tracking | ❌ | ✅ | 🔧 Optional |
| Lifecycle hooks | ❌ | ✅ | 🔧 Optional |
| Testing | ❌ | ✅ | 🔧 Recommended |
| Documentation | ❌ | ✅ | 🔧 Recommended |

## 💡 Pro Tips

1. **Start with the example agents** - They're production-ready
2. **Test without server first** - Use `agent_testing.py`
3. **Use structured AI outputs** - More reliable than parsing text
4. **Implement fallbacks** - Don't rely solely on AI
5. **Track history** - Context improves decision-making
6. **Log everything** - Makes debugging easier
7. **Monitor statistics** - Optimize based on metrics
8. **Handle errors gracefully** - Network issues happen

## 📞 Need Help?

1. **Read the docs**: Start with `FRAMEWORK_GUIDE.md`
2. **Check examples**: `wordle_agent_example.py` and `cluedle_agent_example.py`
3. **View diagrams**: `VISUAL_REFERENCE.md`
4. **Run tests**: `agent_testing.py`

---

**Framework Version**: 1.0  
**Total Code**: 1000+ lines  
**Documentation**: 4 comprehensive files  
**Examples**: 2 complete implementations  
**Tests**: 7 test cases  

**Status**: ✅ Production Ready

---

**Quick Links**:
- 📖 [Full Documentation](AGENT_FRAMEWORK_README.md)
- 📚 [Usage Guide](FRAMEWORK_GUIDE.md)
- 📊 [Visual Reference](VISUAL_REFERENCE.md)
- 📦 [Package Summary](PACKAGE_SUMMARY.md)
