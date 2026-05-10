# 🚀 Advanced Python Desktop Applications Suite

A **professional collection** of 10 desktop applications built with **Python**, **Tkinter**, **concurrent programming**, **SQL databases**, **REST APIs**, and **modern UI design**.

Each app demonstrates real‑world software engineering patterns:  
multithreading, multiprocessing, robust logging, theme engines, and clean architecture.

---

## 📦 Included Applications

| # | Application | File | Key Features |
|---|-------------|------|--------------|
| 1 | 🌡️ Temperature Converter | `temperature_adv_python.py` | CPU/IO bound processing, logging |
| 2 | ⚖️ BMI Calculator | `bmi_adv_python.py` | Matplotlib chart, JSON history |
| 3 | 🌤️ Weather Dashboard | `weather_api_adv_tk_python.py` | OpenWeatherMap API, multiprocessing |
| 4 | 🔐 Password Generator | `password_adv.py` | Multiprocessing, multi‑theme |
| 5 | 🧮 Advanced Calculator | `calculator_python_adv.py` | AST‑based safe eval, functions |
| 6 | 🎵 Lyrics Timestamp Tool | `time_lyric.py` | Audio playback, JSON export |
| 7 | 📞 PhoneBook Manager | `phone_book.py` | SQL Server CRUD, theme switching |
| 8 | 🏥 MedLink Inventory | `allocate_medical_product.py` | SQL Server, Excel export |
| 9 | 🐍 Snake & Ladders Game | `snake_ladders.py` | Animated board, state persistence |
|10 | 🎯 Number Guessing Master | `guess_number_adv_python.py` | Queue‑based, theme engine |

---

## ⚙️ System Requirements

- **Python 3.8+** (recommended 3.10+)
- **Operating System:** Windows / macOS / Linux
- **For database apps:** Microsoft SQL Server with `ODBC Driver 17 for SQL Server`
- **Internet connection** (only for Weather app)

---

## 📥 Installation

1. Clone or download all script files to a local folder.
2. Install the required external dependencies:

```bash
pip install requests matplotlib numpy pygame pyodbc openpyxl

⚠️ For the Weather App, you need a free API key from OpenWeatherMap.
Replace "your key!" in weather_api_adv_tk_python.py with your actual key.

---

▶️ How to Run

Each application is self‑contained. Execute any script from the terminal:

python temperature_adv_python.py
python bmi_adv_python.py
...

All apps log their activity to .log files and/or to the console.

---

📋 Application Details

---

1. 🌡️ Temperature Converter

Converts between Celsius, Fahrenheit, and Kelvin.

· CPU‑bound conversions run in a ProcessPoolExecutor.
· Asynchronous history logging with ThreadPoolExecutor.
· Dark themed interface with modern styling.

---

2. ⚖️ Advanced BMI Calculator

Calculates BMI and tracks history over time.

· Multiprocessing for the calculation (CPU‑bound).
· Threaded JSON history saving (I/O‑bound).
· Embedded matplotlib chart showing last 10 records.
· Color‑coded health categories with detailed recommendations.

---

3. 🌤️ Professional Weather Dashboard

Fetches live weather data from OpenWeatherMap.

· Coordinates or city name input.
· Quick‑select popular cities dropdown.
· API calls run in separate threads (I/O‑bound).
· Data processing uses a ProcessPoolExecutor (CPU‑bound).
· Beautiful card‑based UI with dark theme.

---

4. 🔐 Professional Password Generator

Generates strong random passwords using multiprocessing.

· Adjustable length (6–32 characters) and character sets.
· Multiple themes (Dark, Light, Blue, etc.) via a theme manager.
· Uses ProcessPoolExecutor for CPU‑bound generation.
· Copy‑to‑clipboard functionality.

---

5. 🧮 Advanced Scientific Calculator

Feature‑rich calculator with safe expression evaluation.

· Supports trigonometric, hyperbolic, logarithmic functions (in degrees).
· AST‑based sandboxed evaluator – no eval().
· Toggleable advanced panel with extra functions.
· Dark mode with custom color‑coded buttons.

---

6. 🎵 Lyrics Timestamp Generator

Creates synchronized lyrics timestamps while playing audio.

· Load audio files and lyrics (from file or manual input).
· pygame.mixer for audio playback.
· Real‑time timestamp recording – tap “Next Line” to mark times.
· Exports to timestamps.json. Auto‑switches to JSON viewer.

---

7. 📞 PhoneBook Man

ager

Full CRUD phonebook backed by Microsoft SQL Server.

· Add, edit, delete, and search contacts.
· Saves to phone database (table contacts auto‑created).
· Dark/Light theme switching.
· Detailed contact view with formatted text.
· Uses pyodbc with connection error handling.

---

8. 🏥 MedLink Inventory Manager

Manages medical product inventory and allocations to hospitals.

· SQL Server database with tables: hospitals, items, allocations.
· Add items (stent/generic) with diameter, length, price, stock.
· Allocate items to hospitals with price recording.
· Generate and export allocation reports to Excel (using openpyxl).
· Toggle between Simple (hide price) and Advanced modes.

---

9. 🐍 Snake & Ladders Game

Multiplayer board game with animated graphics.

· Up to 4 players with distinct colors.
· Beautiful dark board with snakes and ladders drawn artistically.
· Dice roll animated in thread; move calculation is CPU‑bound.
· Save/Load game state to JSON file.
· Heavy game analysis using ProcessPoolExecutor.

---

10. 🎯 Number Guessing Master

Guess the random number with hints and statistics.

· Immersive UI with 6 selectable themes.
· Queue‑based architecture for thread‑safe communication.
· CPU‑bound hint processing (higher/lower).
· Live feedback log with timestamps.
· Binary search tip displayed.

---

📊 Logging & Error Handling

Every application uses Python’s logging module:

· File logs (e.g., temperature_converter.log, bmi_calculator.log)
· Console output for real‑time monitoring
· All errors are caught and shown via messagebox, preventing silent crashes.

---

📝 License

These applications are provided for educational and demonstration purposes.
Feel free to use, modify, and integrate them into your own projects.

---

👤 Author

Created with ❤️ by a Python enthusiast.
For questions or contributions, please reach out via GitHub.

---
