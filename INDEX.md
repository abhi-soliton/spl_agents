# 🎮 Game Agent Framework - Start Here!

Welcome to the **Game Agent Framework** - a production-ready Python framework for building AI-powered game agents.

## ⚡ Quick Start (30 seconds)

```bash
# Run the Wordle agent immediately
cd wordle
python run_agent.py
```

That's it! The agent will connect, play games, and show statistics.

## 📚 Documentation Guide

### 🚀 Just Starting? Read These First:

1. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** ⭐ START HERE
   - One-page cheat sheet
   - Code snippets ready to copy/paste
   - Common patterns and solutions
   
2. **[PACKAGE_SUMMARY.md](PACKAGE_SUMMARY.md)** 
   - What you have and why it's awesome
   - Feature overview
   - Next steps guide

### 📖 Building Your Agent? Read These:

3. **[FRAMEWORK_GUIDE.md](FRAMEWORK_GUIDE.md)** ⭐ MAIN GUIDE
   - Complete usage guide
   - Step-by-step instructions
   - Best practices
   - Configuration options
   
4. **[VISUAL_REFERENCE.md](VISUAL_REFERENCE.md)**
   - Message flow diagrams
   - State machine visualization
   - Class hierarchy charts

### 🔍 Need API Details? Reference This:

5. **[AGENT_FRAMEWORK_README.md](AGENT_FRAMEWORK_README.md)** ⭐ FULL API
   - Complete API reference
   - All methods and properties
   - Advanced usage patterns
   - Examples for every feature

## 📁 File Structure

```
wordle/
│
├── 🎯 CORE FILES (Use these to build agents)
│   ├── game_agent_framework.py      ← Core framework (import this)
│   ├── wordle_agent_example.py      ← Working Wordle agent
│   ├── run_agent.py                 ← Run agents from here
│   └── agent_testing.py             ← Test your agents
│
└── 📚 DOCUMENTATION (Read these to learn)
    ├── QUICK_REFERENCE.md           ← ⭐ Start here (1-page reference)
    ├── PACKAGE_SUMMARY.md           ← What you have
    ├── FRAMEWORK_GUIDE.md           ← ⭐ Main guide (how to use)
    ├── VISUAL_REFERENCE.md          ← Diagrams and flowcharts
    ├── AGENT_FRAMEWORK_README.md    ← ⭐ Full API reference
    └── INDEX.md                     ← You are here!
```

## 🎯 Choose Your Path

### Path 1: "Just Run It!" 🏃‍♂️
**Time: 30 seconds**

```bash
python run_agent.py
```

Done! Watch it play games automatically.

---

### Path 2: "I Want to Understand" 📖
**Time: 15 minutes**

1. Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md) (5 min)
2. Read [PACKAGE_SUMMARY.md](PACKAGE_SUMMARY.md) (5 min)
3. Run `python run_agent.py` and watch (5 min)

---

### Path 3: "I'm Building My Own Agent" 🛠️
**Time: 1-2 hours**

1. **Understand the framework** (30 min)
   - Read [FRAMEWORK_GUIDE.md](FRAMEWORK_GUIDE.md)
   - Review [VISUAL_REFERENCE.md](VISUAL_REFERENCE.md)

2. **Study the examples** (30 min)
   - Read `wordle_agent_example.py`

3. **Test without server** (15 min)
   - Run `python agent_testing.py`
   - Understand the test patterns

