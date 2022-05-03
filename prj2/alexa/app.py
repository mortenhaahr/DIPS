from concurrent.futures import thread
from flask import Flask, request
import json
from mqtt_callback_client import MQTTCallbackClient
import socket
import threading
import logging

base_topic = "pi_server"
client = None
context = {}


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


basic_response = {
    "version": "1.0",
    "sessionAttributes": {
        # "supportedHoroscopePeriods": {
        #     "daily": True,
        #     "weekly": False,
        #     "monthly": False,
        # }
    },
    "response": {
        "outputSpeech": {
            "type": "PlainText",
            "text": f"I'm sorry I didn't quite get that. Try saying HELP.",
        },
        # "card": {
        #     "type": "Simple",
        #     "title": "Mood",
        #     "content": "Today will provide you a new learning opportunity.  Stick with it and the possibilities will be endless.",
        # },
        # "reprompt": {
        #     "outputSpeech": {
        #         "type": "PlainText",
        #         "text": "Can I help you with anything else?",
        #     }
        # },
        "shouldEndSession": False,
    },
}

app = Flask(__name__)  # __name__ = filename


def launch_handler(data_request):
    global context
    try:
        emotion = context["emotion"]["emotion"]
    except KeyError:
        emotion = "undefined"
    response = create_basic_text_response(
        f"""Hi there! Your current emotion is set to {emotion}. You can change it by saying: "Change my emotion to happy". I currently support the emotions "angry", "happy", "sad" and "neutral"."""
    )
    return json.dumps(response)


def set_emotion_callback(intent):
    emotion = intent["slots"]["emotion"]["value"]
    emotion_topic = f"{base_topic}/emotion"
    client.publish(emotion_topic, json.dumps({"emotion": emotion}))
    response = create_basic_text_response(f"""Changing your emotion to {emotion}.""")
    return json.dumps(response)


def get_emotion_callback(intent):
    response = create_basic_text_response(
        f"""Your mood is currently set to {context.get("emotion", "undefined")}. Do you want to change it?"""
    )
    return json.dumps(response)


def intent_handler(data_request):
    intents_callbacks = {
        "set_emotion": set_emotion_callback,
        "get_emotion": get_emotion_callback,
    }
    intent = data_request["intent"]["name"]
    print("Intent handler called")
    invocation = intents_callbacks.get(intent, default_command)
    return invocation(data_request["intent"])


def default_command(data_request):
    print("Default command called")
    return json.dumps(basic_response)


request_types = {
    "LaunchRequest": launch_handler,
    "IntentRequest": intent_handler,
}  # Unsupported so far: CanFulfillIntentRequest, SessionEndedRequest


@app.route("/", methods=["POST", "GET"])  # Post is for new data and get is for all
def mood_controller():
    data = request.get_json()
    command_type = data["request"]["type"]
    invocation = request_types.get(command_type, default_command)
    return invocation(data["request"])


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s : %(levelname)s:  %(message)s"
    )
    client = MQTTCallbackClient(client_id="rpi-audio-hej")
    broker_ip = socket.gethostbyname("rpi-server.local")
    client.connect(broker_ip, 1883)
    client.subscribe(f"{base_topic}/context/#", callback=get_context)
    t = threading.Thread(target=client.loop_forever)
    t.start()
    app.run()  # NOTE: Debug doesn't work with paho running in background. It will make MQTT not work.
