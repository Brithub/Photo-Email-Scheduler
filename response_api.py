import datetime
import os
import yaml
from fastapi import FastAPI, Request
import random

app = FastAPI()


# to start, run fastapi run response_api.py
@app.get("/photo_taken/{user}")
def photo_taken(user):
    # Write a file to mark that the photo was taken

    # get current path
    current_path = os.path.abspath(os.path.dirname(__file__))
    now = datetime.datetime.now()
    today_date = f"{now.year}/{now.month}/{now.day}"
    write_path = f"{current_path}/markers/{user}/{today_date}"

    # check if the path exists, if it does, we're going to prompt the user to add a new message as they have already taken a photo today
    if os.path.exists(write_path):
        new_message_type = random.choice(['response', 'subject', 'content'])
        return (f"You are already real. "
                f"Come up with a new message to use as a {new_message_type}!🇰🇷{new_message_type}")

    print("making this path", write_path)
    # make the markers directories if they don't exist
    os.makedirs(write_path, exist_ok=True)

    # write to new file even if it doesn't exist
    with open(write_path + "/marker", "w") as f:
        f.write("Photo taken")

    # open messages.yaml file
    messages = yaml.safe_load(open(f"{current_path}/messages.yml"))

    responses = messages.get("response", ["That's Great!!! You did it!!"])

    # pick one response randomly
    return random.choice(responses)


@app.put("/add_text/{message_type}")
async def add_text(message_type: str, request: Request):
    # Read the body of the request
    message_text = await request.body()
    message_text = message_text.decode()

    current_path = os.path.abspath(os.path.dirname(__file__))
    message_path = f"{current_path}/messages.yml"

    with open(message_path, "r") as file:
        messages = yaml.safe_load(file)

    # append the text to the message type and write it back to the file
    if message_type not in messages:
        messages[message_type] = [message_text]
    else:
        print("here's the message type", message_type)
        print("here's the message text", message_text)
        print("type of message text", type(messages))
        preexisting = messages[message_type]
        print("type of preexisting", type(preexisting))
        messages.get(message_type, ["abcd"]).append(message_text)

    # write the new messages to the file
    with open(message_path, "w") as file:
        messages_string = yaml.dump(messages)
        file.write(messages_string)

    return "Message added"
