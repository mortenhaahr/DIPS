#!/usr/bin/env python3

from concurrent.futures import thread
import time
from flask import Flask, request
import json
from mqtt_callback_client import MQTTCallbackClient
import socket
import threading
import logging
import subprocess

from mqtt_callback_client import MQTTCallbackClient
import pygame

def send_alexa_command(cmd, device="MortenEchoDot"):
    output = subprocess.run(
        [
            "alexa_remote_control.sh",
            "-d",
            device,
            "-e",
            f"textcommand: {cmd}",
        ],
        capture_output=True,
    )
    return output


client = None
emotion = None
room = None

class Speaker():
    def __init__(self):
        self.room1_playing = False
        self.room2_playing = False
        self.Mac = "00:58:50:1D:B3:35"
        self.connected = False
        
        self.Rooms = {"Room1": "Kitchen",
                    "Room2": "Livingroom"}
        self.song = {"sad": 'Tammy-Stan-Devereaux.mp3', 
                    "happy": 'Pharrell-Williams-Happy-f7.mp3',
                    "angry": 'arthur-vyncke-cherry-metal.mp3', #Cherry Metal by Arthur Vyncke | https://soundcloud.com/arthurvost Creative Commons Attribution-ShareAlike 3.0 Unported https://creativecommons.org/licenses/by-sa/3.0/deed.en_US Music promoted by https://www.chosic.com/free-music/all/ 
                    "neutral": 'Illusions.mp3'} #Illusions by Keys of Moon | https://soundcloud.com/keysofmoon Music promoted by https://www.chosic.com/free-music/all/ Creative Commons CC BY 4.0 https://creativecommons.org/licenses/by/4.0/
 
        pygame.mixer.init()
        pygame.mixer.music.load(self.song["happy"])  
        
    def loadMusic(self, file):
        pygame.mixer.music.load(file)

    def stopMusic(self,roomNr):
        def wait_and_stop():
            # time.sleep(2) # Wait a little bit so we don't interrupt the lady
            send_alexa_command("stop the music")
        if roomNr == 1:
            threading.Thread(target=wait_and_stop).start()
            self.room1_playing = False
        elif roomNr == 2:
            self.room2_playing = False
            pygame.mixer.music.stop()
        else:
            logging.info("stopMusic: Unknown roomNr")

    def playMusic(self, emotion, roomNr):
        def wait_and_play(emotion):
            # time.sleep(3) # Wait a little bit so we don't interrupt the lady
            if emotion == "neutral":
                send_alexa_command("play my library songs")
            else:
                send_alexa_command(f"play {emotion} music")

        if emotion == None:
            logging.warning("Emotion is undefined")
            return
        if roomNr == 1:
            if self.room1_playing == False:
                self.room1_playing = True
                logging.debug("Playing in room 1")
                threading.Thread(target=lambda: wait_and_play(emotion)).start()
        elif roomNr == 2:
            if self.room2_playing == False:
                self.room2_playing = True
                logging.debug("Playing in room 2")
                pygame.mixer.music.play(loops=-1)  
        else:
            logging.info("playMusic: Unknown roomNr")

    def updatePlayStatus(self):
        self.playing = pygame.mixer.music.get_busy()
        return self.playing
        
    def emotion_callback(self, topic, payload):
        global emotion
        if emotion == payload['emotion']:
            return
        emotion = payload['emotion']
        logging.debug("emotionCallback \n")
        self.loadMusic(self.song[emotion])
        # Check if music is already playing
        if self.room1_playing == True:
            self.room1_playing = False
            self.playMusic(emotion=emotion,roomNr=1)
        if self.room2_playing == True:
            self.room2_playing = False
            self.playMusic(emotion=emotion,roomNr=2)

    def room_callback(self, topic, payload, roomNr):
        global emotion
        playing = payload['music_playing']
        logging.debug(f"Room Calback for room: {roomNr}")
        if playing == True:
            self.playMusic(emotion,roomNr)
        else:
            self.stopMusic(roomNr)

    def setupTopics(self,client):
        client.subscribe("pi_server/context/emotion", callback=self.emotion_callback,qos=1)
        client.subscribe("pi_server/context/room" + "1" + "/music_playing", callback=lambda topic, payload: self.room_callback(topic, payload, 1))
        client.subscribe("pi_server/context/room" + "2" + "/music_playing", callback=lambda topic, payload: self.room_callback(topic, payload, 2))


base_topic = "pi_server"
context = {}
last_command = ""


