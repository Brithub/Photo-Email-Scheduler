import datetime
import os
import pickle
import random
import smtplib
import ssl
import time
import uuid
from email.mime.text import MIMEText
from pathlib import Path

from storage import MessagesResponse, read_saved_messages
from time_helper import user_timezone, now

user_map = {"sam": "sam@britton.email", "katie": "luovakatie@gmail.com"}

UTC = datetime.timezone.utc

meta_path = os.getenv("META_DIRECTORY")

if not meta_path:
    print("No meta directory available, writing to tmp")
    meta_path = f"/tmp/{uuid.uuid4()}"

def send_message(email):
    smtp_server = "smtp.gmail.com"
    sender_email = "sammie.b.automation@gmail.com"

    password = os.getenv("GMAIL_AUTOMATION_PASSWORD")

    if password is None:
        raise Exception("Unable to get credentials from envvar")

    text_subtype = "plain"

    # select a random message from messages.yml
    all_messages: MessagesResponse = read_saved_messages()

    random.seed(int(now().strftime("%Y%m%d")))
    subject = random.choice(all_messages.subjects)
    content = random.choice(all_messages.contents)

    msg = MIMEText(content, text_subtype)
    msg["Subject"] = subject
    msg["From"] = sender_email

    print("emailing " + email)
    context = ssl.create_default_context()

    retries_remaining: int = 5
    message_sent = False

    while retries_remaining > 0 and not message_sent:
        try:
            with smtplib.SMTP(smtp_server, port=587) as server:
                server.ehlo()
                server.starttls(context=context)
                server.login(sender_email, password)
                server.sendmail(sender_email, email, msg.as_string())
                print("email sent")
                message_sent = True
        except smtplib.SMTPException:
            delay = (6 - retries_remaining) * 60
            retries_remaining -= 1
            print(f"failed to send email, retrying in {delay} seconds")
            time.sleep(delay)


def pick_time(user: str, snooze_days: int = 1) -> datetime.datetime:
    # Get current time with the specified timezone
    now_user = now(user) + datetime.timedelta(days=snooze_days)
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

    schedule_path = Path(f"{meta_path}/schedules/{user}/schedule.pickle")
    with open(schedule_path, "wb") as file:
        pickle.dump(new_deadline, file)


def get_current_deadline(user: str) -> datetime.datetime:
    schedule_path = Path(f"{meta_path}/schedules/{user}/schedule.pickle")
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


def is_user_early(user: str) -> bool:
    # Early's not a bad thing, this allows us to be real for the day before the deadline even gets here
    deadline = get_current_deadline(user)
    return now(user).day == deadline.day


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
