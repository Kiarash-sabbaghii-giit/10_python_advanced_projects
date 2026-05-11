import tkinter as tk
from tkinter import ttk, messagebox
import threading
import random
import logging
import queue
import time
from datetime import datetime

# Log setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('number_guess_game.log'),
        logging.StreamHandler()
    ]
)


class ThemeManager:

    THEMES = {
        "Dark Mode": {
            'bg': '#1a1a1a',
            'fg': '#ffffff',
            'accent': '#BB86FC',
            'secondary': '#03DAC6',
            'card_bg': '#2d2d2d',
            'text_bg': '#3d3d3d',
            'text_fg': '#ffffff',
            'button_bg': '#3700B3',
            'button_fg': '#ffffff',
            'entry_bg': '#3d3d3d',
            'entry_fg': '#ffffff',
            'border': '#444444'
        },
        "Blue Ocean": {
            'bg': '#0f1a2a',
            'fg': '#e6f7ff',
            'accent': '#4fc3f7',
            'secondary': '#81d4fa',
            'card_bg': '#1e2a3a',
            'text_bg': '#2d3e50',
            'text_fg': '#e6f7ff',
            'button_bg': '#0288d1',
            'button_fg': '#ffffff',
            'entry_bg': '#2d3e50',
            'entry_fg': '#e6f7ff',
            'border': '#3d4e60'
        },
        "Forest Green": {
            'bg': '#1b2e1b',
            'fg': '#e8f5e8',
            'accent': '#4caf50',
            'secondary': '#81c784',
            'card_bg': '#2d3e2d',
            'text_bg': '#3d4e3d',
            'text_fg': '#e8f5e8',
            'button_bg': '#2e7d32',
            'button_fg': '#ffffff',
            'entry_bg': '#3d4e3d',
            'entry_fg': '#e8f5e8',
            'border': '#4d5e4d'
        },
        "Purple Passion": {
            'bg': '#2d1b3d',
            'fg': '#f3e5f5',
            'accent': '#ba68c8',
            'secondary': '#ce93d8',
            'card_bg': '#3d2b4d',
            'text_bg': '#4d3b5d',
            'text_fg': '#f3e5f5',
            'button_bg': '#7b1fa2',
            'button_fg': '#ffffff',
            'entry_bg': '#4d3b5d',
            'entry_fg': '#f3e5f5',
            'border': '#5d4b6d'
        },
        "Sunset Orange": {
            'bg': '#332222',
            'fg': '#ffebee',
            'accent': '#ff8a65',
            'secondary': '#ffab91',
            'card_bg': '#443333',
            'text_bg': '#554444',
            'text_fg': '#ffebee',
            'button_bg': '#d84315',
            'button_fg': '#ffffff',
            'entry_bg': '#554444',
            'entry_fg': '#ffebee',
            'border': '#665555'
        },
        "Cyber Neon": {
            'bg': '#0a0a12',
            'fg': '#00ffcc',
            'accent': '#ff00ff',
            'secondary': '#00ffff',
            'card_bg': '#151522',
            'text_bg': '#222233',
            'text_fg': '#00ffcc',
            'button_bg': '#ff00ff',
            'button_fg': '#000000',
            'entry_bg': '#222233',
            'entry_fg': '#00ffcc',
            'border': '#333344'
        }
    }


class NumberGuessGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 Number Guessing Master")
        self.root.geometry("750x650")
        self.root.minsize(700, 600)

        # Theme setup
        self.theme_manager = ThemeManager()
        self.current_theme = "Dark Mode"

        # Game variables
        self.target_number = None
        self.max_range = 100000
        self.user_range = 500
        self.attempts = 0
        self.game_active = False

        # Thread communication
        self.guess_queue = queue.Queue()
        self.result_queue = queue.Queue()

        self.setup_ui()
        self.apply_theme()
        self.start_io_thread()

        logging.info("Game initialized")

    def setup_ui(self):
        """Create professional UI with theme support"""
        # Main container - using ttk for better theme support
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header frame
        self.header_frame = ttk.Frame(self.main_container)
        self.header_frame.pack(fill=tk.X, pady=(0, 20))

        # Title
        self.title_label = ttk.Label(
            self.header_frame,
            text="🎯 NUMBER GUESSING MASTER",
            font=('Arial', 24, 'bold')
        )
        self.title_label.pack(side=tk.LEFT)

        # Theme selector
        theme_frame = ttk.Frame(self.header_frame)
        theme_frame.pack(side=tk.RIGHT)

        ttk.Label(theme_frame, text="Theme:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)

        self.theme_var = tk.StringVar(value=self.current_theme)
        self.theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=list(self.theme_manager.THEMES.keys()),
            state="readonly",
            width=15
        )
        self.theme_combo.pack(side=tk.LEFT, padx=5)
        self.theme_combo.bind('<<ComboboxSelected>>', self.change_theme)

        # Main content frame
        content_frame = ttk.Frame(self.main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Controls
        self.left_panel = ttk.LabelFrame(
            content_frame,
            text="CONTROL PANEL",
            padding="20"
        )
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))

        # Range selection
        ttk.Label(self.left_panel, text="SELECT RANGE (1 to):",
                  font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 10))

        self.range_var = tk.StringVar(value="500")
        self.range_combo = ttk.Combobox(
            self.left_panel,
            textvariable=self.range_var,
            values=["100", "500", "1000", "5000", "10000", "50000", "100000"],
            state="readonly",
            font=('Arial', 11),
            width=12
        )
        self.range_combo.pack(fill=tk.X, pady=(0, 20))

        # Start game button
        self.start_btn = ttk.Button(
            self.left_panel,
            text="🚀 START NEW GAME",
            command=self.start_game
        )
        self.start_btn.pack(fill=tk.X, pady=5)

        # Game stats
        self.stats_frame = ttk.LabelFrame(
            self.left_panel,
            text="GAME STATS",
            padding="15"
        )
        self.stats_frame.pack(fill=tk.X, pady=20)

        self.stats_label = ttk.Label(
            self.stats_frame,
            text="Attempts: 0\nRange: 1-500\nStatus: Ready",
            font=('Arial', 10),
            justify=tk.CENTER
        )
        self.stats_label.pack()

        # Quick tips
        tips_frame = ttk.LabelFrame(
            self.left_panel,
            text="💡 QUICK TIPS",
            padding="15"
        )
        tips_frame.pack(fill=tk.X)

        tips_text = "• Use binary search strategy\n• Start from the middle\n• Watch the hints carefully\n• Have fun!"
        ttk.Label(tips_frame, text=tips_text, font=('Arial', 9)).pack(anchor=tk.W)

        # Right panel - Game area
        self.right_panel = ttk.LabelFrame(
            content_frame,
            text="GAME AREA",
            padding="20"
        )
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Guess input section
        input_frame = ttk.Frame(self.right_panel)
        input_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(input_frame, text="ENTER YOUR GUESS:",
                  font=('Arial', 11, 'bold')).pack(anchor=tk.W)

        input_subframe = ttk.Frame(input_frame)
        input_subframe.pack(fill=tk.X, pady=10)

        self.guess_var = tk.StringVar()

        # Use regular tk Entry for better control
        self.guess_entry = tk.Entry(
            input_subframe,
            textvariable=self.guess_var,
            font=('Arial', 14, 'bold'),
            width=15,
            justify=tk.CENTER,
            state='disabled'
        )
        self.guess_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.guess_entry.bind('<Return>', lambda e: self.submit_guess())

        self.submit_btn = ttk.Button(
            input_subframe,
            text="🎯 SUBMIT GUESS",
            command=self.submit_guess,
            state='disabled',
            width=15
        )
        self.submit_btn.pack(side=tk.RIGHT)

        # Feedback area
        feedback_frame = ttk.LabelFrame(
            self.right_panel,
            text="GAME FEEDBACK"
        )
        feedback_frame.pack(fill=tk.BOTH, expand=True)

        # Create text widget with minimal styling
        self.feedback_text = tk.Text(
            feedback_frame,
            height=15,
            font=('Consolas', 10),
            state='disabled',
            relief='flat',
            padx=15,
            pady=15,
            wrap=tk.WORD
        )

        # Scrollbar for feedback
        scrollbar = ttk.Scrollbar(feedback_frame, command=self.feedback_text.yview)
        self.feedback_text.config(yscrollcommand=scrollbar.set)

        self.feedback_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def change_theme(self, event=None):
        """Change application theme"""
        self.current_theme = self.theme_var.get()
        self.apply_theme()
        logging.info(f"Theme changed to: {self.current_theme}")

    def apply_theme(self):
        """Apply current theme using ttk styles"""
        theme = self.theme_manager.THEMES[self.current_theme]

        style = ttk.Style()
        style.theme_use('clam')

        # Configure main styles
        style.configure('.',
                        background=theme['bg'],
                        foreground=theme['fg'])

        # Configure specific widget styles
        style.configure('TFrame',
                        background=theme['bg'])

        style.configure('TLabel',
                        background=theme['bg'],
                        foreground=theme['fg'])

        style.configure('TLabelframe',
                        background=theme['card_bg'],
                        foreground=theme['accent'])

        style.configure('TLabelframe.Label',
                        background=theme['card_bg'],
                        foreground=theme['accent'])

        style.configure('TButton',
                        background=theme['button_bg'],
                        foreground=theme['button_fg'])

        style.configure('TCombobox',
                        fieldbackground=theme['entry_bg'],
                        background=theme['entry_bg'],
                        foreground=theme['entry_fg'])

        # Configure entry field (tk widget)
        self.guess_entry.config(
            background=theme['entry_bg'],
            foreground=theme['entry_fg'],
            insertbackground=theme['fg'],  # Cursor color
            relief='solid',
            borderwidth=1
        )

        # Configure text widget
        self.feedback_text.config(
            background=theme['text_bg'],
            foreground=theme['text_fg'],
            insertbackground=theme['fg']  # Cursor color
        )

    def start_io_thread(self):
        """Start IO thread for game logic"""
        io_thread = threading.Thread(target=self.io_worker, daemon=True)
        io_thread.start()
        logging.info("IO thread started")

    def io_worker(self):
        """Handle IO-bound operations"""
        while True:
            try:
                # Get user guess from queue (blocking with timeout to allow graceful loop)
                user_guess = self.guess_queue.get(timeout=1)

                # Process guess directly (no multiprocessing) — simple and fast
                result = self.process_guess_cpu(user_guess, self.target_number, self.attempts)

                # Put result back to queue
                self.result_queue.put(result)

            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"IO worker error: {e}")
                # include error text so UI shows more info
                self.result_queue.put({"error": True, "message": f"An error occurred during processing: {e}"})

    def process_guess_cpu(self, user_guess, target_number, current_attempts):
        """CPU-bound guess processing"""
        try:
            guess_num = int(user_guess)

            if target_number is None:
                return {
                    "error": True,
                    "attempts": current_attempts,
                    "message": "❌ Game has not been started or target number is missing."
                }

            if guess_num == target_number:
                return {
                    "correct": True,
                    "attempts": current_attempts + 1,
                    "message": f"🎉 CONGRATULATIONS! You guessed it!\nThe number was {target_number}.\nTotal attempts: {current_attempts + 1}"
                }
            elif guess_num < target_number:
                return {
                    "correct": False,
                    "hint": "higher",
                    "attempts": current_attempts + 1,
                    "message": f"📈 Try a HIGHER number than {guess_num}"
                }
            else:
                return {
                    "correct": False,
                    "hint": "lower",
                    "attempts": current_attempts + 1,
                    "message": f"📉 Try a LOWER number than {guess_num}"
                }

        except ValueError:
            return {
                "error": True,
                "attempts": current_attempts,
                "message": "❌ Please enter a valid number!"
            }

    def start_game(self):
        """Start new game"""
        try:
            self.user_range = int(self.range_var.get())
            if self.user_range < 1 or self.user_range > self.max_range:
                raise ValueError("Invalid range")

            # Generate random number directly (no multiprocessing)
            self.target_number = random.randint(1, self.user_range)

            self.attempts = 0
            self.game_active = True

            # Enable UI
            self.guess_entry.config(state='normal')
            self.submit_btn.config(state='normal')
            self.start_btn.config(state='disabled')

            # Clear feedback
            self.feedback_text.config(state='normal')
            self.feedback_text.delete(1.0, tk.END)
            self.feedback_text.insert(tk.END, f"🎮 NEW GAME STARTED!\n")
            self.feedback_text.insert(tk.END, f"🔢 Guess a number between 1 and {self.user_range}\n")
            self.feedback_text.insert(tk.END, f"💡 Use binary search for best results!\n\n")
            self.feedback_text.insert(tk.END, "=" * 50 + "\n\n")
            self.feedback_text.config(state='disabled')

            # Update stats
            self.update_stats()

            # Focus on entry
            self.guess_entry.focus()

            logging.info(f"New game started - Target: {self.target_number}, Range: 1-{self.user_range}")

        except ValueError as e:
            messagebox.showerror("Error", "Please select a valid number range!")
            logging.error(f"Start game error: {e}")

    def submit_guess(self):
        """Submit user guess"""
        if not self.game_active:
            messagebox.showwarning("Warning", "Please start a new game first!")
            return

        guess = self.guess_var.get().strip()
        if not guess:
            messagebox.showwarning("Warning", "Please enter a number!")
            return

        # Disable input temporarily
        self.guess_entry.config(state='disabled')
        self.submit_btn.config(state='disabled')

        # Add to queue for processing
        self.guess_queue.put(guess)

        # Schedule result check
        self.root.after(100, self.check_result)

    def check_result(self):
        """Check for processing result"""
        try:
            result = self.result_queue.get_nowait()

            # Safe dictionary access
            message = result.get("message", "Unknown result")

            if result.get("error"):
                self.show_feedback(message, "error")
                # Re-enable input on error
                self.guess_entry.config(state='normal')
                self.submit_btn.config(state='normal')
                self.guess_var.set("")
                self.guess_entry.focus()
            elif result.get("correct"):
                self.attempts = result.get("attempts", self.attempts)
                self.show_feedback(message, "success")
                self.end_game()
            else:
                self.attempts = result.get("attempts", self.attempts)
                self.show_feedback(message, "info")
                # Re-enable input for next guess
                self.guess_entry.config(state='normal')
                self.submit_btn.config(state='normal')
                self.guess_var.set("")
                self.guess_entry.focus()

            # Update stats
            self.update_stats()

        except queue.Empty:
            # Check again later
            self.root.after(100, self.check_result)

    def show_feedback(self, message, message_type):
        """Display feedback message"""
        self.feedback_text.config(state='normal')

        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.feedback_text.insert(tk.END, f"[{timestamp}] {message}\n\n")

        # Auto-scroll to bottom
        self.feedback_text.see(tk.END)
        self.feedback_text.config(state='disabled')

        logging.info(f"Feedback: {message}")

    def update_stats(self):
        """Update game statistics display"""
        status = "Active" if self.game_active else "Ready"
        stats_text = f"Attempts: {self.attempts}\nRange: 1-{self.user_range}\nStatus: {status}"
        self.stats_label.config(text=stats_text)

    def end_game(self):
        """End current game"""
        self.game_active = False
        self.guess_entry.config(state='disabled')
        self.submit_btn.config(state='disabled')
        self.start_btn.config(state='normal')

        logging.info("Game ended")


def main():
    """Main application entry point"""
    try:
        root = tk.Tk()
        app = NumberGuessGame(root)

        # Center window
        root.update_idletasks()
        x = (root.winfo_screenwidth() - root.winfo_reqwidth()) // 2
        y = (root.winfo_screenheight() - root.winfo_reqheight()) // 2
        root.geometry(f"+{x}+{y}")

        logging.info("Application started successfully")
        root.mainloop()

    except Exception as e:
        logging.critical(f"Application failed to start: {e}")
        raise

if __name__ == "__main__":
    main()
