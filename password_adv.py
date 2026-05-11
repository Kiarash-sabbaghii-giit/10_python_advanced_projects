import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import multiprocessing
import queue
import logging
import random
import string
import time
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('password_generator.log'),
        logging.StreamHandler()
    ]
)


class ThemeManager:
    """Manages application themes"""

    THEMES = {
        "Dark": {
            "bg": "#2b2b2b",
            "fg": "#ffffff",
            "accent": "#007acc",
            "secondary": "#3c3c3c",
            "text_bg": "#1e1e1e",
            "button_bg": "#007acc",
            "button_fg": "#ffffff"
        },
        "Light": {
            "bg": "#f0f0f0",
            "fg": "#000000",
            "accent": "#0078d4",
            "secondary": "#e1e1e1",
            "text_bg": "#ffffff",
            "button_bg": "#0078d4",
            "button_fg": "#ffffff"
        },
        "Blue": {
            "bg": "#001f3f",
            "fg": "#ffffff",
            "accent": "#39cccc",
            "secondary": "#003366",
            "text_bg": "#001a33",
            "button_bg": "#39cccc",
            "button_fg": "#001f3f"
        }
    }

    @classmethod
    def get_theme(cls, theme_name: str) -> Dict[str, str]:
        return cls.THEMES.get(theme_name, cls.THEMES["Dark"])


class PasswordGenerator:
    """Handles CPU-bound password generation using multiprocessing"""

    @staticmethod
    def generate_password_process(args):
        """Static method for multiprocessing"""
        length, use_uppercase, use_lowercase, use_digits, use_symbols, count = args

        characters = ""
        if use_lowercase:
            characters += string.ascii_lowercase
        if use_uppercase:
            characters += string.ascii_uppercase
        if use_digits:
            characters += string.digits
        if use_symbols:
            characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        if not characters:
            characters = string.ascii_letters + string.digits

        passwords = []
        for _ in range(count):
            password = ''.join(random.choice(characters) for _ in range(length))
            passwords.append(password)

        return passwords


