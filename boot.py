#!/usr/bin/python

import os
import time
import Adafruit_CharLCD as LCD

#class MyPi(object):
#    # menu


lcd = LCD.Adafruit_CharLCDPlate()

# Make list of button value, text, and backlight color.
buttons = ( (LCD.SELECT, 'Select'),
            (LCD.LEFT,   'Left'  ),
            (LCD.UP,     'Up'    ),
            (LCD.DOWN,   'Down'  ),
            (LCD.RIGHT,  'Right' ) )

sameCount = 0
preButton = -1
while True:
    time.sleep(0.01)
    for button in buttons:
        if lcd.is_pressed(button[0]):
            lcd.clear()
            lcd.message(button[1] + str(sameCount))
            if preButton == button[0]:
                if sameCount > 50:
                    if preButton == LCD.SELECT:
                        os.system('sudo shutdown -h now')
                        lcd.clear()
                        lcd.message('shutdown')
                else:
                    sameCount += 1
            else:
                sameCount = 0
                preButton = button[0]

