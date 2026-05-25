from dataclasses import asdict

from email_sender import (
    get_or_init_messages,
    is_user_late,
    generate_new_schedule,
    is_user_early,
)
import os
import random

import yaml
from fastapi import FastAPI, Request

from time_helper import now, write_timezone

app = FastAPI()


# to start, run fastapi run response_api.py
@app.get("/photo_taken/{user}/{timezone}")
def photo_taken(user, timezone) -> str:

    print(f"Message from {user}")

    current_path = os.path.abspath(os.path.dirname(__file__))
    meta_directory = os.environ.get("META_DIRECTORY", current_path)

    write_timezone(user, timezone)

    if is_user_late(user) or is_user_early(user):
        # Generate a new schedule
        generate_new_schedule(user)

        # open messages.yaml file
        messages = get_or_init_messages(meta_directory)

        # pick one response randomly
        return random.choice(messages.responses)

    else:

        new_message_type = random.choice(["responses", "subjects", "contents"])
        return (
            f"You are already real. "
            f"Come up with a new message to use as {new_message_type}!🇰🇷{new_message_type}"
        )


@app.put("/add_text/{message_type}")
async def add_text(message_type: str, request: Request) -> str:
    # Read the body of the request
    message_text = await request.body()
    message_text = message_text.decode()

    if message_type not in ["responses", "subjects", "contents"]:
        return "Invalid message type"

    current_path = os.path.abspath(os.path.dirname(__file__))
    meta_directory = os.environ.get("META_DIRECTORY", current_path)

    messages = get_or_init_messages(f"{meta_directory}")

    old_messages = messages.__getattribute__(message_type)
    old_messages.append(message_text)

    messages.__setattr__(message_type, old_messages)

    # write the new messages to the file
    with open(f"{meta_directory}/messages.yml", "w") as file:
        yaml.dump(asdict(messages), file)

    return "Message added"


@app.post("/lunch_numbers/{number}")
async def lunch_number(number: int, request: Request) -> str:
    current_path = os.path.abspath(os.path.dirname(__file__))

    try:
        number = int(number)
    except ValueError:
        return "Invalid number"

    if number < 0 or number > 999:
        return "Invalid number"

    file_exists = os.path.exists(f"{current_path}/lunch_numbers.yml")
    if not file_exists:
        previous_data = {}
    else:
        previous_data = yaml.safe_load(open(f"{current_path}/lunch_numbers.yml"))

    current_total = len(previous_data.keys())

    message = ""

    if number / 10 == 67 or number % 100 == 67:
        message += "(six seven haha) "

    if number not in previous_data:
        # first time!
        previous_data[number] = 1

        percentage = ((current_total + 1) * 1.0) / 10

        message += f"New number! We're {percentage:.1f}% of the way there!"

    else:
        count = previous_data[number]
        percentage = (current_total * 1.0) / 10

        if 11 <= (number % 100) <= 13:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")

        message_options = [
            f"I'm so sorry, we've already got {count} {number}s",
            f"We've already got {count} {number}s... We'll get em next time",
            f"That's the {count}{suffix} time we've got {number} :(",
            f"We already have {number}...",
            f"So we've already got {number}, but we gotta try",
            f"I'm afraid {number} isn't it, we're still at {percentage:.1f}% for now",
        ]

        message += random.choice(message_options)
        previous_data[number] += 1

    with open(f"{current_path}/lunch_numbers.yml", "w") as file:
        yaml.dump(previous_data, file)

    return message
