import json
import logging
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from queue import Queue
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.font as tkfont
from typing import List, Dict, Tuple

# Logging setup
LOG_FILE = Path.home() / '.snake_game.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('snake_game')


class ProfessionalTheme:
    """Professional dark theme with vibrant colors"""

    COLORS = {
        'primary': '#0f0f23',
        'secondary': '#1a1a2e',
        'accent': '#16213e',
        'board_light': '#2d4059',
        'board_dark': '#222831',
        'text_primary': '#ffffff',
        'text_secondary': '#b0b0b0',
        'success': '#00b894',
        'warning': '#fdcb6e',
        'danger': '#e84393',
        'info': '#74b9ff'
    }

    PLAYER_COLORS = {
        0: {'primary': '#ff6b6b', 'secondary': '#ff5252', 'name': 'Red'},  # Red Player
        1: {'primary': '#4ecdc4', 'secondary': '#00cec9', 'name': 'Teal'},  # Teal Player
        2: {'primary': '#ffe66d', 'secondary': '#ffd32a', 'name': 'Yellow'},  # Yellow Player
        3: {'primary': '#a29bfe', 'secondary': '#6c5ce7', 'name': 'Purple'}  # Purple Player
    }


class GameConfig:
    """Game configuration"""
    BOARD_SIZE = 100
    SNAKES = {
        16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 64: 60,
        87: 24, 93: 73, 95: 75, 98: 78
    }
    LADDERS = {
        1: 38, 4: 14, 9: 31, 21: 42, 28: 84, 36: 44,
        51: 67, 71: 91, 80: 100
    }
    MAX_PLAYERS = 4
    MAX_TURNS = 100


@dataclass
class Player:
    """Player class"""
    name: str
    position: int = 0
    turns: int = 0
    snakes_bitten: int = 0
    ladders_climbed: int = 0
    total_moves: int = 0
    player_id: int = 0

    def to_dict(self):
        return asdict(self)


