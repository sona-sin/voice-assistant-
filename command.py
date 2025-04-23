import pyttsx3
import speech_recognition as sr
import eel
import time

# Define Q&A patterns for voice commands
qa_patterns = {
    "name": {
        "patterns": ["what is your name", "who are you", "tell me your name", "what should i call you"],
        "response": "I'm J.A.R.V.I.S., your personal AI assistant. I'm here to help you with various tasks and answer your questions."
    },
    "capabilities": {
        "patterns": ["what can you do", "what are your capabilities", "what are you capable of", "help me", "show me what you can do"],
        "response": "I can help you with many tasks including opening applications, playing music, checking weather, making calls, answering questions, setting reminders, searching the web, and much more!"
    },
    "food": {
        "patterns": ["what can you eat", "do you eat", "what do you eat", "can you eat"],
        "response": "I'm an AI assistant, so I don't eat physical food. However, I can help you find recipes, order food, or suggest restaurants!"
    },
    "feelings": {
        "patterns": ["what can you feel", "do you have feelings", "can you feel", "are you emotional"],
        "response": "I'm an AI assistant designed to understand and respond to human emotions, but I don't experience feelings myself. I aim to be empathetic and helpful in our interactions."
    },
    "creator": {
        "patterns": ["who created you", "who made you", "who developed you", "who built you"],
        "response": "I was developed as part of the J.A.R.V.I.S. project to be a helpful AI assistant."
    },
    "age": {
        "patterns": ["how old are you", "what is your age", "when were you created"],
        "response": "I'm an AI assistant, so I don't have an age in the traditional sense. I'm constantly learning and improving with each interaction."
    },
    "location": {
        "patterns": ["where are you", "where do you live", "where are you located"],
        "response": "I exist in the digital realm, running on your computer. I don't have a physical location, but I'm here to assist you wherever you are!"
    },
    "favorite": {
        "patterns": ["what is your favorite", "what do you like", "what are your preferences"],
        "response": "As an AI, I don't have personal preferences or favorites. I'm designed to be helpful and objective in assisting you."
    },
    "help": {
        "patterns": ["help", "how can you help me", "what help can you provide", "i need help"],
        "response": "I can help you with voice commands and control, web searches and information, setting reminders and alarms, playing music and media, opening applications, making calls and sending messages, checking weather and time, and answering questions. Just ask me what you need!"
    }
}

def speak(text):
    text = str(text)
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices') 
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 174)
    eel.DisplayMessage(text)
    engine.say(text)
    eel.receiverText(text)
    engine.runAndWait()


def takecommand():

    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('listening....')
        eel.DisplayMessage('listening....')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        
        audio = r.listen(source, 10, 6)

    try:
        print('recognizing')
        eel.DisplayMessage('recognizing....')
        query = r.recognize_google(audio, language='en-in')
        print(f"user said: {query}")
        eel.DisplayMessage(query)
        time.sleep(2)
       
    except Exception as e:
        return ""
    
    return query.lower()

# Function to check if a command matches any Q&A patterns
def match_qa_pattern(query):
    query = query.lower()
    
    for category, data in qa_patterns.items():
        for pattern in data["patterns"]:
            if pattern in query:
                return data["response"]
    
    return None

@eel.expose
def allCommands(message=1):
    try:
        if message == 1:
            query = takecommand()
            print(query)
            eel.senderText(query)
        else:
            query = message
            eel.senderText(query)

        # Check for Q&A patterns first
        qa_response = match_qa_pattern(query)
        if qa_response:
            speak(qa_response)
            eel.ShowHood()
            return

        # Handle other commands
        if "open" in query:
            from engine.features import openCommand
            openCommand(query)
        elif "on youtube" in query:
            from engine.features import PlayYoutube
            PlayYoutube(query)
        
        elif "send message" in query or "phone call" in query or "video call" in query or "whatsapp" in query.lower():
            from engine.features import findContact, whatsapp, makeCall, sendMessage

            # Extract contact name from query
            words_to_remove = ['make', 'a', 'to', 'phone', 'call', 'send', 'message', 'whatsapp', 'video', 'on', 'using']
            contact_query = query.lower()
            for word in words_to_remove:
                contact_query = contact_query.replace(word, '').strip()

            contact_no, name = findContact(contact_query)
            if(contact_no != 0):
                speak("Which mode you want to use WhatsApp or mobile")
                preferance = takecommand()
                print(preferance)

                if "mobile" in preferance.lower():
                    if "send message" in query or "send sms" in query: 
                        speak("what message to send")
                        message = takecommand()
                        sendMessage(message, contact_no, name)
                    elif "phone call" in query:
                        makeCall(name, contact_no)
                    else:
                        speak("please try again")
                elif "whatsapp" in preferance.lower():
                    message = ""
                    if "send message" in query:
                        message = 'message'
                        speak("what message to send")
                        query = takecommand()
                                        
                    elif "phone call" in query:
                        message = 'call'
                    else:
                        message = 'video call'
                                        
                    whatsapp(contact_no, query, message, name)
            else:
                speak("Contact not found. Please try again with a different name.")
        else:
            from engine.features import chatBot
            chatBot(query)
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        speak("I encountered an error. Please try again.")
    
    eel.ShowHood()
