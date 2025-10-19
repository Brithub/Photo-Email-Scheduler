from datetime import timezone
import datetime
import os
from pathlib import Path


def write_timezone(user: str, timezone_str: str) -> None:
    current_path = os.path.abspath(os.path.dirname(__file__))
    meta_directory = os.environ.get("META_DIRECTORY", current_path)

    timezone_path = f"{meta_directory}/timezones/{user}"

    Path(timezone_path).parent.mkdir(parents=True, exist_ok=True)

    with open(timezone_path, "w") as f:
        f.write(timezone_str)


def user_timezone(user: str) -> timezone:

    current_path = os.path.abspath(os.path.dirname(__file__))
    meta_directory = os.environ.get("META_DIRECTORY", current_path)

    timezone_path = f"{meta_directory}/timezones/{user}"

    if not os.path.exists(timezone_path):
        # Default to EST (-0500) if no timezone file exists
        timezone_str = "-0500"
        write_timezone(user, timezone_str)

    with open(timezone_path) as f:
        timezone_str = f.read().strip()

    hours = int(timezone_str[0:3])
    minutes = int(timezone_str[3:5] or 0)

    # Create a timezone object using datetime.timezone
    return datetime.timezone(datetime.timedelta(hours=hours, minutes=minutes))


def now(user="sam") -> datetime.datetime:
    return datetime.datetime.now(user_timezone(user))
