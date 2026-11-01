import os
import random
import re
from dataclasses import fields

import yaml
from fastapi import FastAPI, Request

from email_sender import (
    is_user_late,
    generate_new_schedule,
    is_user_early, get_current_deadline,
)
from storage import MessagesResponse, write_message, read_saved_messages
from time_helper import write_timezone

app = FastAPI()


# to start, run fastapi run response_api.py
@app.get("/photo_taken/{user}/{timezone}")
def photo_taken(user, timezone) -> str:

    print(f"Message from {user}")

    write_timezone(user, timezone)

    if is_user_late(user) or is_user_early(user):
        # Generate a new schedule
        generate_new_schedule(user)

        # open messages.yaml file
        messages = read_saved_messages()

        # pick one response randomly
        return random.choice(messages.responses)

    else:

        new_message_type = random.choice(["responses", "subjects", "contents", "statuses"])
        return (
            f"You are already real. "
            f"Come up with a new message to use as {new_message_type}!🇰🇷{new_message_type}"
        )

@app.get(path="/next_scheduled_photo/{user}")
def next_scheduled_photo(user) -> str:
    # If we want to be able to do more native notifications for alerts, we need to expose the data
    return str(get_current_deadline(user))


@app.put("/add_text/{message_type}")
async def add_text(message_type: str, request: Request) -> str:
    # Read the body of the request
    message_text = await request.body()
    message_text = message_text.decode()

    if message_type not in [f.name for f in fields(MessagesResponse)]:
        return "Invalid message type"

    write_message(message_type=message_type, message_text=message_text)
    return "Message added"

@app.get("/messages/{message_type}")
def get_messages(message_type: str) -> str:
    some_messages = getattr(read_saved_messages(), message_type.lower())
    return "\n".join(some_messages)

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

    message = "(six seven haha) " if "67" in str(number) else ""

    if number not in previous_data:
        # first time!
        previous_data[number] = 1

        percentage = ((current_total + 1) * 1.0) / 10

        message_options = [
            f"New number! We're {percentage:.1f}% of the way there!",
            f"Let's go!!!! First time for {number}! {percentage:.1f}% of the way there!",
            f"New number new number! Only {1000-current_total} remaining!",
            f"Yeah, that's a new number 😎. Only {1000-current_total} left to go!",
            f"We've never seen {number} before!!!! We're now at {percentage:.1f}%!!!",
        ]

        message += random.choice(message_options)

    else:
        count = previous_data[number]
        percentage = (current_total * 1.0) / 10

        new_count = count + 1
        if 11 <= (new_count % 100) <= 13:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(new_count % 10, "th")

        message_options = [
            f"I'm so sorry, we've already got {count} {number}s",
            f"We've already got {count} {number}s... We'll get em next time",
            f"That's the {new_count}{suffix} time we've got {number} :(",
            f"We already have {number}...",
            f"So we've already got {number}, but we gotta try",
            f"I'm afraid {number} isn't it, we're still at {percentage:.1f}% for now",
            f"That's the {new_count}{suffix} time, we've seen {number}, but thank you for trying",
            f"{number} is already taken, next time try and get one of the {1000-current_total} remaining numbers 🙇",
        ]

        message += random.choice(message_options)
        previous_data[number] += 1

    with open(f"{current_path}/lunch_numbers.yml", "w") as file:
        yaml.dump(previous_data, file)

    return message
