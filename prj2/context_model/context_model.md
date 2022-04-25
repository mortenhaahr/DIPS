# Context model
This document describes the context model that is built and used in the project. The idea is to build a model that includes the factors that may affect the state of the smart home. 

One of the main parts of our system is to determine the mood. Therefore, we also try to aggregate some information from our context model into our decision support system to try and determine the mood with greater confidence.

## Time and date
The time and date is used in the system e.g. for the light. When it is late it dims the light.

## Emotion
The emotion of the user is a qualitative measurement that determines which mood the user has.
The available options are:
- angry
- happy
- sad
- neutral

The emotion values are generated through a camera that runs a ML model to determine the emotion of the person looking into the camera.

## Location
Which room the user is in. Used to determine which room to play music in and turn of the lights of no user is present in the current room.

## Positioning
Coordinates of the home. Used to determine which playlist to choose music from (e.g. Danish hits or German hits)

# Nice to haves

## Weather
The weather can be used in multiple ways in our system. It can be used to implement features like closing the windows if it is raining, preparing a hot cup of cocoa if it is snowing etc. Most of these features are not implemented in our system but they are thought in as a way to scale the system.

## Profile
It would be very nice to have profiling added to the system with some facial recognition, looking at the connected wifi devices or similar to determine which user is in the home and who is the mood based on. Maybe even with support for moods of different people.