import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser
import os
import smtplib
import pyaudio
import cv2
import random
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import phonenumbers
from phonenumbers import geocoder, timezone, carrier
import pyautogui
from googletrans import Translator
import time

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


def wishMe():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 17:
        speak("Good Afternoon!")
    elif 17 <= hour < 19:
        speak("Good Evening!")
    else:
        speak("Good Night!")

    speak("I am BetelMatrix AI. Please tell me how may I help you")


def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that. Could you please repeat?")
        return "None"
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        return "None"
    return query


def sendEmail(to, content):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login('youremail@gmail.com', 'your-password-here')
    server.sendmail('youremail@gmail.com', to, content)
    server.close()


# Function to track hand motion and mark other objects
def track_objects_in_motion():
    # Initialize the camera
    cap = cv2.VideoCapture(0)

    # Check if the camera is opened successfully
    if not cap.isOpened():
        print("Error: Unable to open camera")
        return

    # Create a background subtractor object
    bg_subtractor = cv2.createBackgroundSubtractorMOG2()

    # Get the screen resolution
    screen_width, screen_height = pyautogui.size()

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Apply background subtraction
        fg_mask = bg_subtractor.apply(frame)

        # Find contours in the foreground mask
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Initialize a list to store the centroids of detected objects
        object_centroids = []

        # Draw bounding boxes around the contours and mark object centroids
        for contour in contours:
            if cv2.contourArea(contour) > 1000:
                x, y, w, h = cv2.boundingRect(contour)
                # Draw green rectangle for hand coordinates
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # Draw red rectangle for other coordinates
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                # Calculate centroid
                cx, cy = x + w // 2, y + h // 2
                object_centroids.append((cx, cy))
                # Mark centroid on frame
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

        # Calculate distance between objects
        if len(object_centroids) >= 2:
            # Assuming two objects are detected
            object1, object2 = object_centroids[:2]
            # Calculate Euclidean distance
            distance = np.sqrt((object1[0] - object2[0]) ** 2 + (object1[1] - object2[1]) ** 2)
            # Display distance on frame
            cv2.putText(frame, f"Distance: {distance:.2f} pixels", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (255, 255, 255), 2)

            # Scale the hand position to screen dimensions
            x = np.interp((object1[0] + object2[0]) / 2, [0, 640], [0, screen_width])
            y = np.interp((object1[1] + object2[1]) / 2, [0, 480], [0, screen_height])

            # Move the cursor
            pyautogui.moveTo(x, y)

        # Display the captured frame with object motion tracking
        cv2.imshow('Object Motion Tracker', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera
    cap.release()
    cv2.destroyAllWindows()


# Define a list of jokes
jokes = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "What did one plate say to the other plate? Dinner's on me!",
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "What did one ocean say to the other ocean? Nothing, they just waved.",
    "Why did the bicycle fall over? Because it was two-tired!"
]

# Function to tell a joke
def tellJoke():
    if 'last_joke' not in tellJoke.__dict__:
        tellJoke.last_joke = None

    # Select a random joke, ensuring it's different from the last one
    joke = random.choice(jokes)
    while joke == tellJoke.last_joke:
        joke = random.choice(jokes)

    speak(joke)
    tellJoke.last_joke = joke


def generate_equation_plot():
    # Generate x values
    x = np.linspace(-10, 10, 400)

    # Example quadratic equation: y = ax^2 + bx + c
    a = random.randint(1, 3)  # Random coefficient
    b = random.randint(-5, 5)  # Random coefficient
    c = random.randint(-20, 20)  # Random constant term

    # Calculate y values
    y = a * x ** 2 + b * x + c

    # Plot the equation
    plt.figure(figsize=(8, 6))
    plt.plot(x, y, label=f'Equation: {a}x^2 + {b}x + {c}')
    plt.title('Generated Equation Plot')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.grid(True)
    plt.legend()
    plt.show()


def solve_equation(equation):
    try:
        x = sp.symbols('x')
        solution = sp.solve(equation, x)
        speak("The solutions are:")
        for sol in solution:
            speak(sol.evalf())
    except Exception as e:
        speak("Sorry, I couldn't solve the equation.")


def track_phone_details(phone):
    try:
        ph = phonenumbers.parse(phone, "CH")
        country = geocoder.description_for_number(ph, "en")
        timezones = timezone.time_zones_for_number(ph)
        carrier_name = carrier.name_for_number(ph, "en")

        print("Country:", country)
        print("Timezones:", list(timezones))
        print("Carrier:", carrier_name)
    except Exception as e:
        print("Error:", e)


