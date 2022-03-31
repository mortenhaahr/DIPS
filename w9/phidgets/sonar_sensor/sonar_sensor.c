#include <phidget22.h>
#include <stdio.h>

// SETUP:
// VINT Hub Phidget with 6 ports.
// DST1200_0 sensor connected. (Multiple can also be connected)

// Code found from: https://www.phidgets.com/?view=code_samples&lang=C
// By specifying the DST1200_0 sensor.

static void CCONV onDistanceChange(PhidgetDistanceSensorHandle ch, void *ctx, uint32_t distance)
{
	printf("Distance: %u\n", distance);
}

int main()
{
	// Create channel
	PhidgetDistanceSensorHandle distanceSensor0;
	PhidgetDistanceSensor_create(&distanceSensor0);
	Phidget_setHubPort((PhidgetHandle) distanceSensor0, 0); // Set port to 0. If this is the only sensor it is unnecessary as it has auto-discovery.
	// Give callback function
	PhidgetDistanceSensor_setOnDistanceChangeHandler(distanceSensor0, onDistanceChange, NULL);

	// Add an extra Sensor
	// PhidgetDistanceSensorHandle distanceSensor5;
	// PhidgetDistanceSensor_create(&distanceSensor5);
	// Phidget_setHubPort((PhidgetHandle) distanceSensor5, 5);
	// // Give callback function
	// PhidgetDistanceSensor_setOnDistanceChangeHandler(distanceSensor5, onDistanceChange, NULL);
	// Phidget_openWaitForAttachment((PhidgetHandle)distanceSensor5, 5000);

	Phidget_openWaitForAttachment((PhidgetHandle)distanceSensor0, 5000);
	// Wait until Enter has been pressed before exiting
	getchar();
	Phidget_close((PhidgetHandle)distanceSensor0);
	PhidgetDistanceSensor_delete(&distanceSensor0);
}