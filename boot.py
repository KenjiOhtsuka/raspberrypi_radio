#!/usr/bin/python

import commands
import os
import shlex
import time
import Adafruit_CharLCD as LCD
import socket
import fcntl
import subprocess

class MyPi(object):
    def __init__(self):
        self.volume = \
            int(commands.getoutput('amixer sget PCM | awk -F"[][%]" \'/dB/ { print $2 }\''))
        self.lcd    = \
            LCD.Adafruit_CharLCDPlate()
    
    def shutdown(self):
        os.system('sudo shutdown -h now')

    def reboot(self):
        os.system('sudo shutdown -r now')

    def show_message(self, text, clear=True):
        if clear:
            self.lcd.clear()
        self.lcd.message(text)

    def up_volume(self):
        if self.volume < 100:
            self.volume += 1
            self.set_device_volume(self.volume)

    def down_volume(self):
        if self.volume > 0:
            self.volume -= 1
            self.set_device_volume(self.volume)

    def set_device_volume(self, value):
        os.system('amixer -q sset PCM ' + str(value) + '%')

    def play(self):
        self.player_pid = subprocess.Popen(shlex.split('mplayer -quiet -playlist http://www.listenlive.eu/bbcradio4.m3u'))

    def get_wlan_ip(self):
        return MyPi.get_ip('wlan0')

    def get_wlan_ip(self):
        return MyPi.get_ip('eth0')

    def get_ip(ifname):
        ip = MyPi.ifconfig(ifname)
        if ip == None:
            return 'No IP Address'
        return ip

    def ifconfig(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            result = fcntl.ioctl(s.fileno(), 0x8915, #SIOCGIFADDR,
                (ifname+'\0'*32)[:32])
        except IOError:
            return None

        return socket.inet_ntoa(result[20:24])

if __name__ == "__main__":
    myPi = MyPi()
    self.player_pid = subprocess.Popen(shlex.split('mplayer -playlist http://www.listenlive.eu/bbcradio4.m3u'))

    sameCount = 0
    preButton = -1
    while True:
        time.sleep(0.02)
        if myPi.lcd.is_pressed(LCD.SELECT):
            if preButton == LCD.SELECT:
                sameCount += 1
            else:
                sameCount = 0
            myPi.show_message('SELECT ' + str(sameCount))
            if sameCount > 40:
                myPi.show_message('shutdown')
                myPi.shutdown()
                break
            preButton = LCD.SELECT
        elif lcd.is_pressed(LCD.UP):
            if preButton in (LCD.UP, LCD.DOWN):
                myPi.up_volume()
            myPi.show_message(str(myPi.volume))
            preButton = LCD.UP
        elif lcd.is_pressed(LCD.DOWN):
            if preButton in (LCD.UP, LCD.DOWN):
                myPi.down_volume()
            myPi.show_message(str(myPi.volume))
            preButton = LCD.DOWN
        elif lcd.is_pressed(LCD.LEFT):
            myPi.show_message('LEFT')
            preButton = LCD.LEFT
        elif lcd.is_pressed(LCD.RIGHT):
            myPi.show_message('RIGHT')
            preButton = LCD.RIGHT

