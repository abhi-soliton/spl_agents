"""
Cluedle Agent V2 - Handles Acknowledgments and Metadata

This agent properly handles:
1. Game started acknowledgment
2. Clue/metadata acknowledgments
3. Command responses
4. Game results

Message Examples:
{
  "matchId":"M-23A18D9E-51C1-4387-A98D-CA03AD64CF03",
  "gameId":"G-C1A4CC95-CA1E-4810-B3C8-2AC4B54D6ACF",
  "yourId":"55",
  "type":"ack",
  "ackFor":"game started",
  "ackData":""
}

{
  "matchId":"M-91B97737-289D-435D-9D12-9B7E9E2880CA",
  "gameId":"G-86ABF112-3334-47D5-B120-CF332AA9E8A1",
  "yourId":"43",
  "type":"ack",
  "ackFor":"meta data",
  "ackData":"Which AI company launched the Claude 3 model?"
}
"""

import os
import sys
from typing import Optional, Any
from openai import OpenAI
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_agent_framework_v2 import (
    SimpleGameAgent,
    GameConfig,
    GameType,
    GameMessage,
    AgentRunner,
)


class CluedleAgentV2(SimpleGameAgent):
    """
    Simple Cluedle Agent using V2 framework.
    
    Handles:
    - Game started acknowledgments
    - Metadata/clue acknowledgments
    - AI-powered answering
    - Multiple clues
    """
    
    def __init__(self, config: GameConfig, use_ai: bool = True):
        super().__init__(config, GameType.CLUEDLE)
        self.use_ai = use_ai
        self.ai_client = None
        
        # Load AI if available
        load_dotenv()
        if use_ai and os.getenv("OPENAI_API_KEY"):
            try:
                self.ai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                self.log("🤖 AI enabled (OpenAI)")
            except Exception as e:
                self.log(f"⚠️ AI initialization failed: {e}")
                self.use_ai = False
        else:
            self.log("📝 Running without AI")
    
    def on_game_started(self, message: GameMessage):
        """Called when game starts (ackFor='game started')"""
        self.log("🧩 New Cluedle game started!")
        self.log(f"Match ID: {self.match_id}")
        self.log(f"Game ID: {self.game_id}")
        self.log(f"Your ID: {self.your_id}")
    
    def on_clue_received(self, clue: str, message: GameMessage):
        """Called when clue received (ackFor='meta data')"""
        self.log(f"🔍 Clue #{len(self.clues)}: {clue}")
        
        # Analyze the clue
        clue_lower = clue.lower()
        
        # Simple keyword detection
        if "claude" in clue_lower:
            self.game_state["hint"] = "anthropic"
            self.log("💡 Detected keyword: Claude → Anthropic")
        elif "chatgpt" in clue_lower or "gpt" in clue_lower:
            self.game_state["hint"] = "openai"
            self.log("💡 Detected keyword: GPT → OpenAI")
        elif "gemini" in clue_lower or "bard" in clue_lower:
            self.game_state["hint"] = "google"
            self.log("💡 Detected keyword: Gemini → Google")
    
    async def make_move(self, message: GameMessage) -> Optional[Any]:
        """Generate answer based on all clues"""
        if not self.clues:
            self.log("⚠️ No clues received yet!")
            return "anthropic"
        
        # Try AI first
        if self.use_ai and self.ai_client:
            ai_answer = await self._get_ai_answer()
            if ai_answer:
                return ai_answer
        
        # Fallback to keyword detection
        if "hint" in self.game_state:
            answer = self.game_state["hint"]
            self.log(f"📝 Using keyword-based answer: {answer}")
            return answer
        
        # Ultimate fallback
        self.log("🎲 Using default answer")
        return "anthropic"
    
    async def _get_ai_answer(self) -> Optional[str]:
        """Use AI to answer based on clues"""
        try:
            # Build prompt with all clues
            prompt = "Answer this question based on the following clue(s):\n\n"
            for i, clue in enumerate(self.clues, 1):
                prompt += f"{i}. {clue}\n"
            prompt += "\nProvide only the answer (a single word or short phrase), nothing else."
            
            self.log("🤖 Asking AI...")
            
            response = self.ai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are excellent at solving riddles and answering trivia questions based on clues."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=50,
                temperature=0.7,
            )
            
            answer = response.choices[0].message.content.strip().lower()
            self.log(f"🤖 AI suggests: {answer}")
            return answer
            
        except Exception as e:
            self.log(f"⚠️ AI request failed: {e}")
            return None
    
    def on_game_ended(self, message: GameMessage):
        """Called when game ends"""
        self.log("✅ Cluedle game completed!")
        self.log(f"📊 Total clues received: {len(self.clues)}")
        if self.clues:
            self.log("📝 Clues were:")
            for i, clue in enumerate(self.clues, 1):
                self.log(f"  {i}. {clue}")


