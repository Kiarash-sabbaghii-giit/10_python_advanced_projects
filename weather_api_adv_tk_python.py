import tkinter as tk
from tkinter import ttk, messagebox
import threading
import multiprocessing
import requests
import logging
from datetime import datetime
import json
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weather_app.log'),
        logging.StreamHandler()
    ]
)


class WeatherAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.logger = logging.getLogger(__name__)

    def get_weather_by_coords(self, lat, lon):
        """Get weather data by coordinates - IO Bound"""
        try:
            self.logger.info(f"Fetching weather for lat: {lat}, lon: {lon}")
            url = f"{self.base_url}?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            raise

    def get_city_coordinates(self, city_name):
        """Get coordinates for city name - IO Bound"""
        try:
            url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={self.api_key}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data:
                return data[0]['lat'], data[0]['lon'], data[0]['country']
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Geocoding request failed: {e}")
            raise


class WeatherProcessor:
    """CPU Bound operations for weather data processing"""

    @staticmethod
    def process_weather_data(raw_data):
        """Process raw weather data - CPU Bound"""
        start_time = time.time()

        # Simulate CPU-intensive processing
        processed_data = {
            'temperature': round(raw_data['main']['temp'], 1),
            'feels_like': round(raw_data['main']['feels_like'], 1),
            'humidity': raw_data['main']['humidity'],
            'pressure': raw_data['main']['pressure'],
            'wind_speed': raw_data['wind']['speed'],
            'wind_direction': WeatherProcessor._get_wind_direction(raw_data['wind'].get('deg', 0)),
            'description': raw_data['weather'][0]['description'].title(),
            'city': raw_data['name'],
            'country': raw_data['sys']['country'],
            'visibility': raw_data.get('visibility', 'N/A'),
            'sunrise': WeatherProcessor._format_timestamp(raw_data['sys']['sunrise']),
            'sunset': WeatherProcessor._format_timestamp(raw_data['sys']['sunset']),
            'icon': raw_data['weather'][0]['icon']
        }

        # Additional calculations
        processed_data['temp_min'] = round(raw_data['main']['temp_min'], 1)
        processed_data['temp_max'] = round(raw_data['main']['temp_max'], 1)

        processing_time = time.time() - start_time
        logging.info(f"Weather data processed in {processing_time:.3f} seconds")

        return processed_data

    @staticmethod
    def _get_wind_direction(degrees):
        """Convert wind degrees to direction"""
        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                      'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        index = round(degrees / 22.5) % 16
        return directions[index]

    @staticmethod
    def _format_timestamp(timestamp):
        """Format UNIX timestamp to readable time"""
        return datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Weather App")
        self.root.configure(bg='#1a1a1a')
        self.root.geometry('800x700')

        # API configuration
        self.api_key = "your key!"
        self.weather_api = WeatherAPI(self.api_key)

        # Popular cities database - MOVED THIS BEFORE setup_ui()
        self.cities = {
            "New York": (40.7128, -74.0060),
            "London": (51.5074, -0.1278),
            "Tokyo": (35.6895, 139.6917),
            "Paris": (48.8566, 2.3522),
            "Sydney": (-33.8688, 151.2093),
            "Dubai": (25.2048, 55.2708),
            "Singapore": (1.3521, 103.8198),
            "Mumbai": (19.0760, 72.8777),
            "Berlin": (52.5200, 13.4050),
            "Rome": (41.9028, 12.4964)
        }

        self.setup_ui()
        self.logger = logging.getLogger(__name__)

    def setup_ui(self):
        """Setup professional UI with dark theme"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#1a1a1a', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(
            main_frame,
            text="🌤 Professional Weather Dashboard",
            font=('Arial', 24, 'bold'),
            fg='white',
            bg='#1a1a1a'
        )
        title_label.pack(pady=(0, 30))

        # Input frame
        input_frame = tk.Frame(main_frame, bg='#1a1a1a')
        input_frame.pack(fill=tk.X, pady=(0, 20))

        # Mode selection
        mode_frame = tk.Frame(input_frame, bg='#1a1a1a')
        mode_frame.pack(fill=tk.X, pady=(0, 15))

        self.mode_var = tk.StringVar(value="coords")
        tk.Radiobutton(
            mode_frame, text="Coordinates", variable=self.mode_var,
            value="coords", command=self.toggle_input_mode,
            font=('Arial', 10), fg='white', bg='#1a1a1a', selectcolor='black'
        ).pack(side=tk.LEFT, padx=(0, 20))

        tk.Radiobutton(
            mode_frame, text="City Name", variable=self.mode_var,
            value="city", command=self.toggle_input_mode,
            font=('Arial', 10), fg='white', bg='#1a1a1a', selectcolor='black'
        ).pack(side=tk.LEFT)

        # Coordinates input frame
        self.coords_frame = tk.Frame(input_frame, bg='#1a1a1a')

        tk.Label(self.coords_frame, text="Latitude:",
                 font=('Arial', 10), fg='white', bg='#1a1a1a').grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.lat_entry = tk.Entry(self.coords_frame, font=('Arial', 11), width=15, bg='#333', fg='white',
                                  insertbackground='white')
        self.lat_entry.grid(row=0, column=1, padx=(0, 20))

        tk.Label(self.coords_frame, text="Longitude:",
                 font=('Arial', 10), fg='white', bg='#1a1a1a').grid(row=0, column=2, sticky='w', padx=(0, 10))
        self.lon_entry = tk.Entry(self.coords_frame, font=('Arial', 11), width=15, bg='#333', fg='white',
                                  insertbackground='white')
        self.lon_entry.grid(row=0, column=3, padx=(0, 20))

        # City input frame
        self.city_frame = tk.Frame(input_frame, bg='#1a1a1a')

        tk.Label(self.city_frame, text="City Name:",
                 font=('Arial', 10), fg='white', bg='#1a1a1a').pack(side=tk.LEFT, padx=(0, 10))
        self.city_entry = tk.Entry(self.city_frame, font=('Arial', 11), width=20, bg='#333', fg='white',
                                   insertbackground='white')
        self.city_entry.pack(side=tk.LEFT, padx=(0, 20))

        # Quick cities dropdown
        tk.Label(self.city_frame, text="Quick Select:",
                 font=('Arial', 10), fg='white', bg='#1a1a1a').pack(side=tk.LEFT, padx=(0, 10))
        self.city_var = tk.StringVar()
        city_dropdown = ttk.Combobox(self.city_frame, textvariable=self.city_var,
                                     values=list(self.cities.keys()), state="readonly",
                                     font=('Arial', 10), width=15)
        city_dropdown.pack(side=tk.LEFT)
        city_dropdown.bind('<<ComboboxSelected>>', self.on_city_selected)

        self.coords_frame.pack(fill=tk.X)

        # Submit button
        self.submit_btn = tk.Button(
            input_frame,
            text="Get Weather Data",
            command=self.get_weather,
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='white',
            padx=30,
            pady=10,
            cursor='hand2'
        )
        self.submit_btn.pack(pady=15)

        # Loading indicator
        self.loading_label = tk.Label(
            input_frame,
            text="",
            font=('Arial', 10),
            fg='yellow',
            bg='#1a1a1a'
        )
        self.loading_label.pack()

        # Results frame
        self.results_frame = tk.Frame(main_frame, bg='#2d2d2d', relief=tk.RAISED, bd=1)
        self.results_frame.pack(fill=tk.BOTH, expand=True)

        # Initialize results display
        self.setup_results_display()

    def toggle_input_mode(self):
        """Toggle between coordinates and city input mode"""
        if self.mode_var.get() == "coords":
            self.city_frame.pack_forget()
            self.coords_frame.pack(fill=tk.X)
        else:
            self.coords_frame.pack_forget()
            self.city_frame.pack(fill=tk.X)

    def on_city_selected(self, event):
        """Handle city selection from dropdown"""
        selected_city = self.city_var.get()
        if selected_city in self.cities:
            self.city_entry.delete(0, tk.END)
            self.city_entry.insert(0, selected_city)

    def setup_results_display(self):
        """Setup the results display area"""
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Main results container
        container = tk.Frame(self.results_frame, bg='#2d2d2d', padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        # City name and country
        self.city_label = tk.Label(
            container,
            text="Select location to see weather",
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#2d2d2d'
        )
        self.city_label.pack(pady=(0, 20))

        # Weather grid
        grid_frame = tk.Frame(container, bg='#2d2d2d')
        grid_frame.pack(fill=tk.BOTH, expand=True)

        # Left column
        left_frame = tk.Frame(grid_frame, bg='#2d2d2d')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Right column
        right_frame = tk.Frame(grid_frame, bg='#2d2d2d')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Temperature
        self.temp_label = self.create_info_card(left_frame, "Temperature", "N/A", "°C")
        self.temp_label.pack(fill=tk.X, pady=(0, 10))

        # Feels like
        self.feels_like_label = self.create_info_card(left_frame, "Feels Like", "N/A", "°C")
        self.feels_like_label.pack(fill=tk.X, pady=(0, 10))

        # Weather description
        self.desc_label = self.create_info_card(left_frame, "Conditions", "N/A", "")
        self.desc_label.pack(fill=tk.X, pady=(0, 10))

        # Humidity
        self.humidity_label = self.create_info_card(left_frame, "Humidity", "N/A", "%")
        self.humidity_label.pack(fill=tk.X, pady=(0, 10))

        # Pressure
        self.pressure_label = self.create_info_card(right_frame, "Pressure", "N/A", "hPa")
        self.pressure_label.pack(fill=tk.X, pady=(0, 10))

        # Wind
        self.wind_label = self.create_info_card(right_frame, "Wind Speed", "N/A", "m/s")
        self.wind_label.pack(fill=tk.X, pady=(0, 10))

        # Visibility
        self.visibility_label = self.create_info_card(right_frame, "Visibility", "N/A", "meters")
        self.visibility_label.pack(fill=tk.X, pady=(0, 10))

        # Sunrise/Sunset
        self.sun_times_label = self.create_info_card(right_frame, "Sunrise/Sunset", "N/A / N/A", "")
        self.sun_times_label.pack(fill=tk.X, pady=(0, 10))

    def create_info_card(self, parent, title, value, unit):
        """Create a professional info card"""
        card = tk.Frame(parent, bg='#3d3d3d', relief=tk.RAISED, bd=1, padx=15, pady=10)

        # Title
        title_label = tk.Label(
            card,
            text=title,
            font=('Arial', 10, 'bold'),
            fg='#cccccc',
            bg='#3d3d3d'
        )
        title_label.pack(anchor='w')

        # Value
        value_label = tk.Label(
            card,
            text=f"{value} {unit}",
            font=('Arial', 12),
            fg='white',
            bg='#3d3d3d'
        )
        value_label.pack(anchor='w')

        return card

    def get_weather(self):
        """Main method to fetch and process weather data"""
        self.loading_label.config(text="Loading weather data...")
        self.submit_btn.config(state=tk.DISABLED)

        # Run API call in thread (IO Bound)
        thread = threading.Thread(target=self._fetch_weather_thread)
        thread.daemon = True
        thread.start()

    def _fetch_weather_thread(self):
        """Thread for IO-bound API calls"""
        try:
            if self.mode_var.get() == "coords":
                lat = self.lat_entry.get().strip()
                lon = self.lon_entry.get().strip()

                if not lat or not lon:
                    self.root.after(0,
                                    lambda: messagebox.showerror("Error", "Please enter both latitude and longitude"))
                    return

                try:
                    lat_float = float(lat)
                    lon_float = float(lon)
                except ValueError:
                    self.root.after(0, lambda: messagebox.showerror("Error", "Please enter valid numeric coordinates"))
                    return

                raw_data = self.weather_api.get_weather_by_coords(lat_float, lon_float)

            else:  # City mode
                city_name = self.city_entry.get().strip()
                if not city_name:
                    self.root.after(0, lambda: messagebox.showerror("Error", "Please enter a city name"))
                    return

                coords_data = self.weather_api.get_city_coordinates(city_name)
                if not coords_data:
                    self.root.after(0, lambda: messagebox.showerror("Error", "City not found"))
                    return

                lat, lon, country = coords_data
                raw_data = self.weather_api.get_weather_by_coords(lat, lon)

            # Process data using multiprocessing (CPU Bound)
            self._process_weather_data(raw_data)

        except Exception as e:
            self.logger.error(f"Weather fetch error: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch weather data: {str(e)}"))
            self.root.after(0, self._reset_ui)

    def _process_weather_data(self, raw_data):
        """Process weather data using multiprocessing for CPU-bound tasks"""

        def process_callback(result):
            self.root.after(0, lambda: self._display_weather_data(result))

        def process_error_callback(error):
            self.logger.error(f"Processing error: {error}")
            self.root.after(0, lambda: messagebox.showerror("Error", "Failed to process weather data"))
            self.root.after(0, self._reset_ui)

        # Use multiprocessing for CPU-bound task
        pool = multiprocessing.Pool(1)
        pool.apply_async(
            WeatherProcessor.process_weather_data,
            (raw_data,),
            callback=process_callback,
            error_callback=process_error_callback
        )
        pool.close()

    def _display_weather_data(self, processed_data):
        """Display processed weather data in UI"""
        try:
            # Update UI with weather data
            self.city_label.config(text=f"{processed_data['city']}, {processed_data['country']}")

            # Update all info cards
            self._update_info_card(self.temp_label, f"{processed_data['temperature']} °C")
            self._update_info_card(self.feels_like_label, f"{processed_data['feels_like']} °C")
            self._update_info_card(self.desc_label, processed_data['description'])
            self._update_info_card(self.humidity_label, f"{processed_data['humidity']} %")
            self._update_info_card(self.pressure_label, f"{processed_data['pressure']} hPa")
            self._update_info_card(self.wind_label,
                                   f"{processed_data['wind_speed']} m/s {processed_data['wind_direction']}")

            visibility_text = f"{processed_data['visibility']}" if processed_data['visibility'] != 'N/A' else "N/A"
            self._update_info_card(self.visibility_label, f"{visibility_text} meters")

            self._update_info_card(self.sun_times_label, f"{processed_data['sunrise']} / {processed_data['sunset']}")

            self.logger.info(f"Weather data displayed for {processed_data['city']}")

        except Exception as e:
            self.logger.error(f"Display error: {e}")
            messagebox.showerror("Error", "Failed to display weather data")
        finally:
            self._reset_ui()

    def _update_info_card(self, card, new_value):
        """Update the value in an info card"""
        value_label = card.winfo_children()[1]  # Second child is the value label
        value_label.config(text=new_value)

    def _reset_ui(self):
        """Reset UI elements after operation"""
        self.loading_label.config(text="")
        self.submit_btn.config(state=tk.NORMAL)


def main():
    """Main application entry point"""
    try:
        root = tk.Tk()
        app = WeatherApp(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"Application error: {e}")
        messagebox.showerror("Fatal Error", f"The application encountered an error: {str(e)}")


if __name__ == "__main__":
    main()