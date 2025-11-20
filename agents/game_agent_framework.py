"""
Game Agent Framework - Modular Template for Wordle and other games

This framework provides:
- Base agent class with connection and message handling
- Agent runner for game lifecycle management
- Enums for game states, commands, and result types
- Extensible architecture for different game types
"""

import asyncio
import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, UTC
from enum import Enum
from typing import Optional, Any, Dict, List

import websockets


# ==================== Enums ====================

class GameType(Enum):
    """Supported game types"""
    WORDLE = "wordle"
    CUSTOM = "custom"


class MessageType(Enum):
    """Types of messages received from the server"""
    GAME_START = "game start"
    GAME_RESULT = "game result"
    COMMAND = "command"
    ACKNOWLEDGEMENT = "acknowledgement"
    ERROR = "error"
    UNKNOWN = "unknown"


class GameCommand(Enum):
    """Commands that require agent response"""
    GUESS = "guess"
    SOLVE = "solve"
    HINT = "hint"
    UNKNOWN = "unknown"


class GameResult(Enum):
    """Possible game outcomes"""
    WIN = "win"
    LOSS = "loss"
    TIMEOUT = "timeout"
    ERROR = "error"
    ABANDONED = "abandoned"
    UNKNOWN = "unknown"


class AgentState(Enum):
    """Agent lifecycle states"""
    IDLE = "idle"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    PLAYING = "playing"
    GAME_OVER = "game_over"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class FeedbackType(Enum):
    """Feedback types for guesses (Wordle-style)"""
    CORRECT = "correct"
    PRESENT = "present"
    ABSENT = "absent"


# ==================== Data Classes ====================

@dataclass
class GameConfig:
    """Configuration for a game session"""
    ws_url: str
    connect_timeout: int = 10
    recv_timeout: int = 2
    keep_alive: bool = True
    max_reconnect_attempts: int = 3
    reconnect_delay: int = 5


@dataclass
class ParsedMessage:
    """Standardized message structure from server"""
    raw: str
    type: MessageType
    command: Optional[GameCommand]
    match_id: Optional[str]
    game_id: Optional[str]
    your_id: Optional[str]
    otp: Optional[str]
    word_length: Optional[int]
    max_attempts: Optional[int]
    last_guess: str
    last_result: List[str]
    current_attempt: Optional[int]
    result: Optional[GameResult]
    word: Optional[str]
    metadata: Dict[str, Any]  # For game-specific data


@dataclass
class GameStats:
    """Statistics for the current game session"""
    games_played: int = 0
    games_won: int = 0
    games_lost: int = 0
    total_guesses: int = 0
    current_game_guesses: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


# ==================== Base Agent ====================