4. **Build your agent** (30 min)
   - Copy the minimal template from [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
   - Implement `make_move()` and `build_response()`
   - Test with `agent_testing.py`
   - Deploy with `AgentRunner.run_agent()`

---

### Path 4: "I Need Advanced Features" 🚀
**Time: 2+ hours**

1. Complete "Path 3" first
2. Read [AGENT_FRAMEWORK_README.md](AGENT_FRAMEWORK_README.md) (full API)
3. Study advanced patterns:
   - AI integration with OpenAI
   - Multiple strategies with fallbacks
   - State tracking and context awareness
   - Custom message parsing
4. Implement and test thoroughly

---

## 🎓 Learning Resources

### For Beginners
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - One-page cheat sheet
- [PACKAGE_SUMMARY.md](PACKAGE_SUMMARY.md) - High-level overview
- `run_agent.py` - See it in action

### For Developers
- [FRAMEWORK_GUIDE.md](FRAMEWORK_GUIDE.md) - Complete usage guide
- [VISUAL_REFERENCE.md](VISUAL_REFERENCE.md) - Diagrams
- `wordle_agent_example.py` - Production code example

### For Advanced Users
- [AGENT_FRAMEWORK_README.md](AGENT_FRAMEWORK_README.md) - Full API
- `game_agent_framework.py` - Source code
- `agent_testing.py` - Testing patterns

## 📖 Documentation at a Glance

| Document | Purpose | Read When | Time |
|----------|---------|-----------|------|
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | One-page cheat sheet | Starting or need quick lookup | 5 min |
| [PACKAGE_SUMMARY.md](PACKAGE_SUMMARY.md) | What you have & why | Want overview | 10 min |
| [FRAMEWORK_GUIDE.md](FRAMEWORK_GUIDE.md) | How to use the framework | Building an agent | 30 min |
| [VISUAL_REFERENCE.md](VISUAL_REFERENCE.md) | Diagrams & flowcharts | Need visual understanding | 15 min |
| [AGENT_FRAMEWORK_README.md](AGENT_FRAMEWORK_README.md) | Complete API reference | Need specific details | 1 hour |

## 🎯 Common Tasks

### Task: Run the Example Agent
```bash
python run_agent.py
```

### Task: Test Without Server
```bash
python agent_testing.py
```

### Task: Create Minimal Agent
```python
# Copy from QUICK_REFERENCE.md section "Minimal Agent (10 lines)"
```

### Task: Customize Wordle Agent
```python
# 1. Open wordle_agent_example.py
# 2. Modify make_move() method
# 3. Change ai_model or strategies
# 4. Run with run_agent.py
```

### Task: Add New Game Type
```python
# 1. Create new file: my_game_agent.py
# 2. Copy template from FRAMEWORK_GUIDE.md
# 3. Implement make_move() and build_response()
# 4. Add to run_agent.py
```

## 🧪 Testing Your Agent

```python
# Option 1: Run test suite
python agent_testing.py

# Option 2: Import and test specific agent
from agent_testing import AgentTester
from my_agent import MyAgent

tester = AgentTester(MyAgent(config))
await tester.run_all_tests()
```

## 📊 What You Get

### Code
- ✅ 520 lines of core framework
- ✅ 240 lines Wordle agent (complete)
- ✅ 300 lines testing framework
- ✅ Ready-to-run scripts

### Documentation
- ✅ 5 comprehensive markdown files
- ✅ Code examples throughout
- ✅ Diagrams and visualizations
- ✅ API reference
- ✅ Usage guides

### Features
- ✅ WebSocket connection management
- ✅ Message parsing and routing
- ✅ Game lifecycle handling
- ✅ Statistics tracking
- ✅ OpenAI integration
- ✅ Error handling & reconnection
- ✅ Comprehensive testing

## 🎨 Architecture Overview

```
You → AgentRunner → Your Agent → BaseGameAgent → WebSocket → Game Server
                         ↓
                    make_move()      (you implement this)
                         ↓
                 build_response()    (you implement this)
```

**That's it!** Everything else is handled for you.

## 🚀 Getting Started Checklist

- [ ] Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- [ ] Run `python run_agent.py` to see it work
- [ ] Run `python agent_testing.py` to test
- [ ] Read [FRAMEWORK_GUIDE.md](FRAMEWORK_GUIDE.md)
- [ ] Copy minimal agent template
- [ ] Implement your `make_move()` logic
- [ ] Implement your `build_response()` format
- [ ] Test your agent
- [ ] Deploy and play!

## 💡 Pro Tips

1. **Start simple** - Use the minimal agent template first
2. **Test early** - Use `agent_testing.py` before connecting
3. **Study examples** - Both agents are production-ready
4. **Use the docs** - Everything is documented
5. **Ask questions** - Check the relevant documentation file

## 🎯 Your First Agent in 5 Steps

```python
# 1. Import
from game_agent_framework import BaseGameAgent, GameConfig, GameType, ParsedMessage, AgentRunner

# 2. Create class
class MyAgent(BaseGameAgent):
    def __init__(self, config):
        super().__init__(config, GameType.WORDLE)
    
    # 3. Implement make_move
    async def make_move(self, parsed):
        return "hello"[:parsed.word_length or 5]
    
    # 4. Implement build_response
    def build_response(self, parsed, move):
        return {"matchId": parsed.match_id, "gameId": parsed.game_id, 
                "otp": parsed.otp, "guess": move} if move else None

# 5. Run it
AgentRunner.run_agent(MyAgent(GameConfig(ws_url="ws://localhost:2025")))
```

**Congratulations!** You just built a game agent! 🎉

## 📞 Need Help?

### "How do I...?"
→ Check [FRAMEWORK_GUIDE.md](FRAMEWORK_GUIDE.md)

### "What does this do...?"
→ Check [AGENT_FRAMEWORK_README.md](AGENT_FRAMEWORK_README.md)

### "Show me a picture..."
→ Check [VISUAL_REFERENCE.md](VISUAL_REFERENCE.md)

### "I need a quick reference..."
→ Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

### "What can this framework do...?"
→ Check [PACKAGE_SUMMARY.md](PACKAGE_SUMMARY.md)

---

## 🎯 Summary

You have a **complete, production-ready framework** with:

- ✅ Core framework (520 lines)
- ✅ Example Wordle agent
- ✅ Testing framework
- ✅ 5 documentation files
- ✅ Quick start scripts
- ✅ Full type safety
- ✅ AI integration

**Total: 800+ lines of code + comprehensive docs**

---

## 🏁 Ready to Start?

### Absolute Beginner?
👉 **Read**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)  
👉 **Run**: `python run_agent.py`

### Want to Build?
👉 **Read**: [FRAMEWORK_GUIDE.md](FRAMEWORK_GUIDE.md)  
👉 **Study**: `wordle_agent_example.py`  
👉 **Test**: `python agent_testing.py`

### Need API Details?
👉 **Read**: [AGENT_FRAMEWORK_README.md](AGENT_FRAMEWORK_README.md)

---

**Happy Building! 🚀**

*Framework Version: 1.0 | Status: Production Ready ✅*
