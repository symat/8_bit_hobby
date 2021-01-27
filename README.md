# 8_bit_hobby
Developing an 8bit computer and peripherals, testers, debuggers, etc.

After some thoughts, I think this project will feature:
* an eZ80 microcontroller based home made computer
  * something similar to this project: https://z20x.computer/
* raspberry pi for debugging the machine
  * implementing the Zilog Debug Interface to be able to connect to the eZ80
  * create tools to load code to the RAM / ROM / flash drive
* porting / implementing some basic OS, hopefully in C


## Prerequisites

Beside building the computer and the devboard :)

* install python libraries (I'm using python 3.6 on Raspberry Pi OS)
  * `sudo pip install gpiozero` - for easily managing GPIO pins

* additional things, if we would use the MCP23S17 I/O extender chip (not yet)
  * 'sudo pip install spidev RPiMCP23S17'
  * you need to load the SPI kernel modules before you can use SPI devices. Use the gpio command: `gpio load spi`

* to be able to open / edit the PCB plans, install: kicad (https://kicad.org/download/ubuntu/)

