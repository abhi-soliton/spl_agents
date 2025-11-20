"""
Game Agent Framework V2 - Enhanced Modular Design

Improvements:
- Simplified for non-Python developers
- Handles acknowledgments and metadata
- Supports different game types (Wordle, Cluedle, 2D Grid games, etc.)
- More flexible message handling
- Easy to extend without touching core code
"""

import asyncio
import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
from typing import Optional, Any, Dict, List, Callable

import websockets


# ==================== Enums ====================

class GameType(Enum):
    """Supported game types"""
    WORDLE = "wordle"
    CLUEDLE = "cluedle"
    GRID_2D = "grid_2d"
    CUSTOM = "custom"


class MessageType(Enum):
    """Types of messages from server"""
    ACK = "ack"                          # Acknowledgment message
    COMMAND = "command"                  # Command requiring response
    RESULT = "result"                    # Game result
    ERROR = "error"                      # Error message
    UNKNOWN = "unknown"                  # Unrecognized


class AckType(Enum):
    """Types of acknowledgments"""
    GAME_STARTED = "game started"
    META_DATA = "meta data"
    GUESS_RECEIVED = "guess received"
    MOVE_RECEIVED = "move received"
    UNKNOWN = "unknown"


# ==================== Data Classes ====================

@dataclass
class GameConfig:
    """Configuration for game connection"""
    ws_url: str
    connect_timeout: int = 10
    recv_timeout: int = 2
    keep_alive: bool = True
    max_reconnect_attempts: int = 3
    reconnect_delay: int = 5


@dataclass
class GameMessage:
    """Simplified message structure - works for all game types"""
    raw: str                              # Original JSON string
    match_id: Optional[str] = None        # Match identifier
    game_id: Optional[str] = None         # Game identifier
    your_id: Optional[str] = None         # Player identifier
    message_type: MessageType = MessageType.UNKNOWN
    
    # For acknowledgments
    ack_for: Optional[str] = None         # What is being acknowledged
    ack_data: Any = None                  # Additional data (clue, metadata, etc.)
    
    # For commands
    command: Optional[str] = None         # Command type (guess, move, etc.)
    
    # For results
    result: Optional[str] = None          # Win, loss, etc.
    answer: Optional[str] = None          # The correct answer
    
    # Game state data
    game_data: Dict[str, Any] = field(default_factory=dict)  # Flexible storage


@dataclass
class GameStats:
    """Statistics tracker"""
    games_played: int = 0
    games_won: int = 0
    games_lost: int = 0
    total_moves: int = 0
    current_game_moves: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


# ==================== Simple Game Agent Base ====================

