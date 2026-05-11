import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import time
import os
from pygame import mixer


class LyricsTimestampGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 Advanced Lyrics Timestamp Generator 🎵")
        self.root.geometry("1200x900")
        self.root.configure(bg='#0f1a2b')
        self.root.resizable(True, True)

        mixer.init()

        # App state
        self.current_line = 0
        self.recording = False
        self.start_time = 0
        self.timestamps = []
        self.audio_loaded = False
        self.lyrics = []
        self.selected_audio_file = ""
        self.json_output = ""

        # Colors
        self.bg_color = '#0f1a2b'
        self.card_bg = '#1e293b'
        self.primary = '#3b82f6'
        self.secondary = '#60a5fa'
        self.accent = '#f59e0b'
        self.success = '#10b981'
        self.warning = '#f59e0b'
        self.error = '#ef4444'
        self.text_color = '#f8fafc'
        self.text_secondary = '#cbd5e1'
        self.json_bg = '#000000'
        self.json_text = '#ffffff'

        self.setup_ui()

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.setup_styles()

        self.main_tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.json_tab = tk.Frame(self.notebook, bg=self.bg_color)

        self.notebook.add(self.main_tab, text="🎵 Main")
        self.notebook.add(self.json_tab, text="📋 JSON Output")

        self.setup_main_tab()
        self.setup_json_tab()

    def setup_styles(self):
        style = ttk.Style()

        style.configure('TNotebook', background=self.bg_color)
        style.configure(
            'TNotebook.Tab',
            background=self.card_bg,
            foreground=self.text_color,
            padding=[20, 10],
            font=('Arial', 10, 'bold')
        )
        style.map(
            'TNotebook.Tab',
            background=[('selected', self.card_bg)],
            foreground=[('selected', self.accent)],
        )

        style.configure(
            'Custom.Horizontal.TProgressbar',
            background=self.accent,
            troughcolor=self.card_bg,
            bordercolor=self.card_bg,
            lightcolor=self.accent,
            darkcolor=self.accent
        )

    def setup_main_tab(self):
        main_frame = tk.Frame(self.main_tab, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(main_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_color)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)

        self.create_main_ui_elements()

    def setup_json_tab(self):
        json_container = tk.Frame(self.json_tab, bg=self.bg_color)
        json_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        title_label = tk.Label(
            json_container,
            text="📋 JSON Output Viewer",
            font=('Arial', 24, 'bold'),
            fg=self.accent,
            bg=self.bg_color
        )
        title_label.pack(pady=(0, 20))

        self.json_info_label = tk.Label(
            json_container,
            text="No JSON data available yet.",
            font=('Arial', 12),
            fg=self.text_secondary,
            bg=self.bg_color
        )
        self.json_info_label.pack(pady=(0, 10))

        json_display_frame = tk.Frame(json_container, bg=self.bg_color)
        json_display_frame.pack(fill=tk.BOTH, expand=True)

        self.json_display = scrolledtext.ScrolledText(
            json_display_frame,
            font=('Consolas', 12),
            bg=self.json_bg,
            fg=self.json_text,
            wrap=tk.WORD,
            relief='flat',
            padx=15,
            pady=15,
            insertbackground=self.text_color
        )
        self.json_display.pack(fill=tk.BOTH, expand=True)
        self.json_display.config(state=tk.DISABLED)

    def create_main_ui_elements(self):
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.create_header_section()
        self.create_audio_section()
        self.create_lyrics_input_section()
        self.create_status_section()
        self.create_lyrics_display_section()
        self.create_control_section()
        self.create_progress_section()

    def create_header_section(self):
        header_frame = tk.Frame(self.scrollable_frame, bg=self.bg_color)
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 30))

        tk.Label(
            header_frame,
            text="🎵 Advanced Lyrics Timestamp Generator 🎵",
            font=('Arial', 24, 'bold'),
            fg=self.accent,
            bg=self.bg_color
        ).pack(pady=(0, 10))

        tk.Label(
            header_frame,
            text="Create synchronized lyrics timestamps with real-time editing",
            font=('Arial', 12),
            fg=self.text_secondary,
            bg=self.bg_color
        ).pack()

    def create_audio_section(self):
        frame = tk.Frame(self.scrollable_frame, bg=self.card_bg, relief='ridge', bd=2)
        frame.grid(row=1, column=0, sticky='ew', pady=(0, 20))

        tk.Label(
            frame, text="🎵 Audio File", font=('Arial', 16, 'bold'),
            fg=self.text_color, bg=self.card_bg
        ).pack(anchor='w', padx=20, pady=15)

        container = tk.Frame(frame, bg=self.card_bg)
        container.pack(fill='x', padx=20, pady=(0, 15))

        self.audio_btn = tk.Button(
            container, text="🎵 Choose Audio File",
            font=('Arial', 11, 'bold'), bg=self.primary, fg=self.text_color,
            relief='raised', bd=3, width=20, height=1,
            command=self.select_audio_file
        )
        self.audio_btn.pack(side='left', padx=(0, 15))

        self.audio_label = tk.Label(
            container,
            text="No audio file selected",
            font=('Arial', 11),
            fg=self.text_secondary,
            bg=self.card_bg,
            anchor='w'
        )
        self.audio_label.pack(side='left', fill='x', expand=True)

    def create_lyrics_input_section(self):
        frame = tk.Frame(self.scrollable_frame, bg=self.card_bg, relief='ridge', bd=2)
        frame.grid(row=2, column=0, sticky='ew', pady=(0, 20))

        tk.Label(
            frame, text="📝 Lyrics Input",
            font=('Arial', 16, 'bold'), fg=self.text_color, bg=self.card_bg
        ).pack(anchor='w', padx=20, pady=15)

        container = tk.Frame(frame, bg=self.card_bg)
        container.pack(fill='x', padx=20, pady=(0, 10))

        tk.Button(
            container, text="📁 Upload Lyrics File",
            font=('Arial', 11, 'bold'), bg=self.primary, fg=self.text_color,
            relief='raised', bd=3, width=18, height=1,
            command=self.upload_lyrics_file
        ).pack(side='left', padx=(0, 15))

        tk.Button(
            container, text="✏️ Manual Input",
            font=('Arial', 11, 'bold'), bg=self.success, fg=self.text_color,
            relief='raised', bd=3, width=18, height=1,
            command=self.show_manual_input
        ).pack(side='left')

        self.manual_input_frame = tk.Frame(frame, bg=self.card_bg)

        tk.Label(
            self.manual_input_frame,
            text="Enter lyrics (one line per row):",
            font=('Arial', 11, 'bold'),
            fg=self.text_color,
            bg=self.card_bg
        ).pack(anchor='w', padx=20, pady=(10, 5))

        self.lyrics_text_input = scrolledtext.ScrolledText(
            self.manual_input_frame,
            font=('Arial', 11),
            bg=self.card_bg,
            fg='#ffffff',
            wrap=tk.WORD,
            height=6,
            relief='flat',
            padx=10,
            pady=10
        )
        self.lyrics_text_input.pack(fill='x', padx=20, pady=(0, 10))

        tk.Button(
            self.manual_input_frame,
            text="💾 Save Lyrics",
            font=('Arial', 11, 'bold'),
            bg=self.success,
            fg=self.text_color,
            relief='raised',
            bd=3,
            width=15,
            height=1,
            command=self.save_manual_lyrics
        ).pack(anchor='e', padx=20, pady=(0, 15))

    def create_status_section(self):
        frame = tk.Frame(self.scrollable_frame, bg=self.card_bg, relief='ridge', bd=2)
        frame.grid(row=3, column=0, sticky='ew', pady=(0, 20))

        tk.Label(
            frame, text="📊 Status",
            font=('Arial', 16, 'bold'), fg=self.text_color, bg=self.card_bg
        ).pack(anchor='w', padx=20, pady=15)

        self.status_label = tk.Label(
            frame,
            text="Please upload audio file and add lyrics to begin",
            font=('Arial', 12),
            fg=self.text_secondary,
            bg=self.card_bg,
            justify='left'
        )
        self.status_label.pack(fill='x', padx=20, pady=(0, 15))

    def create_lyrics_display_section(self):
        frame = tk.Frame(self.scrollable_frame, bg=self.card_bg, relief='ridge', bd=2)
        frame.grid(row=4, column=0, sticky='ew', pady=(0, 20))

        tk.Label(
            frame, text="🎤 Current Lyrics Line",
            font=('Arial', 16, 'bold'), fg=self.text_color, bg=self.card_bg
        ).pack(anchor='w', padx=20, pady=15)

        container = tk.Frame(frame, bg=self.card_bg)
        container.pack(fill='x', padx=20, pady=(0, 15))

        self.current_lyrics_display = tk.Text(
            container,
            font=('Arial', 18, 'bold'),
            bg=self.card_bg,
            fg=self.accent,
            wrap=tk.WORD,
            height=3,
            relief='flat',
            padx=20,
            pady=20
        )
        self.current_lyrics_display.pack(fill='x')
        self.current_lyrics_display.config(state=tk.DISABLED)

    def create_control_section(self):
        frame = tk.Frame(self.scrollable_frame, bg=self.card_bg, relief='ridge', bd=2)
        frame.grid(row=5, column=0, sticky='ew', pady=(0, 20))

        tk.Label(
            frame, text="🎮 Controls",
            font=('Arial', 16, 'bold'), fg=self.text_color, bg=self.card_bg
        ).pack(anchor='w', padx=20, pady=15)

        container = tk.Frame(frame, bg=self.card_bg)
        container.pack(fill='x', padx=20, pady=(0, 15))

        center = tk.Frame(container, bg=self.card_bg)
        center.pack(expand=True)

        self.start_btn = tk.Button(
            center,
            text="⏺️ START RECORDING",
            font=('Arial', 12, 'bold'),
            bg='#dc2626',
            fg=self.text_color,
            relief='raised',
            bd=4,
            width=18,
            height=2,
            state='disabled',
            command=self.start_recording
        )
        self.start_btn.pack(side='left', padx=(0, 15))

        self.next_btn = tk.Button(
            center,
            text="➡️ NEXT LINE",
            font=('Arial', 12, 'bold'),
            bg=self.success,
            fg=self.text_color,
            relief='raised',
            bd=4,
            width=18,
            height=2,
            state='disabled',
            command=self.next_line
        )
        self.next_btn.pack(side='left')

    def create_progress_section(self):
        frame = tk.Frame(self.scrollable_frame, bg=self.card_bg, relief='ridge', bd=2)
        frame.grid(row=6, column=0, sticky='ew', pady=(0, 20))

        tk.Label(
            frame, text="📈 Progress",
            font=('Arial', 16, 'bold'), fg=self.text_color, bg=self.card_bg
        ).pack(anchor='w', padx=20, pady=15)

        container = tk.Frame(frame, bg=self.card_bg)
        container.pack(fill='x', padx=20, pady=(0, 15))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            container,
            variable=self.progress_var,
            maximum=100,
            style='Custom.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill='x', pady=5)

        self.progress_label = tk.Label(
            frame,
            text="0/0 lines completed (0%)",
            font=('Arial', 12),
            fg=self.text_secondary,
            bg=self.card_bg
        )
        self.progress_label.pack(pady=(0, 15))

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def select_audio_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.m4a"), ("All Files", "*.*")]
        )

        if file_path:
            self.selected_audio_file = file_path
            filename = os.path.basename(file_path)
            display_name = filename if len(filename) <= 40 else filename[:37] + "..."

            self.audio_label.config(text=f"✓ {display_name}", fg=self.success)

            try:
                mixer.music.load(file_path)
                self.audio_loaded = True
                self.update_status()

            except:
                messagebox.showerror("Error", "Failed to load audio file")
                self.audio_label.config(text="✗ Error loading file", fg=self.error)
                self.audio_loaded = False

    def upload_lyrics_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Lyrics File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.lyrics = [line.strip() for line in f if line.strip()]

                self.update_status()
                self.display_current_line()
                messagebox.showinfo("Success", f"Loaded {len(self.lyrics)} lines from file")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load lyrics file: {str(e)}")
                self.lyrics = []

    def show_manual_input(self):
        self.manual_input_frame.pack(fill='x', pady=(10, 0))
        self.lyrics_text_input.delete(1.0, tk.END)

    def save_manual_lyrics(self):
        text_content = self.lyrics_text_input.get(1.0, tk.END).strip()
        if text_content:
            self.lyrics = [line.strip() for line in text_content.split('\n') if line.strip()]
            self.manual_input_frame.pack_forget()
            self.update_status()
            self.display_current_line()
            messagebox.showinfo("Success", f"Saved {len(self.lyrics)} lines from manual input")
        else:
            messagebox.showwarning("Warning", "Please enter some lyrics text")

    def update_status(self):
        if not self.audio_loaded or not self.lyrics:
            status_text = "Please upload audio file and add lyrics to begin"
            status_color = self.text_secondary
            self.start_btn.config(state='disabled')
            self.next_btn.config(state='disabled')

        elif not self.recording:
            status_text = f"Ready! Audio loaded and {len(self.lyrics)} lyrics lines ready. Click START RECORDING!"
            status_color = self.success
            self.start_btn.config(state='normal')
            self.next_btn.config(state='disabled')

        else:
            elapsed = time.time() - self.start_time
            status_text = f"⏱️ Recording... {elapsed:.2f}s | Line {self.current_line + 1} of {len(self.lyrics)}"
            status_color = self.accent
            self.start_btn.config(state='disabled')
            self.next_btn.config(state='normal')

        self.status_label.config(text=status_text, fg=status_color)
        self.update_progress()

    def display_current_line(self):
        self.current_lyrics_display.config(state='normal')
        self.current_lyrics_display.delete(1.0, 'end')

        if self.current_line < len(self.lyrics):
            text = self.lyrics[self.current_line]
            self.current_lyrics_display.insert(1.0, text)
        else:
            self.current_lyrics_display.insert(1.0, "🎉 All lines completed!\nSwitching to JSON Output...")

        self.current_lyrics_display.tag_configure("center", justify='center')
        self.current_lyrics_display.tag_add("center", "1.0", "end")

        self.current_lyrics_display.config(state=tk.DISABLED)
        self.update_progress()

    def update_progress(self):
        if self.lyrics:
            progress = (self.current_line / len(self.lyrics)) * 100
            self.progress_var.set(progress)
            self.progress_label.config(
                text=f"{self.current_line}/{len(self.lyrics)} lines completed ({int(progress)}%)"
            )
        else:
            self.progress_var.set(0)
            self.progress_label.config(text="0/0 lines completed (0%)")

    def start_recording(self):
        if not self.audio_loaded or not self.lyrics:
            messagebox.showerror("Error", "Load audio and lyrics first")
            return

        self.recording = True
        self.start_time = time.time()
        self.timestamps = []
        self.current_line = 0

        try:
            mixer.music.play()
            self.update_status()
            self.display_current_line()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to play audio: {str(e)}")
            self.recording = False
            self.update_status()

    def next_line(self):
        if not self.recording or self.current_line >= len(self.lyrics):
            return

        t = time.time() - self.start_time
        self.timestamps.append({
            "text": self.lyrics[self.current_line],
            "time_ms": int(t * 1000),
            "time_seconds": round(t, 2)
        })

        self.current_line += 1

        if self.current_line >= len(self.lyrics):
            self.recording = False
            mixer.music.stop()
            self.save_timestamps()

            # Auto-switch to JSON
            self.notebook.select(1)
            self.update_json_tab()

        else:
            self.display_current_line()

        self.update_status()

    def save_timestamps(self):
        self.json_output = json.dumps(self.timestamps, ensure_ascii=False, indent=2)

        try:
            with open("timestamps.json", "w", encoding="utf-8") as f:
                f.write(self.json_output)

            messagebox.showinfo(
                "Success",
                f"Saved {len(self.timestamps)} timestamps!\nSwitching to JSON Output."
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save JSON: {str(e)}")

    def update_json_tab(self):
        self.json_display.config(state=tk.NORMAL)
        self.json_display.delete(1.0, tk.END)
        self.json_display.insert(1.0, self.json_output)
        self.json_display.config(state=tk.DISABLED)
        self.json_info_label.config(
            text=f"Loaded {len(self.timestamps)} timestamps.",
            fg=self.success
        )
        self.json_display.see(1.0)


def main():
    root = tk.Tk()
    app = LyricsTimestampGenerator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
