import datetime

import os
import random
import smtplib, ssl
import time
from dataclasses import dataclass
from pathlib import Path
import pickle

import yaml

from email.mime.text import MIMEText

from time_helper import user_timezone, now

user_map = {"sam": "sam@britton.email", "katie": "luovakatie@gmail.com"}

current_path = os.path.dirname(os.path.realpath(__file__))
UTC = datetime.timezone.utc


@dataclass
class MessagesResponse:
    subjects: list[str]
    contents: list[str]
    responses: list[str]


def get_or_init_messages(path: str = current_path) -> MessagesResponse:

    messages_path = path + "/messages.yml"
    # initialization route
    if not os.path.exists(messages_path):
        messages = {
            "subjects": ["Subject 1", "Subject 2", "Subject 3"],
            "contents": ["Content 1", "Content 2", "Content 3"],
            "responses": ["Response 1", "Response 2", "Response 3"],
        }

        Path(messages_path).parent.mkdir(exist_ok=True, parents=True)
        with open(messages_path, "w") as f:
            yaml.dump(messages, f)

    loaded_messages = yaml.safe_load(open(messages_path))
    messages = MessagesResponse(
        subjects=loaded_messages["subjects"],
        contents=loaded_messages["contents"],
        responses=loaded_messages["responses"],
    )

    return messages


def send_message(email):
    smtp_server = "smtp.gmail.com"
    sender_email = "sammie.b.automation@gmail.com"

    password = os.getenv("GMAIL_AUTOMATION_PASSWORD")

    if password is None:
        raise Exception("Unable to get credentials from envvar")

    text_subtype = "plain"

    # select a random message from messages.yml
    all_messages: MessagesResponse = get_or_init_messages()

    random.seed(int(now().strftime("%Y%m%d")))
    subject = random.choice(all_messages.subjects)
    content = random.choice(all_messages.contents)

    msg = MIMEText(content, text_subtype)
    msg["Subject"] = subject
    msg["From"] = sender_email

    print("emailing " + email)
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port=587) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, email, msg.as_string())
        print("email sent")


def pick_time(user: str, snooze_days: int = 1) -> datetime.datetime:
    # Get current time with the specified timezone
    now_user = now(user)
    day_of_week = now_user.weekday()

    match day_of_week:
        case 0:  # Mondays
            start_hour: int = 15  # 3pm
        case 1:  # Tuesdays
            start_hour: int = 10  # 10am
        case 2:  # Wednesdays
            start_hour: int = 10  # 10am
        case 3:  # Thursdays
            start_hour: int = 15  # 3pm
        case 4:  # Fridays
            start_hour: int = 15  # 3pm
        case 5:  # Saturdays
            start_hour: int = 10  # 10am
        case _:  # Sundays
            start_hour: int = 10  # 10am

    # pick a random time between start and end
    alert_timestamp = datetime.datetime(
        day=now_user.day,
        month=now_user.month,
        year=now_user.year,
        hour=random.randint(
            start_hour, 20
        ),  # end limit is 8:59, I'm trying to get some sleep!
        minute=random.randint(0, 59),
        second=0,
        microsecond=0,
        tzinfo=user_timezone(user),
    )

    alert_timestamp = alert_timestamp + datetime.timedelta(days=snooze_days)

    return alert_timestamp


def generate_new_schedule(user: str) -> None:

    # This should be in the user dict but that's for later
    if user == "katie":
        old_deadline = get_current_deadline(user)
        time_latent = old_deadline - datetime.datetime.now(UTC)
        minutes_late = abs(time_latent.total_seconds() / 60)
        print(f"Katie was {minutes_late} minutes late")
        # Depending on how early be real, the longer break before it's time to be real again
        snooze_days = max(5 - int(minutes_late / 30), 1)
        print(f"Snoozing bereal by {snooze_days=}")
    else:
        snooze_days = 1

    new_deadline = pick_time(user, snooze_days)

    pretty_new_time = new_deadline.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Next time {user} has to be real is {pretty_new_time}")

    schedule_path = Path(f"{current_path}/schedules/{user}/schedule.pickle")
    with open(schedule_path, "wb") as file:
        pickle.dump(new_deadline, file)


def get_current_deadline(user: str) -> datetime.datetime:
    schedule_path = Path(f"{current_path}/schedules/{user}/schedule.pickle")
    try:
        with open(schedule_path, "rb") as f:
            deadline = pickle.load(f)
    except Exception:
        print("No available schedules, starting now")
        deadline = datetime.datetime(year=2000, month=1, day=1, tzinfo=UTC)
    return deadline


def is_user_late(user: str) -> bool:

    deadline = get_current_deadline(user)
    # now if we're at or past the time to send the message
    return datetime.datetime.now(UTC) >= deadline


def schedule_message():
    while True:
        for user in user_map.keys():
            if is_user_late(user):
                # send the message
                send_message(user_map[user])

        # sleep for 5 minutes
        time.sleep(60 * 5)


# main function
def main():
    print("Starting message scheduler")
    schedule_message()


if __name__ == "__main__":
    main()