class SimpleGameAgent(ABC):
    """
    Simplified base class for game agents.
    
    For non-Python developers: You only need to implement these methods:
    1. on_game_started() - Called when game starts
    2. on_clue_received() - Called when you get a clue/hint
    3. make_move() - Return your guess/move
    4. on_game_ended() - Called when game ends
    
    Everything else is handled automatically!
    """

    def __init__(self, config: GameConfig, game_type: GameType = GameType.CUSTOM):
        self.config = config
        self.game_type = game_type
        self.stats = GameStats()
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        
        # Current game state (accessible in all methods)
        self.match_id: Optional[str] = None
        self.game_id: Optional[str] = None
        self.your_id: Optional[str] = None
        self.clues: List[str] = []
        self.game_state: Dict[str, Any] = {}

    # ==================== Utility Methods ====================

    def log(self, message: str, emoji: str = "ℹ️"):
        """Simple logging"""
        timestamp = datetime.now(UTC).strftime("%H:%M:%S")
        print(f"[{timestamp}] {emoji} {message}")

    # ==================== Message Parsing (Simple) ====================

    def parse_message(self, msg: str) -> Optional[GameMessage]:
        """Parse JSON message into simple structure"""
        try:
            data = json.loads(msg)
        except json.JSONDecodeError:
            return None

        # Determine message type
        msg_type = MessageType.UNKNOWN
        if "type" in data:
            type_str = data["type"].lower()
            if type_str == "ack":
                msg_type = MessageType.ACK
            elif type_str == "result":
                msg_type = MessageType.RESULT
            elif type_str == "error":
                msg_type = MessageType.ERROR
        
        if "command" in data:
            msg_type = MessageType.COMMAND

        return GameMessage(
            raw=msg,
            match_id=data.get("matchId"),
            game_id=data.get("gameId"),
            your_id=data.get("yourId"),
            message_type=msg_type,
            ack_for=data.get("ackFor"),
            ack_data=data.get("ackData"),
            command=data.get("command"),
            result=data.get("result"),
            answer=data.get("word") or data.get("answer"),
            game_data=data,  # Store everything
        )

    # ==================== Message Handlers ====================

    def handle_acknowledgment(self, message: GameMessage):
        """Handle ACK messages"""
        self.log(f"Acknowledgment: {message.ack_for}")
        
        if message.ack_for == "game started":
            # New game started
            self.match_id = message.match_id
            self.game_id = message.game_id
            self.your_id = message.your_id
            self.clues = []
            self.game_state = {}
            self.stats.games_played += 1
            self.stats.current_game_moves = 0
            self.stats.start_time = datetime.now(UTC)
            
            self.log(f"🎮 Game started: {self.game_id}", "🎮")
            self.on_game_started(message)
        
        elif message.ack_for == "meta data":
            # Received clue or metadata
            if message.ack_data:
                self.clues.append(str(message.ack_data))
                self.log(f"🧩 Clue received: {message.ack_data}", "🧩")
                self.on_clue_received(message.ack_data, message)
        
        else:
            # Other acknowledgments
            self.on_acknowledgment(message)

    async def handle_command(self, message: GameMessage) -> Optional[Dict[str, Any]]:
        """Handle command messages that need responses"""
        self.log(f"Command received: {message.command}")
        
        # Get the move from the agent
        move = await self.make_move(message)
        
        if move:
            self.stats.current_game_moves += 1
            self.stats.total_moves += 1
            self.log(f"🧠 Move #{self.stats.current_game_moves}: {move}", "🧠")
        
        # Build the response
        response = self.build_response(message, move)
        return response

    def handle_result(self, message: GameMessage):
        """Handle game result"""
        self.stats.end_time = datetime.now(UTC)
        
        result = message.result or "unknown"
        answer = message.answer or "unknown"
        
        if result.lower() == "win":
            self.stats.games_won += 1
            self.log(f"🏆 YOU WON! Answer: {answer} | Moves: {self.stats.current_game_moves}", "🏆")
        elif result.lower() == "loss":
            self.stats.games_lost += 1
            self.log(f"❌ Game Over. Answer: {answer} | Moves: {self.stats.current_game_moves}", "❌")
        else:
            self.log(f"🎯 Game Result: {result} | Answer: {answer}", "🎯")
        
        self.on_game_ended(message)
        self.print_stats()

    # ==================== Methods to Override ====================

    @abstractmethod
    def on_game_started(self, message: GameMessage):
        """
        Called when a new game starts.
        
        Simple example:
            def on_game_started(self, message):
                self.log("Let's play!")
        """
        pass

    @abstractmethod
    def on_clue_received(self, clue: str, message: GameMessage):
        """
        Called when you receive a clue or hint.
        
        Simple example:
            def on_clue_received(self, clue, message):
                self.log(f"Got clue: {clue}")
                # Think about the clue...
        """
        pass

    @abstractmethod
    async def make_move(self, message: GameMessage) -> Optional[Any]:
        """
        Return your guess/move based on the current game state.
        
        Simple example:
            async def make_move(self, message):
                return "anthropic"  # Your guess
        
        You have access to:
        - self.clues (list of all clues received)
        - self.game_state (store anything you want)
        - message.game_data (all data from server)
        """
        pass

    @abstractmethod
    def on_game_ended(self, message: GameMessage):
        """
        Called when the game ends.
        
        Simple example:
            def on_game_ended(self, message):
                self.log("Game finished!")
        """
        pass

    # ==================== Optional Hooks ====================

    def on_acknowledgment(self, message: GameMessage):
        """Override to handle other acknowledgments"""
        pass

    def on_connected(self):
        """Override to handle connection events"""
        pass

    def on_disconnected(self):
        """Override to handle disconnection"""
        pass

    def on_error(self, message: GameMessage):
        """Override to handle errors"""
        self.log(f"Error: {message.game_data}", "🚨")

    # ==================== Response Builder ====================

    def build_response(self, message: GameMessage, move: Optional[Any]) -> Optional[Dict[str, Any]]:
        """
        Build response to send to server.
        Override this if your game has a different response format.
        
        Default format works for most games:
        {
            "matchId": "...",
            "gameId": "...",
            "otp": "...",
            "guess": "your_move"
        }
        """
        if not move:
            return None

        return {
            "matchId": self.match_id or message.match_id,
            "gameId": self.game_id or message.game_id,
            "otp": message.game_data.get("otp"),
            "guess": str(move),
        }

    # ==================== Main Loop ====================

    async def handle_message(self, message: GameMessage) -> Optional[Dict[str, Any]]:
        """Route messages to appropriate handlers"""
        if message.message_type == MessageType.ACK:
            self.handle_acknowledgment(message)
            return None
        
        elif message.message_type == MessageType.COMMAND:
            return await self.handle_command(message)
        
        elif message.message_type == MessageType.RESULT:
            self.handle_result(message)
            return None
        
        elif message.message_type == MessageType.ERROR:
            self.on_error(message)
            return None
        
        return None

    async def run_loop(self):
        """Main game loop"""
        self.log(f"👂 Listening for messages...")
        
        while self._ws and not self._ws.closed:
            try:
                msg = await asyncio.wait_for(
                    self._ws.recv(),
                    timeout=self.config.recv_timeout
                )
                
                parsed = self.parse_message(msg)
                if not parsed:
                    self.log("⚠️ Invalid message received", "⚠️")
                    continue

                response = await self.handle_message(parsed)
                
                if response:
                    await self._ws.send(json.dumps(response))

            except asyncio.TimeoutError:
                if self.config.keep_alive:
                    continue
                self.log("⏹️ No messages, closing connection", "⏹️")
                break
                
            except websockets.exceptions.ConnectionClosedOK:
                self.log("Connection closed by server", "🔒")
                break
                
            except websockets.exceptions.ConnectionClosedError as e:
                self.log(f"Connection error: {e}", "❌")
                break
                
            except Exception as e:
                self.log(f"Unexpected error: {e}", "🚨")
                break

    async def connect_and_run(self):
        """Connect to server and start game loop"""
        attempt = 0
        while attempt < self.config.max_reconnect_attempts:
            try:
                self.log(f"🔌 Connecting to {self.config.ws_url} (attempt {attempt + 1})")
                
                async with websockets.connect(
                    self.config.ws_url,
                    open_timeout=self.config.connect_timeout
                ) as ws:
                    self._ws = ws
                    self.log("✅ Connected!", "✅")
                    self.on_connected()
                    
                    await self.run_loop()
                    break
                    
            except Exception as e:
                self.log(f"Connection failed: {e}", "❌")
                attempt += 1
                if attempt < self.config.max_reconnect_attempts:
                    self.log(f"⏳ Retrying in {self.config.reconnect_delay}s...")
                    await asyncio.sleep(self.config.reconnect_delay)
        
        self.on_disconnected()

    def print_stats(self):
        """Print game statistics"""
        if self.stats.games_played == 0:
            return
        
        win_rate = (self.stats.games_won / self.stats.games_played * 100)
        avg_moves = (self.stats.total_moves / self.stats.games_played)
        
        self.log("=" * 50, "📊")
        self.log(f"Games Played: {self.stats.games_played}", "📊")
        self.log(f"Games Won: {self.stats.games_won}", "📊")
        self.log(f"Games Lost: {self.stats.games_lost}", "📊")
        self.log(f"Win Rate: {win_rate:.1f}%", "📊")
        self.log(f"Total Moves: {self.stats.total_moves}", "📊")
        self.log(f"Avg Moves/Game: {avg_moves:.1f}", "📊")
        self.log("=" * 50, "📊")


