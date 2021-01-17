#!/bin/bash

ssh pi "mkdir -p /home/pi/8_bit_hobby"

rsync -a --exclude '.idea' --exclude '.git' ./ pi:/home/pi/8_bit_hobby