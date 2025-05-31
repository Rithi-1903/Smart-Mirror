import speech_recognition as sr
import pyttsx3
import time
import webbrowser

from google_voice_search import listen_for_command  # ✅ Import listen_for_command
from google_voice_search import google_search
from youtube_voice_search import search_youtube  # ✅ Import YouTube search function

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()

def speak(text):
    """Convert text to speech"""
    engine.say(text)
    engine.runAndWait()

def voice_assistant(root, home_screen, web_searcher):
    """Main function to listen and respond to voice commands"""
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.pause_threshold = 0.8

    while True:
        try:
            with sr.Microphone() as source:
                print("Listening...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=5)

                try:
                    command = recognizer.recognize_google(audio).lower()
                    print(f"Recognized: {command}")

                    if "hello smart" in command:
                        home_screen.show_greeting("Hello there! Welcome back!")  # ✅ Fix: Added text argument
                        speak("What would you like to perform?")

                    elif "google search" in command:
                        speak("What would you like to search for?")
                        query = listen_for_command()

                        if query:
                            speak(f"Searching for {query}")
                            from google_voice_search import display_search_results
                            display_search_results(root, query, home_screen)  # ✅ Now correctly displays and allows selection
                        else:
                            speak("I didn't understand. Please try again.")

                    elif "youtube search" in command:
                        speak("What would you like to search on YouTube?")
                        search_youtube(root, home_screen)  # ✅ Calls YouTube search function

                    elif "go home" in command:
                        home_screen.show_main_screen()
                        speak("Returning to home screen")

                    elif "search" in command:
                        query = command.replace("search", "").strip()
                        speak(f"Searching the web for {query}")
                        web_searcher.search(query)  # Calls web search

                    elif "exit" in command or "close" in command:
                        speak("Goodbye!")
                        root.quit()
                        break

                    else:
                        speak("I'm sorry, I didn't understand that command.")

                except sr.UnknownValueError:
                    speak("Sorry, I didn't catch that.")
                except sr.RequestError:
                    speak("API is currently unavailable.")

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)
