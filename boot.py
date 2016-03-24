#!/usr/bin/python

import commands
import os
import shlex
import time
import Adafruit_CharLCD as LCD

import MyPi


myPi = MyPi()

lcd = LCD.Adafruit_CharLCDPlate()

# Make list of button value, text, and backlight color.

sameCount = 0
preButton = -1
while True:
    time.sleep(0.01)
    if lcd.is_pressed(LCD.SELECT):
        if preButton == LCD.SELECT:
            sameCount += 1
            lcd.clear()
        else:
            sameCount = 0
            lcd.clear()
        lcd.message('SELECT ' + str(sameCount))
        if sameCount > 40:
            lcd.clear()
            lcd.message('shutdown')
            os.system('sudo shutdown -h now')
            break
        preButton = LCD.SELECT
    elif lcd.is_pressed(LCD.UP):
        if preButton in (LCD.UP, LCD.DOWN):
            myPi.up_volume()
        lcd.clear()
        lcd.message(str(myPi.volume))
        preButton = LCD.UP
    elif lcd.is_pressed(LCD.DOWN):
        if preButton in (LCD.UP, LCD.DOWN):
            myPi.down_volume()
        lcd.clear()
        lcd.message(str(myPi.volume))
        preButton = LCD.DOWN
    elif lcd.is_pressed(LCD.LEFT):
        lcd.clear()
        lcd.message('LEFT')
        preButton = LCD.LEFT
    elif lcd.is_pressed(LCD.RIGHT):
        lcd.clear()
        lcd.message('RIGHT')
        preButton = LCD.RIGHT

