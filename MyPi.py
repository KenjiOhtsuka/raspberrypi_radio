import os
import Network
class MyPi(object):
    def __init__(self):
        self.volume = int(commands.getoutput('amixer sget PCM | awk -F"[][%]" \'/dB/ { print $2 }\''))

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

    def play():
        #if 
        self.player_pid = subprocess.Popen(shlex.split('mplayer -quiet -playlist http://www.listenlive.eu/bbcradio4.m3u'))

