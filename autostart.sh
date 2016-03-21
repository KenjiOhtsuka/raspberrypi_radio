#!/bin/sh
sudo mplayer -quiet -playlist http://www.listenlive.eu/bbcradio4.m3u &
sudo python /home/pi/raspberrypi_radio/boot.py
