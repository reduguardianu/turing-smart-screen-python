# turing-smart-screen-python - a Python system monitor and library for USB-C displays like Turing Smart Screen or XuanFang
# https://github.com/mathoudebine/turing-smart-screen-python/

# Copyright (C) 2021-2023  Matthieu Houdebine (mathoudebine)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from library.lcd.lcd_comm import Orientation
from library.lcd.lcd_comm_rev_a import LcdCommRevA
from library.lcd.lcd_comm_rev_b import LcdCommRevB
from library.lcd.lcd_comm_rev_c import LcdCommRevC
from library.lcd.lcd_comm_rev_d import LcdCommRevD
from library.lcd.lcd_simulated import LcdSimulated
from library.log import logger

class Display:
    def __init__(self,
                 com_port,
                 revision,
                 width,
                 height,
                 brightness,
                 display_rgb_led,
                 update_queue=None):
        self.lcd = None
        self.brightness = brightness
        self.display_rgb_led = display_rgb_led
        self.lcd = LcdCommRevA(com_port=com_port, update_queue=update_queue)
        match revision:
            case "A":
                self.lcd = LcdCommRevA(com_port=com_port, update_queue=update_queue)
            case "B":
                self.lcd = LcdCommRevB(com_port=com_port, update_queue=update_queue)
            case "C":
                self.lcd = LcdCommRevC(com_port=com_port, update_queue=update_queue, display_width=width, display_height=height)
            case "D":
                self.lcd = LcdCommRevD(com_port=com_port, update_queue=update_queue)
            case "SIMU":
                self.lcd = LcdSimulated(display_width=width, display_height=height)
            case _:
                logger.error("Unknown display revision '", revision, "'")


    def setup(self):
        self.lcd.Reset()

        # Send initialization commands
        self.lcd.InitializeComm()


    def turn_on(self):
        # Turn screen on in case it was turned off previously
        self.lcd.ScreenOn()

        # Set brightness
        self.lcd.SetBrightness(self.brightness)

        # Set backplate RGB LED color (for supported HW only)
        self.lcd.SetBackplateLedColor(self.display_rgb_led)

    def turn_off(self):
        # Turn screen off
        self.lcd.ScreenOff()

        # Turn off backplate RGB LED
        self.lcd.SetBackplateLedColor(led_color=(0, 0, 0))
