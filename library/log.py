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

# Configure logging format
import gzip
import locale
import logging
import shutil
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent
_LOG_FILE = _PROJECT_ROOT / "log.log"
_LOG_ARCHIVE_DIR = _PROJECT_ROOT / "logs"
_MAX_ARCHIVES = 10


def _rotate_log():
    if not _LOG_FILE.exists() or _LOG_FILE.stat().st_size == 0:
        return
    _LOG_ARCHIVE_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_path = _LOG_ARCHIVE_DIR / f"log.{timestamp}.log.gz"
    with open(_LOG_FILE, "rb") as f_in, gzip.open(archive_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    _LOG_FILE.unlink()
    # Remove oldest archives beyond the keep limit
    archives = sorted(_LOG_ARCHIVE_DIR.glob("log.*.log.gz"))
    for old in archives[:-_MAX_ARCHIVES]:
        old.unlink()


_rotate_log()

# use current locale for date/time formatting in logs
locale.setlocale(locale.LC_ALL, '')

logging.basicConfig(  # format='%(asctime)s [%(levelname)s] %(message)s in %(pathname)s:%(lineno)d',
    format="%(asctime)s [%(filename)s][%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler(_LOG_FILE, maxBytes=1000000, backupCount=0),  # Log in textfile max 1MB
        logging.StreamHandler()  # Log also in console
    ],
    datefmt='%x %X')

logger = logging.getLogger('turing')
logger.setLevel(logging.DEBUG)  # Lowest log level : print all messages

sys.excepthook = lambda type, value, traceback: logger.error("Uncaught exception", exc_info=(type, value, traceback))