class GameState:
    """Game state management"""

    def __init__(self):
        self.players: List[Player] = []
        self.current_player_index = 0
        self.game_started = False
        self.game_over = False
        self.winner = None
        self.move_history = []
        self.start_time = None

    def add_player(self, name: str, player_id: int):
        """Add new player"""
        self.players.append(Player(name, player_id=player_id))
        logger.info(f"Player added: {name}")

    def next_turn(self):
        """Move to next player's turn"""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def get_current_player(self) -> Player:
        """Get current player"""
        return self.players[self.current_player_index]

    def save_game(self, filename: str):
        """Save game state (IO Bound)"""
        try:
            data = {
                'players': [p.to_dict() for p in self.players],
                'current_player_index': self.current_player_index,
                'game_started': self.game_started,
                'game_over': self.game_over,
                'winner': self.winner,
                'move_history': self.move_history,
                'saved_at': datetime.now().isoformat()
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Game saved: {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving game: {e}")
            return False

    def load_game(self, filename: str):
        """Load game state (IO Bound)"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.players = [Player(**p) for p in data['players']]
            self.current_player_index = data['current_player_index']
            self.game_started = data['game_started']
            self.game_over = data['game_over']
            self.winner = data['winner']
            self.move_history = data['move_history']
            logger.info(f"Game loaded: {filename}")
            return True
        except Exception as e:
            logger.error(f"Error loading game: {e}")
            return False


class GameEngine:
    """Core game engine"""

    def __init__(self):
        self.config = GameConfig()
        self.state = GameState()
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.process_pool = ProcessPoolExecutor(max_workers=2)

    def calculate_move(self, player: Player, dice_roll: int) -> Dict:
        """Calculate player move (CPU Bound)"""
        start_pos = player.position
        new_pos = start_pos + dice_roll
        player.total_moves += dice_roll

        # Check for win
        if new_pos >= self.config.BOARD_SIZE:
            player.position = self.config.BOARD_SIZE
            return {
                'type': 'win',
                'start_pos': start_pos,
                'end_pos': self.config.BOARD_SIZE,
                'dice_roll': dice_roll,
                'player_id': player.player_id
            }

        # Check for snake
        if new_pos in self.config.SNAKES:
            end_pos = self.config.SNAKES[new_pos]
            player.snakes_bitten += 1
            player.position = end_pos
            return {
                'type': 'snake',
                'start_pos': start_pos,
                'snake_pos': new_pos,
                'end_pos': end_pos,
                'dice_roll': dice_roll,
                'player_id': player.player_id
            }

        # Check for ladder
        if new_pos in self.config.LADDERS:
            end_pos = self.config.LADDERS[new_pos]
            player.ladders_climbed += 1
            player.position = end_pos
            return {
                'type': 'ladder',
                'start_pos': start_pos,
                'ladder_pos': new_pos,
                'end_pos': end_pos,
                'dice_roll': dice_roll,
                'player_id': player.player_id
            }

        # Normal move
        player.position = new_pos
        return {
            'type': 'normal',
            'start_pos': start_pos,
            'end_pos': new_pos,
            'dice_roll': dice_roll,
            'player_id': player.player_id
        }

    def heavy_analysis(self, game_data: Dict) -> Dict:
        """Heavy game analysis (CPU Bound)"""
        # Simulate complex computations
        positions = [p['position'] for p in game_data['players']]
        moves = game_data['moves']

        # Complex statistical calculations
        total_score = 0
        for pos in positions:
            for move in moves:
                # Heavy computations
                for _ in range(1000):
                    total_score = (total_score * 31 + pos + move.get('dice_roll', 0)) & 0xFFFFFFFF

        # Calculate player rankings
        players_sorted = sorted(game_data['players'], key=lambda x: x['position'], reverse=True)
        rankings = {p['player_id']: i + 1 for i, p in enumerate(players_sorted)}

        analysis_result = {
            'total_score': total_score % 1000000,
            'average_position': sum(positions) / len(positions),
            'move_count': len(moves),
            'player_rankings': rankings,
            'analysis_time': time.time()
        }

        logger.info(f"Game analysis completed: {analysis_result}")
        return analysis_result


class AnimatedGameBoard(tk.Canvas):
    """Animated game board with beautiful graphics"""

    def __init__(self, parent, theme: ProfessionalTheme, size=650):
        super().__init__(parent, width=size, height=size, bg=theme.COLORS['primary'],
                         highlightthickness=0)
        self.theme = theme
        self.size = size
        self.cell_size = size // 10
        self.animations = []
        self.initialize_board()

    def initialize_board(self):
        """Draw the game board"""
        self.delete("all")

        # Draw board cells with gradient effect
        for i in range(100):
            row = 9 - (i // 10)
            col = i % 10 if row % 2 == 0 else 9 - (i % 10)

            x1 = col * self.cell_size
            y1 = row * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size

            # Alternating colors with gradient
            base_color = self.theme.COLORS['board_light'] if (i // 10 + i % 10) % 2 == 0 else self.theme.COLORS[
                'board_dark']

            self.create_rectangle(x1, y1, x2, y2, fill=base_color,
                                  outline=self.theme.COLORS['accent'], width=1)

            # Cell number
            self.create_text(x1 + self.cell_size // 2, y1 + self.cell_size // 2,
                             text=str(i + 1), fill=self.theme.COLORS['text_secondary'],
                             font=('Arial', 8, 'bold'))

        # Draw snakes and ladders
        self.draw_snakes_and_ladders()

        # Draw start and finish
        self.draw_special_cells()

    def draw_special_cells(self):
        """Draw start and finish cells"""
        # Start cell (1)
        start_pos = self.get_cell_center(1)
        self.create_oval(start_pos[0] - 15, start_pos[1] - 15, start_pos[0] + 15, start_pos[1] + 15,
                         fill=self.theme.COLORS['success'], outline='white', width=2)
        self.create_text(start_pos[0], start_pos[1], text="START", fill='white',
                         font=('Arial', 7, 'bold'))

        # Finish cell (100)
        finish_pos = self.get_cell_center(100)
        self.create_oval(finish_pos[0] - 15, finish_pos[1] - 15, finish_pos[0] + 15, finish_pos[1] + 15,
                         fill=self.theme.COLORS['danger'], outline='white', width=2)
        self.create_text(finish_pos[0], finish_pos[1], text="GOAL", fill='white',
                         font=('Arial', 7, 'bold'))

    def draw_snakes_and_ladders(self):
        """Draw snakes and ladders with beautiful styling"""
        # Ladders (green)
        for start, end in GameConfig.LADDERS.items():
            self.draw_ladder(start, end)

        # Snakes (red)
        for start, end in GameConfig.SNAKES.items():
            self.draw_snake(start, end)

    def draw_ladder(self, start: int, end: int):
        """Draw a ladder"""
        start_pos = self.get_cell_center(start)
        end_pos = self.get_cell_center(end)

        # Ladder lines with shadow effect
        for offset in [2, 0]:
            color = '#1e8449' if offset == 0 else '#145a32'
            self.create_line(start_pos[0] + offset, start_pos[1] + offset,
                             end_pos[0] + offset, end_pos[1] + offset,
                             fill=color, width=4)

        # Ladder icon
        self.create_text(start_pos[0], start_pos[1] - 20, text="🪜",
                         font=('Arial', 14))

    def draw_snake(self, start: int, end: int):
        """Draw a snake"""
        start_pos = self.get_cell_center(start)
        end_pos = self.get_cell_center(end)

        # Curved snake body
        control_x = (start_pos[0] + end_pos[0]) // 2
        control_y = (start_pos[1] + end_pos[1]) // 2 - 50

        self.create_line(start_pos[0], start_pos[1], control_x, control_y, end_pos[0], end_pos[1],
                         fill='#e74c3c', width=6, smooth=True)

        # Snake head
        self.create_text(end_pos[0], end_pos[1] - 15, text="🐍",
                         font=('Arial', 12))

    def get_cell_center(self, cell_num: int) -> Tuple[int, int]:
        """Get center coordinates of a cell"""
        row = 9 - ((cell_num - 1) // 10)
        col = (cell_num - 1) % 10 if row % 2 == 0 else 9 - ((cell_num - 1) % 10)

        x = col * self.cell_size + self.cell_size // 2
        y = row * self.cell_size + self.cell_size // 2
        return (x, y)

    def update_players(self, players: List[Player]):
        """Update player positions with animations"""
        # Remove previous players
        self.delete("player")

        for player in players:
            if player.position > 0:
                pos = self.get_cell_center(player.position)
                player_color = self.theme.PLAYER_COLORS[player.player_id]

                # Create player token with unique color
                token_size = 16
                self.create_oval(pos[0] - token_size, pos[1] - token_size,
                                 pos[0] + token_size, pos[1] + token_size,
                                 fill=player_color['primary'], outline=player_color['secondary'],
                                 width=3, tags="player")

                # Player number
                self.create_text(pos[0], pos[1], text=str(player.player_id + 1),
                                 fill='white', font=('Arial', 10, 'bold'), tags="player")


class SnakeAndLadderGame(tk.Tk):
    """Main Snake and Ladder Game Application"""

    def __init__(self):
        super().__init__()

        self.theme = ProfessionalTheme()
        self.engine = GameEngine()

        self.setup_ui()
        self.setup_styling()

        logger.info("Snake and Ladder Game initialized")

    def setup_ui(self):
        """Setup the user interface"""
        self.title("🎯 Professional Snake & Ladders")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        self.configure(bg=self.theme.COLORS['primary'])

        # Custom fonts
        self.title_font = tkfont.Font(family="Arial", size=18, weight="bold")
        self.subtitle_font = tkfont.Font(family="Arial", size=12, weight="bold")
        self.normal_font = tkfont.Font(family="Arial", size=10)

        self.create_widgets()

    def setup_styling(self):
        """Setup ttk styling"""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure styles
        style.configure('TFrame', background=self.theme.COLORS['primary'])
        style.configure('TLabel', background=self.theme.COLORS['primary'],
                        foreground=self.theme.COLORS['text_primary'])
        style.configure('TButton', font=self.normal_font)

    def create_widgets(self):
        """Create application widgets"""
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left panel - Controls and info
        left_panel = ttk.Frame(main_container, width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left_panel.pack_propagate(False)

        # Right panel - Game board
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.create_control_panel(left_panel)
        self.create_game_panel(right_panel)

    def create_control_panel(self, parent):
        """Create game control panel"""
        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(header_frame, text="🎯 SNAKE & LADDERS",
                 font=self.title_font, fg=self.theme.COLORS['text_primary'],
                 bg=self.theme.COLORS['primary']).pack(pady=10)

        # Game status
        self.status_label = tk.Label(header_frame, text="Ready to start game",
                                     font=self.subtitle_font, fg=self.theme.COLORS['info'],
                                     bg=self.theme.COLORS['primary'], wraplength=320)
        self.status_label.pack(pady=5)

        # Current player info
        self.player_info = tk.Label(header_frame, text="", font=self.normal_font,
                                    fg=self.theme.COLORS['text_primary'],
                                    bg=self.theme.COLORS['primary'], justify=tk.LEFT)
        self.player_info.pack(pady=10)

        # Control buttons
        self.create_control_buttons(parent)

        # Players info
        self.create_players_display(parent)

        # Game log
        self.create_game_log(parent)

    def create_control_buttons(self, parent):
        """Create game control buttons"""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=20)

        button_configs = [
            ("👤 Add Player", self.add_player),
            ("🎲 Roll Dice", self.roll_dice),
            ("🔄 New Game", self.new_game),
            ("💾 Save Game", self.save_game),
            ("📂 Load Game", self.load_game),
            ("📊 Analyze Game", self.analyze_game)
        ]

        for text, command in button_configs:
            btn = ttk.Button(btn_frame, text=text, command=command, style='TButton')
            btn.pack(fill=tk.X, pady=3)

    def create_players_display(self, parent):
        """Create players information display"""
        players_frame = ttk.LabelFrame(parent, text="🎮 Players", padding=10)
        players_frame.pack(fill=tk.X, pady=10)

        self.players_text = tk.Text(players_frame, height=8, width=35,
                                    bg=self.theme.COLORS['secondary'],
                                    fg=self.theme.COLORS['text_primary'],
                                    font=('Consolas', 9), relief='flat')
        self.players_text.pack(fill=tk.BOTH, expand=True)

    def create_game_log(self, parent):
        """Create game log display"""
        log_frame = ttk.LabelFrame(parent, text="📝 Game Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.log_text = tk.Text(log_frame, height=12, width=35,
                                bg=self.theme.COLORS['secondary'],
                                fg=self.theme.COLORS['text_secondary'],
                                font=('Consolas', 8), relief='flat')

        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_game_panel(self, parent):
        """Create game board panel"""
        # Board container
        board_container = ttk.Frame(parent)
        board_container.pack(expand=True, pady=20)

        # Game board
        self.board = AnimatedGameBoard(board_container, self.theme, 650)
        self.board.pack()

        # Legend
        self.create_legend(parent)

    def create_legend(self, parent):
        """Create game legend"""
        legend_frame = ttk.Frame(parent)
        legend_frame.pack(fill=tk.X, pady=10)

        # Player colors legend
        legend_text = "Player Colors: "
        for i in range(4):
            color_info = self.theme.PLAYER_COLORS[i]
            legend_text += f"{i + 1}.{color_info['name']}  "

        legend_label = tk.Label(legend_frame, text=legend_text, font=self.normal_font,
                                fg=self.theme.COLORS['text_secondary'],
                                bg=self.theme.COLORS['primary'])
        legend_label.pack()

    def add_player(self):
        """Add a new player to the game"""
        if len(self.engine.state.players) >= GameConfig.MAX_PLAYERS:
            messagebox.showwarning("Warning", f"Maximum {GameConfig.MAX_PLAYERS} players allowed")
            return

        player_id = len(self.engine.state.players)
        player_name = f"Player {player_id + 1}"
        self.engine.state.add_player(player_name, player_id)
        self.update_display()
        self.log_game(f"Player {player_id + 1} joined the game")

    def roll_dice(self):
        """Roll dice for current player"""
        if len(self.engine.state.players) < 2:
            messagebox.showwarning("Warning", "At least 2 players required to start")
            return

        if not self.engine.state.game_started:
            self.engine.state.game_started = True
            self.engine.state.start_time = datetime.now()

        # Show rolling animation
        current_player = self.engine.state.get_current_player()
        self.status_label.config(text=f"🎲 {current_player.name} is rolling dice...")
        self.update_idletasks()

        # Execute dice roll in separate thread
        self.engine.thread_pool.submit(self._perform_dice_roll)

    def _perform_dice_roll(self):
        """Perform dice roll in background thread"""
        time.sleep(1.5)  # Simulate rolling time

        dice_roll = random.randint(1, 6)
        current_player = self.engine.state.get_current_player()

        # Calculate move
        move_result = self.engine.calculate_move(current_player, dice_roll)
        current_player.turns += 1

        # Create move log
        player_color = self.theme.PLAYER_COLORS[current_player.player_id]['name']
        move_log = f"{current_player.name} rolled: {dice_roll}"

        if move_result['type'] == 'snake':
            move_log += f" - Snake! {move_result['snake_pos']}→{move_result['end_pos']} 📉"
        elif move_result['type'] == 'ladder':
            move_log += f" - Ladder! {move_result['ladder_pos']}→{move_result['end_pos']} 📈"
        elif move_result['type'] == 'win':
            move_log += f" - VICTORY! 🏆"
            self.engine.state.game_over = True
            self.engine.state.winner = current_player.name

        self.engine.state.move_history.append(move_result)

        # Update UI in main thread
        self.after(0, lambda: self._update_after_move(move_log, move_result))

    def _update_after_move(self, move_log: str, move_result: Dict):
        """Update UI after move completion"""
        self.log_game(move_log)
        self.update_display()

        if move_result['type'] == 'win':
            messagebox.showinfo("Congratulations!",
                                f"🎉 {self.engine.state.winner} won the game!\n"
                                f"Total turns: {self.engine.state.get_current_player().turns}")
        else:
            self.engine.state.next_turn()

    def new_game(self):
        """Start a new game"""
        self.engine.state = GameState()
        self.update_display()
        self.log_game("New game started")

    def save_game(self):
        """Save current game state"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Save Game"
        )

        if filename and self.engine.state.save_game(filename):
            messagebox.showinfo("Success", f"Game saved successfully!\n{filename}")
            self.log_game(f"Game saved: {filename}")

    def load_game(self):
        """Load game state from file"""
        filename = filedialog.askopenfilename(
            title="Load Game",
            filetypes=[("JSON files", "*.json")]
        )

        if filename and self.engine.state.load_game(filename):
            self.update_display()
            self.log_game(f"Game loaded: {filename}")
        else:
            messagebox.showerror("Error", "Failed to load game file")

    def analyze_game(self):
        """Perform heavy game analysis"""
        if not self.engine.state.move_history:
            messagebox.showwarning("Warning", "No game data available for analysis")
            return

        game_data = {
            'players': [p.to_dict() for p in self.engine.state.players],
            'moves': self.engine.state.move_history
        }

        self.log_game("Starting game analysis... (CPU Intensive)")

        # Execute analysis in process pool
        future = self.engine.process_pool.submit(self.engine.heavy_analysis, game_data)

        def on_analysis_complete(fut):
            try:
                result = fut.result()
                self.log_game(f"Analysis complete - Score: {result['total_score']}")

                # Show rankings
                ranking_text = "Player Rankings:\n"
                for player_id, rank in result['player_rankings'].items():
                    player_name = f"Player {player_id + 1}"
                    ranking_text += f"#{rank} - {player_name}\n"

                messagebox.showinfo("Game Analysis",
                                    f"📊 Analysis Results:\n"
                                    f"Total Score: {result['total_score']}\n"
                                    f"Average Position: {result['average_position']:.1f}\n"
                                    f"Total Moves: {result['move_count']}\n\n"
                                    f"{ranking_text}")
            except Exception as e:
                self.log_game(f"Analysis error: {e}")
                messagebox.showerror("Analysis Error", f"Failed to analyze game: {e}")

        future.add_done_callback(on_analysis_complete)

    def update_display(self):
        """Update game display"""
        # Update status
        if self.engine.state.game_over:
            status = f"🏆 Game Over! Winner: {self.engine.state.winner}"
        elif self.engine.state.game_started:
            current_player = self.engine.state.get_current_player()
            player_color = self.theme.PLAYER_COLORS[current_player.player_id]['name']
            status = f"🎮 Current Turn: {current_player.name} ({player_color})"
        else:
            player_count = len(self.engine.state.players)
            status = f"👥 Players: {player_count}/{GameConfig.MAX_PLAYERS} - Ready to start"

        self.status_label.config(text=status)

        # Update player info
        if self.engine.state.players:
            current_player = self.engine.state.get_current_player()
            info_text = f"Current Player: {current_player.name}\n"
            info_text += f"Position: {current_player.position}/100\n"
            info_text += f"Turns: {current_player.turns}\n"
            info_text += f"Total Moves: {current_player.total_moves}\n"
            info_text += f"Snakes: {current_player.snakes_bitten} | Ladders: {current_player.ladders_climbed}"
            self.player_info.config(text=info_text)

        # Update players display
        self.update_players_display()

        # Update game board
        self.board.update_players(self.engine.state.players)

    def update_players_display(self):
        """Update players information display"""
        self.players_text.delete(1.0, tk.END)

        for i, player in enumerate(self.engine.state.players):
            player_color = self.theme.PLAYER_COLORS[player.player_id]
            color_display = f"[{player_color['name']}]"

            player_info = (f"Player {i + 1} {color_display}\n"
                           f"  Position: {player.position:3d}\n"
                           f"  Turns:    {player.turns:3d}\n"
                           f"  Snakes:   {player.snakes_bitten:2d}\n"
                           f"  Ladders:  {player.ladders_climbed:2d}\n"
                           f"  Total:    {player.total_moves:3d}\n{'-' * 20}\n")

            self.players_text.insert(tk.END, player_info)

    def log_game(self, message: str):
        """Add message to game log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)

        # Also log to system logger
        logger.info(message)


def main():
    """Main application entry point"""
    try:
        app = SnakeAndLadderGame()
        app.mainloop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()