import os
import time
import datetime
import subprocess
from notify import NotificationManager
from utils.parse_json import parse_json

def schedule_next_job(delay_seconds):

    # first check if there is a pending job within the same time +- 5 seconds
    result = subprocess.run([
        "termux-job-scheduler",
        "--pending"
    ], capture_output=True).stdout.decode("utf-8")
    
    if "Pending Job 1" in result:
        # extract the period from the result
        period = int(result.split("periodic: ")[1].split("ms")[0])

        # if the period is within the same time +- 5 seconds, then do nothing
        if period - 5000 <= delay_seconds * 1000 <= period + 5000:
            return

    # Convert seconds to milliseconds for the deadline
    deadline_ms = delay_seconds * 1000
    print(f"Scheduling next job in {int(delay_seconds // 3600)} hours and {int((delay_seconds % 3600) // 60)} mins.")
    subprocess.run([
        "termux-job-scheduler",
        "--job-id", "1",
        "--period-ms", str(deadline_ms),
        "--script", os.path.join(os.path.dirname(__file__), "utils", "job.sh"),
        "--battery-not-low", "false"
    ])

def main():
    # Build the path to the JSON file from the data directory which is in the parent directory
    json_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "huda-budapest.json")
    masjid_data = parse_json(json_file)["rawdata"]
    
    # Initialize the notification manager
    notification_manager = NotificationManager()

    now = datetime.datetime.now()
    month = now.month - 1  # months are just 0-11 in the JSON data
    day_str = "{:d}".format(now.day)
    
    # Access the prayer times for today from JSON data
    try:
        prayer_times = masjid_data["calendar"][month][day_str]
    except KeyError:
        print(f"No data for today's date: month {now.month}, day {now.day}.")
        return

    # Find the next upcoming prayer time
    for prayer_time in prayer_times:

        # Parse the prayer time string into a datetime object
        prayer_parsed_time = datetime.datetime.strptime(prayer_time, "%H:%M")
        # the date part is irrelevant, so we replace it with the current date
        next_prayer_time = datetime.datetime.combine(now.date(), prayer_parsed_time.time())

        # if now is within the prayer time by 5 minutes, cuz scheduler might not be accurate
        if now < next_prayer_time + datetime.timedelta(minutes=5) and now > next_prayer_time - datetime.timedelta(minutes=5):
            # Send a notification when it's time for prayer
            notification_manager.send_notification(
                title="Prayer Time",
                content=f"It's time for prayer at {prayer_time}."
            )

        # Check if now is before the next prayer time
        if now < next_prayer_time:
            # Calculate the time difference between now and the next prayer
            time_diff = int((next_prayer_time - now).total_seconds())
            print(f"Waiting {int(time_diff // 3600)} hours and {int((time_diff % 3600) // 60)} mins for prayer at {prayer_time}...")
            
            # Set job to save resources
            schedule_next_job(time_diff)

            if next_prayer_time == prayer_times[0]:
                # Print a message at the start of a new day
                print("-------------------------")
                print("New day, May it be blessed .. date: ", datetime.datetime.now().date())

            break # Exit the loop after finding the next prayer time

        elif next_prayer_time == prayer_times[4]:
            # No upcoming prayer today; wait until midnight to check again
            print("No upcoming prayer today. Waiting until midnight...")
            schedule_next_job(60 * 60 * (24 - now.hour)) # Sleep until after midnight
            

if __name__ == "__main__":
    main()