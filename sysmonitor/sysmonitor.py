from datetime import timedelta
import queue
import time
from library import config
from library.lcd.lcd_comm import Orientation
from library.display import Display
from library.log import logger
from sysmonitor import tasks_to_schedule
from library.scheduler import async_job, schedule

def _get_full_path(path, name):
    if name:
        return path + name
    else:
        return None


def _get_theme_orientation() -> Orientation:
    if config.THEME_DATA["display"]["DISPLAY_ORIENTATION"] == 'portrait':
        if config.CONFIG_DATA["display"].get("DISPLAY_REVERSE", False):
            return Orientation.REVERSE_PORTRAIT
        else:
            return Orientation.PORTRAIT
    elif config.THEME_DATA["display"]["DISPLAY_ORIENTATION"] == 'landscape':
        if config.CONFIG_DATA["display"].get("DISPLAY_REVERSE", False):
            return Orientation.REVERSE_LANDSCAPE
        else:
            return Orientation.LANDSCAPE
    else:
        logger.warning("Orientation '", config.THEME_DATA["display"]["DISPLAY_ORIENTATION"],
                       "' unknown, using portrait")
        return Orientation.PORTRAIT


def _get_theme_size() -> tuple[int, int]:
    if config.THEME_DATA["display"].get("DISPLAY_SIZE", '') == '2.1"':
        return 480, 480
    elif config.THEME_DATA["display"].get("DISPLAY_SIZE", '') == '3.5"':
        return 320, 480
    elif config.THEME_DATA["display"].get("DISPLAY_SIZE", '') == '5"':
        return 480, 800
    elif config.THEME_DATA["display"].get("DISPLAY_SIZE", '') == '8.8"':
        return 480, 1920
    else:
        logger.warning(
            f'Cannot find valid DISPLAY_SIZE property in selected theme {config.CONFIG_DATA["config"]["THEME"]}, defaulting to 3.5"')
        return 320, 480


class SysMonitor(Display):
    def __init__(self, device):
        width, height = _get_theme_size()
        #com_port = config.CONFIG_DATA['config']['COM_PORT']
        com_port = device
        revision = config.CONFIG_DATA['display']['REVISION']
        brightness = config.CONFIG_DATA["display"]["BRIGHTNESS"]
        display_rgb_led = config.THEME_DATA['display'].get("DISPLAY_RGB_LED", (255, 255, 255))
        self.update_queue = queue.Queue()

        super().__init__(
            com_port=com_port,
            revision=revision,
            width=width,
            height=height,
            brightness=brightness,
            display_rgb_led=display_rgb_led,
            update_queue=self.update_queue)

    def run(self):
        self.stopping = False
        self.setup()
        # Turn on display, set brightness and LEDs for supported HW
        self.turn_on()
        
        # Set orientation
        self.lcd.SetOrientation(_get_theme_orientation())
        self.QueueHandler()
        self.display_static_images()
        self.display_static_text()
        self.wait_for_empty_queue(10)
        logger.info("Starting system monitoring")
        import library.stats as stats

        tasks_to_schedule.CPUPercentage(self); time.sleep(0.25)
        tasks_to_schedule.CPUFrequency(self); time.sleep(0.25)
        tasks_to_schedule.CPULoad(self); time.sleep(0.25)
        tasks_to_schedule.CPUTemperature(self); time.sleep(0.25)
        tasks_to_schedule.CPUFanSpeed(self); time.sleep(0.25)
        if stats.Gpu.is_available():
            tasks_to_schedule.GpuStats(self); time.sleep(0.25)
        tasks_to_schedule.MemoryStats(self); time.sleep(0.25)
        tasks_to_schedule.DiskStats(self); time.sleep(0.25)
        tasks_to_schedule.NetStats(self); time.sleep(0.25)
        tasks_to_schedule.DateStats(self); time.sleep(0.25)
        tasks_to_schedule.SystemUptimeStats(self); time.sleep(0.25)
        tasks_to_schedule.CustomStats(self); time.sleep(0.25)
        tasks_to_schedule.WeatherStats(self); time.sleep(0.25)
        tasks_to_schedule.PingStats(self); time.sleep(0.25)

    def turn_off(self):
        super().turn_off()
        self.stopping = True
        self.wait_for_empty_queue()

    def display_static_images(self):
        if config.THEME_DATA.get('static_images', False):
            for image in config.THEME_DATA['static_images']:
                logger.debug(f"Drawing Image: {image}")
                self.lcd.DisplayBitmap(
                    bitmap_path=config.THEME_DATA['PATH'] + config.THEME_DATA['static_images'][image].get("PATH"),
                    x=config.THEME_DATA['static_images'][image].get("X", 0),
                    y=config.THEME_DATA['static_images'][image].get("Y", 0),
                    width=config.THEME_DATA['static_images'][image].get("WIDTH", 0),
                    height=config.THEME_DATA['static_images'][image].get("HEIGHT", 0)
                )

    def display_static_text(self):
        if config.THEME_DATA.get('static_text', False):
            for text in config.THEME_DATA['static_text']:
                logger.debug(f"Drawing Text: {text}")
                self.lcd.DisplayText(
                    text=config.THEME_DATA['static_text'][text].get("TEXT"),
                    x=config.THEME_DATA['static_text'][text].get("X", 0),
                    y=config.THEME_DATA['static_text'][text].get("Y", 0),
                    width=config.THEME_DATA['static_text'][text].get("WIDTH", 0),
                    height=config.THEME_DATA['static_text'][text].get("HEIGHT", 0),
                    font=config.FONTS_DIR + config.THEME_DATA['static_text'][text].get("FONT",
                                                                                       "roboto-mono/RobotoMono-Regular.ttf"),
                    font_size=config.THEME_DATA['static_text'][text].get("FONT_SIZE", 10),
                    font_color=config.THEME_DATA['static_text'][text].get("FONT_COLOR", (0, 0, 0)),
                    background_color=config.THEME_DATA['static_text'][text].get("BACKGROUND_COLOR", (255, 255, 255)),
                    background_image=_get_full_path(config.THEME_DATA['PATH'],
                                                    config.THEME_DATA['static_text'][text].get("BACKGROUND_IMAGE",
                                                                                               None)),
                    align=config.THEME_DATA['static_text'][text].get("ALIGN", "left"),
                    anchor=config.THEME_DATA['static_text'][text].get("ANCHOR", "lt"),
                )

    def wait_for_empty_queue(self, timeout: int = 5):
        # Waiting for all pending request to be sent to display
        logger.info("Waiting for all pending request to be sent to display (%ds max)..." % timeout)

        wait_time = 0
        while not self.is_queue_empty() and wait_time < timeout:
            time.sleep(0.1)
            wait_time = wait_time + 0.1

        logger.debug("(Waited %.1fs)" % wait_time)


    @async_job("Queue_Handler_SysMonitor")
    @schedule(timedelta(milliseconds=1).total_seconds())
    def QueueHandler(self):
        # Do next action waiting in the queue
        if self.stopping:
            # Empty the action queue to allow program to exit cleanly
            while not self.update_queue.empty():
                f, args = self.update_queue.get()
                f(*args)
        else:
            # Execute first action in the queue
            f, args = self.update_queue.get()
            if f:
                f(*args)


    def is_queue_empty(self) -> bool:
        return self.update_queue.empty()
