import os
import uuid
from pathlib import Path

from time_helper import user_timezone, write_timezone


def test_write_timezone() -> None:
    test_meta_directory = f"/tmp/{uuid.uuid4()}"
    os.environ["META_DIRECTORY"] = test_meta_directory

    write_timezone("sam", "-0800")

    assert os.path.exists(f"{test_meta_directory}/timezones/sam")


def test_user_timezone_existing_file():
    # Test timezone reading from file

    test_meta_directory = f"/tmp/{uuid.uuid4()}"
    os.environ["META_DIRECTORY"] = test_meta_directory

    sam_timezone_path = f"{test_meta_directory}/timezones/sam"
    Path(sam_timezone_path).parent.mkdir(parents=True, exist_ok=True)

    with open(sam_timezone_path, "w") as f:
        f.write("-0700")

    assert str(user_timezone("sam")) == "UTC-07:00"


def test_user_timezone_no_file():
    # Test default timezone when no file exists

    test_meta_directory = f"/tmp/{uuid.uuid4()}"
    os.environ["META_DIRECTORY"] = test_meta_directory

    assert str(user_timezone("sam")) == "UTC-05:00"
