"""
Agent Evaluation Runner with Mock Server

This module provides a mock server that simulates game sessions
and evaluates agent performance against a set of test words.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from game_agent_framework import (
    BaseGameAgent,
    ParsedMessage,
    GameConfig,
)


@dataclass
class GameSession:
    """Represents a single game session"""
    target_word: str
    match_id: str
    game_id: str
    otp: str = "mock-otp-123"
    max_attempts: int = 6
    guesses: List[str] = field(default_factory=list)
    feedback: List[List[str]] = field(default_factory=list)
    won: bool = False
    attempts_used: int = 0
    
    @property
    def word_length(self) -> int:
        return len(self.target_word)


class MockGameServer:
    """
    Mock game server that simulates Wordle-style games.
    Handles game lifecycle and provides feedback for guesses.
    """
    
    def __init__(self, test_words: List[str]):
        self.test_words = test_words
        self.current_session: Optional[GameSession] = None
        self.session_counter = 0
    
    def start_game(self, word: str) -> Dict[str, Any]:
        """Start a new game session"""
        self.session_counter += 1
        self.current_session = GameSession(
            target_word=word.lower(),
            match_id=f"mock-match-{self.session_counter}",
            game_id=f"mock-game-{self.session_counter}",
        )
        
        return {
            "type": "game start",
            "matchId": self.current_session.match_id,
            "gameId": self.current_session.game_id,
            "otp": self.current_session.otp,
            "wordLength": self.current_session.word_length,
            "maxAttempts": self.current_session.max_attempts,
        }
    
    def calculate_feedback(self, guess: str) -> List[str]:
        """
        Calculate Wordle-style feedback for a guess.
        
        Returns:
            List of feedback: "correct", "present", or "absent"
        """
        if not self.current_session:
            return []
        
        target = self.current_session.target_word.lower()
        guess = guess.lower()
        feedback = []
        
        # Track used letters in target
        target_letters = list(target)
        
        # First pass: mark correct positions
        for i, letter in enumerate(guess):
            if i < len(target) and letter == target[i]:
                feedback.append("correct")
                target_letters[i] = None  # Mark as used
            else:
                feedback.append("unknown")  # Placeholder
        
        # Second pass: mark present letters
        for i, letter in enumerate(guess):
            if feedback[i] == "correct":
                continue
            
            if letter in target_letters:
                feedback[i] = "present"
                target_letters[target_letters.index(letter)] = None  # Mark as used
            else:
                feedback[i] = "absent"
        
        return feedback
    
    def process_guess(self, guess: str) -> Dict[str, Any]:
        """
        Process a guess and return the command message with feedback.
        
        Returns:
            Command message with feedback for the guess
        """
        if not self.current_session:
            raise ValueError("No active game session")
        
        guess = guess.lower()
        feedback = self.calculate_feedback(guess)
        
        self.current_session.guesses.append(guess)
        self.current_session.feedback.append(feedback)
        self.current_session.attempts_used += 1
        
        # Check if won
        if all(f == "correct" for f in feedback):
            self.current_session.won = True
        
        return {
            "type": "command",
            "command": "guess",
            "matchId": self.current_session.match_id,
            "gameId": self.current_session.game_id,
            "otp": self.current_session.otp,
            "wordLength": self.current_session.word_length,
            "maxAttempts": self.current_session.max_attempts,
            "currentAttempt": self.current_session.attempts_used + 1,
            "lastGuess": guess,
            "lastResult": feedback,
        }
    
    def end_game(self) -> Dict[str, Any]:
        """End the current game and return result"""
        if not self.current_session:
            raise ValueError("No active game session")
        
        result = "win" if self.current_session.won else "loss"
        
        return {
            "type": "game result",
            "matchId": self.current_session.match_id,
            "gameId": self.current_session.game_id,
            "result": result,
            "word": self.current_session.target_word,
        }


@dataclass
class EvaluationResult:
    """Results from evaluating an agent on a word"""
    word: str
    won: bool
    attempts: int
    guesses: List[str]
    success: bool  # Whether agent completed without errors


class AgentEvaluator:
    """
    Evaluates agent performance against test words using a mock server.
    """
    
    def __init__(self, agent_factory: callable, test_words: List[str]):
        """
        Args:
            agent_factory: Callable that returns a new agent instance
            test_words: List of words to test
        """
        self.agent_factory = agent_factory
        self.test_words = test_words
        self.results: List[EvaluationResult] = []
    
    async def evaluate_word(self, word: str) -> EvaluationResult:
        """Evaluate agent performance on a single word"""
        print(f"\n{'='*60}")
        print(f"🎯 Testing word: {word.upper()}")
        print(f"{'='*60}")
        
        # Create fresh agent and mock server for this word
        agent = self.agent_factory()
        mock_server = MockGameServer([word])
        
        # Start game
        game_start_msg = mock_server.start_game(word)
        parsed_start = agent.parse_message(json.dumps(game_start_msg))
        
        if not parsed_start:
            print("❌ Failed to parse game start message")
            return EvaluationResult(word, False, 0, [], False)
        
        agent.handle_game_start(parsed_start)
        
        # Game loop
        guesses = []
        success = True
        
        try:
            while mock_server.current_session.attempts_used < mock_server.current_session.max_attempts:
                # Get first guess (simulate command message)
                if not guesses:
                    # First guess - send initial command
                    command_msg = {
                        "type": "command",
                        "command": "guess",
                        "matchId": mock_server.current_session.match_id,
                        "gameId": mock_server.current_session.game_id,
                        "otp": mock_server.current_session.otp,
                        "wordLength": mock_server.current_session.word_length,
                        "maxAttempts": mock_server.current_session.max_attempts,
                        "currentAttempt": 1,
                        "lastGuess": "",
                        "lastResult": [],
                    }
                    parsed = agent.parse_message(json.dumps(command_msg))
                else:
                    # Send feedback from last guess
                    command_msg = mock_server.process_guess(guesses[-1])
                    parsed = agent.parse_message(json.dumps(command_msg))
                
                if not parsed:
                    print("❌ Failed to parse message")
                    success = False
                    break
                
                # Get agent's guess
                guess = await agent.make_move(parsed)
                
                if not guess:
                    print("❌ Agent failed to make a guess")
                    success = False
                    break
                
                guesses.append(guess)
                print(f"📝 Guess {len(guesses)}: {guess}")
                
                # Check if correct
                feedback = mock_server.calculate_feedback(guess)
                print(f"   Feedback: {' '.join(feedback)}")
                
                if all(f == "correct" for f in feedback):
                    mock_server.current_session.won = True
                    mock_server.current_session.attempts_used = len(guesses)
                    break
        
        except Exception as e:
            print(f"❌ Error during evaluation: {e}")
            import traceback
            traceback.print_exc()
            success = False
        
        # End game
        end_msg = mock_server.end_game()
        parsed_end = agent.parse_message(json.dumps(end_msg))
        if parsed_end:
            agent.handle_game_result(parsed_end)
        
        result = EvaluationResult(
            word=word,
            won=mock_server.current_session.won,
            attempts=len(guesses),
            guesses=guesses,
            success=success,
        )
        
        # Print result
        if result.won:
            print(f"✅ WON in {result.attempts} attempts!")
        else:
            print(f"❌ LOST - Failed to guess '{word}' in {result.attempts} attempts")
        
        return result
    
    async def run_evaluation(self) -> Dict[str, Any]:
        """Run evaluation on all test words"""
        print("="*60)
        print("🧪 AGENT EVALUATION SUITE")
        print("="*60)
        print(f"Test words: {', '.join(self.test_words)}")
        print()
        
        for word in self.test_words:
            result = await self.evaluate_word(word)
            self.results.append(result)
        
        # Print summary
        self.print_summary()
        
        return self.get_summary_stats()
    
    def print_summary(self):
        """Print evaluation summary"""
        print("\n" + "="*60)
        print("📊 EVALUATION SUMMARY")
        print("="*60)
        
        for result in self.results:
            status = "✅ WIN" if result.won else "❌ LOSS"
            print(f"\n{result.word.upper()}: {status}")
            print(f"  Attempts: {result.attempts}/{6}")
            print(f"  Guesses: {', '.join(result.guesses)}")
            if not result.success:
                print(f"  ⚠️ Evaluation had errors")
        
        # Overall stats
        wins = sum(1 for r in self.results if r.won)
        total = len(self.results)
        win_rate = (wins / total * 100) if total > 0 else 0
        avg_attempts = sum(r.attempts for r in self.results if r.won) / wins if wins > 0 else 0
        
        print("\n" + "-"*60)
        print(f"Total Games: {total}")
        print(f"Wins: {wins}")
        print(f"Losses: {total - wins}")
        print(f"Win Rate: {win_rate:.1f}%")
        if wins > 0:
            print(f"Avg Attempts (wins only): {avg_attempts:.1f}")
        print("="*60)
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        wins = sum(1 for r in self.results if r.won)
        total = len(self.results)
        
        return {
            "total_games": total,
            "wins": wins,
            "losses": total - wins,
            "win_rate": (wins / total * 100) if total > 0 else 0,
            "avg_attempts": sum(r.attempts for r in self.results if r.won) / wins if wins > 0 else 0,
            "results": [
                {
                    "word": r.word,
                    "won": r.won,
                    "attempts": r.attempts,
                    "guesses": r.guesses,
                }
                for r in self.results
            ]
        }


# ==================== Example Usage ====================

async def run_evaluation_example():
    """Example of running agent evaluation"""
    from wordle_agent_example import WordleAgent
    
    # Test words
    test_words = [
        "kanal", "apple", "world", "crane", "slate",
        # "iring", "vibes", "happy", "comas", "colos",
        # "loved", "frown", "glide", "plumb", "trick",
        # "frost", "grape", "blush", "charm", "dwell",
    ]
    
    # Agent factory
    def create_agent():
        config = GameConfig(
            ws_url="ws://mock:9999",  # Not actually used
            connect_timeout=1,
            recv_timeout=1,
        )
        return WordleAgent(
            config=config,
            ai_model="gpt-4o",
            use_ai=True,  # Set to False for faster testing without AI
        )
    
    # Run evaluation
    evaluator = AgentEvaluator(create_agent, test_words)
    stats = await evaluator.run_evaluation()
    
    print(f"\n🎉 Evaluation complete!")
    print(f"Win rate: {stats['win_rate']:.1f}%")


if __name__ == "__main__":
    print("🧪 Agent Evaluation Runner\n")
    asyncio.run(run_evaluation_example())
