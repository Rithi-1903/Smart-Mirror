import speech_recognition as sr 
import pyttsx3
import webbrowser
import requests
import subprocess
import time
from googleapiclient.discovery import build
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
import re
import os
import signal

# Replace with your YouTube API Key
API_KEY = "AIzaSyAt79idOwyWxfc-yhPFjvFkgBdBCXkrFgs"

# Initialize Speech Engine
engine = pyttsx3.init()

def speak(text):
    """Convert text to speech"""
    engine.say(text)
    engine.runAndWait()

def listen_for_command():
    """Capture voice input and convert it to text"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio).lower()
            print(f"Recognized: {command}")
            return command
        except sr.UnknownValueError:
            print("Could not understand the command.")
            return None
        except sr.RequestError:
            print("Could not request results, check internet connection.")
            return None

def get_youtube_results(query, max_results=5):
    """Fetch top YouTube search results using API"""
    youtube = build("youtube", "v3", developerKey=API_KEY)
    request = youtube.search().list(
        q=query,
        part="snippet",
        maxResults=max_results,
        type="video"
    )
    response = request.execute()

    videos = []
    for i, item in enumerate(response.get("items", [])):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        thumbnail_url = item["snippet"]["thumbnails"]["medium"]["url"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        duration = get_video_duration(video_id)  # ✅ Get video duration
        videos.append({"title": title, "thumbnail": thumbnail_url, "url": video_url, "duration": duration})
    
    return videos

def get_video_duration(video_id):
    """Retrieve the duration of a YouTube video using API"""
    youtube = build("youtube", "v3", developerKey=API_KEY)
    request = youtube.videos().list(
        part="contentDetails",
        id=video_id
    )
    response = request.execute()
    
    if "items" in response and len(response["items"]) > 0:
        duration_iso = response["items"][0]["contentDetails"]["duration"]
        return parse_duration(duration_iso)
    
    return 0

def parse_duration(duration_iso):
    """Convert ISO 8601 duration format to seconds"""
    match = re.match(r'PT(\d+H)?(\d+M)?(\d+S)?', duration_iso)
    hours = int(match.group(1)[:-1]) * 3600 if match.group(1) else 0
    minutes = int(match.group(2)[:-1]) * 60 if match.group(2) else 0
    seconds = int(match.group(3)[:-1]) if match.group(3) else 0
    return hours + minutes + seconds

def display_youtube_results(root, home_screen, query):
    """Hide all elements and show YouTube search results on a blank screen"""
    videos = get_youtube_results(query)

    if not videos:
        speak("Sorry, no results found.")
        home_screen.show_main_screen()
        return

    # Hide home screen elements
    home_screen.hide_all_widgets()

    # Create a new frame for displaying search results
    search_frame = tk.Frame(root, bg="black")
    search_frame.pack(fill="both", expand=True)

    # Add centered "YouTube Search" label
    heading_label = tk.Label(search_frame, text="YouTube Search", fg="white", bg="black", 
                             font=("Arial", 24, "bold"))
    heading_label.pack(pady=10)

    # Add centered query topic label
    query_label = tk.Label(search_frame, text=query, fg="white", bg="black", font=("Arial", 16))
    query_label.pack(pady=5)

    video_labels = []
    thumbnails = []  # Keep a reference for images

    # Display search results first
    for i, video in enumerate(videos):
        # Fetch thumbnail image
        response = requests.get(video["thumbnail"])
        img_data = Image.open(BytesIO(response.content))
        img_data = img_data.resize((200, 120))
        img = ImageTk.PhotoImage(img_data)
        thumbnails.append(img)  # Store reference

        # Create a frame for each video
        video_frame = tk.Frame(search_frame, bg="black", pady=10)
        video_frame.pack(anchor="w", padx=20, pady=5)

        # Display thumbnail
        thumbnail_label = tk.Label(video_frame, image=img, bg="black")
        thumbnail_label.image = img
        thumbnail_label.pack(side="left", padx=10)

        # Display title
        title_label = tk.Label(video_frame, text=f"Option {i+1}: {video['title']}", 
                               fg="white", bg="black", font=("Arial", 14), wraplength=500)
        title_label.pack(side="left")

        video_labels.append((thumbnail_label, title_label))

    # Now read out the results
    speak("Here are the top YouTube results.")
    for i, video in enumerate(videos):
        speak(f"Option {i+1}: {video['title']}")

      

    # Ask user for option selection
    open_video(videos, root, home_screen, search_frame)
    # Continuously listen for "go home" command
    while True:
        command = listen_for_command()
        if command == "go home":
            speak("Going back to home screen.")
            search_frame.destroy()
            home_screen.show_main_screen()
            return    

def open_video(videos, root, home_screen, search_frame):
    """Ask user for selection, open video, and close browser when it finishes"""
    recognizer = sr.Recognizer()

    option_keywords = {
        "one": 0, "option one": 0, "first": 0, "option 1": 0, "option on": 0, "option o": 0,
        "two": 1, "option two": 1, "second": 1, "option 2": 1, "option tw": 1, "option to": 1, "option too": 1, " too": 1, "to": 1,
        "three": 2, "option three": 2, "third": 2, "option 3": 2, "option the": 2, "option tree": 2, "option thr": 2, "option thre": 2, "option threee":2,
        "four": 3, "option four": 3, "fourth": 3, "option 4": 3, "option fou": 3, "option for": 3, "option fo": 3, "for": 3, "option fourr": 3, "option fur":3,
        "five": 4, "option five": 4, "fifth": 4, "option 5": 4, "option fiv": 4, "option fi": 4, "option fivee":4, "option fivth":4, "option fivve":4, "option fee":4, 
    }
    
    while True:  
        speak("Which option would you like to select? Say Option 1, First, and so on.")
        with sr.Microphone() as source:
            try:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5)
                command = recognizer.recognize_google(audio).lower()
                print(f"User Selected: {command}")

                for keyword, index in option_keywords.items():
                    if keyword in command and index < len(videos):
                        speak(f"Opening {videos[index]['title']}")
                        webbrowser.open(videos[index]["url"])

                        # Get video duration & wait
                        duration = videos[index]["duration"]
                        print(f"Video duration: {duration} seconds")
                        time.sleep(duration + 5)  # Wait for video + buffer
                        close_browser()

                         #Ensure we return to the home screen
                        for widget in root.winfo_children():
                            widget.destroy()
                            home_screen.show_main_screen()
                        speak("Returning to the home screen.")

                        # Close browser

                        
                        speak("Returning to home screen.")
                        search_frame.destroy()
                        home_screen.show_main_screen()
                        return
                
                speak("I didn't understand your choice. Please try again.")

            except sr.UnknownValueError:
                speak("Sorry, I didn't catch that. Please say the option number again.")
            except sr.RequestError:
                speak("API is currently unavailable. Try again later.")

def close_browser():
    """Close browser after reading content"""
    os.system("taskkill /IM chrome.exe /F")
    os.system("taskkill /IM firefox.exe /F")
    os.system("pkill -f firefox")
    os.system("pkill -f chrome")

def search_youtube(root, home_screen):
    """Handle YouTube voice search with a blank screen display"""
    home_screen.hide_all_widgets()
    
    
    query = listen_for_command()
    if query:
        if "go home" in query.lower():
            speak("Returning to home screen")
            home_screen.show()  # Assuming 'show' method brings back the home screen
            return
        speak(f"Searching YouTube for {query}")
        display_youtube_results(root, home_screen, query)
    else:
        speak("I didn't understand. Please try again.")
