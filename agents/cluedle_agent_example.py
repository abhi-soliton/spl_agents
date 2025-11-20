"""
Cluedle Agent Implementation - V2 Enhanced

UPDATED: Now handles acknowledgments and metadata properly!

Message Format Examples:
1. Game Started:
   {"matchId":"M-123", "gameId":"G-456", "yourId":"55", 
    "type":"ack", "ackFor":"game started", "ackData":""}

2. Clue Received:
   {"matchId":"M-123", "gameId":"G-456", "yourId":"55", 
    "type":"ack", "ackFor":"meta data", 
    "ackData":"Which AI company launched the Claude 3 model?"}

This agent uses the simplified V2 framework for easier development.
"""

import os
from typing import Optional, Any
from openai import OpenAI
from dotenv import load_dotenv

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_agent_framework_v2 import (
    SimpleGameAgent,
    GameConfig,
    GameType,
    GameMessage,
    AgentRunner,
)


# ==================== Cluedle-specific Models ====================

class CluedleGuess(BaseModel):
    """Structured output for Cluedle guesses"""
    guess: str
    confidence: Optional[float] = None
    reasoning: Optional[str] = None


class CluedleAgent(BaseGameAgent):
    """
    Cluedle-specific agent implementation.
    
    Cluedle typically involves:
    - Receiving clues about the target word/phrase
    - Making educated guesses based on clues
    - Potentially different feedback mechanisms
    
    This is a template - adjust based on actual Cluedle game mechanics.
    """

    def __init__(
        self,
        config: GameConfig,
        ai_model: str = "gpt-5-nano",
        use_ai: bool = True,
    ):
        super().__init__(config, GameType.CLUEDLE)
        self.ai_model = ai_model
        self.use_ai = use_ai
        self._ai_client: Optional[OpenAI] = None
        
        # Track clues and guesses
        self.clues_received: List[str] = []
        self.guess_history: List[str] = []
        
        load_dotenv()
        if use_ai and not os.getenv("OPENAI_API_KEY"):
            self.log("⚠️ OPENAI_API_KEY not found; AI features disabled", "🚨")
            self.use_ai = False

    def _get_ai_client(self) -> Optional[OpenAI]:
        """Lazy-load OpenAI client"""
        if not self.use_ai:
            return None
        
        if self._ai_client is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return None
            self._ai_client = OpenAI(api_key=api_key)
        
        return self._ai_client

    def _extract_clues(self, parsed: ParsedMessage) -> List[str]:
        """Extract clues from the message metadata"""
        # Adjust based on actual Cluedle message format
        clues = []
        
        if "clue" in parsed.metadata:
            clues.append(parsed.metadata["clue"])
        
        if "clues" in parsed.metadata and isinstance(parsed.metadata["clues"], list):
            clues.extend(parsed.metadata["clues"])
        
        if "hint" in parsed.metadata:
            clues.append(f"Hint: {parsed.metadata['hint']}")
        
        return clues

    def _build_clue_context(self, parsed: ParsedMessage) -> str:
        """Build context from all clues received"""
        context_parts = [
            "You are playing Cluedle. Use the clues to guess the target word or phrase.",
        ]
        
        # Add current clues
        current_clues = self._extract_clues(parsed)
        if current_clues:
            self.clues_received.extend(current_clues)
        
        if self.clues_received:
            context_parts.append("\nClues received:")
            for i, clue in enumerate(self.clues_received, 1):
                context_parts.append(f"  {i}. {clue}")
        
        # Add previous guesses
        if self.guess_history:
            context_parts.append("\nPrevious guesses:")
            for i, guess in enumerate(self.guess_history, 1):
                context_parts.append(f"  {i}. {guess}")
        
        # Add constraints
        word_length = parsed.word_length
        if word_length:
            context_parts.append(f"\nThe answer has {word_length} letters.")
        
        context_parts.append("\nProvide your next guess.")
        
        return "\n".join(context_parts)

    async def _ai_solve_clue(self, context: str) -> Optional[str]:
        """Use AI to solve based on clues"""
        client = self._get_ai_client()
        if client is None:
            return None

        try:
            response = client.beta.chat.completions.parse(
                model=self.ai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at solving word puzzles and riddles. Analyze the clues carefully and provide your best guess."
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                response_format=CluedleGuess,
            )
            
            parsed_response = response.choices[0].message.parsed
            if parsed_response and parsed_response.guess:
                guess = parsed_response.guess.strip().lower()
                
                if parsed_response.confidence:
                    self.log(f"🎯 AI confidence: {parsed_response.confidence:.0%}", "📊")
                
                if parsed_response.reasoning:
                    self.log(f"💭 AI reasoning: {parsed_response.reasoning}", "🤔")
                
                return guess
            
            return None
            
        except Exception as exc:
            self.log(f"⚠️ AI solve failed: {exc}", "🚨")
            return None

    def _fallback_guess(self, parsed: ParsedMessage) -> str:
        """Fallback strategy when AI is unavailable"""
        # Look for obvious patterns in metadata
        if "category" in parsed.metadata:
            category = parsed.metadata["category"].lower()
            # Common categories and default guesses
            fallbacks = {
                "animal": "cat",
                "color": "blue",
                "food": "pizza",
                "sport": "soccer",
                "country": "france",
            }
            if category in fallbacks:
                return fallbacks[category]
        
        # Generic fallback
        word_length = parsed.word_length or 5
        return "a" * word_length

    async def make_move(self, parsed: ParsedMessage) -> Optional[str]:
        """Generate the next Cluedle guess"""
        # Build context from clues
        context = self._build_clue_context(parsed)
        
        # Try AI solution
        if self.use_ai:
            guess = await self._ai_solve_clue(context)
            if guess:
                self.guess_history.append(guess)
                return guess
            self.log("⚠️ AI solve failed; using fallback", "🔄")
        
        # Fallback
        fallback = self._fallback_guess(parsed)
        self.guess_history.append(fallback)
        self.log(f"✳️ Using fallback guess: {fallback}", "🔄")
        return fallback

    def build_response(self, parsed: ParsedMessage, move: Optional[str]) -> Optional[Dict[str, Any]]:
        """Build Cluedle response payload"""
        if not move:
            return None

        # Standard fields
        response = {
            "matchId": parsed.match_id,
            "gameId": parsed.game_id,
            "otp": parsed.otp,
            "guess": move,
        }
        
        # Add any Cluedle-specific fields
        # Adjust based on actual game protocol
        
        return response

    def on_game_start(self, parsed: ParsedMessage):
        """Reset state for new game"""
        self.clues_received = []
        self.guess_history = []
        self.log("🧩 New Cluedle game started")

    def on_game_result(self, parsed: ParsedMessage):
        """Log game completion"""
        if parsed.word:
            self.log(f"📝 The answer was: {parsed.word.upper()}")
        
        self.log(f"🔍 Total clues received: {len(self.clues_received)}")
        self.log(f"🎯 Total guesses made: {len(self.guess_history)}")


# ==================== Custom Cluedle Variant ====================

class CrosswordStyleCluedleAgent(CluedleAgent):
    """
    Example of further specialization for crossword-style clues.
    """

    def _build_clue_context(self, parsed: ParsedMessage) -> str:
        """Enhanced context building for crossword-style clues"""
        context = super()._build_clue_context(parsed)
        
        # Add crossword-specific context
        if "across" in parsed.metadata or "down" in parsed.metadata:
            context += "\n\nThis is a crossword-style clue."
            if "position" in parsed.metadata:
                context += f"\nPosition: {parsed.metadata['position']}"
        
        return context


# ==================== Main Entry Point ====================

if __name__ == "__main__":
    # Configuration
    config = GameConfig(
        ws_url="ws://localhost:2025",
        connect_timeout=10,
        recv_timeout=2,
        keep_alive=True,
        max_reconnect_attempts=3,
        reconnect_delay=5,
    )
    
    # Create Cluedle agent
    agent = CluedleAgent(
        config=config,
        ai_model="gpt-5-nano",
        use_ai=True,
    )
    
    # Run the agent
    print("=" * 60)
    print("🧩 Cluedle Agent Starting...")
    print("=" * 60)
    AgentRunner.run_agent(agent)
