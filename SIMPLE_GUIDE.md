# 🎮 Simple Game Agent Guide - For Everyone!

**No Python experience needed!** This guide explains everything in simple terms.

## 🚀 Quick Start (30 seconds)

```bash
# Run the examples
python simple_agent_examples.py

# Choose which game agent to run (1-5)
```

## 📖 What is This?

Think of this as a **robot that plays games for you**. You tell the robot:
1. What to do when the game starts
2. What to do when you get a clue
3. How to make a move
4. What to do when the game ends

The robot handles everything else automatically!

## 🎯 Super Simple Example

Here's a complete game agent in just **20 lines**:

```python
from game_agent_framework_v2 import SimpleGameAgent, GameConfig, AgentRunner

class MyAgent(SimpleGameAgent):
    
    def on_game_started(self, message):
        """Game started - get ready"""
        self.log("Let's play!")
    
    def on_clue_received(self, clue, message):
        """You got a clue - remember it"""
        self.log(f"Got clue: {clue}")
    
    async def make_move(self, message):
        """Return your guess"""
        return "anthropic"  # Your answer here
    
    def on_game_ended(self, message):
        """Game ended - all done"""
        self.log("Game finished!")

# Run it!
config = GameConfig(ws_url="ws://localhost:2025")
AgentRunner.run_agent(MyAgent(config))
```

That's it! **You're done!** 🎉

## 📚 Understanding the 4 Methods

### Method 1: `on_game_started`
**When**: Game begins  
**What to do**: Reset/prepare for new game

```python
def on_game_started(self, message):
    self.log("New game!")
    self.my_data = []  # Reset your data
```

### Method 2: `on_clue_received`
**When**: You get a clue or hint  
**What to do**: Save it, think about it

```python
def on_clue_received(self, clue, message):
    self.log(f"Clue: {clue}")
    # Think about the clue...
```

### Method 3: `make_move`
**When**: Your turn to play  
**What to do**: Return your guess/move

```python
async def make_move(self, message):
    # Your logic here
    return "my_answer"
```

### Method 4: `on_game_ended`
**When**: Game finishes  
**What to do**: See results, clean up

```python
def on_game_ended(self, message):
    self.log("Done!")
```

## 🎮 Real Examples

### Example 1: Cluedle (Answer Questions)

```python
class MyCluedleAgent(SimpleGameAgent):
    def __init__(self, config):
        super().__init__(config)
        self.all_clues = []  # Store clues here
    
    def on_game_started(self, message):
        self.all_clues = []  # Start fresh
    
    def on_clue_received(self, clue, message):
        self.all_clues.append(clue)  # Save the clue
    
    async def make_move(self, message):
        # Simple logic: look for keywords
        text = " ".join(self.all_clues).lower()
        
        if "claude" in text:
            return "anthropic"
        elif "chatgpt" in text:
            return "openai"
        else:
            return "google"
    
    def on_game_ended(self, message):
        self.log(f"I used {len(self.all_clues)} clues")
```

### Example 2: Wordle (Guess Words)

```python
class MyWordleAgent(SimpleGameAgent):
    def __init__(self, config):
        super().__init__(config)
        self.words = ["arose", "slate", "crane"]
        self.turn = 0
    
    def on_game_started(self, message):
        self.turn = 0
    
    def on_clue_received(self, clue, message):
        pass  # Wordle doesn't use clues
    
    async def make_move(self, message):
        word = self.words[self.turn % len(self.words)]
        self.turn += 1
        return word
    
    def on_game_ended(self, message):
        self.log(f"Used {self.turn} guesses")
```

### Example 3: Grid Game (Chess, TicTacToe, etc.)

```python
class MyGridAgent(SimpleGameAgent):
    def __init__(self, config):
        super().__init__(config)
        self.moves = []
    
    def on_game_started(self, message):
        self.moves = []
    
    def on_clue_received(self, clue, message):
        self.log(f"Hint: {clue}")
    
    async def make_move(self, message):
        # First move: center
        if not self.moves:
            return "B2"
        # Other moves: next available
        return f"A{len(self.moves) + 1}"
    
    def on_game_ended(self, message):
        self.log(f"Made {len(self.moves)} moves")
```

## 💾 Accessing Data

Inside your methods, you have access to:

```python
self.clues          # List of all clues received
self.game_state     # Dictionary to store anything
self.match_id       # Current match ID
self.game_id        # Current game ID
self.your_id        # Your player ID

message.game_data   # All data from the server
```

### Example: Using Data

```python
async def make_move(self, message):
    # Use clues
    print(self.clues)  # ["Clue 1", "Clue 2", ...]
    
    # Store your own data
    self.game_state["my_note"] = "remember this"
    
    # Access server data
    if "wordLength" in message.game_data:
        length = message.game_data["wordLength"]
    
    return "my_guess"
```

