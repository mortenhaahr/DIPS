from flask import Flask, request
import json
from mqtt_callback_client import MQTTCallbackClient
import socket
import threading
import logging

base_topic = "pi_server"
client = None
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
        f"""Your current emotion is set to {emotion}. I support the emotions "angry", "happy", "sad" and "neutral". Do you want to change your mood?"""
    )
    last_command = "launch"
    return json.dumps(response)


def set_emotion_callback(intent):
    global last_command
    emotion = intent["slots"]["emotion"]["value"]
    emotion_topic = f"{base_topic}/emotion"
    client.publish(emotion_topic, json.dumps({"emotion": emotion}))
    response = create_basic_text_response(
        f"""Changing your emotion to {emotion}.""", end_session=True
    )
    last_command = "get_emotion"
    return json.dumps(response)


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
    return json.dumps(response)


def yes_handler(intent):
    global last_command
    old_last_command = last_command
    last_command = "yes"
    if old_last_command == "get_emotion" or old_last_command == "launch":
        return json.dumps(create_basic_text_response("All right. How do you feel?."))

    return json.dumps(
        create_basic_text_response(
            "I'm sorry I can't let you do that Dave.", end_session=True
        )
    )


def no_handler(intent):
    global last_command
    last_command = "no"
    return json.dumps(
        create_basic_text_response("All right. Talk to you soon.", end_session=True)
    )


def intent_handler(data_request):
    intents_callbacks = {
        "set_emotion": set_emotion_callback,
        "get_emotion": get_emotion_callback,
        "AMAZON.YesIntent": yes_handler,
        "AMAZON.NoIntent": no_handler,
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
    return json.dumps(response)


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
