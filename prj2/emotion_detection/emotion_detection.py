#!/usr/bin/env python3
""" NOTE: To run this script out of debug mode run: `python -O emotion_detection.py`. (-O stands for optimize)"""
import json
import socket
import cv2
import pandas as pd
import datetime
from time import sleep

import face_recognition
from deepface import DeepFace
from paho.mqtt.client import Client as MQTTClient, MQTTv311


def get_frame(video_capture):
    ret = False
    while not ret:
        ret, frame = video_capture.read()
    return frame


def draw_debug_info(frame):
    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_frame = frame[:, :, ::-1]

    # Find all the faces in the current frame of video
    # NOTE: This is computationally very expensive. Turn off in production
    face_locations = face_recognition.face_locations(rgb_frame)
    # Display the results
    for top, right, bottom, left in face_locations:
        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

    # Display the resulting image
    cv2.imshow("Video", frame)
    cv2.waitKey(1)  # Show img for at least 1 sec


def get_emotions(video_capture, n_samples, time_cap_seconds=10):
    """Blocking function for getting `n_samples` successful samples in a row. Throws timeout error if and error occurs after `time_cap_seconds`.

    The reasoning behind starting over on an unsuccessful row:
        If we get an unsuccessful row it is most likely due to the target not being in correct position or moving.
        So better to start over than to try and work with mixed/noisy data.
    """
    time_cap = datetime.datetime.now() + datetime.timedelta(seconds=time_cap_seconds)
    while True:
        emotions = []
        if datetime.datetime.now() > time_cap:
            raise TimeoutError("Tried getting mood for too long")
        for _ in range(n_samples):
            frame = get_frame(video_capture)
            if __debug__:
                draw_debug_info(frame)
            try:
                emotions.append(DeepFace.analyze(frame, actions=["emotion"]))
            except Exception as e:
                print(e)
                break
        else:
            return emotions


def detect_face(frame) -> bool:
    rgb_frame = frame[:, :, ::-1]
    face_locations = face_recognition.face_locations(rgb_frame)
    return bool(face_locations)


class PublisherMQTTClient(MQTTClient):
    """MQTT client with a fixed publisher topic"""

    # fmt: off
    def __init__(self, publisher_topic, client_id="", clean_session=None, userdata=None, protocol=MQTTv311, transport="tcp", reconnect_on_failure=True):
        self.publisher_topic = publisher_topic
        super().__init__(client_id, clean_session, userdata, protocol, transport, reconnect_on_failure)
    # fmt: on

    def publish(self, payload=None, qos=0, retain=False, properties=None):
        return super().publish(self.publisher_topic, payload, qos, retain, properties)


def setup_mqtt_client():
    """Function to setup the MQTT function"""
    TOPIC = "pi_server/emotion"
    client = PublisherMQTTClient(publisher_topic=TOPIC, client_id="emotion_cam")
    broker_ip = socket.gethostbyname("rpi-server.local")
    client.connect(broker_ip, 1883)
    return client


def main():
    video_capture = cv2.VideoCapture("/dev/video0")
    if __debug__:
        n_samples = 10
    else:
        n_samples = 30
    mqtt_client = setup_mqtt_client()
    while True:
        frame = get_frame(video_capture)
        face_detected = detect_face(frame)
        if __debug__ or True:
            print(f"face: {face_detected}")
        if face_detected:
            try:
                emotions = get_emotions(video_capture, n_samples)
                emotions = map(lambda e: e["emotion"], emotions) # Get the emotion entries
                emotions = pd.DataFrame(emotions)
                emotions = emotions.mean(axis=0)
                dominant_emotion = emotions.idxmax()
                if __debug__ or True:
                    print(emotions)
                mqtt_client.publish(json.dumps({"emotion": dominant_emotion}))
                sleep(2)  # Sleep long if face was detected to avoid duplicates
            except TimeoutError as e:
                print(e)
        sleep(0.1)

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
