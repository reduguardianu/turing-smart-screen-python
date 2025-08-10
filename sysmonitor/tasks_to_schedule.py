from datetime import timedelta
from library import stats, config
from library.scheduler import async_job, schedule


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