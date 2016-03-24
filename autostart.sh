#!/bin/sh
_IP=$(hostname -I) || true
sudo python /home/pi/raspberrypi_radio/boot.py
