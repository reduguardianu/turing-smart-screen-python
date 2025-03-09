# turing-smart-screen-python - a Python system monitor and library for USB-C displays like Turing Smart Screen or XuanFang
# https://github.com/mathoudebine/turing-smart-screen-python/

# Copyright (C) 2021-2023  Matthieu Houdebine (mathoudebine)
# Copyright (C) 2022-2023  Rollbacke
# Copyright (C) 2022-2023  Ebag333
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

import sched
import threading
import time
from datetime import timedelta
from functools import wraps

import library.config as config
import library.stats as stats

STOPPING = False


def async_job(threadname=None):
    """ wrapper to handle asynchronous threads """

    def decorator(func):
        """ Decorator to extend async_func """

        @wraps(func)
        def async_func(*args, **kwargs):
            """ create an asynchronous function to wrap around our thread """
            func_hl = threading.Thread(target=func, name=threadname, args=args, kwargs=kwargs)
            func_hl.start()
            return func_hl

        return async_func

    return decorator


def schedule(interval):
    """ wrapper to schedule asynchronous threads """

    def decorator(func):
        """ Decorator to extend periodic """

        def periodic(scheduler, periodic_interval, action, actionargs=()):
            """ Wrap the scheduler with our periodic interval """
            global STOPPING
            if not STOPPING:
                # If the program is not stopping: re-schedule the task for future execution
                scheduler.enter(periodic_interval, 1, periodic,
                                (scheduler, periodic_interval, action, actionargs))
            action(*actionargs)

        @wraps(func)
        def wrap(
                *args,
                **kwargs
        ):
            """ Wrapper to create our schedule and run it at the appropriate time """
            if interval == 0:
                return
            scheduler = sched.scheduler(time.time, time.sleep)
            periodic(scheduler, interval, func, args)
            scheduler.run()

        return wrap

    return decorator


@async_job("CPU_Percentage")
@schedule(timedelta(seconds=config.THEME_DATA['STATS']['CPU']['PERCENTAGE'].get("INTERVAL", 0)).total_seconds())
def CPUPercentage(display):
    """ Refresh the CPU Percentage """
    # logger.debug("Refresh CPU Percentage")
    stats.CPU.percentage(display)


@async_job("CPU_Frequency")
@schedule(timedelta(seconds=config.THEME_DATA['STATS']['CPU']['FREQUENCY'].get("INTERVAL", 0)).total_seconds())
def CPUFrequency(display):
    """ Refresh the CPU Frequency """
    # logger.debug("Refresh CPU Frequency")
    stats.CPU.frequency(display)


@async_job("CPU_Load")
@schedule(timedelta(seconds=config.THEME_DATA['STATS']['CPU']['LOAD'].get("INTERVAL", 0)).total_seconds())
def CPULoad(display):
    """ Refresh the CPU Load """
    # logger.debug("Refresh CPU Load")
    stats.CPU.load(display)


@async_job("CPU_Temperature")
@schedule(timedelta(seconds=config.THEME_DATA['STATS']['CPU']['TEMPERATURE'].get("INTERVAL", 0)).total_seconds())
def CPUTemperature(display):
    """ Refresh the CPU Temperature """
    # logger.debug("Refresh CPU Temperature")
    stats.CPU.temperature(display)


@async_job("CPU_FanSpeed")
@schedule(timedelta(seconds=config.THEME_DATA['STATS']['CPU']['FAN_SPEED'].get("INTERVAL", 0)).total_seconds())
def CPUFanSpeed(display):
    """ Refresh the CPU Fan Speed """
    # logger.debug("Refresh CPU Fan Speed")
    stats.CPU.fan_speed(display)


@async_job("GPU_Stats")
@schedule(timedelta(seconds=config.THEME_DATA['STATS'].get('GPU', {}).get("INTERVAL", 0)).total_seconds())
def GpuStats(display):
    """ Refresh the GPU Stats """
    # logger.debug("Refresh GPU Stats")
    stats.Gpu.stats(display)


@async_job("Memory_Stats")
@schedule(timedelta(seconds=config.THEME_DATA['STATS'].get('MEMORY', {}).get("INTERVAL", 0)).total_seconds())
def MemoryStats(display):
    # logger.debug("Refresh memory stats")
    stats.Memory.stats(display)


@async_job("Disk_Stats")
@schedule(timedelta(seconds=config.THEME_DATA['STATS'].get('DISK', {}).get("INTERVAL", 0)).total_seconds())
def DiskStats(display):
    # logger.debug("Refresh disk stats")
    stats.Disk.stats(display)


@async_job("Net_Stats")
@schedule(timedelta(seconds=config.THEME_DATA['STATS'].get('NET', {}).get("INTERVAL", 0)).total_seconds())
def NetStats(display):
    # logger.debug("Refresh net stats")
    stats.Net.stats(display)


@async_job("Date_Stats")
@schedule(timedelta(seconds=config.THEME_DATA['STATS'].get('DATE', {}).get("INTERVAL", 0)).total_seconds())
def DateStats(display):
    # logger.debug("Refresh date stats")
    stats.Date.stats(display)


@async_job("SystemUptime_Stats")
@schedule(timedelta(seconds=config.THEME_DATA['STATS'].get('UPTIME', {}).get("INTERVAL", 0)).total_seconds())
def SystemUptimeStats(display):
    # logger.debug("Refresh system uptime stats")
    stats.SystemUptime.stats(display)


@async_job("Custom_Stats")
@schedule(timedelta(seconds=config.THEME_DATA['STATS'].get('CUSTOM', {}).get("INTERVAL", 0)).total_seconds())
def CustomStats(display):
    # print("Refresh custom stats")
    stats.Custom.stats(display)


@async_job("Weather_Stats")
@schedule(timedelta(seconds=max(300.0, config.THEME_DATA['STATS'].get('WEATHER', {}).get("INTERVAL", 0))).total_seconds())
def WeatherStats(display):
    # logger.debug("Refresh Weather data")
    stats.Weather.stats(display)


@async_job("Ping_Stats")
@schedule(timedelta(seconds=config.THEME_DATA['STATS'].get('PING', {}).get("INTERVAL", 0)).total_seconds())
def PingStats(display):
    # logger.debug("Refresh Ping data")
    stats.Ping.stats(display)


@async_job("Queue_Handler")
@schedule(timedelta(milliseconds=1).total_seconds())
def QueueHandler():
    # Do next action waiting in the queue
    global STOPPING
    if STOPPING:
        # Empty the action queue to allow program to exit cleanly
        while not config.update_queue.empty():
            f, args = config.update_queue.get()
            f(*args)
    else:
        # Execute first action in the queue
        f, args = config.update_queue.get()
        if f:
            f(*args)


def is_queue_empty() -> bool:
    return config.update_queue.empty()