def number_to_digit(number_word):
    num_dict = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
    return num_dict.get(number_word, None)


def create_pie_chart():
    speak("How many labels do you want to create for the pie chart?")
    num_labels = takeCommand()

    # Check if the speech recognition failed
    if num_labels == "None":
        speak("Sorry, I couldn't recognize the number of labels.")
        return

    num_labels = number_to_digit(num_labels.lower())

    if num_labels is None:
        speak("Sorry, I couldn't recognize the number of labels.")
        return

    labels = []
    sizes = []

    for i in range(num_labels):
        speak(f"What is the name of label number {i + 1}?")
        label = takeCommand()

        # Check if the speech recognition failed
        if label == "None":
            speak(f"Sorry, I couldn't recognize the name of label number {i + 1}.")
            return

        labels.append(label)

        speak(f"What is the size of label {label}?")
        size = takeCommand()

        # Check if the speech recognition failed
        if size == "None":
            speak(f"Sorry, I couldn't recognize the size of label {label}.")
            return

        sizes.append(float(size))

    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Pie Chart')
    plt.show()


def convert_units(measurement, unit_from, unit_to):
    conversions = {
        'length': {
            'cm': {
                'm': 0.01,
                'mm': 10,
                'km': 0.00001,
                'inch': 0.393701,
                'foot': 0.0328084,
                'yard': 0.0109361,
                'mile': 0.00000621371
            },
            'm': {
                'cm': 100,
                'mm': 1000,
                'km': 0.001,
                'inch': 39.3701,
                'foot': 3.28084,
                'yard': 1.09361,
                'mile': 0.000621371
            },
            'mm': {
                'cm': 0.1,
                'm': 0.001,
                'km': 0.000001,
                'inch': 0.0393701,
                'foot': 0.00328084,
                'yard': 0.00109361,
                'mile': 6.21371e-7
            }
        },
        'weight': {
            'kg': {
                'g': 1000,
                'mg': 1e+6,
                'tonne': 0.001,
                'lb': 2.20462,
                'oz': 35.274
            },
            'g': {
                'kg': 0.001,
                'mg': 1000,
                'tonne': 1e-6,
                'lb': 0.00220462,
                'oz': 0.035274
            },
            'mg': {
                'kg': 1e-6,
                'g': 0.001,
                'tonne': 1e-9,
                'lb': 2.20462e-6,
                'oz': 3.5274e-5
            }
        },
        'temperature': {
            'celsius': {
                'fahrenheit': lambda x: x * 9 / 5 + 32,
                'kelvin': lambda x: x + 273.15
            },
            'fahrenheit': {
                'celsius': lambda x: (x - 32) * 5 / 9,
                'kelvin': lambda x: (x + 459.67) * 5 / 9
            },
            'kelvin': {
                'celsius': lambda x: x - 273.15,
                'fahrenheit': lambda x: x * 9 / 5 - 459.67
            }
        }
    }

    if measurement not in conversions:
        return None

    if unit_from not in conversions[measurement] or unit_to not in conversions[measurement][unit_from]:
        return None

    if callable(conversions[measurement][unit_from][unit_to]):
        return conversions[measurement][unit_from][unit_to]
    else:
        return conversions[measurement][unit_from][unit_to] * float(measurement)


def list_functions():
    speak("I can help you with the following tasks:")
    speak("1. Search on Wikipedia")
    speak("2. Search on YouTube")
    speak("3. Search on Google")
    speak("4. Open Stack Overflow")
    speak("5. Play music")
    speak("6. Open Spotify")
    speak("7. Tell the time")
    speak("8. Send an email")
    speak("9. Track hand motion")
    speak("10. Tell a joke")
    speak("11. Plot an equation")
    speak("12. Solve an equation")
    speak("13. Track phone details")
    speak("14. Create a pie chart")
    speak("15. Convert units")
    speak("16. Track objects in motion")
    speak("17. Open WhatsApp")
    speak("18. Exit")


def translate(text, dest_lang):
    translator = Translator()
    translated_text = translator.translate(text, dest=dest_lang).text
    return translated_text


