#!/usr/bin/python

import commands
import fcntl
import json
import os
import shlex
import socket
import subprocess
import time

import Adafruit_CharLCD as LCD

class MyPi(object):
    STATUS_PLAYING      = 1
    STATUS_MENU         = 2
    STATUS_TIME         = 3
    STATUS_RADIO_SELECT = 4
    STATUS_IP           = 5

    menu_items = [
        {
            "key"     : STATUS_TIME,
            "display" : "Time",
        },
        {
            "key"     : STATUS_RADIO_SELECT,
            "display" : 'Select Radio Station',
        },
        {
            "key"     : STATUS_IP,
            "display" : 'Show IP Address',
        },
    ]
    radio_stations = [
        {
            "name" : "BBC4",
            "url"  : "http://www.listenlive.eu/bbcradio4.m3u",
        },
        {
            "name" : "Classic",
            "url"  : "",
        },
        {
            "name" : "J-WAVE",
            "url"  : ""
        }
    ]
  
    def __init__(self):
        self.volume = \
            int(commands.getoutput('amixer sget PCM | awk -F"[][%]" \'/dB/ { print $2 }\''))
        self.lcd    = \
            LCD.Adafruit_CharLCDPlate()
        self.status = STATUS_PLAYING
        self.menu_index = 0
    
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
        self.show_message("Volume¥n" + str(self.volume))

    def down_volume(self):
        if self.volume > 0:
            self.volume -= 1
            self.set_device_volume(self.volume)
        self.show_message("Volume¥n" + str(self.volume))

    def play(self):
        self.player_pid = subprocess.Popen(shlex.split('mplayer -quiet -playlist http://www.listenlive.eu/bbcradio4.m3u'))

    def press_select(self):
        if self.status == STATUS_PLAYING:
            # show menu
            self.status = STATUS_MENU
            self.show_message(menu_items[self.menu_index])

    def press_up(self):
        if self.status == STATUS_MENU:
            self.menu_index += 1
            self.menu_index %= len(menu_items)
            self.show_message(menu_items[self.menu_index])
        elif self.status == STATUS_RADIO_SELECT:
        elif self.status == STATUS_VOLUME:

    def press_down(self):
        if self.status == STATUS_MENU:
            self.menu_index -= 1
            self.menu_index %= len(menu_items)
            if self.menu_index < 0:
                self.menu_index += len(menu_items)
            self.show_message(menu_items[self.menu_index])
        elif self.status == STATUS_RADIO_SELECT:
        elif self.status == STATUS_VOLUME:

    def press_right(self):
        if self.status == STATUS_MENU:
            menu_key = menu_items[self.menu_index]['key']
            if menu_key == STATUS_VOLUME:
            elif menu_key == STATUS_RADIO_SELECT:
            elif menu_key == STATUS_TIME:

    def press_left(self):
        if self.status == STATUS_MENU:
            
    ############################################################################
    # dont call below methods from outside
    ############################################################################
    def set_device_volume(self, value):
        os.system('amixer -q sset PCM ' + str(value) + '%')

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
    myPi.play()

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
        elif myPi.lcd.is_pressed(LCD.UP):
            if preButton in (LCD.UP, LCD.DOWN):
                myPi.up_volume()
            myPi.show_message(str(myPi.volume))
            preButton = LCD.UP
        elif myPi.lcd.is_pressed(LCD.DOWN):
            if preButton in (LCD.UP, LCD.DOWN):
                myPi.down_volume()
            myPi.show_message(str(myPi.volume))
            preButton = LCD.DOWN
        elif myPi.lcd.is_pressed(LCD.LEFT):
            myPi.show_message('LEFT')
            preButton = LCD.LEFT
        elif myPi.lcd.is_pressed(LCD.RIGHT):
            myPi.show_message('RIGHT')
            preButton = LCD.RIGHT

