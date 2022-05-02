#!/usr/bin/env python3
from paho.mqtt.client import Client as MQTTClient, MQTTv311
from paho.mqtt.client import topic_matches_sub
import logging
import json


class MQTTCallbackClient(MQTTClient):
    """Similar to mqtt.Client but supports adding callbacks subscribed topics.
    Known limitation: It is currently only possible to provide a single callback method per topic.
    """

    # fmt: off
    def __init__(self, client_id="", clean_session=None, userdata=None, protocol=MQTTv311, transport="tcp", reconnect_on_failure=True):
        self.topic_handlers = {}
        super().__init__(client_id, clean_session, userdata, protocol, transport, reconnect_on_failure)
    # fmt: on

    def on_message(self, client, userdata, msg) -> None:
        """Looks for matching callback methods when a message is received on a subscribed topic."""
        logging.debug(f"Received msg from topic '{msg.topic}': {msg.payload}")
        try:
            payload = json.loads(msg.payload)
            self.call_matching(msg.topic, payload)
        except ValueError:
            # This class can only handle JSON messages.
            logging.debug("Invalid JSON format. Ignoring previous message.")

    def call_matching(self, msg_topic: str, payload: dict) -> None:
        """Calls the callbacks that matches the provided topic."""
        for topic in self.topic_handlers.keys():
            if topic_matches_sub(topic, msg_topic):
                self.topic_handlers[topic](payload)  # Call it

    def subscribe(self, topic, qos=0, options=None, properties=None, callback=None):
        """Subscribes to the topic and adds the callback method if provided."""
        if callback:
            self.topic_handlers[topic] = callback
        return super().subscribe(topic, qos, options, properties)

    def unsubscribe(self, topic, properties=None):
        """Unsubscribes to the topic and adds the callback method if provided."""
        self.topic_handlers.pop(
            topic, None
        )  # Return None if key not found (don't throw)
        return super().unsubscribe(topic, properties)
