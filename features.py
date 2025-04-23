import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import shlex

import re
import sqlite3
import struct
import subprocess
import time
import webbrowser
from playsound import playsound
import eel
import pyaudio
import pyautogui
from engine.command import speak
from engine.config import ASSISTANT_NAME
# Playing assiatnt sound function
import pywhatkit as kit
import pvporcupine

from engine.helper import extract_yt_term, remove_words
from hugchat import hugchat

con = sqlite3.connect("jarvis.db")
cursor = con.cursor()

@eel.expose
def playAssistantSound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)

    
def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query.lower()

    app_name = query.strip()

    if app_name != "":

        try:
            cursor.execute(
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong")

       

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)


def hotword():
    porcupine=None
    paud=None
    audio_stream=None
    try:
       
        # pre trained keywords    
        porcupine=pvporcupine.create(keywords=["jarvis","alexa"]) 
        paud=pyaudio.PyAudio()
        audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        
        # loop for streaming
        while True:
            keyword=audio_stream.read(porcupine.frame_length)
            keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

            # processing keyword comes from mic 
            keyword_index=porcupine.process(keyword)

            # checking first keyword detetcted for not
            if keyword_index>=0:
                print("hotword detected")

                # pressing shorcut key win+j
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
                
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()



# find contacts
def findContact(query):
    
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'WhatsApp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
    
def whatsapp(mobile_no, message, flag, name):
    try:
        # Format the phone number (remove any spaces and ensure it starts with +)
        mobile_no = mobile_no.replace(" ", "")
        if not mobile_no.startswith('+'):
            mobile_no = '+' + mobile_no
            
        # Remove the country code for the URL if it exists
        url_phone = mobile_no
        if url_phone.startswith('+91'):
            url_phone = url_phone[3:]  # Remove +91 prefix
            
        # Set appropriate messages based on the flag
        if flag == 'message':
            jarvis_message = f"Message sent successfully to {name}"
            eel.DisplayMessage(f"Sending message to {name}...")
            speak(f"Sending message to {name}")
            
            # For messages, we'll use the web.WhatsApp.com URL
            web_url = f"https://web.whatsapp.com/send?phone={url_phone}&text={shlex.quote(message)}"
            webbrowser.open(web_url)
            
        elif flag == 'call':
            jarvis_message = f"Calling {name}..."
            eel.DisplayMessage(f"Calling {name}...")
            speak(f"Calling {name}")
            
            # For calls, we'll try to open WhatsApp directly and then use keyboard shortcuts
            try:
                # Try to open WhatsApp desktop app
                # os.system('start "" "C:\\Users\\%USERNAME%\\AppData\\Local\\WhatsApp\\WhatsApp.exe"')
                os.system('start "" "C:\\Users\\sonam\\OneDrive\\Desktop\\WhatsApp- Shortcut.lnk"')
                time.sleep(3)  # Wait for WhatsApp to open
                
                # Press Ctrl+Shift+P to open the search
                pyautogui.hotkey('ctrl', 'shift', 'p')
                time.sleep(1)
                
                # Type the contact name
                pyautogui.write(name)
                time.sleep(1)
                
                # Press Enter to select the contact
                pyautogui.press('enter')
                time.sleep(1)
                
                # Press Ctrl+Shift+C to start a call
                pyautogui.hotkey('ctrl', 'shift', 'c')
                
            except Exception as e:
                print(f"Error with whatsapp call: {e}")
                # Fallback to web.WhatsApp.com
                web_url = f"https://web.whatsapp.com/call/voice/{url_phone}"
                webbrowser.open(web_url)
                
        else:  # video call
            jarvis_message = f"Starting video call with {name}..."
            eel.DisplayMessage(f"Starting video call with {name}...")
            speak(f"Starting video call with {name}")
            
            # For video calls, we'll try to open WhatsApp directly and then use keyboard shortcuts
            try:
                # Try to open WhatsApp desktop app
                os.system('start "" "C:\\Users\\sonam\\OneDrive\\Desktop\\WhatsApp - Shortcut.lnk"')
                time.sleep(3)  # Wait for WhatsApp to open
                
                # Press Ctrl+Shift+P to open the search
                pyautogui.hotkey('ctrl', 'shift', 'p')
                time.sleep(1)
                
                # Type the contact name
                pyautogui.write(name)
                time.sleep(1)
                
                # Press Enter to select the contact
                pyautogui.press('enter')
                time.sleep(1)
                
                # Press Ctrl+Shift+V to start a video call
                pyautogui.hotkey('ctrl', 'shift', 'v')
                
            except Exception as e:
                print(f"Error with whatsapp video call: {e}")
                # Fallback to web.WhatsApp.com
                web_url = f"https://web.whatsapp.com/call/video/{url_phone}"
                webbrowser.open(web_url)
        
        # Display success message
        eel.DisplayMessage(jarvis_message)
        speak(jarvis_message)
        
    except Exception as e:
        error_message = f"Error with WhatsApp: {str(e)}"
        print(error_message)
        speak("Sorry, there was an error with WhatsApp")
        eel.DisplayMessage("Sorry, there was an error with WhatsApp")

# chat bot 
def chatBot(query):
    user_input = query.lower()
    chatbot = hugchat.ChatBot(cookie_path="engine\cookies.json")
    id = chatbot.new_conversation()
    chatbot.change_conversation(id)
    response =  chatbot.chat(user_input)
    print(response)
    speak(response)
    return str(response)

# android automation

def makeCall(name, mobileNo):
    mobileNo =mobileNo.replace(" ", "")
    speak("Calling "+name)
    command = 'adb shell am start -a android.intent.action.CALL -d tel:'+mobileNo
    os.system(command)


# to send message
def sendMessage(message, mobileNo, name):
    from engine.helper import replace_spaces_with_percent_s, goback, keyEvent, tapEvents, adbInput
    message = replace_spaces_with_percent_s(message)
    mobileNo = replace_spaces_with_percent_s(mobileNo)
    speak("sending message")
    goback(4)
    time.sleep(1)
    keyEvent(3)
    # open sms app
    tapEvents(136, 2220)
    #start chat
    tapEvents(819, 2192)
    # search mobile no
    adbInput(mobileNo)
    #tap on name
    tapEvents(601, 574)
    # tap on input
    tapEvents(390, 2270)
    #message
    adbInput(message)
    #send
    tapEvents(957, 1397)
    speak("message send successfully to "+name)