# ==================== Simple Runner ====================

class AgentRunner:
    """Simple runner for agents"""
    
    def __init__(self, agent: SimpleGameAgent):
        self.agent = agent

    async def run(self):
        """Run the agent"""
        try:
            await self.agent.connect_and_run()
        except KeyboardInterrupt:
            self.agent.log("⏹️ Stopped by user", "⏹️")
        except Exception as e:
            self.agent.log(f"Runner error: {e}", "🚨")
        finally:
            self.agent.print_stats()

    @staticmethod
    def run_agent(agent: SimpleGameAgent):
        """Convenience method to run with asyncio"""
        runner = AgentRunner(agent)
        asyncio.run(runner.run())


# ==================== Example: Simple Cluedle Agent ====================

if __name__ == "__main__":
    
    class MyCluedleAgent(SimpleGameAgent):
        """
        Example Cluedle agent - SUPER SIMPLE!
        Just 4 methods to implement.
        """
        
        def __init__(self, config: GameConfig):
            super().__init__(config, GameType.CLUEDLE)
            self.my_notes = []  # Store anything you want
        
        def on_game_started(self, message: GameMessage):
            """Game started - reset state"""
            self.log("🎮 New Cluedle game!")
            self.my_notes = []
        
        def on_clue_received(self, clue: str, message: GameMessage):
            """Got a clue - think about it"""
            self.log(f"🤔 Thinking about clue: {clue}")
            self.my_notes.append(f"Clue says: {clue}")
            
            # You can analyze the clue here
            if "AI company" in clue and "Claude" in clue:
                self.game_state["answer_hint"] = "anthropic"
        
        async def make_move(self, message: GameMessage) -> Optional[Any]:
            """Return your guess"""
            # Access all your data:
            # - self.clues (all clues)
            # - self.game_state (your storage)
            # - self.my_notes (custom storage)
            
            if "answer_hint" in self.game_state:
                return self.game_state["answer_hint"]
            
            return "anthropic"  # Default guess
        
        def on_game_ended(self, message: GameMessage):
            """Game ended"""
            self.log("Game finished!")
            self.log(f"Notes I took: {self.my_notes}")
    
    # Run it!
    config = GameConfig(ws_url="ws://localhost:2025")
    agent = MyCluedleAgent(config)
    
    print("=" * 60)
    print("🧩 Simple Cluedle Agent")
    print("=" * 60)
    AgentRunner.run_agent(agent)
