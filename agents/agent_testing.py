"""
Testing and Validation Utilities for Game Agents

This module provides tools for testing agents without connecting to a live server.
Useful for development, debugging, and unit testing.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from game_agent_framework import (
    BaseGameAgent,
    ParsedMessage,
    GameConfig,
    GameType,
    MessageType,
    GameCommand,
    GameResult,
)


@dataclass
class MockMessage:
    """Mock message for testing"""
    message_type: str
    command: Optional[str] = None
    match_id: str = "test-match-123"
    game_id: str = "test-game-456"
    otp: str = "test-otp-789"
    word_length: int = 5
    max_attempts: int = 6
    current_attempt: int = 1
    last_guess: str = ""
    last_result: List[str] = None
    result: Optional[str] = None
    word: Optional[str] = None

    def to_json(self) -> str:
        """Convert to JSON string"""
        data = {
            "type": self.message_type,
            "command": self.command,
            "matchId": self.match_id,
            "gameId": self.game_id,
            "otp": self.otp,
            "wordLength": self.word_length,
            "maxAttempts": self.max_attempts,
            "currentAttempt": self.current_attempt,
            "lastGuess": self.last_guess,
            "lastResult": self.last_result or [],
            "result": self.result,
            "word": self.word,
        }
        return json.dumps({k: v for k, v in data.items() if v is not None})


class AgentTester:
    """
    Test harness for game agents.
    Simulates server messages and validates agent responses.
    """

    def __init__(self, agent: BaseGameAgent):
        self.agent = agent

    async def test_game_start(self) -> bool:
        """Test agent handles game start correctly"""
        print("\n🧪 Testing: Game Start Handler")
        
        msg = MockMessage(
            message_type="game start",
            word_length=5,
            max_attempts=6,
        )
        
        parsed = self.agent.parse_message(msg.to_json())
        if parsed and parsed.type == MessageType.GAME_START:
            self.agent.handle_game_start(parsed)
            print("✅ Game start handled correctly")
            return True
        
        print("❌ Failed to handle game start")
        return False

    async def test_make_guess(self) -> bool:
        """Test agent can make a guess"""
        print("\n🧪 Testing: Make Guess")
        
        msg = MockMessage(
            message_type="command",
            command="guess",
            current_attempt=1,
        )
        
        parsed = self.agent.parse_message(msg.to_json())
        if not parsed:
            print("❌ Failed to parse message")
            return False
        
        guess = await self.agent.make_move(parsed)
        if guess:
            print(f"✅ Agent made guess: {guess}")
            return True
        
        print("❌ Agent failed to make guess")
        return False

    async def test_build_response(self) -> bool:
        """Test agent can build valid response"""
        print("\n🧪 Testing: Build Response")
        
        msg = MockMessage(
            message_type="command",
            command="guess",
        )
        
        parsed = self.agent.parse_message(msg.to_json())
        if not parsed:
            print("❌ Failed to parse message")
            return False
        
        guess = await self.agent.make_move(parsed)
        response = self.agent.build_response(parsed, guess)
        
        if response:
            required_fields = ["matchId", "gameId", "otp", "guess"]
            has_all_fields = all(field in response for field in required_fields)
            
            if has_all_fields:
                print(f"✅ Valid response: {response}")
                return True
            else:
                print(f"❌ Response missing required fields: {response}")
                return False
        
        print("❌ Failed to build response")
        return False

    async def test_game_result_win(self) -> bool:
        """Test agent handles win correctly"""
        print("\n🧪 Testing: Game Result (Win)")
        
        msg = MockMessage(
            message_type="game result",
            result="win",
            word="hello",
        )
        
        parsed = self.agent.parse_message(msg.to_json())
        if parsed and parsed.type == MessageType.GAME_RESULT:
            self.agent.handle_game_result(parsed)
            print("✅ Win handled correctly")
            return True
        
        print("❌ Failed to handle win")
        return False

    async def test_game_result_loss(self) -> bool:
        """Test agent handles loss correctly"""
        print("\n🧪 Testing: Game Result (Loss)")
        
        msg = MockMessage(
            message_type="game result",
            result="loss",
            word="world",
        )
        
        parsed = self.agent.parse_message(msg.to_json())
        if parsed and parsed.type == MessageType.GAME_RESULT:
            self.agent.handle_game_result(parsed)
            print("✅ Loss handled correctly")
            return True
        
        print("❌ Failed to handle loss")
        return False

    async def test_feedback_parsing(self) -> bool:
        """Test agent correctly parses feedback"""
        print("\n🧪 Testing: Feedback Parsing")
        
        test_cases = [
            (["correct", "present", "absent", "correct", "absent"], True),
            (["green", "yellow", "gray", "g", "y"], True),
            (["c", "p", "a", "correct", "present"], True),
        ]
        
        all_passed = True
        for feedback, expected_success in test_cases:
            msg = MockMessage(
                message_type="command",
                command="guess",
                last_guess="arose",
                last_result=feedback,
                current_attempt=2,
            )
            
            parsed = self.agent.parse_message(msg.to_json())
            if parsed and len(parsed.last_result) == 5:
                print(f"✅ Parsed feedback: {feedback} -> {parsed.last_result}")
            else:
                print(f"❌ Failed to parse feedback: {feedback}")
                all_passed = False
        
        return all_passed

    async def test_multiple_guesses_sequence(self) -> bool:
        """Test agent handles sequence of guesses"""
        print("\n🧪 Testing: Multiple Guess Sequence")
        
        # Simulate a game with feedback
        guesses_and_feedback = [
            ("arose", ["absent", "correct", "absent", "absent", "present"]),
            ("track", ["absent", "correct", "correct", "absent", "absent"]),
            ("bread", ["absent", "correct", "correct", "correct", "absent"]),
        ]
        
        for guess, feedback in guesses_and_feedback:
            msg = MockMessage(
                message_type="command",
                command="guess",
                last_guess=guess,
                last_result=feedback,
                current_attempt=len(guesses_and_feedback) + 1,
            )
            
            parsed = self.agent.parse_message(msg.to_json())
            if not parsed:
                print(f"❌ Failed to parse message for guess: {guess}")
                return False
            
            next_guess = await self.agent.make_move(parsed)
            if not next_guess:
                print(f"❌ Failed to generate guess after: {guess}")
                return False
            
            print(f"✅ After {guess} ({feedback}), agent guessed: {next_guess}")
        
        return True

    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        print("=" * 70)
        print("🧪 Starting Agent Test Suite")
        print("=" * 70)
        
        tests = [
            ("Game Start", self.test_game_start),
            ("Make Guess", self.test_make_guess),
            ("Build Response", self.test_build_response),
            ("Game Result (Win)", self.test_game_result_win),
            ("Game Result (Loss)", self.test_game_result_loss),
            ("Feedback Parsing", self.test_feedback_parsing),
            ("Multiple Guesses", self.test_multiple_guesses_sequence),
        ]
        
        results = {}
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results[test_name] = result
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Test '{test_name}' raised exception: {e}")
                results[test_name] = False
                failed += 1
        
        print("\n" + "=" * 70)
        print("📊 Test Summary")
        print("=" * 70)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {passed / (passed + failed) * 100:.1f}%")
        print("=" * 70)
        
        return results


# ==================== Example Usage ====================

async def test_agent_example():
    """Example of testing an agent"""
    from wordle_agent_example import WordleAgent
    
    # Create agent with test config (won't actually connect)
    config = GameConfig(
        ws_url="ws://test:9999",
        connect_timeout=1,
        recv_timeout=1,
    )
    
    agent = WordleAgent(
        config=config,
        use_ai=False,  # Disable AI for faster testing
    )
    
    # Run tests
    tester = AgentTester(agent)
    results = await tester.run_all_tests()
    
    # Check if all tests passed
    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 All tests passed! Agent is ready.")
    else:
        print("\n⚠️ Some tests failed. Review the output above.")
        failed_tests = [name for name, passed in results.items() if not passed]
        print(f"Failed tests: {', '.join(failed_tests)}")


if __name__ == "__main__":
    print("🧪 Game Agent Testing Framework\n")
    asyncio.run(test_agent_example())
