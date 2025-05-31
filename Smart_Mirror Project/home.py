import tkinter as tk
import datetime
import calendar
import requests
import threading
import pyttsx3
import queue
import json

API_KEY = "a1b4584c1be3ed0ad82ffed7d01a83e5"
CITY = "Kalpetta"
WEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
EVENTS_FILE = "events.json"

class HomeScreen:
    def __init__(self, root):
        self.root = root
        self.engine = pyttsx3.init()
        self.weather_queue = queue.Queue()
        self.setup_ui()
        self.check_weather_queue()

    def setup_ui(self):
        """Initialize all UI components"""
        self.root.configure(bg="black")

        # Date Label
        self.date_label = tk.Label(self.root, text="", font=("Arial", 35, "bold"), fg="white", bg="black")
        self.date_label.place(relx=0.5, rely=0.1, anchor="center")

        # Weather Label
        self.weather_label = tk.Label(self.root, text="Fetching Weather...", font=("Arial", 30), fg="white", bg="black")
        self.weather_label.place(x=50, y=200)

        # Time Label
        self.time_label = tk.Label(self.root, text="", font=("Arial", 60, "bold"), fg="white", bg="black")
        self.time_label.place(relx=0.9, rely=0.4, anchor="e")

        # Greeting Label
        self.greeting_label = tk.Label(self.root, text="", font=("Arial", 30), fg="white", bg="black")
        self.greeting_label.place(relx=0.9, rely=0.5, anchor="e")

        # Calendar Label
        self.calendar_label = tk.Label(self.root, text="", font=("Courier", 18), fg="white", bg="black", justify=tk.LEFT)
        self.calendar_label.place(relx=0.9, rely=0.85, anchor="e")

        # Events Label
        self.events_label = tk.Label(self.root, text="", font=("Arial", 20), fg="white", bg="black", justify=tk.LEFT, anchor="w")
        self.events_label.place(relx=0.1, rely=0.75, anchor="w")

        # Start updates
        self.update_time()
        self.update_calendar()
        self.update_events()
        threading.Thread(target=self.get_weather, daemon=True).start()

        

    def check_weather_queue(self):
        """Check for weather updates from the queue"""
        try:
            while True:
                weather_data = self.weather_queue.get_nowait()
                self.weather_label.config(text=weather_data)
        except queue.Empty:
            pass
        self.root.after(100, self.check_weather_queue)

    def update_time(self):
        """Update time and greeting"""
        now = datetime.datetime.now()
        self.time_label.config(text=now.strftime("%H:%M:%S"))
        self.date_label.config(text=now.strftime("%A, %d %B %Y"))

        hour = now.hour
        if 5 <= hour < 12:
            greeting = "Good Morning ☀️"
        elif 12 <= hour < 16:
            greeting = "Good Afternoon ☀️"
        else:
            greeting = "Good Night 🌙"
        self.greeting_label.config(text=greeting)

        self.time_label.after(1000, self.update_time)

    def update_calendar(self):
        """Update calendar display"""
        now = datetime.datetime.now()
        cal_text = calendar.TextCalendar(calendar.MONDAY).formatmonth(now.year, now.month)
        self.calendar_label.config(text=cal_text)
        self.calendar_label.after(60000, self.update_calendar)

    def show_greeting(self, text):
        """Speak out the greeting using text-to-speech"""
        self.engine.say(text)
        self.engine.runAndWait()
    

    def update_events(self):
        """Load and display events from events.json properly"""
        try:
            with open(EVENTS_FILE, "r") as file:
                events = json.load(file)

            event_texts = [f"📅 {event['title']}\n\n🕒 Start: {event['start_time']}\n\n🕒 End: {event['end_time']}\n\n\n" for event in events]
            event_text = "\n".join(event_texts) if event_texts else "No Events Available"
        except Exception:
            event_text = "No Events Available"

        if hasattr(self, 'events_label'):
            self.events_label.config(text=event_text, anchor="w", justify="left", wraplength=500)
            self.events_label.place(x=50, y=450)

        self.root.after(60000, self.update_events)

    def get_weather(self):
        """Fetch weather data and update UI through queue"""
        try:
            response = requests.get(WEATHER_URL)
            data = response.json()

            if response.status_code == 200:
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"].capitalize()
                weather_data = f"{temp}°C\n{desc}"
                self.weather_queue.put(weather_data)
            else:
                self.weather_queue.put("Weather API Error\nTry again later")
        except Exception as e:
            print(f"Error fetching weather: {e}")
            self.weather_queue.put("Weather Error\nCheck connection")

    def show_main_screen(self):
        self.hide_all_widgets()
        self.setup_ui()
        self.update_events()
        
            
    def hide_all_widgets(self):
        """Hide all widgets on the home screen."""
        for widget in self.root.winfo_children():
            widget.place_forget()        

# Run the Tkinter App
if __name__ == "__main__":
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    app = HomeScreen(root)
    root.mainloop()