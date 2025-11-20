# 🚀 Framework V2 - What Changed and Why

## 📊 Quick Comparison

| Feature | V1 (Original) | V2 (New - Simplified) |
|---------|---------------|----------------------|
| **Lines to implement** | ~50-100 | ~20-30 |
| **Methods required** | 2 (make_move, build_response) | 4 (on_game_started, on_clue_received, make_move, on_game_ended) |
| **ACK handling** | Manual parsing | Automatic |
| **Metadata/Clues** | Manual extraction | Automatic (delivered in callback) |
| **Learning curve** | Medium | Easy |
| **Best for** | Python developers | Everyone (including non-Python devs) |
| **Game types** | Wordle-focused | Any game type |
| **2D Grid games** | Needs customization | Built-in support |

## 🎯 Key Improvements in V2

### 1. **Automatic Acknowledgment Handling**

**V1 (Manual):**
```python
def parse_message(self, text):
    obj = json.loads(text)
    # You have to check ackFor yourself
    if obj.get("ackFor") == "game started":
        # Handle game start
    elif obj.get("ackFor") == "meta data":
        # Extract clue from ackData
```

**V2 (Automatic):**
```python
def on_game_started(self, message):
    # Automatically called when game starts!
    self.log("Game started!")

def on_clue_received(self, clue, message):
    # Clue is already extracted and passed to you!
    self.log(f"Got clue: {clue}")
```

### 2. **Simplified Message Structure**

**V1 (Complex):**
```python
@dataclass
class ParsedMessage:
    raw: str
    type: Optional[str]
    command: Optional[str]
    match_id: Optional[str]
    game_id: Optional[str]
    your_id: Optional[str]
    otp: Optional[str]
    word_length: Optional[int]
    max_attempts: Optional[int]
    last_guess: str
    last_result: List[str]
    current_attempt: Optional[int]
    ack_for: Optional[str]
    ack_data: Optional[str]
    result: Optional[str]
    word: Optional[str]
```

**V2 (Simple):**
```python
@dataclass
class GameMessage:
    raw: str
    match_id: Optional[str]
    game_id: Optional[str]
    your_id: Optional[str]
    message_type: MessageType
    ack_for: Optional[str]
    ack_data: Any                     # Flexible!
    command: Optional[str]
    result: Optional[str]
    answer: Optional[str]
    game_data: Dict[str, Any]         # Everything else here
```

### 3. **Clearer Lifecycle**

**V1:**
- Game start hidden in message handling
- Clues not explicitly handled
- No clear callback for clues

**V2:**
- `on_game_started()` - Clear game start
- `on_clue_received()` - Dedicated clue handler
- `on_game_ended()` - Clear game end

## 🔄 Migration Guide

### Example: Simple Wordle Agent

**V1 Code:**
```python
from game_agent_framework import BaseGameAgent, GameConfig, ParsedMessage

class MyWordleAgent(BaseGameAgent):
    async def make_move(self, parsed: ParsedMessage) -> Optional[str]:
        if parsed.command != "guess":
            return None
        return "hello"
    
    def build_response(self, parsed: ParsedMessage, move: Optional[str]):
        return {
            "matchId": parsed.match_id,
            "gameId": parsed.game_id,
            "otp": parsed.otp,
            "guess": move,
        }
```

**V2 Code:**
```python
from game_agent_framework_v2 import SimpleGameAgent, GameConfig, GameMessage

class MyWordleAgent(SimpleGameAgent):
    def on_game_started(self, message):
        self.log("Game started!")
    
    def on_clue_received(self, clue, message):
        pass  # Wordle doesn't use clues
    
    async def make_move(self, message):
        return "hello"
    
    def on_game_ended(self, message):
        self.log("Game ended!")
```

### Example: Cluedle Agent with ACKs

**V1 Code (Complex):**
```python
class MyCluedleAgent(BaseGameAgent):
    def parse_message(self, msg):
        parsed = super().parse_message(msg)
        # Manual ACK handling
        if parsed.type == "ack":
            if parsed.ack_for == "game started":
                self.game_started = True
            elif parsed.ack_for == "meta data":
                self.clue = parsed.ack_data
        return parsed
    
    async def make_move(self, parsed):
        if not self.clue:
            return None
        # Use self.clue
        return self.solve_clue(self.clue)
```

**V2 Code (Simple):**
```python
class MyCluedleAgent(SimpleGameAgent):
    def on_game_started(self, message):
        self.log("Ready to play!")
    
    def on_clue_received(self, clue, message):
        self.log(f"Got clue: {clue}")
        # Clue is automatically saved in self.clues
    
    async def make_move(self, message):
        # All clues available in self.clues
        return self.solve_clue(self.clues)
    
    def on_game_ended(self, message):
        self.log("Done!")
```

## 🎮 New Game Type Support

### 2D Grid Games (New in V2!)

```python
class My2DGameAgent(SimpleGameAgent):
    def __init__(self, config):
        super().__init__(config, GameType.GRID_2D)
    
    def on_game_started(self, message):
        # Check grid size
        if "gridSize" in message.game_data:
            self.size = message.game_data["gridSize"]
    
    def on_clue_received(self, clue, message):
        self.log(f"Hint: {clue}")
    
    async def make_move(self, message):
        return "B2"  # Return coordinates
    
    def on_game_ended(self, message):
        self.log("Game over!")
    
    def build_response(self, message, move):
        # Custom format for grid games
        return {
            "matchId": self.match_id,
            "gameId": self.game_id,
            "otp": message.game_data.get("otp"),
            "position": move,  # or "move", "coordinates", etc.
        }
```

