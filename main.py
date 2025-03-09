#!/usr/bin/env python
# turing-smart-screen-python - a Python system monitor and library for USB-C displays like Turing Smart Screen or XuanFang
# https://github.com/mathoudebine/turing-smart-screen-python/

# Copyright (C) 2021-2023  Matthieu Houdebine (mathoudebine)
# Copyright (C) 2022-2023  Rollbacke
# Copyright (C) 2022-2023  Ebag333
# Copyright (C) 2022-2023  w1ld3r
# Copyright (C) 2022-2023  Charles Ferguson (gerph)
# Copyright (C) 2022-2023  Russ Nelson (RussNelson)
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

# This file is the system monitor main program to display HW sensors on your screen using themes (see README)
import glob
import os
import sys

import atexit
import locale
import platform
import signal
import subprocess
import time
from pathlib import Path
from PIL import Image
from sysmonitor import SysMonitor
from weather import Weather
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from threading import Thread

from library.log import logger


MAIN_DIRECTORY = str(Path(__file__).parent.resolve()) + "/"

class TuringSmartScreenRunner:
    def __init__(self):
        self.sysMonitor = SysMonitor()
        self.weather = Weather()

    def start(self):
        Thread(target=self.sysMonitor.run, daemon=True).start()
        Thread(target=self.weather.run, daemon=True).start()

    def stop(self, qtApp):
        self.sysMonitor.turn_off()
        self.weather.turn_off()
        qtApp.quit()

if __name__ == "__main__":

    app = TuringSmartScreenRunner()

    # Apply system locale to this program
    locale.setlocale(locale.LC_ALL, '')

    logger.debug("Using Python %s" % sys.version)


    def on_signal_caught(signum, frame=None):
        logger.info("Caught signal %d, exiting" % signum)
        app.stop()


    def on_exit_tray(tray_icon, item):
        logger.info("Exit from tray icon")
        app.stop()


    def on_clean_exit(*args):
        logger.info("Program will now exit")
        app.stop()

    # Set the different stopping event handlers, to send a complete frame to the LCD before exit
    signal.signal(signal.SIGINT, on_signal_caught)
    signal.signal(signal.SIGTERM, on_signal_caught)
    signal.signal(signal.SIGQUIT, on_signal_caught)

    app.start()
    qtApp = QApplication([])
    qtApp.setQuitOnLastWindowClosed(False)
    icon = QIcon("tray.png")

    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)

    menu = QMenu()

    quitOption = QAction("Quit")
    quitOption.triggered.connect(lambda:app.stop(qtApp))
    menu.addAction(quitOption)

    tray.setContextMenu(menu)
    qtApp.exec()
