"""
Simple Examples for Different Game Types

These examples show how easy it is to create agents for different games.
Each agent only implements 4 methods!
"""

from game_agent_framework_v2 import SimpleGameAgent, GameConfig, GameType, GameMessage, AgentRunner
from typing import Optional, Any
import os
from openai import OpenAI
from dotenv import load_dotenv


# ==================== Example 1: Simple Wordle Agent ====================

class SimpleWordleAgent(SimpleGameAgent):
    """
    Wordle Agent - Guess 5-letter words.
    """
    
    def __init__(self, config: GameConfig):
        super().__init__(config, GameType.WORDLE)
        self.common_words = ["arose", "slate", "crane", "trace", "brake"]
        self.guess_number = 0
    
    def on_game_started(self, message: GameMessage):
        self.log("🎮 New Wordle game!")
        self.guess_number = 0
    
    def on_clue_received(self, clue: str, message: GameMessage):
        """Wordle doesn't use clues, but we handle it anyway"""
        pass
    
    async def make_move(self, message: GameMessage) -> Optional[Any]:
        """Return next guess"""
        # Simple strategy: use common starting words
        if self.guess_number < len(self.common_words):
            word = self.common_words[self.guess_number]
        else:
            word = "hello"  # Fallback
        
        self.guess_number += 1
        return word
    
    def on_game_ended(self, message: GameMessage):
        self.log(f"Game ended after {self.guess_number} guesses")


# ==================== Example 4: 2D Grid Game Agent ====================

class Simple2DGridAgent(SimpleGameAgent):
    """
    2D Grid Game - For games like TicTacToe, Chess, Checkers, etc.
    
    Moves are typically coordinates like "A1", "B3", etc.
    """
    
    def __init__(self, config: GameConfig):
        super().__init__(config, GameType.GRID_2D)
        self.grid_size = 3  # 3x3 grid
        self.my_moves = []
    
    def on_game_started(self, message: GameMessage):
        self.log("🎲 New 2D Grid game!")
        self.my_moves = []
        
        # Check if message has grid size
        if "gridSize" in message.game_data:
            self.grid_size = message.game_data["gridSize"]
            self.log(f"Grid size: {self.grid_size}x{self.grid_size}")
    
    def on_clue_received(self, clue: str, message: GameMessage):
        """Might receive hints about good moves"""
        self.log(f"💡 Hint: {clue}")
    
    async def make_move(self, message: GameMessage) -> Optional[Any]:
        """Return coordinates for next move"""
        # Simple strategy: try center first, then corners, then edges
        
        if not self.my_moves:
            # First move: go center
            center = self.grid_size // 2
            move = f"{chr(65 + center)}{center + 1}"  # e.g., "B2" for 3x3
            self.my_moves.append(move)
            return move
        
        # Subsequent moves: just pick next available
        # (In real game, you'd check which cells are empty)
        row = len(self.my_moves) // self.grid_size
        col = len(self.my_moves) % self.grid_size
        move = f"{chr(65 + col)}{row + 1}"
        self.my_moves.append(move)
        return move
    
    def on_game_ended(self, message: GameMessage):
        self.log(f"Game ended! My moves: {self.my_moves}")
    
    def build_response(self, message: GameMessage, move: Optional[Any]) -> Optional[dict]:
        """Custom response format for grid games"""
        if not move:
            return None
        
        # Grid games might need different format
        return {
            "matchId": self.match_id,
            "gameId": self.game_id,
            "otp": message.game_data.get("otp"),
            "move": move,  # Note: "move" instead of "guess"
            "position": move,  # Some games use "position"
        }


# ==================== Example 5: Custom Game with Special Handling ====================

class CustomGameAgent(SimpleGameAgent):
    """
    Template for any custom game.
    
    Shows how to handle special acknowledgments and custom data.
    """
    
    def __init__(self, config: GameConfig):
        super().__init__(config, GameType.CUSTOM)
    
    def on_game_started(self, message: GameMessage):
        self.log("🎮 Custom game starting!")
        
        # Access any custom data from the message
        if "specialRules" in message.game_data:
            rules = message.game_data["specialRules"]
            self.log(f"📜 Special rules: {rules}")
    
    def on_clue_received(self, clue: str, message: GameMessage):
        self.log(f"Got data: {clue}")
    
    async def make_move(self, message: GameMessage) -> Optional[Any]:
        """Your game logic here"""
        return "my_move"
    
    def on_game_ended(self, message: GameMessage):
        self.log("Game finished!")
    
    def on_acknowledgment(self, message: GameMessage):
        """Handle special acknowledgments"""
        ack_type = message.ack_for
        ack_data = message.ack_data
        
        if ack_type == "special event":
            self.log(f"⭐ Special event: {ack_data}")
        elif ack_type == "bonus round":
            self.log(f"🎁 Bonus round: {ack_data}")
        
        # Store in game state for later use
        self.game_state[ack_type] = ack_data


# ==================== Main - Run Any Agent ====================

if __name__ == "__main__":
    import sys
    
    # Configuration
    config = GameConfig(
        ws_url="ws://localhost:2025",
        connect_timeout=10,
        recv_timeout=2,
        keep_alive=True,
    )
    
    # Choose which agent to run
    print("=" * 60)
    print("🎮 Simple Game Agents")
    print("=" * 60)
    print("1. Simple Wordle Agent")
    print("2. 2D Grid Game Agent")
    print("3. Custom Game Agent")
    print("=" * 60)
    
    choice = input("Choose agent (1-3): ").strip()
    
    if choice == "1":
        agent = SimpleWordleAgent(config)
        print("🎮 Running Simple Wordle Agent...")
    elif choice == "2":
        agent = Simple2DGridAgent(config)
        print("🎲 Running 2D Grid Agent...")
    elif choice == "3":
        agent = CustomGameAgent(config)
        print("🎯 Running Custom Agent...")
    else:
        # Default to Wordle
        agent = SimpleWordleAgent(config)
        print("🎮 Running Simple Wordle Agent (default)...")
    
    print("=" * 60)
    AgentRunner.run_agent(agent)
