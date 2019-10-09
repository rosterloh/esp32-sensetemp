# ESP32 SenseTemp
MicroPython on an ESP32 connected to a SenseTemp

## Setup
- ```pip3 install -U --user esptool micropy-cli```
- Get the [latest](https://micropython.org/download#esp32) micropython and flash ESP32
- ```espefuse.py --port /dev/ttyUSB0 set_flash_voltage 3.3V```
- ```micropy stubs add esp32-micropython-1.11.0```
- ```micropy```

## Links
- [SenseTemp Crowdsupply](https://www.crowdsupply.com/capable-robot-components/sensetemp)
- [SenseTemp Github](https://github.com/CapableRobot/SenseTemp)
- [micropy](https://github.com/BradenM/micropy-cli)
- [PyMakr](https://github.com/pycom/pymakr-vsc)