import json
import tkinter as tk
from datetime import datetime

def load_events(file_path="events.json"):
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


def display_events():
    """Fetch and return formatted events as text."""
    events = load_events()
    
    if not events:
        return "No events found!"

    event_text = ""
    for event in events:
        start_time = datetime.fromisoformat(event["start_time"])
        end_time = datetime.fromisoformat(event["end_time"])

        event_text += f"📅 {event['title']}\n"
        event_text += f"   🕒 Start: {start_time.strftime('%Y-%m-%d %I:%M %p')}\n"
        event_text += f"   🕒 End: {end_time.strftime('%Y-%m-%d %I:%M %p')}\n\n"  # Extra line for spacing
    
    return event_text.strip()  # Remove trailing newline

def create_gui():
    """Create a Tkinter window and place event text in bottom-left corner."""
    root = tk.Tk()
    root.title("Event Viewer")

    # Set window size
    root.geometry("800x600")  # Width x Height
    root.configure(bg="black")

    # Fetch events
    event_text = display_events()

    # Label to display events
    event_label = tk.Label(root, text=event_text, font=("Arial", 14), 
                           fg="white", bg="black", justify="left", anchor="sw")
    
    # Position the label slightly above the bottom-left corner
    event_label.place(relx=0.02, rely=0.85, anchor="sw")  # Adjust rely for height

    root.mainloop()

# Run the GUI
create_gui()