def get_context(topic, payload):
    """Known error: If the topic has a value that is a json object that equals to the name of the subtopic then the json object will be overwritten."""
    from functools import reduce
    from pydantic.utils import deep_update

    global context
    update_to_context = topic.split("/")[2:]
    update_to_context.append(payload)
    # From SO: https://stackoverflow.com/questions/7653726/how-to-turn-a-list-into-nested-dict-in-python
    updated_context_nested_dict = reduce(lambda x, y: {y: x}, update_to_context[::-1])
    context = deep_update(context, updated_context_nested_dict)
    logging.debug(f"Updated context: {context}")


def create_basic_text_response(
    text, reprompt_text="Can I help you with anything else?", end_session=False
):
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": text,
            },
            "reprompt": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": reprompt_text,
                }
            },
            "shouldEndSession": end_session,
        },
    }


app = Flask(__name__)  # __name__ = filename


def launch_handler(data_request):
    global context, last_command
    try:
        emotion = context["emotion"]["emotion"]
    except KeyError:
        emotion = "undefined"
    response = create_basic_text_response(
        f"""Your current emotion is set to {emotion}. You can change it by saying: "Change my emotion to happy". I support the emotions "angry", "happy", "sad" and "neutral"."""
    )
    last_command = "launch"
    return response


def set_emotion_callback(intent):
    global last_command
    emotion = intent["slots"]["emotion"]["value"]
    emotion_topic = f"{base_topic}/emotion"
    client.publish(emotion_topic, json.dumps({"emotion": emotion}))
    response = create_basic_text_response(
        f"""Changing your emotion to {emotion}.""", end_session=True
    )
    last_command = "get_emotion"
    return response


def get_emotion_callback(intent):
    global context, last_command
    try:
        emotion = context["emotion"]["emotion"]
    except KeyError:
        emotion = "undefined"
    response = create_basic_text_response(
        f"""Your emotion is currently set to {emotion}. Do you want to change it?"""
    )
    last_command = "get_emotion"
    return response


def get_room_occupied(intent):
    global last_command
    last_command = "get_room_occupied"
    room_number = intent["slots"]["room_number"]["value"]
    try:
        occupied = context[f"room{room_number}"]["occupied"]["occupied"]
        occupied = "" if occupied else "not "
        return create_basic_text_response(
            f"Room number {room_number} is currently {occupied} occupied. Was there anything else?"
        )
    except KeyError:
        return create_basic_text_response(
            f"I'm sorry I don't know if room number {room_number} is occupied. Can I help you with anything else?"
        )


def get_lamp_status_no_room_number(intent):
    global last_command
    last_command = "get_lamp_status_no_room_number"
    lamps = []
    for i in range(2):
        try:
            status = context[f"room{i+1}"]["lamp"]["on"]
            lamps.append(status)
        except KeyError:
            lamps.append(None)
    logging.info(f"Lamps: {lamps}")
    if None in lamps:
        if lamps[0] != lamps[1]:
            if lamps[0] is None:
                text_response = (
                    "I don't know the status of lamp 1 but the lamp in room 2 is "
                    + ("on." if lamps[1] else "off.")
                )
                text_response += " Do you need help with anything else?"
            else:
                text_response = "The lamp in room 1 is currently " + (
                    "on" if lamps[0] else "off"
                )
                text_response += " and I don't know if the lamp in room 2 is on or off. Do you need help with anything else?"
        else:
            # both are None
            text_response = "I'm sorry. I don't know the status of any of the lamps. Can I help you with something else?"
        return create_basic_text_response(text_response)

    try:
        binary_switch = intent["slots"]["binary_switch"]["value"]
        if lamps[0] is True and lamps[1] is True and binary_switch == "on":
            return create_basic_text_response(
                "Yes. The both the lamps are turned on. Can I help you with anything else?"
            )
        elif lamps[0] is False and lamps[1] is True and binary_switch == "on":
            return create_basic_text_response(
                "The lamp in room 1 is off but the lamp in room 2 is on. Need more help?"
            )
        elif lamps[0] is True and lamps[1] is False and binary_switch == "on":
            return create_basic_text_response(
                "The lamp in room 1 is on but the lamp in room 2 is off. Need more help?"
            )
        elif binary_switch == "on":
            return create_basic_text_response(
                "No. Both of the lamps are turned off. Do you need anything else?"
            )

        if lamps[0] is False and lamps[1] is False and binary_switch == "off":
            return create_basic_text_response(
                "Yes. The lamps in both rooms are turned off. Can I help you with anything else?"
            )
        elif lamps[0] is False and lamps[1] is True and binary_switch == "on":
            return create_basic_text_response(
                "The lamp in room 1 is off but the lamp in room 2 is on. Need more help?"
            )
        elif lamps[0] is True and lamps[1] is False and binary_switch == "on":
            return create_basic_text_response(
                "The lamp in room 1 is on but the lamp in room 2 is off. Need more help?"
            )
        elif binary_switch == "off":
            return create_basic_text_response(
                "No. Both of the lamps are turned on. Do you need anything else?"
            )
        else:
            return default_command()
    except KeyError:
        # Means user didn't ask something like "are the lamps **on**""
        if lamps[0] and lamps[1]:
            text_response = (
                "Both the lamps are currently turned on. What else can I help you with?"
            )
        elif not lamps[0] and not lamps[1]:
            text_response = "Both the lamps are currently turned off. Anything else?"
        else:
            text_response = "The lamp in room 1 is " + ("on" if lamps[0] else "off")
            text_response += " and the lamp in room 2 is " + (
                "on" if lamps[1] else "off"
            )
            text_response += ". Need anything else?"
        return create_basic_text_response(text_response)


