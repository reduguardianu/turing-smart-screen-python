from os.path import exists
import time
import geocoder
from datetime import datetime
from library.display import Display
from library.lcd.lcd_comm import Orientation
import requests
from library.scheduler import async_job, schedule
import sched
import queue
from unidecode import unidecode
from datetime import timedelta

API_KEY = "787062c127484d7a53ebf55455d1a432"
HR24 = True
DEGC = True
FONT_COLOR = (31, 180, 31)
FONT_COLOR_DARKER = (15, 90, 15)
FONT="res/fonts/generale-mono/GeneraleMonoA.ttf"
DEGC=True

class Weather(Display):
    def __init__(self):
        #com_port = config.CONFIG_DATA['config']['COM_PORT']
        com_port = "/dev/ttyACM0"
        revision = "A"
        brightness = 20
        display_rgb_led = (255, 255, 255)
        self.update_queue = queue.Queue()
        self.oldicon = None
        self.stopping = False
        super().__init__(
            com_port=com_port,
            width = 0,
            height = None,
            revision=revision,
            brightness=brightness,
            display_rgb_led=display_rgb_led,
            update_queue=self.update_queue)

    def run(self):
        self.setup()
        self.turn_on()
        self.lcd.SetOrientation(Orientation.LANDSCAPE)
        self.QueueHandler()
        self.set_location(); time.sleep(1)
        self.set_weather(); time.sleep(0.25)
        self.set_time(); time.sleep(0.25)

    def turn_off(self):
        super().turn_off()
        self.stopping = True
        self.wait_for_empty_queue()

    @async_job("Location_checker")
    @schedule(600)
    def set_location(self):
        loc_ip = geocoder.ip('me')
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        self.location = loc_ip.city
        # url used for requests
        self.complete_url = base_url + "appid=" + API_KEY + "&q=" + self.location

    @async_job("Weather_checker")
    @schedule(60)
    def set_weather(self):
        # receive weather api request
        # {'coord': {'lon': 17.0333, 'lat': 51.1}, 'weather': [{'id': 800, 'main': 'Clear', 'description': 'clear sky', 'icon': '01n'}], 'base': 'stations', 'main': {'temp': 275.96, 'feels_like': 273.9, 'temp_min': 274.15, 'temp_max': 277.08, 'pressure': 1029, 'humidity': 75, 'sea_level': 1029, 'grnd_level': 1012}, 'visibility': 10000, 'wind': {'speed': 2.06, 'deg': 260}, 'clouds': {'all': 0}, 'dt': 1741040460, 'sys': {'type': 2, 'id': 2100308, 'country': 'PL', 'sunrise': 1740979946, 'sunset': 1741019730}, 'timezone': 3600, 'id': 3081368, 'name': 'Wrocław', 'cod': 200}
        response = requests.get(self.complete_url)
        x = response.json()
        if x["cod"] != "404":
            # get current weather and temperature
            y = x["main"]
            z = x["weather"]
            self.description = z[0]["description"]
            # convert temperature to C or F
            if DEGC:
                self.current_temp = str(round(y["temp"]-273.15,1))+"°C"
                self.feels_like = str(round(y["feels_like"]-273.15,1))+"°C"
            else:
                self.current_temp = str(round(((y["temp"]-273.15)*9/5+32),1))+"°F"
                self.feels_like = str(round(((y["feels_like"]-273.15)*9/5+32),1))+"°F"
            # variables for time, sunrise, and sunset
            tm = x["dt"]
            w = x["sys"]
            sunrise = w["sunrise"]
            sunset = w["sunset"]
            self.current_weather = z[0]["main"]
            # check if it's night or day and if weather has changed for background
            if (tm > sunrise and tm < sunset):  self.newicon = "day" +  self.current_weather
            else:  self.newicon = "night" +  self.current_weather
            if  self.newicon !=  self.oldicon:
                self.oldicon =  self.newicon
                # check if background exists, else use default outlier background ie. haze, fog, mist
                self.background = "res/backgrounds/"+ self.newicon+".png"
                if not exists(self.background):
                    if "day" in self.newicon: self.background = "res/backgrounds/dayElse.png"
                    else: self.background = "res/backgrounds/nightElse.png"
                # display background
                self.lcd.DisplayBitmap(self.background)
        else:
             self.location = "City Not Found"
        # Display location
        self.lcd.DisplayText(unidecode(self.location), 35, 270,
                            font=FONT,
                            font_size=20,
                            font_color=FONT_COLOR_DARKER,
                            background_image=self.background)
        # Display custom text with solid background
        self.lcd.DisplayText(f"{self.current_temp:>8}", 150, 160,
                            font=FONT,
                            font_size=40,
                            font_color=FONT_COLOR,
                            background_image=self.background)

        self.lcd.DisplayText(f"Feels like: {self.feels_like:<20}", 70, 205,
                            font=FONT,
                            font_size=20,
                            font_color=FONT_COLOR_DARKER,
                            background_image=self.background)

        # Display custom text with solid background
        self.lcd.DisplayText(f"{self.description:<30}", 35, 240,
                            font=FONT,
                            font_size=25,
                            font_color=FONT_COLOR,
                            background_image=self.background)

    @async_job("Time updater")
    @schedule(1)
    def set_time(self):
        # get current time
        now = datetime.now()
        day_str = now.strftime('%A')
        date_day_str = now.strftime('%d')
        date_month_str = now.strftime('%m')
        date_year_str = now.strftime('%Y')
        dt_str = f"{date_day_str:>4}\n{date_month_str:>4}\n{date_year_str}"
        # 24 hour or 12 hour clock
        seconds = int(now.strftime("%S"))

        if(HR24): tm_str = now.strftime("%H:%M")
        else: tm_str = now.strftime("%I:%M:%S %p")
        # Display Day
        self.lcd.DisplayText(f"{unidecode(day_str):<15}", 30, 20,
                            font=FONT,
                            font_size=25,
                            font_color=FONT_COLOR_DARKER,
                            background_image=self.background)

        # Display Date
        self.lcd.DisplayText(dt_str, 230, 50,
                            font=FONT,
                            font_size=25,
                            font_color=FONT_COLOR_DARKER,
                            background_image=self.background)

        self.lcd.DisplayRadialProgressBar(
            xc=390,
            yc=85,
            radius = 70,
            bar_width=5,
            angle_start=-90,
            angle_end=270,
            angle_steps=60,
            min_value=0,
            max_value=59,
            clockwise=True,
            bar_color=FONT_COLOR_DARKER,
            background_image=self.background,
            value=seconds,
            text=tm_str,
            font_size=38,
            font_color=FONT_COLOR,
            font=FONT
        )


    @async_job("Queue_Handler")
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
    def wait_for_empty_queue(self, timeout: int = 5):
        # Waiting for all pending request to be sent to display

        wait_time = 0
        while not scheduler.is_queue_empty() and wait_time < timeout:
            time.sleep(0.1)
            wait_time = wait_time + 0.1

        logger.debug("(Waited %.1fs)" % wait_time)
