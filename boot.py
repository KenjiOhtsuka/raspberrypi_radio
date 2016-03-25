#!/usr/bin/python

import commands
import datetime
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
    STATUS_REBOOT       = 6
    STATUS_SHUTDOWN     = 7

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
        {
            "key"     : STATUS_REBOOT,
            "display" : 'Reboot',
        },
        {
            "key"     : STATUS_SHUTDOWN,
            "display" : 'Shutdown',
        },
    ]
    radio_stations = [
        {
            "name" : "BBC4",
            "url"  : "http://www.listenlive.eu/bbcradio4.m3u",
        },
        {
            "name" : "Symphony",
            "url"  : "http://yp.shoutcast.com/sbin/tunein-station.pls?id=178543",
        },
        {
            "name" : "Chumber",
            "url"  : "http://yp.shoutcast.com/sbin/tunein-station.pls?id=631044",
        },
        {
            "name" : "J-WAVE",
            "url"  : "http://www.j-wave.co.jp/radiobar/source/j-wave2.asx",
        },
    ]
  
    def __init__(self):
        self.volume = \
            int(commands.getoutput('amixer sget PCM | awk -F"[][%]" \'/dB/ { print $2 }\''))
        self.lcd    = \
            LCD.Adafruit_CharLCDPlate()
        self.status = STATUS_PLAYING
        self.menu_index          = 0
        self.radio_station_index = 0

    def is_connected(self):
        response = os.system('ping -c 1 google.com')
        if response == 0:
            return True
        else:
            return False
    
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
        self.show_volume()

    def down_volume(self):
        if self.volume > 0:
            self.volume -= 1
            self.set_device_volume(self.volume)
        self.show_volume()

    def show_volume(self):
        self.show_message("Volume¥n" + str(self.volume))

    def show_datetime(self):
        self.show_message(datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    def show_ip(self):
        eth0_ip = self.ifconfig('eth0')
        if eth0_ip == None: eth0_ip = 'None'
        wlan0_ip = self.ifconfig('wlan0')
        if wlan0_ip == None: wlan0_ip = 'None'
        self.show_message(
            'eth0  ' + eth0_ip + "\n" +
            "wlan0 " + wlan0_ip)

    def play(self, radio_station_index = 0):
        if self.is_connected():
            if self.player_pid.returncode == None:
                self.player_pid.wait()
            self.player_pid = \
                subprocess.Popen(
                    shlex.split(
                        'mplayer -quiet -playlist ' + radio_stations[radio_station_index]))
            return
        self.show_message("Not Connected")

    def press_select(self):
        if self.status == STATUS_PLAYING:
            # show menu
            self.status = STATUS_MENU
            self.show_message(menu_items[self.menu_index])
        else:
            self.status = STATUS_PLAYING

    def press_up(self):
        if self.status == STATUS_MENU:
            self.menu_index -= 1
            self.menu_index %= len(menu_items)
            if self.menu_index < 0:
                self.menu_index += len(menu_items)
            self.show_message(menu_items[self.menu_index])
        elif self.status == STATUS_RADIO_SELECT:
            self.radio_station_index -= 1
            self.radio_station_index %= len(radio_stations)
            if self.radio_station_index < 0:
                self.radio_station_index += len(radio_stations)
            self.show_message(radio_stations[self.radio_station_index]['name'])
        elif self.status == STATUS_VOLUME:
            self.up_volume()

    def press_down(self):
        if self.status == STATUS_MENU:
            self.menu_index += 1
            self.menu_index %= len(menu_items)
            self.show_message(menu_items[self.menu_index])
        elif self.status == STATUS_RADIO_SELECT:
            self.radio_station_index += 1
            self.radio_station_index %= len(radio_stations)
            self.show_message(radio_stations[self.radio_station_index]['name'])
        elif self.status == STATUS_VOLUME:
            self.down_volume()

    def press_right(self):
        if self.status == STATUS_MENU:
            menu_key = menu_items[self.menu_index]['key']
            if menu_key == STATUS_VOLUME:
                self.status = menu_key
                self.show_volume()
            elif menu_key == STATUS_RADIO_SELECT:
                self.status = menu_key
                self.show_message(radio_stations[self.radio_station_index]['name'])
            elif menu_key == STATUS_IP:
                self.show_ip()
            elif menu_key == STATUS_TIME:
                self.show_datetime()
            elif menu_key == STATUS_SHUTDOWN:
                self.show_message("Do you want to\nShutdown?")
            elif menu_key == STATUS_REBOOT:
                self.show_message("Do you want to\nReboot?")
        elif self.status == STATUS_RADIO_SELECT:
            self.play()
            self.status = STATUS_PLAYING
        elif self.status == STATUS_SHUTDOWN:
            self.show_message('Start Shutdown')
            self.shutdown()
        elif self.status == STATUS_REBOOT:
            self.show_message('Start Reboot')
            self.reboot()
            
    def press_left(self):
        if self.status == STATUS_MENU:
            self.press_select()
            return
        if self.status == STATUS_VOLUME:
            self.status = STATUS_MENU
            self.show_message(menu_items[self.menu_index])
            return
        if menu_key == STATUS_RADIO_SELECT:
            self.status = STATUS_MENU
            self.show_message(menu_items[self.menu_index])
            return
        if menu_key == STATUS_TIME:
            self.status = STATUS_MENU
            self.show_message(menu_items[self.menu_index])
            return
        if menu_key == STATUS_IP:
            self.status = STATUS_MENU
            self.show_message(menu_items[self.menu_index])
            return
        if menu_key == STATUS_SHUTDOWN:
            self.status = STATUS_MENU
            self.show_message(menu_items[self.menu_index])
            return
        if menu_key == STATUS_REBOOT:
            self.status = STATUS_MENU
            self.show_message(menu_items[self.menu_index])
            return
            
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

    def detect_button(self):
        if self.lcd.is_pressed(LCD.SELECT):
            self.press_select()
        elif self.lcd.is_pressed(LCD.UP):
            self.press_up()
        elif self.lcd.is_pressed(LCD.DOWN):
            self.press_down()
        elif self.lcd.is_pressed(LCD.LEFT):
            self.press_down()
        elif self.lcd.is_pressed(LCD.RIGHT):
            self.press_right()

if __name__ == "__main__":
    myPi = MyPi()
    myPi.play()

    while True:
        time.sleep(0.03)
        myPi.detect_button()
