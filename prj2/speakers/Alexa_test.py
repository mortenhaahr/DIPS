import logging
import os
from unittest import case
 
from flask import Flask
from flask_ask import Ask, request, session, question, statement
 
app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)
 
STATUSON = ["on", "switch on", "enable", "power on", "activate", "turn on"] # all values that are defined as synonyms in type
STATUSOFF = ["off", "switch off", "disactivate", "turn off", "disable", "turn off"]
 
MoodsNEUTRAL = ["Neutral", "OK", "Okay", "Balanced", "Disinterested", "Normal"]
MoodsSAD = ["Sad", "Dejected", "Gloomy", "Down", "Dejected", "Miserable", "Low-spirated", "Dejected", "Downcast", "Dispirated","Depressed", "Crying", "Unhappy"]
MoodsANGRY = ["Angry", "Wrathful", "Irate", "Seething", "Livid", "Furious", "Sore", "Mad", "Irate", "Cross", "Frustrated", "Pissed off"]
MoodsHAPPY = ["in a good mood", "Pleased", "Cheerfull", "Glad"]


@ask.launch
def launch():
    speech_text = 'Welcome to the Raspberry Pi alexa automation.'
    return question(speech_text).reprompt(speech_text).simple_card(speech_text)
 
@ask.intent('LightIntent', mapping = {'status':'status'})
def Gpio_Intent(status,room):
    if status in STATUSON:
        return statement('Light was turned on')
    elif status in STATUSOFF:
        return statement('Light was turned off')
    else:
        return statement('Sorry, this command is not possible.')
 
@ask.intent('MoodIntent', mapping = {'Mood':'Mood'})
def Mood_Intent(Mood,room):
    if Mood in MoodsNEUTRAL:
        return statement('Playing neutral music')
    elif Mood in MoodsSAD:
        return statement('Playing sad music')    
    elif Mood in MoodsANGRY:
        return statement('Playing angry music')    
    elif Mood in MoodsHAPPY:
        return statement('Playing happy music')
    else:
        return statement('Sorry, you are in a strange mood')



@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = 'You can say hello to me!'
    return question(speech_text).reprompt(speech_text).simple_card('HelloWorld', speech_text)
 
 
@ask.session_ended
def session_ended():
    return "{}", 200
 
 
if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(debug=True)