from flask import Flask, request
import json


def create_basic_text_response(text, reprompt_text="Can I help you with anything else?", end_session=False):
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
    mood = "happy"
    response = create_basic_text_response(
        f"Hi there! Your current mood is set to {mood}. Do you want to change it?"
    )
    return json.dumps(response)

def intent_handler(data_request):
    print("Intent handler called")
    return default_command(data_request)


def default_command(data_request):
    print("Default command called")
    return json.dumps(basic_response)


request_types = {"LaunchRequest": launch_handler, "IntentRequest": intent_handler} # Unsupported so far: CanFulfillIntentRequest, SessionEndedRequest


@app.route("/", methods=["POST", "GET"])  # Post is for new data and get is for all
def mood_controller():
    data = request.get_json()
    command_type = data["request"]["type"]
    invocation = request_types.get(command_type, default_command)
    return invocation(data["request"])


if __name__ == "__main__":
    app.run(debug=True)