def open_whatsapp_and_send_message(contact_name, message):
    # Open WhatsApp web
    webbrowser.open("https://web.whatsapp.com/")
    time.sleep(12)  # Wait for the page to load (adjust as needed)

    # Locate and click on the search box
    search_box_location = pyautogui.locateCenterOnScreen('whatsapp_search_box.png')
    if search_box_location:
        pyautogui.click(search_box_location)
        time.sleep(2)  # Wait for the search box to be active
        # Type the contact name
        pyautogui.typewrite(contact_name)
        time.sleep(2)  # Wait for the contact list to appear
        # Click on the contact
        contact_location = pyautogui.locateCenterOnScreen('whatsapp_contact.png')
        if contact_location:
            pyautogui.click(contact_location)
            time.sleep(2)  # Wait for the chat to load
            # Type the message
            pyautogui.typewrite(message)
            pyautogui.press('enter')  # Send the message
        else:
            speak("Sorry, I couldn't find the specified contact.")
    else:
        speak("Sorry, I couldn't find the search box on WhatsApp.")


if __name__ == "__main__":
    wishMe()
    while True:
        query = takeCommand().lower()

        # logic for executing tasks based on query
        if 'list functions' in query:
            list_functions()

        elif 'wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences=2)
            speak("According to Wikipedia")
            print(results)
            speak(results)

        elif 'open youtube' in query:
            speak("What do you want to search on YouTube?")
            search_query = takeCommand()
            if search_query != "None":
                speak(f"Searching YouTube for {search_query}")
                webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")

        elif 'open google' in query:
            speak("What do you want to search on Google?")
            search_query = takeCommand()
            if search_query != "None":
                speak(f"Searching Google for {search_query}")
                webbrowser.open(f"https://www.google.com/search?q={search_query}")

        elif 'open stackoverflow' in query:
            speak("Opening Stack Overflow")
            webbrowser.open("https://www.stackoverflow.com")

        elif 'play music' in query:
            music_dir = "C:\\Users\\HP\\Downloads\\Betelmatrix\\Betelmatrix\\Music"
            songs = os.listdir(music_dir)
            print(songs)
            os.startfile(os.path.join(music_dir, songs[0]))

        elif 'open spotify' in query:
            speak("Opening Spotify")
            webbrowser.open("https://open.spotify.com/")

        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"Sir, the time is {strTime}")

        elif 'email to varun' in query:
            try:
                speak("What should I say?")
                content = takeCommand()
                to = "varunmulay2004@gmail.com"
                sendEmail(to, content)
                speak("Email has been sent!")
            except Exception as e:
                print(e)
                speak("Sorry, I am not able to send this email")

        elif 'track hand motion' in query:
            speak("Starting hand motion tracking...")
            track_objects_in_motion()

        elif 'tell me a joke' in query:
            tellJoke()

        elif 'plot equation' in query:
            speak("Generating equation plot...")
            generate_equation_plot()

        elif 'solve equation' in query:
            speak("Please speak the equation.")
            equation_query = takeCommand()
            equation = sp.parse_expr(equation_query)
            solve_equation(equation)

        elif 'track phone details' in query:
            speak("Please provide the phone number.")
            phone_number = takeCommand()
            track_phone_details(phone_number)

        elif 'create pie chart' in query:
            create_pie_chart()

        elif 'convert units' in query:
            speak("What type of measurement would you like to convert? (length, weight, temperature)")
            measurement = takeCommand().lower()
            if measurement in ['length', 'weight', 'temperature']:
                speak("What is the value you'd like to convert?")
                value = takeCommand()
                speak(f"What unit is the value currently in?")
                unit_from = takeCommand().lower()
                speak(f"What unit would you like to convert it to?")
                unit_to = takeCommand().lower()

                conversion_func = convert_units(measurement, unit_from, unit_to)
                if callable(conversion_func):
                    converted_value = conversion_func(float(value))
                    speak(f"The converted value is {converted_value} {unit_to}")
                else:
                    speak("Sorry, I couldn't perform the conversion.")
            else:
                speak("Sorry, I can only convert length, weight, or temperature.")

        elif 'translate' in query:
            speak("What would you like to translate?")
            text = takeCommand()
            speak("Which language would you like to translate it to?")
            dest_lang = takeCommand().lower()

            if dest_lang in ['english','en']:
                 dest_lang = 'en'
            elif dest_lang in ['French','fr']:
                 dest_lang = 'fr'
            
            # Add more language mappings as needed

            translated_text = translate(text, dest_lang)
            speak("Here is the translated text:")
            speak(translated_text)

        elif "track objects in motion" in query:
            track_objects_in_motion()
            break

        elif 'open whatsapp' in query:
            speak("Whom do you want to send the message to?")
            contact_name = takeCommand().lower()
            speak(f"What message do you want to send to {contact_name}?")
            message = takeCommand()
            open_whatsapp_and_send_message(contact_name, message)

        elif 'exit' in query:
            speak("Exiting the assistant")
            break
