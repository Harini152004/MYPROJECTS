import speech_recognition as sr
import sounddevice as sd
import numpy as np
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import webbrowser
import pyjokes
import requests
import json
import nltk
from collections import Counter
from nltk.corpus import stopwords
import re
import time
from googlesearch import search

# Download stopwords if not already available
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Initialize recognizer and speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)


def talk(text):
    """Converts text to speech."""
    print("🤖 Alexa:", text)
    engine.say(text)
    engine.runAndWait()


def record_audio(duration=10, samplerate=44100):
    """Records audio and converts it to speech recognition format."""
    print("🎙️ Listening to discussion...")
    try:
        audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
        sd.wait()
        return np.frombuffer(audio_data, dtype=np.int16)
    except Exception as e:
        print(f"Recording Error: {e}")
        return None


def recognize_speech():
    """Listens to discussion and converts speech to text."""
    try:
        audio = record_audio()
        if audio is not None:
            audio_data = sr.AudioData(audio.tobytes(), 44100, 2)
            discussion_text = recognizer.recognize_google(audio_data).lower()
            print("📝 Recognized Discussion:", discussion_text)
            return discussion_text
    except sr.UnknownValueError:
        talk("I couldn't understand the discussion.")
    except sr.RequestError:
        talk("There was an error processing the audio.")
    return ""


def extract_topics(text):
    """Extracts key topics from discussion using NLP."""
    words = re.findall(r'\b\w+\b', text)  # Tokenize words
    filtered_words = [word for word in words if word.lower() not in stop_words]  # Remove stopwords

    if not filtered_words:
        return []

    most_common_words = Counter(filtered_words).most_common(3)  # Get top 3 topics
    topics = [word[0] for word in most_common_words]
    return topics


def get_wikipedia_info(topic):
    """Fetches summary from Wikipedia for the detected topic."""
    try:
        search_results = wikipedia.search(topic)
        if search_results:
            info = wikipedia.summary(search_results[0], sentences=2)
            return info
        else:
            return "I couldn't find reliable info on Wikipedia."
    except wikipedia.exceptions.DisambiguationError:
        return f"Multiple meanings found for {topic}. Try being more specific."
    except wikipedia.exceptions.PageError:
        return f"Sorry, I couldn't find information on {topic}."
    except:
        return "An error occurred while fetching information."


def google_search(query):
    """Opens a Google search for the query in the default web browser."""
    try:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Searching Google for: {query}"
    except Exception as e:
        print(f"Google Search Error: {e}")
        return "I couldn't open the Google search."



def listen_and_respond():
    """Listens to a discussion, extracts topics, and provides responses."""
    discussion_text = recognize_speech()
    if not discussion_text:
        talk("I couldn't pick up any meaningful discussion.")
        return

    topics = extract_topics(discussion_text)

    if not topics:
        talk("I didn't detect any clear topics. Can you rephrase?")
        return

    talk(f"I detected the following topics: {', '.join(topics)}.")

    for topic in topics:
        wiki_info = get_wikipedia_info(topic)
        google_link = google_search(topic)

        response = f"{topic}: {wiki_info}. More details: {google_link}"
        talk(response)

def get_weather(city="New York"):
    """Fetches weather information from OpenWeatherMap API."""
    api_key = "********************************"  # Replace with a valid API key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        weather_data = json.loads(response.text)
        temp = weather_data["main"]["temp"]
        description = weather_data["weather"][0]["description"]
        talk(f"The current temperature in {city} is {temp} degrees Celsius with {description}.")
    except:
        talk("Sorry, I couldn't fetch the weather data.")



def run_alexa():
    """Processes user commands and performs tasks."""
    command = recognize_speech()
    print(f"🛠️ Command Detected: {command}")

    if not command:
        talk("I couldn't hear anything clearly.")
        return

    if 'play' in command:
        song = command.replace('play', '').strip()
        talk(f'Playing {song}')
        pywhatkit.playonyt(song)
    elif 'time' in command:
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        talk(f'Current time is {current_time}')
    elif 'who is' in command or 'what is' in command:
        topic = command.replace('who is', '').replace('what is', '').strip()
        info = get_wikipedia_info(topic)
        talk(info)
    elif 'weather' in command:
        talk("Please tell me the city name.")
        city = recognize_speech()
        if city:
            get_weather(city)

    elif 'date' in command:
        talk('Sorry, I have a headache')
    elif 'are you single' in command:
        talk('I am in a relationship with WiFi')
    elif 'joke' in command:
        talk(pyjokes.get_joke())
    elif 'weather' in command:
        talk("Please tell me the city name.")
        city = recognize_speech()
        if city:
            get_weather(city)
    elif 'listen to discussion' in command or 'topic' in command:
        listen_and_respond()
    else:
        talk("opening google")
        google_result = google_search(command)
        talk(f"Here is what I found: {google_result}")


while True:
    run_alexa()
