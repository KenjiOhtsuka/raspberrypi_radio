#!/usr/bin/python
# -*- coding: utf-8 -*-

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
    STATUS_VOLUME       = 4
    STATUS_RADIO_SELECT = 5
    STATUS_IP           = 6
    STATUS_REBOOT       = 7
    STATUS_SHUTDOWN     = 8

    menu_items = [
        {
            "key"     : STATUS_VOLUME,
            "display" : 'Control Volume',
        },
        {
            "key"     : STATUS_RADIO_SELECT,
            "display" : 'Radio Station',
        },
        {
            "key"     : STATUS_IP,
            "display" : 'Show IP Address',
        },
        {
            "key"     : STATUS_TIME,
            "display" : "Time",
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
            "name" : "Juzz Big Band - J-Last",
            "url"  : "http://yp.shoutcast.com/sbin/tunein-station.pls?id=99180486"
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
        self.status = MyPi.STATUS_PLAYING
        self.menu_index          = 0
        self.radio_station_index = 0
        self.load_radio_stations()
        self.player_pid          = None

    def load_radio_stations(self):
        if os.path.isfile("config/radio_stations.json"):
            try:
                with open("config/radio_stations.json") as f:
                    self.radio_stations = json.load(f)
                return
            except:
                print 'error'
        if os.path.isfile("config/radio_stations.default.json"):
            try:
                with open("config/radio_stations.default.json") as f:
                    self.radio_stations = json.load(f)
                return
            except:
                print 'error'
        self.radio_stations = MyPi.radio_stations


    def is_connected(self):
        response = os.system('sudo ping -c 1 google.com')
        if response == 0:
            return True
        else:
            return False
    
    def shutdown(self):
        self.stop()
        self.show_message('Start Shutdown')
        os.system('sudo shutdown -h now')

    def reboot(self):
        self.stop()
        self.show_message('Start Reboot')
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
        self.show_message("Volume\n" + str(self.volume))

    def show_datetime(self):
        self.show_message(datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    def show_ip(self):
        self.show_message(
            'eth0  ' + self.get_eth_ip() + "\n" +
            "wlan0 " + self.get_wlan_ip())

    def play(self, radio_station_index = 0):
        if self.is_connected():
            self.stop()
            self.player_pid = \
                subprocess.Popen(
                    shlex.split(
                        'mplayer -quiet -playlist ' + self.radio_stations[radio_station_index]['url']),
                    stdin=subprocess.PIPE)
            return
        self.show_message("Not Connected")

    def stop(self):
        if self.player_pid != None and self.player_pid.returncode == None:
            self.show_message('Stopping')
            self.player_pid.stdin.write('q')
            self.player_pid.wait()
            self.show_message('Stopped')

    def show_playing(self):
        self.show_message("Playing\n" + self.radio_stations[self.radio_station_index]['name'])

    def show_menu_item(self, menu_index):
        self.show_message(str(self.menu_index + 1) + ' ' + MyPi.menu_items[self.menu_index]['display'])

    def press_select(self):
        if self.status == MyPi.STATUS_PLAYING:
            self.status = MyPi.STATUS_MENU
            self.show_menu_item(self.menu_index)
            time.sleep(0.3)
        else:
            self.status = MyPi.STATUS_PLAYING
            self.show_playing()
            time.sleep(0.3)

    def press_up(self):
        if self.status == MyPi.STATUS_MENU:
            self.menu_index -= 1
            self.menu_index %= len(MyPi.menu_items)
            if self.menu_index < 0:
                self.menu_index += len(MyPi.menu_items)
            self.show_menu_item(self.menu_index)
            time.sleep(0.3)
        elif self.status == MyPi.STATUS_RADIO_SELECT:
            self.radio_station_index -= 1
            self.radio_station_index %= len(self.radio_stations)
            if self.radio_station_index < 0:
                self.radio_station_index += len(self.radio_stations)
            self.show_message(self.radio_stations[self.radio_station_index]['name'])
            time.sleep(0.3)
        elif self.status == MyPi.STATUS_VOLUME:
            self.up_volume()

    def press_down(self):
        if self.status == MyPi.STATUS_MENU:
            self.menu_index += 1
            self.menu_index %= len(MyPi.menu_items)
            self.show_menu_item(self.menu_index)
            time.sleep(0.3)
        elif self.status == MyPi.STATUS_RADIO_SELECT:
            self.radio_station_index += 1
            self.radio_station_index %= len(self.radio_stations)
            self.show_message(self.radio_stations[self.radio_station_index]['name'])
            time.sleep(0.3)
        elif self.status == MyPi.STATUS_VOLUME:
            self.down_volume()

    def press_right(self):
        if self.status == MyPi.STATUS_MENU:
            menu_key = MyPi.menu_items[self.menu_index]['key']
            if menu_key == MyPi.STATUS_VOLUME:
                self.status = menu_key
                self.show_volume()
            elif menu_key == MyPi.STATUS_RADIO_SELECT:
                self.status = menu_key
                self.show_message(self.radio_stations[self.radio_station_index]['name'])
            elif menu_key == MyPi.STATUS_IP:
                self.status = menu_key
                self.show_ip()
            elif menu_key == MyPi.STATUS_TIME:
                self.status = menu_key
                self.show_datetime()
                return
            elif menu_key == MyPi.STATUS_SHUTDOWN:
                self.status = menu_key
                self.show_message("Do you want to\nShutdown?")
            elif menu_key == MyPi.STATUS_REBOOT:
                self.status = menu_key
                self.show_message("Do you want to\nReboot?")
        elif self.status == MyPi.STATUS_RADIO_SELECT:
            self.play(self.radio_station_index)
            self.show_playing()
            self.status = MyPi.STATUS_PLAYING
        elif self.status == MyPi.STATUS_SHUTDOWN:
            self.shutdown()
        elif self.status == MyPi.STATUS_REBOOT:
            self.reboot()
        elif self.status == MyPi.STATUS_IP:
            self.lcd.move_left()
            time.sleep(0.3)
            
    def press_left(self):
        if self.status == MyPi.STATUS_MENU:
            self.press_select()
            return
        if self.status == MyPi.STATUS_VOLUME:
            self.status = MyPi.STATUS_MENU
            self.show_menu_item(self.menu_index)
            time.sleep(0.3)
            return
        if self.status == MyPi.STATUS_RADIO_SELECT:
            self.status = MyPi.STATUS_MENU
            self.show_menu_item(self.menu_index)
            time.sleep(0.3)
            return
        if self.status == MyPi.STATUS_TIME:
            self.status = MyPi.STATUS_MENU
            self.show_menu_item(self.menu_index)
            time.sleep(0.3)
            return
        if self.status == MyPi.STATUS_IP:
            self.status = MyPi.STATUS_MENU
            self.show_menu_item(self.menu_index)
            time.sleep(0.3)
            return
        if self.status == MyPi.STATUS_SHUTDOWN:
            self.status = MyPi.STATUS_MENU
            self.show_menu_item(self.menu_index)
            time.sleep(0.3)
            return
        if self.status == MyPi.STATUS_REBOOT:
            self.status = MyPi.STATUS_MENU
            self.show_menu_item(self.menu_index)
            time.sleep(0.3)
            return
            
    ############################################################################
    # dont call below methods from outside
    ############################################################################
    def set_device_volume(self, value):
        os.system('amixer -q sset PCM ' + str(value) + '%')

    def get_wlan_ip(self):
        return MyPi.get_ip('wlan0')

    def get_eth_ip(self):
        return MyPi.get_ip('eth0')

    @staticmethod
    def get_ip(ifname):
        ip = MyPi.ifconfig(ifname)
        if ip == None:
            return 'No IP Address'
        return ip

    @staticmethod
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
            self.press_left()
        elif self.lcd.is_pressed(LCD.RIGHT):
            self.press_right()

if __name__ == "__main__":
    myPi = MyPi()
    myPi.show_message("Booting")
    myPi.play()
    myPi.show_playing()

    while True:
        time.sleep(0.1)
        myPi.detect_button()
