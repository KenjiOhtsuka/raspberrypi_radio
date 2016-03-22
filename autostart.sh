#!/bin/sh
_IP=$(hostname -I) || true
if [ "$_IP" ]; then
  sudo mplayer -quiet -playlist http://www.listenlive.eu/bbcradio4.m3u &
fi
sudo python /home/pi/raspberrypi_radio/boot.py
