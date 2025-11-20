"""
Wordle Agent Implementation Example

This demonstrates how to create a Wordle agent by inheriting from BaseGameAgent.
Includes OpenAI integration for intelligent guessing.
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel

from game_agent_framework import (
    BaseGameAgent,
    GameConfig,
    GameType,
    ParsedMessage,
    AgentRunner,
)


# ==================== OpenAI Integration ====================

class GuessWord(BaseModel):
    """Structured output format for AI guesses"""
    guess: str
    reasoning: Optional[str] = None

from collections import Counter
from collections import Counter

def generate_word_no_repeats(words, banned=None):
    if banned is None:
        banned = set()

    word_length = len(words[0])
    result = ""
    used = set()  # keep track of used letters

    for pos in range(word_length):
        # letters that appear in this position
        letters = [word[pos] for word in words]
        freq = Counter(letters).most_common()

        # pick the most frequent allowed letter
        chosen = None
        for letter, _ in freq:
            if letter not in used and letter not in banned:
                chosen = letter
                break

        # fallback: pick any unused, allowed letter
        if not chosen:
            for c in "abcdefghijklmnopqrstuvwxyz":
                if c not in used and c not in banned:
                    chosen = c
                    break

        result += chosen
        used.add(chosen)

    return result

def build_word_prompt(
        letters_exist=None,
        letters_not_exist=None,
        exact_positions=None,
        wrong_positions=None,
        word_length=None,
        count=20,
        previous_guesses=None
):
    """
    Build a natural-language prompt to generate words with constraints.

    letters_exist: list of letters that must appear somewhere in the word
    letters_not_exist: list of letters that must NOT appear anywhere
    exact_positions: dict mapping position -> letter (positions are 1-based)
    wrong_positions: dict mapping letter -> set of positions where it can't be (positions are 1-based)
    word_length: int specifying the fixed word length
    count: number of words to generate
    previous_guesses: list of words already guessed (to avoid repetition)
    """

    letters_exist = letters_exist or []
    letters_not_exist = letters_not_exist or []
    exact_positions = exact_positions or {}
    wrong_positions = wrong_positions or {}
    previous_guesses = previous_guesses or []

    parts = []

    # Task with clear output format
    parts.append(f"Generate exactly {count} valid English words that match ALL of the following constraints:")
    parts.append("")  # blank line for readability

    # Word length
    if word_length:
        parts.append(f"CONSTRAINT 1: Word Length")
        parts.append(f"  - Each word must be EXACTLY {word_length} letters long")
        parts.append("")

    # Exact positions (highest priority constraint)
    constraint_num = 2
    if exact_positions:
        parts.append(f"CONSTRAINT {constraint_num}: Fixed Letter Positions")
        for pos, letter in sorted(exact_positions.items()):
            parts.append(f"  - Position {pos} MUST be: '{letter}'")
        parts.append("")
        constraint_num += 1

    # Letters that must appear
    if letters_exist:
        parts.append(f"CONSTRAINT {constraint_num}: Required Letters")
        exist_str = ", ".join(f"'{l}'" for l in letters_exist)
        parts.append(f"  - The word MUST contain all of these letters: {exist_str}")
        parts.append(f"  - These letters can appear in any position (except positions already fixed above)")
        parts.append(f"  - These letters may repeat 2 or more times")
        
        # Add wrong position constraints for each letter
        if wrong_positions:
            parts.append(f"  - Position restrictions for required letters:")
            for letter, positions in sorted(wrong_positions.items()):
                if letter in letters_exist:
                    pos_str = ", ".join(str(p) for p in sorted(positions))
                    parts.append(f"    × '{letter}' CANNOT be at position(s): {pos_str}")
        
        parts.append("")
        constraint_num += 1

    # Letters that must NOT appear
    if letters_not_exist:
        parts.append(f"CONSTRAINT {constraint_num}: Forbidden Letters")
        not_exist_str = ", ".join(f"'{l}'" for l in sorted(letters_not_exist))
        parts.append(f"  - The word MUST NOT contain any of: {not_exist_str}")
        parts.append("")
        constraint_num += 1

    # Optional letters
    letters_may_exist = set("abcdefghijklmnopqrstuvwxyz") - set(letters_not_exist) - set(letters_exist) - set(exact_positions.values())
    if letters_may_exist:
        may_exist_str = ", ".join(f"'{l}'" for l in sorted(letters_may_exist))
        parts.append(f"CONSTRAINT {constraint_num}: New Letters that can present in the word")
        parts.append(f"  - The word MAY use any of: {may_exist_str}")
        parts.append("")
        constraint_num += 1

    # Previous guesses
    if previous_guesses:
        parts.append(f"CONSTRAINT {constraint_num}: No Repeated Guesses")
        parts.append(f"  - DO NOT suggest any of these previously guessed words:")
        for guess in previous_guesses:
            parts.append(f"    × {guess}")
        parts.append("")

    # Output format instructions
    parts.append("=" * 50)
    parts.append("OUTPUT FORMAT:")
    parts.append("  - List ONLY the words, one per line")
    parts.append("  - Use lowercase letters only")
    parts.append("  - Do NOT include numbers, explanations, or punctuation")
    parts.append("  - Do NOT include any other text")
    parts.append("  - Do NOT include numbered lists like 1. 2. 3. ")
    parts.append("")
    parts.append("EXAMPLE OUTPUT:")
    parts.append("apple")
    parts.append("brave")
    parts.append("candy")
    parts.append("=" * 50)
    parts.append("")
    parts.append("YOUR WORDS:")

    return "\n".join(parts)


class WordleAgent(BaseGameAgent):
    """
    Wordle-specific agent with OpenAI integration.
    
    Features:
    - AI-powered guessing using OpenAI models
    - Fallback to simple heuristics if AI fails
    - Learning from feedback to improve guesses
    - Support for both structured and unstructured AI responses
    """

    def __init__(
        self,
        config: GameConfig,
        ai_model: str = "gpt-5-nano",
        use_structured_output: bool = True,
        use_ai: bool = True,
    ):
        super().__init__(config, GameType.WORDLE)
        self.ai_model = ai_model
        self.use_structured_output = use_structured_output
        self.use_ai = use_ai
        self._ai_client: Optional[AsyncOpenAI] = None
        self.alphabet = "abcdefghijklmnopqrstuvwxyz"
        self.letters_exist: list[str] = []
        self.letters_not_exist: set[str] = set()
        self.exact_positions: Dict[int, str] = {}
        self.wrong_positions: Dict[str, set[int]] = {}  # letter -> set of positions where it can't be

        
        # Track game state for AI context
        self.guess_history: list[str] = []
        self.feedback_history: list[list[str]] = []
        
        # Load OpenAI API key
        load_dotenv()
        if use_ai and not os.getenv("OPENAI_API_KEY"):
            self.log("⚠️ OPENAI_API_KEY not found; AI features disabled", "🚨")
            self.use_ai = False


    # parsed.last_result = ["Absent", "Present", "Correct", "Absent", "Correct"]
    # build function to modify letters_exist, letters_not_exist, exact_positions
    def _update_feedback(self, parsed: ParsedMessage):
        """Update internal state based on last guess feedback"""
        if not parsed.last_result or not parsed.last_guess:
            return
        
        last_guess = parsed.last_guess.lower()
        last_result = parsed.last_result
        print("Last guess:", last_guess)
        print("Last result:", last_result)
        
        for idx, (letter, result) in enumerate(zip(last_guess, last_result), start=1):
            if result == "correct":
                self.exact_positions[idx] = letter
                if letter not in self.letters_exist:
                    self.letters_exist.append(letter)
            elif result == "present":
                if letter not in self.letters_exist:
                    self.letters_exist.append(letter)
                # Track wrong position
                if letter not in self.wrong_positions:
                    self.wrong_positions[letter] = set()
                self.wrong_positions[letter].add(idx)
            elif result == "absent":
                # Only add to not_exist if not already confirmed elsewhere
                if letter not in self.letters_exist and letter not in self.exact_positions.values():
                    self.letters_not_exist.add(letter)

    def _get_ai_client(self) -> Optional[AsyncOpenAI]:
        """Lazy-load OpenAI client"""
        if not self.use_ai:
            return None
        
        if self._ai_client is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return None
            self._ai_client = AsyncOpenAI(api_key=api_key)
        
        return self._ai_client

    async def _generate_words(self, count: int, word_length: int) -> Optional[str]:
        """Get AI guess using simple text response"""
        client = self._get_ai_client()
        if client is None:
            return None

        try:
            prompt =  build_word_prompt(
                letters_exist=self.letters_exist,
                letters_not_exist=self.letters_not_exist,
                exact_positions=self.exact_positions,
                wrong_positions=self.wrong_positions,
                word_length=word_length,
                count=count,
                previous_guesses=self.guess_history,
            )
            print("-----")
            print(prompt)
            print("-----")
            response = await client.chat.completions.parse(
                model=self.ai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Wordle player."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                max_completion_tokens=150,
            )
            words_str = response.choices[0].message.content.strip().lower()
            print(f"AI Response:\n{words_str}")
            # Extract just the word if AI added extra text
            words = words_str.split("\n")
            words = [word.strip() for word in words if word.strip()]
            # remove non alphabetic letters from each word, as 1. are added
            words = [''.join(filter(str.isalpha, word)) for word in words if len(word) == word_length]
            # remove unmatched word length
            words = [word for word in words if len(word) == word_length]

            self.log(f"🤖 AI generated words: {words}", "💡")
            
            return words
            
        except Exception as exc:
            self.log(f"⚠️ AI guess failed: {exc}", "🚨")
            return None

    def _fallback_guess(self, parsed: ParsedMessage) -> str:
        """Simple fallback strategy when AI is unavailable"""
        length = parsed.word_length or 5
        
        # Common starting words
        starters = {
            5: ["arose", "slate", "crane", "adieu", "audio"],
            6: ["raised", "seared", "silent"],
            7: ["started", "claimed"],
        }
        
        attempt = parsed.current_attempt or 1
        if attempt == 1 and length in starters:
            return starters[length][0]
        
        # Use alphabet as last resort
        return self.alphabet[:length]

    async def make_move(self, parsed: ParsedMessage) -> Optional[str]:
        guess = await self._make_move(parsed)
        self.guess_history.append(guess)
        return guess

    async def _make_move(self, parsed: ParsedMessage) -> Optional[str]:
        """Generate the next Wordle guess"""
        if not self.guess_history:
            word = "aioue"
            return word
        self._update_feedback(parsed)
        print("Letters exist:", self.letters_exist)
        print("Letters not exist:", self.letters_not_exist)
        print("Exact positions:", self.exact_positions)
        if self.use_ai:
            if len(self.guess_history) == 3 or len(self.letters_exist) >= parsed.word_length - 1 or len(self.guess_history) >= 5:
                words = await self._generate_words(1, parsed.word_length)
                if not words:
                    self.log("⚠️ AI guess failed; using fallback", "🔄")
                    fallback = self._fallback_guess(parsed)
                    self.log(f"✳️ Using fallback guess: {fallback}", "🔄")
                    return fallback
                return words[0]
            words = await self._generate_words(20, parsed.word_length)
            if words:
                guess = generate_word_no_repeats(words, banned=(self.letters_not_exist | set(self.letters_exist)))
                return guess
            self.log("⚠️ AI guess failed; using fallback", "🔄")
        
        # Fallback to simple heuristic
        fallback = self._fallback_guess(parsed)
        self.log(f"✳️ Using fallback guess: {fallback}", "🔄")
        return fallback

    def build_response(self, parsed: ParsedMessage, move: Optional[str]) -> Optional[Dict[str, Any]]:
        """Build Wordle response payload"""
        if not move or not parsed.match_id or not parsed.game_id or not parsed.otp:
            return None

        return {
            "matchId": parsed.match_id,
            "gameId": parsed.game_id,
            "otp": parsed.otp,
            "guess": move,
        }

    def on_game_start(self, parsed: ParsedMessage):
        """Reset history when new game starts"""
        self.guess_history = []
        self.feedback_history = []
        self.log(f"🎮 New Wordle game - Word length: {parsed.word_length}, Max attempts: {parsed.max_attempts}")

    def on_game_result(self, parsed: ParsedMessage):
        """Log game completion"""
        if parsed.word:
            self.log(f"📝 The word was: {parsed.word.upper()}")
        self.letters_exist = []
        self.letters_not_exist = set()
        self.exact_positions = {}
        self.wrong_positions = {}
        self.guess_history = []
        self.feedback_history = []


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
    
    # Create agent factory for new framework
    def create_wordle_agent():
        return WordleAgent(
            config=config,
            ai_model="gpt-4o",
            use_structured_output=True,
            use_ai=True,
        )
    
    # Run the agent
    print("=" * 60)
    print("🎮 Wordle Agent Starting...")
    print("=" * 60)
    
    # Option 1: New agent for each game ID (recommended for Wordle)
    AgentRunner.run_agent(create_wordle_agent, reusable=False)
    
    # Option 2: Single agent handles all games (uncomment to use)
    # AgentRunner.run_agent(create_wordle_agent, reusable=True)
