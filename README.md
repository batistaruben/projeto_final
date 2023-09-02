# proj
Projeto Final de Licenciatura

RASPBERRY PI

To configure the Raspberry PI (Model 3 A+), it is necessary:
- Raspberry PI
- SD Card
- SD Card Reader
- Raspberry PI Imager

Download the software responsible for installing the operating system on the Raspberry PI:
https://www.raspberrypi.com/software/

Connect the SD card to the computer and use the downloaded software to install the OS in the SD card. 
Then, should simply insert the SD card in the existing slot on the Raspberry PI and power on. 
After these steps, should follow the described steps at the Raspberry PI to complete the configuration. 

-------------------------------------------------------------------------------------------------------

ESP32

To configure the ESP32 (WROOM), it is necessary:
- ESP32
- Type-C cable
- Arduino IDE

Download and Install the Arduino IDE software at:
https://www.arduino.cc/en/software

After the installation, open Arduino IDE and go to File>Preferences. At the "Aditional boards manager URLs:" text box
instert the following libraries:
http://arduino.esp8266.com/stable/package_esp8266com_index.json
https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json

After downloading and installing the given libraries should be done. May be necessary in some cases to install some drivers
due to the fact that the port may not be correctly, in that case, download the Drivers of the corresponding ESP32 module.

-------------------------------------------------------------------------------------------------------

Arduino IDE Extra Libraries

The sensors hardware need some libraries to work properly. Also, if you intend to run the given c++ code, you will need to have these libraries installed:

- Adafruit BusIO by Adafruit (version 1.14.3)
- Adafruit SHT31 by Adafruit (version 2.2.2)
- ArduinoJson by Benoit (version 6.21.3)
- AsyncTCP by dvarrel (version 1.1.4)
- DFRobot_DHT11 by DFRobot (version 1.0.0)
- DallasTemperature by Miles Burton (version 3.9.0)
- ESPAsyncTCP by dvarrel (version 1.2.4)
- Microfire_SHT3x by Microfire LLC (version 1.0.0)
- OneWire by Jim Studt (version 2.3.7)
- PubSubClient by Nick O'Leary (version 2.8)
- SHT31 by Rob Tillaart (version 0.3.8)



