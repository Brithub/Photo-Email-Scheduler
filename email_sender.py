import datetime
import os
import random
import smtplib, ssl
import time
import yaml
import keyring

from email.mime.text import MIMEText

from time_helper import user_timezone, now

# python3 email_sender.py
user_map = {
    "sam": "sam@britton.email",
    "katie": "luovakatie@gmail.com"
}

current_path = os.path.dirname(os.path.realpath(__file__))


def get_or_init_messages():
    if not os.path.exists("messages.yml"):
        messages = {
            "subject": [
                "Subject 1",
                "Subject 2",
                "Subject 3"
            ],
            "content": [
                "Content 1",
                "Content 2",
                "Content 3"
            ],
            "response": [
                "Response 1",
                "Response 2",
                "Response 3"
            ]
        }
        with open("messages.yml", "w") as f:
            yaml.dump(messages, f)
    else:
        messages = yaml.safe_load(open("messages.yml"))
    return messages


def send_message(email):
    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    sender_email = "sammie.b.automation@gmail.com"

    password = keyring.get_password("gmail automation", "sammie.b.automation@gmail.com")

    if password is None:
        password = os.getenv("GMAIL_AUTOMATION_PASSWORD")

    text_subtype = 'plain'

    # select a random message from messages.yml
    all_messages = get_or_init_messages()
    subject = random.choice(all_messages.get("subject"))
    content = random.choice(all_messages.get("content"))

    msg = MIMEText(content, text_subtype)
    msg['Subject'] = subject
    msg['From'] = sender_email

    print("emailing " + email)
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, email, msg.as_string())
        print("email sent")


def pick_time(user="sam"):
    # Get current time with the specified timezone
    day_of_week = now(user).weekday()

    # get the start and end possible times
    if day_of_week < 5:
        # weekdays
        # 10% chance of having a 9am starting time
        if random.random() > 0.9:
            start_time = datetime.time(9, 0)
        else:
            start_time = datetime.time(17, 0)
        end_time = datetime.time(22, 0)
    else:
        # weekends
        start_time = datetime.time(10, 0)
        end_time = datetime.time(22, 0)

    # pick a random time between start and end
    alert_time = datetime.time(
        hour=random.randint(start_time.hour, end_time.hour),
        minute=random.randint(0, 59),
        second=0,
        microsecond=0
    )
    return alert_time


def schedule_message():
    while True:
        for user in user_map.keys():
            year = now(user).year
            month = now(user).month
            day = now(user).day
            # if there's no scheduled message for today for the user, decide that schedule
            if not os.path.exists(f"{current_path}/schedules/{user}/{year}/{month}/{day}"):
                alert_time = pick_time(user)
                alert_time_string = alert_time.strftime("%H:%M")

                # make the schedules directory if it doesn't exist
                os.makedirs(f"{current_path}/schedules/{user}/{year}/{month}/{day}", exist_ok=True)

                # write the scheduled message to the file
                with open(f"{current_path}/schedules/{user}/{year}/{month}/{day}/{alert_time_string}", "w") as f:
                    f.write("")
            else:
                # list the files in the schedules dir under the user and today's date
                files = os.listdir(f"{current_path}/schedules/{user}/{year}/{month}/{day}")
                # get the alert time from the file path
                timestamp = str(files[0]).split("/")[-1]
                alert_time = datetime.datetime.strptime(timestamp, "%H:%M").time()
                alert_time = alert_time.replace(tzinfo=user_timezone(user))

            # now if we're at or past the time to send the message, send it with a decreasing delay
            if now(user).time() >= alert_time:
                # check if the message has already been sent
                if os.path.exists(f"{current_path}/markers/{user}/{year}/{month}/{day}"):
                    continue

                # send the message
                send_message(user_map[user], user)

        # sleep for 5 minutes
        time.sleep(60 * 5)


# main function
def main():
    print("Starting message scheduler")
    # with daemon.DaemonContext(pidfile=lockfile.FileLock('/var/run/message.pid')):
    schedule_message()


if __name__ == "__main__":
    main()
