import tkinter as tk
import threading
import json
from datetime import datetime
from home import HomeScreen
from voice_assistant import voice_assistant  # ✅ Import full voice assistant function
from youtube_voice_search import search_youtube
from google_voice_search import listen_for_command, google_search

class SmartMirrorApp:
    def __init__(self):
        """Initialize the Smart Mirror application."""
        # Initialize Tkinter Window
        self.root = tk.Tk()
        self.root.title("Smart Mirror OS")
        self.root.configure(bg="black")
        self.root.attributes('-fullscreen', True)

        # Initialize Home Screen
        self.home_screen = HomeScreen(self.root)

        # Display Events
        self.display_events()

        # Start voice assistant in a separate thread ✅
        self.start_voice_assistant()

        # Close app with Escape key
        self.root.bind("<Escape>", lambda e: self.cleanup_and_exit())


    def load_events(self, file_path="events.json"):
        """Load events from JSON file."""
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
                print("Loaded Events:", data)  # Debugging
                return data.get("events", [])  # Return events list
        except FileNotFoundError:
            print("Error: events.json file not found!")
            return []
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in events.json!")
            return []

    def display_events(self):
        """Fetch and display events in the Tkinter window."""
        events = self.load_events()
        
        if not events:
            event_text = "No Events"
        else:
            event_text = ""
            for event in events:
                start_time = datetime.fromisoformat(event["start_time"])
                end_time = datetime.fromisoformat(event["end_time"])
                event_text += f"📅 {event['title']}\n"
                event_text += f"   🕒 Start: {start_time.strftime('%Y-%m-%d %I:%M %p')}\n"
                event_text += f"   🕒 End: {end_time.strftime('%Y-%m-%d %I:%M %p')}\n\n\n"  # Extra line for spacing
        
        # Label to display events
        self.event_label = tk.Label(self.root, text=event_text.strip(), font=("Arial", 14), 
                                    fg="white", bg="black", justify="left", anchor="sw")
        
        # Position the label slightly above the bottom-left corner
        self.event_label.place(relx=0.02, rely=0.85, anchor="sw")  # Adjust rely for height
        

    def start_voice_assistant(self):
        """Start the voice assistant in a separate thread to keep it listening."""
        threading.Thread(target=voice_assistant, args=(self.root, self.home_screen, self), daemon=True).start()

    def cleanup_and_exit(self):
        """Ensure proper cleanup before exiting."""
        self.root.quit()
        self.root.destroy()

    def run(self):
        """Run the Tkinter main loop."""
        self.root.mainloop()

if __name__ == "__main__":
    app = SmartMirrorApp()
    app.run()
