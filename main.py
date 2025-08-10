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
import sys


import locale

import signal

import time
from pathlib import Path

from library.inactivity_checker import InactivityChecker
from sysmonitor.sysmonitor import SysMonitor
from weather.weather import Weather
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from threading import Thread

from library.log import logger
from configparser import ConfigParser

MAIN_DIRECTORY = str(Path(__file__).parent.resolve()) + "/"

class TuringSmartScreenRunner:
    def __init__(self, config):
        if config.has_section("sysmonitor"):
            self.sysMonitor = SysMonitor(config.get("sysmonitor", "device"))
        else:
            self.sysMonitor = None
        if config.has_section("weather"):
            self.weather = Weather(config.get("weather", "device"))
        else:
            self.weather = None
        
        if self.sysMonitor is None and self.weather is None:
            logger.error("No sysmonitor or weather device configured, exiting")
            sys.exit(1)

    def start(self):
        if self.sysMonitor is not None:
            self.sysmonitorThread = Thread(target=self.sysMonitor.run, daemon=True)
            self.sysmonitorThread.start()
        if self.weather is not None:
            self.weatherThread = Thread(target=self.weather.run, daemon=True)
            self.weatherThread.start()

    def stop(self):
        if self.sysMonitor is not None:
            self.sysMonitor.turn_off()
        if self.weather is not None:
            self.weather.turn_off()



if __name__ == "__main__":

    config = ConfigParser()
    config.read("config.ini")

    app = TuringSmartScreenRunner(config)

    # Apply system locale to this program
    locale.setlocale(locale.LC_ALL, '')

    logger.debug("Using Python %s" % sys.version)

    qtApp = QApplication([])
    qtApp.setQuitOnLastWindowClosed(False)

    def on_signal_caught(signum, frame=None):
        logger.info("Caught signal %d, exiting" % signum)
        app.stop()
        qtApp.quit()


    def on_exit_tray(tray_icon, item):
        logger.info("Exit from tray icon")
        app.stop()
        qtApp.quit()


    def on_clean_exit(*args):
        logger.info("Program will now exit")
        app.stop()
        qtApp.quit()

    def restart_app(app, reason):
        logger.info(f"Restarting application: {reason}" )
        app.stop()
        time.sleep(10)
        app = TuringSmartScreenRunner()
        app.start()


    # Set the different stopping event handlers, to send a complete frame to the LCD before exit
    signal.signal(signal.SIGINT, on_signal_caught)
    signal.signal(signal.SIGTERM, on_signal_caught)
    signal.signal(signal.SIGQUIT, on_signal_caught)

    app.start()

    icon = QIcon("tray.png")

    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)

    inactivity_checker = InactivityChecker(inactivity_threshold=10, callback=lambda: restart_app(app, "Inactivity timeout reached"))

    menu = QMenu()

    quitOption = QAction("Quit")
    quitOption.triggered.connect(lambda: on_exit_tray(tray, quitOption))

    restartOption = QAction("Restart")
    restartOption.triggered.connect(lambda: restart_app(app, "User requested restart"))

    menu.addAction(restartOption)
    menu.addAction(quitOption)

    tray.setContextMenu(menu)
    qtApp.exec()
