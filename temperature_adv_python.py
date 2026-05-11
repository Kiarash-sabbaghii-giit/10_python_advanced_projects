import tkinter as tk
from tkinter import ttk
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import logging

#  Setting up logging
logging.basicConfig(filename='temperature_converter.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Temperature conversion functions
def c_to_f(c):
    return (c * 9/5) + 32

def f_to_c(f):
    return (f - 32) * 5/9

def c_to_k(c):
    return c + 273.15

def k_to_c(k):
    return k - 273.15

def f_to_k(f):
    return c_to_k(f_to_c(f))

def k_to_f(k):
    return c_to_f(k_to_c(k))

# CPU-bound conversion function
def convert_temperature(value, from_unit, to_unit):
    try:
        value = float(value)
    except ValueError:
        logging.error(f"Invalid input: {value}")
        return "Invalid input"

    logging.info(f"Converting {value} from {from_unit} to {to_unit}")

    conversions = {
        ('Celsius (°C)', 'Fahrenheit (°F)'): c_to_f,
        ('Fahrenheit (°F)', 'Celsius (°C)'): f_to_c,
        ('Celsius (°C)', 'Kelvin (K)'): c_to_k,
        ('Kelvin (K)', 'Celsius (°C)'): k_to_c,
        ('Fahrenheit (°F)', 'Kelvin (K)'): f_to_k,
        ('Kelvin (K)', 'Fahrenheit (°F)'): k_to_f,
        ('Celsius (°C)', 'Celsius (°C)'): lambda x: x,
        ('Fahrenheit (°F)', 'Fahrenheit (°F)'): lambda x: x,
        ('Kelvin (K)', 'Kelvin (K)'): lambda x: x
    }

    func = conversions.get((from_unit, to_unit))
    if func:
        result = func(value)
        logging.info(f"Result: {result}")
        return round(result, 2)
    else:
        logging.error(f"Unsupported conversion: {from_unit} to {to_unit}")
        return "Conversion not supported"

# I/O-bound function to log history asynchronously
def log_history(entry):
    with open('history.txt', 'a') as f:
        f.write(entry + '\n')
    logging.info(f"Logged history: {entry}")

# UI class
class TemperatureConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Temperature Converter")
        self.root.configure(bg='#1e1e1e')
        self.root.geometry('520x400')

        # Thread and Process executors
        self.executor_thread = ThreadPoolExecutor(max_workers=2)
        self.executor_process = ProcessPoolExecutor(max_workers=2)

        # Supported units
        self.units = ['Celsius (°C)', 'Fahrenheit (°F)', 'Kelvin (K)']

        # UI Elements with modern styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TCombobox', fieldbackground='#2e2e2e', background='#2e2e2e', foreground='white')

        tk.Label(root, text="Temperature Converter", bg='#1e1e1e', fg='white', font=('Arial', 20, 'bold')).pack(pady=15)

        self.value_label = tk.Label(root, text="Enter Value:", bg='#1e1e1e', fg='white', font=('Arial', 12))
        self.value_label.pack(pady=5)

        self.value_entry = tk.Entry(root, font=('Arial', 14), justify='center', bg='#2e2e2e', fg='white', insertbackground='white')
        self.value_entry.pack(pady=5)

        self.from_unit_label = tk.Label(root, text="From Unit:", bg='#1e1e1e', fg='white', font=('Arial', 12))
        self.from_unit_label.pack(pady=5)

        self.from_unit_combo = ttk.Combobox(root, values=self.units, state='readonly', font=('Arial', 12), justify='center')
        self.from_unit_combo.current(0)
        self.from_unit_combo.pack(pady=5)

        self.to_unit_label = tk.Label(root, text="To Unit:", bg='#1e1e1e', fg='white', font=('Arial', 12))
        self.to_unit_label.pack(pady=5)

        self.to_unit_combo = ttk.Combobox(root, values=self.units, state='readonly', font=('Arial', 12), justify='center')
        self.to_unit_combo.current(1)
        self.to_unit_combo.pack(pady=5)

        self.convert_button = tk.Button(root, text="Convert", command=self.convert, font=('Arial', 12, 'bold'), bg='#ff9500', fg='white', activebackground='#ffa733', relief='raised')
        self.convert_button.pack(pady=20)

        self.result_label = tk.Label(root, text="Result: ", bg='#1e1e1e', fg='#00ff00', font=('Arial', 16, 'bold'))
        self.result_label.pack(pady=10)

    # Convert button handler
    def convert(self):
        value = self.value_entry.get()
        from_unit = self.from_unit_combo.get()
        to_unit = self.to_unit_combo.get()

        # CPU-bound conversion in separate process
        future = self.executor_process.submit(convert_temperature, value, from_unit, to_unit)
        result = future.result()

        self.result_label.config(text=f"Result: {result} {to_unit}")

        # Log conversion asynchronously
        history_entry = f"{value} {from_unit} -> {result} {to_unit}"
        self.executor_thread.submit(log_history, history_entry)

# Run the application
if __name__ == '__main__':
    root = tk.Tk()
    app = TemperatureConverterApp(root)
    root.mainloop()