class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Password Generator")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        # Current theme
        self.current_theme = "Dark"
        self.apply_theme(self.current_theme)

        # Queue for thread communication
        self.queue = queue.Queue()

        # Setup UI
        self.setup_ui()

        # Start queue checker
        self.check_queue()

        logging.info("Password Generator Application Started")

    def apply_theme(self, theme_name: str):
        """Apply the selected theme"""
        self.current_theme = theme_name
        theme = ThemeManager.get_theme(theme_name)

        self.root.configure(bg=theme["bg"])
        self.style = ttk.Style()
        self.style.configure("TFrame", background=theme["bg"])
        self.style.configure("TLabel", background=theme["bg"], foreground=theme["fg"])
        self.style.configure("TCheckbutton", background=theme["bg"], foreground=theme["fg"])
        self.style.configure("TButton", background=theme["button_bg"], foreground=theme["button_fg"])
        self.style.configure("TScale", background=theme["bg"])
        self.style.configure("TCombobox", background=theme["text_bg"], foreground=theme["fg"])

    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = tk.Label(
            header_frame,
            text="Professional Password Generator",
            font=("Arial", 20, "bold"),
            bg=ThemeManager.get_theme(self.current_theme)["bg"],
            fg=ThemeManager.get_theme(self.current_theme)["accent"]
        )
        title_label.pack(side=tk.LEFT)

        # Theme selector
        theme_frame = ttk.Frame(header_frame)
        theme_frame.pack(side=tk.RIGHT)

        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT, padx=(0, 5))
        self.theme_var = tk.StringVar(value=self.current_theme)
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=list(ThemeManager.THEMES.keys()),
            state="readonly",
            width=10
        )
        theme_combo.pack(side=tk.LEFT)
        theme_combo.bind('<<ComboboxSelected>>', self.on_theme_change)

        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Password Settings", padding="15")
        settings_frame.pack(fill=tk.X, pady=(0, 20))

        # Password length
        length_frame = ttk.Frame(settings_frame)
        length_frame.pack(fill=tk.X, pady=5)

        ttk.Label(length_frame, text="Password Length:").pack(side=tk.LEFT)
        self.length_var = tk.IntVar(value=12)
        length_scale = ttk.Scale(
            length_frame,
            from_=6,
            to=32,
            variable=self.length_var,
            orient=tk.HORIZONTAL
        )
        length_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        self.length_label = ttk.Label(length_frame, text="12")
        self.length_label.pack(side=tk.RIGHT, padx=(10, 0))
        length_scale.configure(command=self.on_length_change)

        # Character types
        chars_frame = ttk.Frame(settings_frame)
        chars_frame.pack(fill=tk.X, pady=10)

        self.uppercase_var = tk.BooleanVar(value=True)
        self.lowercase_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=False)

        ttk.Checkbutton(chars_frame, text="Uppercase Letters", variable=self.uppercase_var).pack(side=tk.LEFT,
                                                                                                 padx=(0, 20))
        ttk.Checkbutton(chars_frame, text="Lowercase Letters", variable=self.lowercase_var).pack(side=tk.LEFT,
                                                                                                 padx=(0, 20))
        ttk.Checkbutton(chars_frame, text="Digits", variable=self.digits_var).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Checkbutton(chars_frame, text="Symbols", variable=self.symbols_var).pack(side=tk.LEFT)

        # Password count
        count_frame = ttk.Frame(settings_frame)
        count_frame.pack(fill=tk.X, pady=5)

        ttk.Label(count_frame, text="Number of Passwords:").pack(side=tk.LEFT)
        self.count_var = tk.IntVar(value=5)
        count_spinbox = ttk.Spinbox(
            count_frame,
            from_=1,
            to=100,
            textvariable=self.count_var,
            width=10
        )
        count_spinbox.pack(side=tk.LEFT, padx=(10, 0))

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 20))

        self.generate_btn = ttk.Button(
            buttons_frame,
            text="Generate Passwords",
            command=self.start_password_generation,
            style="TButton"
        )
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.copy_btn = ttk.Button(
            buttons_frame,
            text="Copy to Clipboard",
            command=self.copy_to_clipboard,
            state="disabled"
        )
        self.copy_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_btn = ttk.Button(
            buttons_frame,
            text="Clear Results",
            command=self.clear_results
        )
        self.clear_btn.pack(side=tk.LEFT)

        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=100
        )
        self.progress.pack(fill=tk.X, pady=(0, 20))

        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Generated Passwords", padding="15")
        results_frame.pack(fill=tk.BOTH, expand=True)

        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            height=15,
            font=("Consolas", 10),
            bg=ThemeManager.get_theme(self.current_theme)["text_bg"],
            fg=ThemeManager.get_theme(self.current_theme)["fg"],
            insertbackground=ThemeManager.get_theme(self.current_theme)["fg"]
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            style="TLabel"
        )
        status_bar.pack(fill=tk.X, pady=(10, 0))

    def on_theme_change(self, event):
        """Handle theme change"""
        new_theme = self.theme_var.get()
        self.apply_theme(new_theme)
        self.update_theme_colors()
        logging.info(f"Theme changed to: {new_theme}")

    def update_theme_colors(self):
        """Update dynamic colors after theme change"""
        theme = ThemeManager.get_theme(self.current_theme)
        self.results_text.configure(
            bg=theme["text_bg"],
            fg=theme["fg"],
            insertbackground=theme["fg"]
        )

    def on_length_change(self, value):
        """Update length label when scale changes"""
        length = int(float(value))
        self.length_label.config(text=str(length))
        self.length_var.set(length)

    def validate_settings(self) -> bool:
        """Validate user settings"""
        if not any([
            self.uppercase_var.get(),
            self.lowercase_var.get(),
            self.digits_var.get(),
            self.symbols_var.get()
        ]):
            messagebox.showerror("Error", "Please select at least one character type!")
            return False
        return True

    def start_password_generation(self):
        """Start password generation in a separate process"""
        if not self.validate_settings():
            return

        # Disable generate button and start progress
        self.generate_btn.config(state="disabled")
        self.progress.start()
        self.status_var.set("Generating passwords...")

        # Get settings
        settings = (
            self.length_var.get(),
            self.uppercase_var.get(),
            self.lowercase_var.get(),
            self.digits_var.get(),
            self.symbols_var.get(),
            self.count_var.get()
        )

        # Start generation in separate process
        threading.Thread(target=self.run_password_generation, args=(settings,), daemon=True).start()

        logging.info(f"Started password generation with settings: {settings}")

    def run_password_generation(self, settings):
        """Run password generation in a separate process (CPU-bound task)"""
        try:
            with multiprocessing.Pool(1) as pool:
                passwords = pool.map(PasswordGenerator.generate_password_process, [settings])[0]

            # Put results in queue for main thread
            self.queue.put(("success", passwords))

        except Exception as e:
            self.queue.put(("error", str(e)))

    def check_queue(self):
        """Check for messages from worker threads/processes"""
        try:
            while True:
                msg_type, data = self.queue.get_nowait()

                if msg_type == "success":
                    self.on_generation_complete(data)
                elif msg_type == "error":
                    self.on_generation_error(data)

        except queue.Empty:
            pass

        self.root.after(100, self.check_queue)

    def on_generation_complete(self, passwords):
        """Handle completed password generation"""
        self.progress.stop()
        self.generate_btn.config(state="normal")
        self.copy_btn.config(state="normal")

        # Display passwords
        self.results_text.delete(1.0, tk.END)
        for i, password in enumerate(passwords, 1):
            self.results_text.insert(tk.END, f"{i:2d}. {password}\n")

        self.status_var.set(f"Generated {len(passwords)} passwords successfully")
        logging.info(f"Password generation completed: {len(passwords)} passwords generated")

    def on_generation_error(self, error_msg):
        """Handle generation errors"""
        self.progress.stop()
        self.generate_btn.config(state="normal")

        messagebox.showerror("Generation Error", f"An error occurred: {error_msg}")
        self.status_var.set("Error during password generation")
        logging.error(f"Password generation error: {error_msg}")

    def copy_to_clipboard(self):
        """Copy generated passwords to clipboard"""
        passwords_text = self.results_text.get(1.0, tk.END).strip()
        if passwords_text:
            self.root.clipboard_clear()
            self.root.clipboard_append(passwords_text)
            self.status_var.set("Passwords copied to clipboard!")
            logging.info("Passwords copied to clipboard")

            # Show temporary confirmation
            self.root.after(2000, lambda: self.status_var.set("Ready"))

    def clear_results(self):
        """Clear the results text area"""
        self.results_text.delete(1.0, tk.END)
        self.copy_btn.config(state="disabled")
        self.status_var.set("Results cleared")
        logging.info("Results cleared")

        # Reset status after delay
        self.root.after(2000, lambda: self.status_var.set("Ready"))


def main():
    """Main function to start the application"""
    try:
        root = tk.Tk()
        app = PasswordGeneratorApp(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"Application error: {e}")
        messagebox.showerror("Application Error", f"The application encountered an error: {e}")


if __name__ == "__main__":
    main()