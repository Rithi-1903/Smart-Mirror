import speech_recognition as sr
import pyttsx3
import webbrowser
import time
import tkinter as tk
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import os

# Initialize Text-to-Speech
engine = pyttsx3.init()

def speak(text):
    """Convert text to speech"""
    engine.say(text)
    engine.runAndWait()

def listen_for_command(timeout=5):
    """Capture voice input with error handling"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=timeout)
            command = recognizer.recognize_google(audio).lower()
            print(f"Recognized: {command}")
            return command
        except sr.UnknownValueError:
            print("Could not understand.")
            return None
        except sr.RequestError:
            print("Check your internet connection.")
            return None
        except sr.WaitTimeoutError:
            print("Listening timed out.")
            return None

def google_search(query, max_results=5):
    """Fetch search results from Google"""
    try:
        return list(search(query, num_results=max_results))
    except Exception as e:
        print(f"Search failed: {e}")
        return []

def open_selected_result(results, root, home_screen):
    """Ask user to select an option using mapped keywords or go home"""
    speak("Please select an option by saying the number, such as 'option one', or say 'Go Home' to return.")

    option_mapping = {
        "one": 0, "option one": 0, "first": 0, "option 1": 0, "option on": 0, "option o": 0,
        "two": 1, "option two": 1, "second": 1, "option 2": 1, "option tw": 1, "option to": 1, "option too": 1, " too": 1, "to": 1,
        "three": 2, "option three": 2, "third": 2, "option 3": 2, "option the": 2, "option tree": 2, "option thr": 2, "option thre": 2, "option threee":2,
        "four": 3, "option four": 3, "fourth": 3, "option 4": 3, "option fou": 3, "option for": 3, "option fo": 3, "for": 3, "option fourr": 3, "option fur":3,
        "five": 4, "option five": 4, "fifth": 4, "option 5": 4, "option fiv": 4, "option fi": 4, "option fivee":4, "option fivth":4, "option fivve":4, "option fee":4, 
    }
    
    while True:
        user_input = listen_for_command()
        
        if user_input == "go home":
            speak("Returning to home screen.")
            home_screen.show_main_screen()
            return
        
        if user_input in option_mapping:
            selected_index = option_mapping[user_input]
            if selected_index < len(results):
                url = results[selected_index]
                speak(f"Opening {url}")
                open_and_read_url(url, root, home_screen)
                return
        
        speak("Invalid choice. Please try again.")

def open_and_read_url(url, root, home_screen):
    """Open URL, read content, then return home"""
    webbrowser.open(url)
    time.sleep(5)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        content = " ".join(p.text for p in paragraphs[:5])
        speak(content if content.strip() else "Sorry, I couldn't read the content.")
    except Exception as e:
        print(f"Error reading webpage: {e}")
        speak("I couldn't read the webpage content.")
    close_browser()
    
    # Ensure we return to the home screen
    for widget in root.winfo_children():
        widget.destroy()
    home_screen.show_main_screen()
    speak("Returning to the home screen.")

def close_browser():
    """Close browser after reading content"""
    os.system("taskkill /IM chrome.exe /F")
    os.system("taskkill /IM firefox.exe /F")
    os.system("pkill -f firefox")
    os.system("pkill -f chrome")

def display_search_results(root, query, home_screen):
    """Display search results and allow user to choose or go home"""
    results = google_search(query)
    if not results:
        speak("No results found.")
        return
    
    result_frame = tk.Frame(root, bg="black")
    result_frame.pack(fill="both", expand=True)
    title_label = tk.Label(result_frame, text="Google Search Results", font=("Arial", 20), bg="black", fg="white")
    title_label.pack(pady=10)
    
    for idx, link in enumerate(results, 1):
        label = tk.Label(result_frame, text=f"{idx}. {link}", font=("Arial", 14), bg="black", fg="white", anchor="w")
        label.pack(fill="x", padx=20, pady=2)
    
    for idx, link in enumerate(results, 1):
        speak(f"Result {idx}: {link}")
    
    open_selected_result(results, root, home_screen)

def get_valid_query():
    """Keep asking for a valid query until recognized"""
    while True:
        speak("What would you like to search for on Google? You can say 'Go Home' anytime.")
        query = listen_for_command()
        if query:
            if query == "go home":
                speak("Returning to home screen.")
                return "go home"
            return query
        speak("I didn't understand. Please say it again.")

def main():
    """Main function to initiate UI and search functionality"""
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.configure(bg="black")
    
    class HomeScreen:
        def show_main_screen(self):
            for widget in root.winfo_children():
                widget.destroy()
            label = tk.Label(root, text="Voice Assistant Home", font=("Arial", 24), fg="white", bg="black")
            label.pack(expand=True)
            speak("Welcome home.")
    
    home_screen = HomeScreen()
    home_screen.show_main_screen()
    
    while True:
        query = get_valid_query()
        if query == "go home":
            home_screen.show_main_screen()
            continue
        
        speak(f"Searching for {query}")
        display_search_results(root, query, home_screen)
    
    root.mainloop()

if __name__ == "__main__":
    main()
