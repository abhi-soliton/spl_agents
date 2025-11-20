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


# ==================== Example 1: Simple Cluedle Agent ====================

class SimpleCluedleAgent(SimpleGameAgent):
    """
    Cluedle Agent - Answer questions based on clues.
    
    For non-programmers: This is ALL the code you need!
    """
    
    def __init__(self, config: GameConfig):
        super().__init__(config, GameType.CLUEDLE)
        # Add any variables you need
        self.all_clues = []
    
    def on_game_started(self, message: GameMessage):
        """Game started - get ready"""
        self.log("🧩 New Cluedle game starting!")
        self.all_clues = []
    
    def on_clue_received(self, clue: str, message: GameMessage):
        """You got a clue - save it"""
        self.all_clues.append(clue)
        self.log(f"📝 Saved clue: {clue}")
    
    async def make_move(self, message: GameMessage) -> Optional[Any]:
        """Return your answer"""
        # Simple logic: look for keywords in clues
        combined_clues = " ".join(self.all_clues).lower()
        
        if "claude" in combined_clues and "ai" in combined_clues:
            return "anthropic"
        elif "chatgpt" in combined_clues or "gpt" in combined_clues:
            return "openai"
        elif "gemini" in combined_clues or "bard" in combined_clues:
            return "google"
        
        # Default guess
        return "anthropic"
    
    def on_game_ended(self, message: GameMessage):
        """Game ended - show results"""
        self.log(f"✅ Game over! I had {len(self.all_clues)} clues")


# ==================== Example 2: AI-Powered Cluedle Agent ====================

class AICluedleAgent(SimpleGameAgent):
    """
    Cluedle Agent with OpenAI - Let AI solve it!
    """
    
    def __init__(self, config: GameConfig, use_ai: bool = True):
        super().__init__(config, GameType.CLUEDLE)
        self.use_ai = use_ai
        self.ai_client = None
        
        load_dotenv()
        if use_ai and os.getenv("OPENAI_API_KEY"):
            self.ai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def on_game_started(self, message: GameMessage):
        self.log("🧩 AI Cluedle agent ready!")
    
    def on_clue_received(self, clue: str, message: GameMessage):
        self.log(f"🤖 AI analyzing clue: {clue}")
    
    async def make_move(self, message: GameMessage) -> Optional[Any]:
        """Use AI to solve based on all clues"""
        if not self.ai_client or not self.clues:
            return "anthropic"
        
        # Build prompt with all clues
        prompt = "Based on these clues, what is the answer?\n\n"
        for i, clue in enumerate(self.clues, 1):
            prompt += f"Clue {i}: {clue}\n"
        prompt += "\nProvide only the answer, nothing else."
        
        try:
            response = self.ai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are great at solving riddles and clues."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.7,
            )
            
            answer = response.choices[0].message.content.strip().lower()
            self.log(f"🤖 AI suggests: {answer}")
            return answer
            
        except Exception as e:
            self.log(f"⚠️ AI failed: {e}")
            return "anthropic"
    
    def on_game_ended(self, message: GameMessage):
        self.log("🎯 Game complete!")


# ==================== Example 3: Simple Wordle Agent ====================

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
    print("1. Simple Cluedle Agent")
    print("2. AI-Powered Cluedle Agent")
    print("3. Simple Wordle Agent")
    print("4. 2D Grid Game Agent")
    print("5. Custom Game Agent")
    print("=" * 60)
    
    choice = input("Choose agent (1-5): ").strip()
    
    if choice == "1":
        agent = SimpleCluedleAgent(config)
        print("🧩 Running Simple Cluedle Agent...")
    elif choice == "2":
        agent = AICluedleAgent(config, use_ai=True)
        print("🤖 Running AI Cluedle Agent...")
    elif choice == "3":
        agent = SimpleWordleAgent(config)
        print("🎮 Running Simple Wordle Agent...")
    elif choice == "4":
        agent = Simple2DGridAgent(config)
        print("🎲 Running 2D Grid Agent...")
    elif choice == "5":
        agent = CustomGameAgent(config)
        print("🎯 Running Custom Agent...")
    else:
        # Default to Cluedle
        agent = SimpleCluedleAgent(config)
        print("🧩 Running Simple Cluedle Agent (default)...")
    
    print("=" * 60)
    AgentRunner.run_agent(agent)