## 🔧 Configuration

Simple configuration options:

```python
config = GameConfig(
    ws_url="ws://localhost:2025",    # Server address
    connect_timeout=10,               # Wait 10 seconds to connect
    recv_timeout=2,                   # Wait 2 seconds for messages
    keep_alive=True,                  # Stay connected between games
)
```

## 📊 Automatic Features

You get these **for FREE** without coding:

✅ Connection to game server  
✅ Message handling  
✅ Statistics tracking  
✅ Automatic reconnection  
✅ Error handling  
✅ Clean logging  
✅ Game state management  

## 🎯 Message Types Explained

### Type 1: Acknowledgment (ACK)

```json
{
  "type": "ack",
  "ackFor": "game started",
  "ackData": ""
}
```

**What it means**: Server is confirming something  
**What happens**: `on_game_started()` is called automatically

### Type 2: Acknowledgment with Clue

```json
{
  "type": "ack",
  "ackFor": "meta data",
  "ackData": "Which AI company launched Claude 3?"
}
```

**What it means**: Server sent you a clue  
**What happens**: `on_clue_received()` is called with the clue

### Type 3: Command (Your Turn)

```json
{
  "command": "guess",
  "wordLength": 5
}
```

**What it means**: Your turn to play  
**What happens**: `make_move()` is called, return your move

### Type 4: Result (Game Over)

```json
{
  "type": "result",
  "result": "win",
  "word": "hello"
}
```

**What it means**: Game ended  
**What happens**: `on_game_ended()` is called

## 🎨 Customization

### Want to handle special messages?

```python
def on_acknowledgment(self, message):
    """Handle special acknowledgments"""
    if message.ack_for == "bonus round":
        self.log("Bonus round!")
```

### Want custom response format?

```python
def build_response(self, message, move):
    """Custom response format"""
    return {
        "matchId": self.match_id,
        "gameId": self.game_id,
        "answer": move,  # Custom field name
    }
```

## 🧪 Testing Your Agent

```bash
# Run the examples and test
python simple_agent_examples.py
```

## 📈 Statistics

Automatically tracked:

- Games played
- Games won/lost
- Total moves made
- Average moves per game
- Win rate

Printed at the end of each game!

## 🚨 Common Mistakes

### Mistake 1: Not returning anything

```python
# ❌ Wrong
async def make_move(self, message):
    guess = "hello"
    # Forgot to return!

# ✅ Right
async def make_move(self, message):
    guess = "hello"
    return guess  # Must return!
```

### Mistake 2: Forgetting to call super().__init__()

```python
# ❌ Wrong
def __init__(self, config):
    self.my_data = []

# ✅ Right
def __init__(self, config):
    super().__init__(config)  # Must call this!
    self.my_data = []
```

### Mistake 3: Not using async/await

```python
# ❌ Wrong
def make_move(self, message):
    return "guess"

# ✅ Right
async def make_move(self, message):  # Must be async!
    return "guess"
```

## 🎓 Next Steps

1. **Start with examples**: Run `simple_agent_examples.py`
2. **Copy a template**: Pick the example closest to your game
3. **Modify the logic**: Change what happens in `make_move()`
4. **Test it**: Run and see how it performs
5. **Improve it**: Add better logic, use AI, etc.

## 🤝 Need Help?

### Question: "How do I access the clues?"
Answer: Use `self.clues` - it's a list of all clues

### Question: "How do I save data between moves?"
Answer: Use `self.game_state["key"] = value`

### Question: "My agent doesn't respond"
Answer: Make sure `make_move()` returns something

### Question: "How do I use AI?"
Answer: See `AICluedleAgent` in `simple_agent_examples.py`

## 📝 Template to Copy

```python
from game_agent_framework_v2 import SimpleGameAgent, GameConfig, AgentRunner

class MyGameAgent(SimpleGameAgent):
    """
    My custom game agent
    """
    
    def __init__(self, config):
        super().__init__(config)
        # Add your variables here
        self.my_data = []
    
    def on_game_started(self, message):
        """Game started"""
        self.log("Game starting!")
        self.my_data = []
    
    def on_clue_received(self, clue, message):
        """Got a clue"""
        self.log(f"Clue: {clue}")
        self.my_data.append(clue)
    
    async def make_move(self, message):
        """Make your move"""
        # YOUR LOGIC HERE
        return "my_guess"
    
    def on_game_ended(self, message):
        """Game ended"""
        self.log("Game over!")

# Run it
if __name__ == "__main__":
    config = GameConfig(ws_url="ws://localhost:2025")
    agent = MyGameAgent(config)
    AgentRunner.run_agent(agent)
```

---

**That's it! You're ready to build game agents!** 🚀

**Remember**: You only need 4 methods. Everything else is automatic!
