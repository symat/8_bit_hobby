#!/usr/bin/python3

# start with sudo, as root access is needed for using GPIO

from gpiozero import LED
from time import sleep

# use "pinout" for the pin list
led = LED(18)

while True:
    led.on()
    sleep(1)
    led.off()
    sleep(1)