class BaseGameAgent(ABC):
    """
    Base class for all game agents.
    Handles connection, message parsing, and game lifecycle.
    Subclasses implement game-specific logic.
    """

    def __init__(self, config: GameConfig, game_type: GameType, reusable: bool = False):
        self.config = config
        self.game_type = game_type
        self.reusable = reusable
        self.state = AgentState.IDLE
        self.stats = GameStats()
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self.current_game_id: Optional[str] = None

    # ==================== Utility Methods ====================

    def ts(self) -> str:
        """Return a short UTC timestamp for log lines"""
        return datetime.now(UTC).strftime("%H:%M:%S")

    def log(self, message: str, emoji: str = "ℹ️"):
        """Consistent logging format"""
        print(f"[{self.ts()}] {emoji} {message}")

    # ==================== Message Parsing ====================

    def parse_message(self, msg: str) -> Optional[ParsedMessage]:
        """Parse incoming JSON message into ParsedMessage"""
        try:
            obj = json.loads(msg)
        except json.JSONDecodeError:
            return None

        # Determine message type
        msg_type = self._parse_message_type(obj.get("type"))
        
        # Determine command type
        command = self._parse_command(obj.get("command"))
        
        # Determine result type
        result = self._parse_result(obj.get("result"))

        # Parse feedback/result list
        last_guess = obj.get("lastGuess", "")
        raw_result = obj.get("lastResult", [])
        normalized_result = self._normalize_feedback(raw_result) if isinstance(raw_result, list) else []

        return ParsedMessage(
            raw=msg,
            type=msg_type,
            command=command,
            match_id=obj.get("matchId"),
            game_id=obj.get("gameId"),
            your_id=obj.get("yourId"),
            otp=obj.get("otp"),
            word_length=obj.get("wordLength"),
            max_attempts=obj.get("maxAttempts"),
            last_guess=last_guess,
            last_result=normalized_result,
            current_attempt=obj.get("currentAttempt"),
            result=result,
            word=obj.get("word"),
            metadata=obj  # Store full object for game-specific needs
        )

    def _parse_message_type(self, type_str: Optional[str]) -> MessageType:
        """Parse message type from string"""
        if not type_str:
            return MessageType.UNKNOWN
        
        type_map = {
            "game start": MessageType.GAME_START,
            "game result": MessageType.GAME_RESULT,
            "command": MessageType.COMMAND,
            "acknowledgement": MessageType.ACKNOWLEDGEMENT,
            "error": MessageType.ERROR,
        }
        return type_map.get(type_str.lower(), MessageType.UNKNOWN)

    def _parse_command(self, command_str: Optional[str]) -> Optional[GameCommand]:
        """Parse command type from string"""
        if not command_str:
            return None
        
        command_map = {
            "guess": GameCommand.GUESS,
            "solve": GameCommand.SOLVE,
            "hint": GameCommand.HINT,
        }
        return command_map.get(command_str.lower(), GameCommand.UNKNOWN)

    def _parse_result(self, result_str: Optional[str]) -> Optional[GameResult]:
        """Parse game result from string"""
        if not result_str:
            return None
        
        result_map = {
            "win": GameResult.WIN,
            "loss": GameResult.LOSS,
            "timeout": GameResult.TIMEOUT,
            "error": GameResult.ERROR,
            "abandoned": GameResult.ABANDONED,
        }
        return result_map.get(result_str.lower(), GameResult.UNKNOWN)

    def _normalize_feedback(self, feedback: List[str]) -> List[str]:
        """Normalize feedback tokens to standard format"""
        normalized = []
        for token in feedback:
            cleaned = str(token).strip().lower()
            if cleaned in {"correct", "green", "g"}:
                normalized.append(FeedbackType.CORRECT.value)
            elif cleaned in {"present", "yellow", "y"}:
                normalized.append(FeedbackType.PRESENT.value)
            else:
                normalized.append(FeedbackType.ABSENT.value)
        return normalized

    # ==================== Game Lifecycle Handlers ====================

    def handle_game_start(self, parsed: ParsedMessage):
        """Handle game start event"""
        self.current_game_id = parsed.game_id
        self.state = AgentState.PLAYING
        self.stats.games_played += 1
        self.stats.current_game_guesses = 0
        self.stats.start_time = datetime.now(UTC)
        
        self.log(f"🎮 Game started - ID: {parsed.game_id}, Word Length: {parsed.word_length}, Max Attempts: {parsed.max_attempts}")
        self.on_game_start(parsed)

    def handle_game_result(self, parsed: ParsedMessage):
        """Handle game result event"""
        self.state = AgentState.GAME_OVER if not self.reusable else AgentState.IDLE
        self.stats.end_time = datetime.now(UTC)
        
        if parsed.result == GameResult.WIN:
            self.stats.games_won += 1
            self.log(f"🎯 Game WON! Word: {parsed.word} | Guesses: {self.stats.current_game_guesses}", "🏆")
        elif parsed.result == GameResult.LOSS:
            self.stats.games_lost += 1
            self.log(f"💔 Game LOST! Word: {parsed.word} | Guesses: {self.stats.current_game_guesses}", "❌")
        else:
            self.log(f"🎯 Game Result: {parsed.result.value if parsed.result else 'unknown'} | Word: {parsed.word}")
        
        # Calculate game duration
        if self.stats.start_time and self.stats.end_time:
            duration = (self.stats.end_time - self.stats.start_time).total_seconds()
            self.log(f"⏱️ Game duration: {duration:.2f}s")
        
        self.on_game_result(parsed)
        self.print_stats()
        
        # Reset current game ID if not reusable
        if not self.reusable:
            self.current_game_id = None

    def handle_acknowledgement(self, parsed: ParsedMessage):
        """Handle acknowledgement messages"""
        self.log(f"✅ Acknowledgement received", "📨")
        self.on_acknowledgement(parsed)

    def handle_error(self, parsed: ParsedMessage):
        """Handle error messages"""
        self.state = AgentState.ERROR
        self.log(f"⚠️ Error received from server", "🚨")
        self.on_error(parsed)

    # ==================== Abstract Methods (implement in subclasses) ====================

    @abstractmethod
    async def make_move(self, parsed: ParsedMessage) -> Optional[str]:
        """
        Generate the next move/guess based on the current game state.
        This is the core game logic that must be implemented by each agent.
        
        Args:
            parsed: The parsed message containing game state
            
        Returns:
            The move/guess as a string, or None if no move can be made
        """
        pass

    @abstractmethod
    def build_response(self, parsed: ParsedMessage, move: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Build the response JSON to send back to the server.
        
        Args:
            parsed: The parsed message
            move: The move/guess generated by make_move()
            
        Returns:
            Dictionary to be sent as JSON, or None if no response needed
        """
        pass

    # ==================== Optional Hooks (override in subclasses if needed) ====================

    def on_game_start(self, parsed: ParsedMessage):
        """Hook called when game starts (optional override)"""
        pass

    def on_game_result(self, parsed: ParsedMessage):
        """Hook called when game ends (optional override)"""
        pass

    def on_acknowledgement(self, parsed: ParsedMessage):
        """Hook called on acknowledgement (optional override)"""
        pass

    def on_error(self, parsed: ParsedMessage):
        """Hook called on error (optional override)"""
        pass

    def on_connected(self):
        """Hook called when connection is established (optional override)"""
        pass

    def on_disconnected(self):
        """Hook called when connection is closed (optional override)"""
        pass

    # ==================== Main Message Handler ====================

    async def handle_message(self, parsed: ParsedMessage) -> Optional[Dict[str, Any]]:
        """
        Main message router - delegates to appropriate handler.
        Returns response dict if a reply is needed.
        """
        # Handle different message types
        if parsed.type == MessageType.GAME_START:
            self.handle_game_start(parsed)
            return None

        if parsed.type == MessageType.GAME_RESULT:
            self.handle_game_result(parsed)
            return None

        if parsed.type == MessageType.ACKNOWLEDGEMENT:
            self.handle_acknowledgement(parsed)
            return None

        if parsed.type == MessageType.ERROR:
            self.handle_error(parsed)
            return None

        # Handle commands that need responses
        if parsed.command in [GameCommand.GUESS, GameCommand.SOLVE]:
            move = await self.make_move(parsed)
            if move:
                self.stats.current_game_guesses += 1
                self.stats.total_guesses += 1
                self.log(f"🧠 Move #{self.stats.current_game_guesses}: {move}")
            
            response = self.build_response(parsed, move)
            return response

        return None

    # ==================== Connection Management ====================

    async def connect_and_run(self):
        """Main entry point - connect and start the game loop"""
        attempt = 0
        while attempt < self.config.max_reconnect_attempts:
            try:
                self.state = AgentState.CONNECTING
                self.log(f"🔌 Connecting to {self.config.ws_url} (attempt {attempt + 1}/{self.config.max_reconnect_attempts})")
                
                async with websockets.connect(
                    self.config.ws_url,
                    open_timeout=self.config.connect_timeout
                ) as ws:
                    self._ws = ws
                    self.state = AgentState.CONNECTED
                    self.log("✅ Connection established")
                    self.on_connected()
                    
                    await self.run_loop()
                    
                    # If we exit normally, no need to retry
                    break
                    
            except websockets.exceptions.WebSocketException as e:
                self.log(f"❌ WebSocket error: {e}", "🔴")
                attempt += 1
                if attempt < self.config.max_reconnect_attempts:
                    self.log(f"⏳ Retrying in {self.config.reconnect_delay}s...")
                    await asyncio.sleep(self.config.reconnect_delay)
            except Exception as e:
                self.log(f"❌ Unexpected error: {e}", "🔴")
                break
        
        self.state = AgentState.DISCONNECTED
        self.on_disconnected()
        self.log("🔌 Disconnected")

    async def run_loop(self):
        """Main game loop - listen for messages and respond"""
        self.log(f"👂 Listening for messages (timeout={self.config.recv_timeout}s)")
        
        while self._ws:
            try:
                msg = await asyncio.wait_for(
                    self._ws.recv(),
                    timeout=self.config.recv_timeout
                )
                
                parsed = self.parse_message(msg)
                if parsed is None:
                    self.log("⚠️ Received non-JSON message; ignoring")
                    continue

                response = await self.handle_message(parsed)
                
                if response:
                    await self._ws.send(json.dumps(response))
                    # self.log(f"📤 Sent response")

            except asyncio.TimeoutError:
                if self.config.keep_alive:
                    continue
                self.log(f"⏹️ No messages within {self.config.recv_timeout}s; closing")
                break
                
            except websockets.exceptions.ConnectionClosedOK:
                self.log("🔒 Connection closed by server (OK)")
                break
                
            except websockets.exceptions.ConnectionClosedError as e:
                self.log(f"❌ Connection closed with error: {e}")
                break
                
            except Exception as e:
                self.log(f"⚠️ Unexpected error in game loop: {e}", "🚨")
                break

    # ==================== Statistics ====================

    def print_stats(self):
        """Print current game statistics"""
        win_rate = (self.stats.games_won / self.stats.games_played * 100) if self.stats.games_played > 0 else 0
        avg_guesses = (self.stats.total_guesses / self.stats.games_played) if self.stats.games_played > 0 else 0
        
        self.log("=" * 50, "📊")
        self.log(f"Games Played: {self.stats.games_played}", "📊")
        self.log(f"Games Won: {self.stats.games_won}", "📊")
        self.log(f"Games Lost: {self.stats.games_lost}", "📊")
        self.log(f"Win Rate: {win_rate:.1f}%", "📊")
        self.log(f"Total Guesses: {self.stats.total_guesses}", "📊")
        self.log(f"Avg Guesses/Game: {avg_guesses:.1f}", "📊")
        self.log("=" * 50, "📊")


# ==================== Agent Runner ====================

class AgentRunner:
    """
    Manages agent lifecycle and provides utilities for running agents.
    Supports multiple game sessions over a single TCP connection.
    When reusable=False, creates a new agent instance for each game ID.
    """

    def __init__(self, agent_factory: callable, reusable: bool = False):
        """
        Args:
            agent_factory: A callable that returns a new BaseGameAgent instance
            reusable: If False, create new agent for each game ID. If True, reuse agents.
        """
        self.agent_factory = agent_factory
        self.reusable = reusable
        self.agents: Dict[str, BaseGameAgent] = {}  # game_id -> agent
        self.primary_agent: Optional[BaseGameAgent] = None
        self._ws: Optional[websockets.WebSocketClientProtocol] = None

    def ts(self) -> str:
        """Return a short UTC timestamp for log lines"""
        return datetime.now(UTC).strftime("%H:%M:%S")

    def log(self, message: str, emoji: str = "ℹ️"):
        """Consistent logging format"""
        print(f"[{self.ts()}] {emoji} {message}")

    def get_or_create_agent(self, game_id: Optional[str]) -> BaseGameAgent:
        """
        Get existing agent for game_id or create a new one.
        
        Args:
            game_id: The game ID from the message
            
        Returns:
            Agent instance for this game
        """
        # If reusable or no game_id, use/create primary agent
        if self.reusable or game_id is None:
            if self.primary_agent is None:
                self.primary_agent = self.agent_factory()
                self.primary_agent._ws = self._ws
                self.log(f"🤖 Created primary agent (reusable={self.reusable})")
            return self.primary_agent
        
        # Create new agent per game ID
        if game_id not in self.agents:
            agent = self.agent_factory()
            agent._ws = self._ws
            self.agents[game_id] = agent
            self.log(f"🤖 Created new agent for game ID: {game_id}")
        
        return self.agents[game_id]

    async def run(self):
        """Run the agent runner with multi-game support"""
        config = self.agent_factory().config  # Get config from factory
        attempt = 0
        
        while attempt < config.max_reconnect_attempts:
            try:
                self.log(f"🔌 Connecting to {config.ws_url} (attempt {attempt + 1}/{config.max_reconnect_attempts})")
                
                async with websockets.connect(
                    config.ws_url,
                    open_timeout=config.connect_timeout
                ) as ws:
                    self._ws = ws
                    self.log("✅ Connection established")
                    
                    await self.run_loop(config)
                    
                    # If we exit normally, no need to retry
                    break
                    
            except websockets.exceptions.WebSocketException as e:
                self.log(f"❌ WebSocket error: {e}", "🔴")
                attempt += 1
                if attempt < config.max_reconnect_attempts:
                    self.log(f"⏳ Retrying in {config.reconnect_delay}s...")
                    await asyncio.sleep(config.reconnect_delay)
            except Exception as e:
                self.log(f"❌ Unexpected error: {e}", "🔴")
                break
        
        self.log("🔌 Disconnected")
        self.print_all_stats()

    async def run_loop(self, config: GameConfig):
        """Main game loop - routes messages to appropriate agents"""
        self.log(f"👂 Listening for messages (timeout={config.recv_timeout}s)")
        
        while self._ws:
            try:
                msg = await asyncio.wait_for(
                    self._ws.recv(),
                    timeout=config.recv_timeout
                )
                
                # Parse message to determine game_id
                try:
                    obj = json.loads(msg)
                    game_id = obj.get("gameId")
                except json.JSONDecodeError:
                    self.log("⚠️ Received non-JSON message; ignoring")
                    continue
                
                # Get or create agent for this game
                agent = self.get_or_create_agent(game_id)
                
                # Parse and handle message
                parsed = agent.parse_message(msg)
                if parsed is None:
                    self.log("⚠️ Failed to parse message; ignoring")
                    continue

                response = await agent.handle_message(parsed)
                
                if response:
                    await self._ws.send(json.dumps(response))

            except asyncio.TimeoutError:
                if config.keep_alive:
                    continue
                self.log(f"⏹️ No messages within {config.recv_timeout}s; closing")
                break
                
            except websockets.exceptions.ConnectionClosedOK:
                self.log("🔒 Connection closed by server (OK)")
                break
                
            except websockets.exceptions.ConnectionClosedError as e:
                self.log(f"❌ Connection closed with error: {e}")
                break
                
            except Exception as e:
                self.log(f"⚠️ Unexpected error in game loop: {e}", "🚨")
                import traceback
                traceback.print_exc()
                break

    def print_all_stats(self):
        """Print statistics for all agents"""
        if self.primary_agent:
            self.log("📊 Primary Agent Stats:")
            self.primary_agent.print_stats()
        
        if self.agents:
            self.log(f"📊 Game-specific Agents: {len(self.agents)} total")
            for game_id, agent in self.agents.items():
                self.log(f"📊 Stats for Game ID: {game_id}")
                agent.print_stats()

    @staticmethod
    def run_agent(agent_factory: callable, reusable: bool = False):
        """Convenience method to run an agent with asyncio"""
        runner = AgentRunner(agent_factory, reusable=reusable)
        try:
            asyncio.run(runner.run())
        except KeyboardInterrupt:
            runner.log("⚠️ Interrupted by user", "⏹️")
        except Exception as e:
            runner.log(f"❌ Runner error: {e}", "🔴")
            import traceback
            traceback.print_exc()


# ==================== Example Usage ====================

if __name__ == "__main__":
    # This is just for demonstration - actual agents should be in separate files
    
    class SimpleWordleAgent(BaseGameAgent):
        """Example Wordle agent implementation"""
        
        def __init__(self, config: GameConfig):
            super().__init__(config, GameType.WORDLE)
            self.alphabet = "abcdefghijklmnopqrstuvwxyz"
        
        async def make_move(self, parsed: ParsedMessage) -> Optional[str]:
            """Simple strategy: just use alphabet letters"""
            length = parsed.word_length or 5
            return self.alphabet[:length]
        
        def build_response(self, parsed: ParsedMessage, move: Optional[str]) -> Optional[Dict[str, Any]]:
            """Build standard Wordle response"""
            if not move or not parsed.match_id or not parsed.game_id or not parsed.otp:
                return None
            
            return {
                "matchId": parsed.match_id,
                "gameId": parsed.game_id,
                "otp": parsed.otp,
                "guess": move,
            }
    
    # Example usage
    config = GameConfig(
        ws_url="ws://localhost:2025",
        connect_timeout=10,
        recv_timeout=2,
        keep_alive=True,
    )
    
    # Option 1: Single agent handles all games (reusable=True)
    # AgentRunner.run_agent(lambda: SimpleWordleAgent(config), reusable=True)
    
    # Option 2: New agent for each game ID (reusable=False, default)
    AgentRunner.run_agent(lambda: SimpleWordleAgent(config), reusable=False)
