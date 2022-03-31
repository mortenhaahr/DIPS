#include <phidget22.h>
#include <stdio.h>

// SETUP:
// Phidget 8/8/8
// LED on output pin 0
// IR sensor on port 0.

// Example generated through https://www.phidgets.com/?view=code_samples&lang=C
// by selecting 1013_0 - PhidgetInterfaceKit 8/8/8 as the device and configuring the ports.

//Declare any event handlers here. These will be called every time the associated event occurs.

static void CCONV onVoltageChange(PhidgetVoltageInputHandle ch, void * ctx, double voltage) {
	printf("IR voltage: %lf\n", voltage);
}

int main() {
	//Declare your Phidget channels and other variables
	PhidgetVoltageInputHandle voltageInput0;
	PhidgetDigitalOutputHandle digitalOutput0;

	//Create your Phidget channels
	PhidgetVoltageInput_create(&voltageInput0);
	PhidgetDigitalOutput_create(&digitalOutput0);

	//Set addressing parameters to specify which channel to open (if any)

	//Assign any event handlers you need before calling open so that no events are missed.
	PhidgetVoltageInput_setOnVoltageChangeHandler(voltageInput0, onVoltageChange, NULL);

	//Open your Phidgets and wait for attachment
	Phidget_openWaitForAttachment((PhidgetHandle)voltageInput0, 5000);
	Phidget_openWaitForAttachment((PhidgetHandle)digitalOutput0, 5000);

	// NB. we couldn't get setDutyCycle to work as intended. Only works with value=1.
	PhidgetDigitalOutput_setDutyCycle(digitalOutput0, 1);

	//Wait until Enter has been pressed before exiting
	getchar();

	//Close your Phidgets once the program is done.
	Phidget_close((PhidgetHandle)voltageInput0);
	Phidget_close((PhidgetHandle)digitalOutput0);

	PhidgetVoltageInput_delete(&voltageInput0);
	PhidgetDigitalOutput_delete(&digitalOutput0);
}
