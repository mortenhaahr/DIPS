# Notes on emotion detection
## Device
- We wanted to run the program on a RPi but we had some dependency issues.
- The emotion detection algorithm is built in Tensorflow which has not been properly ported for the ARM architecture.
- It was actually very difficult to find a similar SBC (single-board computer) like the RPi that isn't using an ARM based CPU. Below are listed a few solutions that could be applied to solve this issue:
  - Spend more money and buy a computer with bigger form factor that runs x86 or x64 architecture.
  - Write your own emotion detection ML algorithm that doesn't depend on Tensorflow. Alternative could potentially be Pytorch, SKlearn or similar.
  - Use a cloud based computation. Have the RPi send the images to a server in the cloud that computes the results and saves it. Have the RPi share the results with the local network.
- Our solution was to use a PC for this small prototype.

## Lighting
- There are some issues with the lighting. If the image is too dark then the ML model doesn't work.

## Context
- It would be really nice if the program had a way to differentiate between two people and could append that to the context model.