class AdvancedCluedleAgent(CluedleAgentV2):
    """
    Advanced version with better context building and reasoning.
    """
    
    def __init__(self, config: GameConfig):
        super().__init__(config, use_ai=True)
        self.previous_answers = []
    
    def on_game_started(self, message: GameMessage):
        super().on_game_started(message)
        self.previous_answers = []
    
    async def _get_ai_answer(self) -> Optional[str]:
        """Enhanced AI answering with more context"""
        try:
            # Build comprehensive prompt
            prompt_parts = [
                "You are solving a trivia question in a game called Cluedle.",
                "\nClues provided:",
            ]
            
            for i, clue in enumerate(self.clues, 1):
                prompt_parts.append(f"\n{i}. {clue}")
            
            if self.previous_answers:
                prompt_parts.append("\n\nNote: These answers were already tried:")
                for ans in self.previous_answers:
                    prompt_parts.append(f"- {ans}")
            
            prompt_parts.append("\n\nProvide your best answer (just the answer, nothing else):")
            
            prompt = "".join(prompt_parts)
            
            self.log("🤖 Asking AI with context...")
            
            response = self.ai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at trivia and riddles. Analyze clues carefully and provide accurate, concise answers."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=100,
                temperature=0.8,
            )
            
            answer = response.choices[0].message.content.strip().lower()
            
            # Clean up the answer
            answer = answer.replace("the answer is ", "")
            answer = answer.replace("answer:", "").strip()
            answer = answer.split()[0] if " " in answer else answer
            
            self.previous_answers.append(answer)
            self.log(f"🤖 AI answer: {answer}")
            
            return answer
            
        except Exception as e:
            self.log(f"⚠️ AI failed: {e}")
            return None
    
    def on_game_ended(self, message: GameMessage):
        super().on_game_ended(message)
        self.log(f"💭 Tried {len(self.previous_answers)} answer(s)")


# ==================== Main ====================

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("🧩 Cluedle Agent V2")
    print("=" * 60)
    print("1. Simple Cluedle Agent (keyword detection)")
    print("2. Simple Cluedle Agent (with AI)")
    print("3. Advanced Cluedle Agent (AI + context)")
    print("=" * 60)
    
    choice = input("Choose agent (1-3, default=2): ").strip() or "2"
    
    config = GameConfig(
        ws_url="ws://localhost:2025",
        connect_timeout=10,
        recv_timeout=2,
        keep_alive=True,
    )
    
    if choice == "1":
        agent = CluedleAgentV2(config, use_ai=False)
        print("📝 Running without AI (keyword detection only)")
    elif choice == "3":
        agent = AdvancedCluedleAgent(config)
        print("🚀 Running Advanced Agent (AI + context)")
    else:
        agent = CluedleAgentV2(config, use_ai=True)
        print("🤖 Running Simple Agent (with AI)")
    
    print("=" * 60)
    AgentRunner.run_agent(agent)
