#!/usr/bin/env python3
""" NOTE: To run this script out of debug mode run: `python -O emotion_detection.py`. (-O stands for optimize)"""
import cv2
import pandas as pd

if __debug__:
    import face_recognition
from deepface import DeepFace


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


def get_emotions(video_capture, n_samples):
    """Blocking function for getting `n_samples` successful samples in a row.

    The reasoning behind starting over on an unsuccessful row:
        If we get an unsuccessful row it is most likely due to the target not being in correct position or moving.
        So better to start over than to try and work with mixed/noisy data.
    """
    while True:
        emotions = []
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


def main():
    # Get a reference to webcam
    video_capture = cv2.VideoCapture("/dev/video0")
    if __debug__:
        n_samples = 10
    else:
        n_samples = 30

    emotions = get_emotions(video_capture, n_samples)
    emotions = map(lambda e: e["emotion"], emotions)
    emotions = pd.DataFrame(emotions)
    if __debug__ or True:  # Don't print in final version
        print(emotions)
    emotions = emotions.mean(axis=0)

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
    if __debug__ or True:  # Don't print in final version
        print(emotions)


if __name__ == "__main__":
    main()
