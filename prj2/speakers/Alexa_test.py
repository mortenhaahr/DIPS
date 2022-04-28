import logging
import os
from time import time
from unittest import case

from arrow import now
 
from flask import Flask
import json
 
app = Flask(__name__)
 
STATUSON = ["on", "switch on", "enable", "power on", "activate", "turn on"] # all values that are defined as synonyms in type
STATUSOFF = ["off", "switch off", "disactivate", "turn off", "disable", "turn off"]
 
MoodsNEUTRAL = ["Neutral", "OK", "Okay", "Balanced", "Disinterested", "Normal"]
MoodsSAD = ["Sad", "Dejected", "Gloomy", "Down", "Dejected", "Miserable", "Low-spirated", "Dejected", "Downcast", "Dispirated","Depressed", "Crying", "Unhappy"]
MoodsANGRY = ["Angry", "Wrathful", "Irate", "Seething", "Livid", "Furious", "Sore", "Mad", "Irate", "Cross", "Frustrated", "Pissed off"]
MoodsHAPPY = ["in a good mood", "Pleased", "Cheerfull", "Glad"]

json_testDic = {
        "type": "IntentRequest",
        "requestId": "requestId",
        "timestamp": "timestamp",
        "dialogState": "string",
        "locale": "en-US",
        "intent": {
            "name": "Mood_Intent",
            "confirmationStatus": "string",
            "slots": {
            "SlotName": {
                "name": "Mood",
                "value": "string",
                "confirmationStatus": "string",
                "slotValue": {},
                "resolutions": {
                "resolutionsPerAuthority": [
                    {
                    "authority": "string",
                    "status": {
                        "code": "string"
                    },
                    "values": [
                        {
                        "value": {
                            "name": "string",
                            "id": "string"
                        }
                        }
                    ]
                    }
                ]
                }
            }
            }
        }
    }


#Launch Request
def launch_req(requestId):
    return{
        "type": "LaunchRequest",
        "requestId": requestId,
        "timestamp": time(),
        "locale": "en-US"
    }




def get_emosion(jsonInput):
    json_obj = json.loads(jsonInput)
    intent = json_obj["intent"]
    slot = intent["slots"]
    if intent["name"] == "Mood_intent":
        return intent.slots.Mood


    




##@ask.intent('MoodIntent', mapping = {'Mood':'Mood'})
#def Mood_Intent(Mood,room):
#    if Mood in MoodsNEUTRAL:
#        return statement('Playing neutral music')
#    elif Mood in MoodsSAD:
#        return statement('Playing sad music')    
#    elif Mood in MoodsANGRY:
#        return statement('Playing angry music')    
#    elif Mood in MoodsHAPPY:
#        return statement('Playing happy music')
#    else:
#        return statement('Sorry, you are in a strange mood')



#@ask.session_ended
#def session_ended():
#    return "{}", 200
 
 
if __name__ == '__main__':
    json_testFile = json.dumps(json_testDic)
    emotion = get_emosion(json_testFile)
    app.run(debug=True)