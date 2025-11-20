"""
Quick Start Script for Game Agent Framework

Run this script to see the framework in action.
You can uncomment different agent types to test them.
"""

import asyncio
from game_agent_framework import GameConfig, AgentRunner

# Uncomment the agent you want to test:

# ==================== Wordle Agent ====================
from wordle_agent_example import WordleAgent

config = GameConfig(
    ws_url="ws://localhost:2025",  # Change to your game server URL
    connect_timeout=10,
    recv_timeout=2,
    keep_alive=True,
    max_reconnect_attempts=3,
    reconnect_delay=5,
)

print("=" * 70)
print("🎮 Starting Wordle Agent")
print("=" * 70)
print(f"Server: {config.ws_url}")
print(f"AI Enabled: True")
print(f"Model: gpt-5-nano")
print("=" * 70)
print()

agent = WordleAgent(
    config=config,
    ai_model="gpt-5-nano",
    use_structured_output=True,
    use_ai=True,
)

AgentRunner.run_agent(agent)


# ==================== Cluedle Agent ====================
# from cluedle_agent_example import CluedleAgent
# 
# config = GameConfig(ws_url="ws://localhost:2025")
# 
# print("=" * 70)
# print("🧩 Starting Cluedle Agent")
# print("=" * 70)
# 
# agent = CluedleAgent(config=config, use_ai=True)
# AgentRunner.run_agent(agent)


# ==================== Custom Simple Agent ====================
# from typing import Optional, Dict, Any
# from game_agent_framework import BaseGameAgent, ParsedMessage, GameType
# 
# class SimpleAgent(BaseGameAgent):
#     """Minimal example agent"""
#     
#     def __init__(self, config: GameConfig):
#         super().__init__(config, GameType.WORDLE)
#         self.alphabet = "abcdefghijklmnopqrstuvwxyz"
#     
#     async def make_move(self, parsed: ParsedMessage) -> Optional[str]:
#         length = parsed.word_length or 5
#         return self.alphabet[:length]
#     
#     def build_response(self, parsed: ParsedMessage, move: Optional[str]) -> Optional[Dict[str, Any]]:
#         if not move:
#             return None
#         return {
#             "matchId": parsed.match_id,
#             "gameId": parsed.game_id,
#             "otp": parsed.otp,
#             "guess": move,
#         }
# 
# config = GameConfig(ws_url="ws://localhost:2025")
# agent = SimpleAgent(config)
# AgentRunner.run_agent(agent)
