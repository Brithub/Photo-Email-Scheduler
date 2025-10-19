from email_sender import get_or_init_messages
import os
import random
from pathlib import Path

import yaml
from fastapi import FastAPI, Request

from time_helper import now, write_timezone

app = FastAPI()


# to start, run fastapi run response_api.py
@app.get("/photo_taken/{user}/{timezone}")
def photo_taken(user, timezone) -> str:

    current_path = os.path.abspath(os.path.dirname(__file__))
    meta_directory = os.environ.get("META_DIRECTORY", current_path)

    write_timezone(user, timezone)

    today_date = f"{now(user).year}/{now(user).month}/{now(user).day}"
    write_path = f"{meta_directory}/markers/{user}/{today_date}"

    # check if the path exists, if it does, we're going to prompt the user to add a new message as they have already taken a photo today
    if os.path.exists(write_path):
        new_message_type = random.choice(["responses", "subjects", "contents"])
        return (
            f"You are already real. "
            f"Come up with a new message to use as a {new_message_type}!🇰🇷{new_message_type}"
        )

    Path(write_path).mkdir(exist_ok=True, parents=True)
    with open(write_path + "/marker", "w") as f:
        f.write("Photo taken")

    # open messages.yaml file
    messages = get_or_init_messages(meta_directory)

    # pick one response randomly
    return random.choice(messages.responses)


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

    new_messages: list[str] = messages.__getattribute__(message_type).append(
        message_text
    )
    messages.__setattr__(message_type, new_messages)

    # write the new messages to the file
    with open(f"{meta_directory}/messages.yml", "w") as file:
        yaml.dump(messages, file)

    return "Message added"
