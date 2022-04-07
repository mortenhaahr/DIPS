#!/usr/bin/env python3
# import libraries
import cv2
import face_recognition
from deepface import DeepFace

# Get a reference to webcam 
video_capture = cv2.VideoCapture("/dev/video0")

# Initialize variables
face_locations = []

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_frame = frame[:, :, ::-1]

    # Find all the faces in the current frame of videon
    face_locations = face_recognition.face_locations(rgb_frame)

    # Display the results
    for top, right, bottom, left in face_locations:
        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

    # Display the resulting image
    cv2.imshow('Video', frame)

    try:
        obj = DeepFace.detectFace(frame)
        analyze = DeepFace.analyze(frame,actions=['age', 'gender', 'race', 'emotion'])  #same thing is happing here as the previous example, we are using the analyze class from deepface and using ‘frame’ as input
        print(analyze['dominant_emotion'])  #here we will only go print out the dominant emotion also explained in the previous example
    except Exception as e:
        print(e)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()