## 📝 Feature Comparison Table

| Feature | V1 | V2 | Winner |
|---------|----|----|--------|
| ACK handling | Manual | Automatic | ✅ V2 |
| Metadata extraction | Manual | Automatic | ✅ V2 |
| Clue tracking | Manual | Automatic | ✅ V2 |
| Game state storage | Manual | Built-in | ✅ V2 |
| 2D Grid games | Hard | Easy | ✅ V2 |
| Custom games | Medium | Easy | ✅ V2 |
| Code brevity | ~50 lines | ~20 lines | ✅ V2 |
| Type safety | Full | Simplified | ⚖️ Tie |
| Learning curve | Medium | Low | ✅ V2 |
| Documentation | Detailed | Simple | ✅ V2 |
| For Python devs | ✅ Good | ✅ Good | ⚖️ Tie |
| For non-Python devs | ❌ Hard | ✅ Easy | ✅ V2 |

## 🤔 Which Should You Use?

### Use V1 If:
- ✅ You're an experienced Python developer
- ✅ You want full control over message parsing
- ✅ You need complex custom message handling
- ✅ You're already using V1 and it works

### Use V2 If:
- ✅ You want the simplest possible API
- ✅ You're new to Python
- ✅ You're building a Cluedle agent (handles ACKs automatically)
- ✅ You're building a 2D grid game
- ✅ You want faster development
- ✅ You want clearer code structure

### Recommendation:
**Use V2 for new projects!** It's simpler, clearer, and handles modern game patterns (ACKs, metadata) automatically.

## 🔀 Side-by-Side Example

### Complete Cluedle Agent

**V1 (BaseGameAgent):**
```python
from game_agent_framework import BaseGameAgent, ParsedMessage

class CluedleAgent(BaseGameAgent):
    def __init__(self, config):
        super().__init__(config, GameType.CLUEDLE)
        self.clue_list = []
    
    def parse_message(self, msg):
        parsed = super().parse_message(msg)
        if parsed.type == "ack" and parsed.ack_for == "meta data":
            if parsed.ack_data:
                self.clue_list.append(parsed.ack_data)
        return parsed
    
    async def make_move(self, parsed: ParsedMessage):
        if parsed.command != "guess":
            return None
        if not self.clue_list:
            return "anthropic"
        return self._analyze_clues()
    
    def build_response(self, parsed, move):
        if not move:
            return None
        return {
            "matchId": parsed.match_id,
            "gameId": parsed.game_id,
            "otp": parsed.otp,
            "guess": move,
        }
    
    def _analyze_clues(self):
        combined = " ".join(self.clue_list).lower()
        if "claude" in combined:
            return "anthropic"
        return "anthropic"
```

**V2 (SimpleGameAgent):**
```python
from game_agent_framework_v2 import SimpleGameAgent

class CluedleAgent(SimpleGameAgent):
    def on_game_started(self, message):
        self.log("Game started!")
    
    def on_clue_received(self, clue, message):
        self.log(f"Clue: {clue}")
    
    async def make_move(self, message):
        # self.clues already contains all clues!
        combined = " ".join(self.clues).lower()
        if "claude" in combined:
            return "anthropic"
        return "anthropic"
    
    def on_game_ended(self, message):
        self.log("Done!")
```

**Lines of code:** V1 = 28 lines, V2 = 12 lines  
**Winner:** ✅ V2 (57% less code!)

## 📚 Documentation Files

### V1 Documentation:
- `AGENT_FRAMEWORK_README.md` - Full V1 API
- `FRAMEWORK_GUIDE.md` - V1 usage guide
- `VISUAL_REFERENCE.md` - V1 diagrams

### V2 Documentation:
- `SIMPLE_GUIDE.md` - Easy guide for V2 ⭐ **START HERE**
- `simple_agent_examples.py` - Working examples
- This file - Migration guide

## 🎯 Quick Decision Tree

```
Are you building a new agent?
│
├─ Yes → Are you experienced with Python?
│   │
│   ├─ Yes → Do you need complex customization?
│   │   │
│   │   ├─ Yes → Use V1 (more control)
│   │   └─ No → Use V2 (faster development)
│   │
│   └─ No → Use V2 (easier to learn)
│
└─ No (modifying existing) → Keep using V1 (if it works)
```

## 🚀 Getting Started with V2

```python
# 1. Import
from game_agent_framework_v2 import SimpleGameAgent, GameConfig, AgentRunner

# 2. Create agent (only 4 methods!)
class MyAgent(SimpleGameAgent):
    def on_game_started(self, message):
        self.log("Starting!")
    
    def on_clue_received(self, clue, message):
        self.log(f"Clue: {clue}")
    
    async def make_move(self, message):
        return "my_guess"
    
    def on_game_ended(self, message):
        self.log("Done!")

# 3. Run it
config = GameConfig(ws_url="ws://localhost:2025")
AgentRunner.run_agent(MyAgent(config))
```

**That's it!** 🎉

## 📊 Summary

| Aspect | V1 | V2 |
|--------|----|----|
| **Best for** | Python developers | Everyone |
| **Complexity** | Medium | Low |
| **Code amount** | More | Less |
| **ACK support** | Manual | Automatic |
| **2D games** | Custom | Built-in |
| **Recommended for new projects** | ❌ | ✅ |

---

**Recommendation: Use V2 for new projects!** It's simpler, handles modern game patterns automatically, and is much easier for non-Python developers.

**Both frameworks work great - choose what fits your needs!** 🎮