def yes_handler(intent):
    global last_command
    old_last_command = last_command
    last_command = "yes"
    if old_last_command == "get_emotion":
        return create_basic_text_response("All right. How do you feel?.")
    elif (
        old_last_command == "get_room_occupied"
        or old_last_command == "get_lamp_status_no_room_number"
    ):
        return create_basic_text_response("What can I help you with?")
    else:
        return create_basic_text_response(
            "I'm sorry I can't let you do that Dave.", end_session=True
        )


def no_handler(intent):
    global last_command
    last_command = "no"
    return create_basic_text_response("All right. Talk to you soon.", end_session=True)


def help_handler(intent):
    global last_command
    last_command = "help"
    return create_basic_text_response(
        "I can help you with managing your smart home. With my help you can manage your emotion, see if any of the rooms are occupied, and check the status of the lights."
    )

def stop_music(intent):
    def wait_and_stop():
        # time.sleep(1)
        send_alexa_command("stop the music")
    global client
    threading.Thread(target=wait_and_stop).start()
    client.publish(f"{base_topic}/audio/commands", json.dumps({"audio_on": False}))
    return create_basic_text_response("All right. Stopping the music.", end_session=True)

def intent_handler(data_request):
    intents_callbacks = {
        "set_emotion": set_emotion_callback,
        "get_emotion": get_emotion_callback,
        "get_room_occupied": get_room_occupied,
        "get_lamp_status_no_room_number": get_lamp_status_no_room_number,
        "stop_music": stop_music,
        "AMAZON.YesIntent": yes_handler,
        "AMAZON.NoIntent": no_handler,
        "AMAZON.HelpIntent": help_handler,
    }
    intent = data_request["intent"]["name"]
    print("Intent handler called")
    invocation = intents_callbacks.get(intent, default_command)
    return invocation(data_request["intent"])


def default_command(data_request):
    global last_command
    print("Default command called")
    response = create_basic_text_response(
        "I'm sorry I didn't quite get that. Try saying HELP."
    )
    last_command = "default"
    return response


request_types = {
    "LaunchRequest": launch_handler,
    "IntentRequest": intent_handler,
}  # Unsupported so far: CanFulfillIntentRequest, SessionEndedRequest


@app.route("/", methods=["POST", "GET"])  # Post is for new data and get is for all
def mood_controller():
    data = request.get_json()
    command_type = data["request"]["type"]
    invocation = request_types.get(command_type, default_command)
    return json.dumps(invocation(data["request"]))

def main():
    global client
    logging.basicConfig(
	    level=logging.DEBUG, format="%(asctime)s : %(levelname)s:  %(message)s"
	)
    #Setup mqtt
    pi_ip = socket.gethostbyname("rpi-server.local")    

    #Setup client
    client = MQTTCallbackClient(client_id="rpi-audio")
    client.connect(pi_ip, 1883)  # rpi-server ip
    client.subscribe(f"{base_topic}/context/#", callback=get_context)

    #Setup speaker
    spk = Speaker()
    spk.setupTopics(client)
     
    t = threading.Thread(target=client.loop_forever)
    t.start()
    app.run()  # NOTE: Debug doesn't work with paho running in background. It will make MQTT not work.

if __name__ == "__main__":
	main()




