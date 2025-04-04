import datetime
import os

current_path = os.path.dirname(os.path.realpath(__file__))

def user_timezone(user="sam"):
    timezone_path = f"{current_path}/timezones/{user}"

    try:
        if os.path.exists(timezone_path):
            with open(timezone_path) as f:
                timezone = f.read().strip()
        else:
            # Default to EST (-0500) if no timezone file exists
            timezone = "-0500"

        hours = int(timezone[0:3])
        minutes = int(timezone[3:5] or 0)

        # Create a timezone object using datetime.timezone
        return datetime.timezone(datetime.timedelta(hours=hours, minutes=minutes))

    except Exception as e:
        # In case of any errors, default to EST
        print(f"Error reading timezone for {user}, defaulting to EST: {str(e)}")
        return datetime.timezone(datetime.timedelta(hours=-5, minutes=0))

def now(user="sam"):
    return datetime.datetime.now(user_timezone(user))
