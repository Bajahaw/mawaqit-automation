import os
import time
import datetime
import subprocess
from notify import NotificationManager
from utils.parse_json import parse_json

def schedule_next_job(delay_seconds):

    # check if there is a pending job within plus or minus 5 seconds
    result = subprocess.run([
        "termux-job-scheduler",
        "--pending"
    ], capture_output=True).stdout.decode("utf-8")
    
    if "Pending Job 1" in result:
        # extract the period value from the result string
        period = int(result.split("periodic: ")[1].split("ms")[0])

        # if the period is within plus or minus 5 seconds of the delay, do nothing
        if period - 5000 <= delay_seconds * 1000 <= period + 5000:
            return

    # convert seconds to milliseconds for the scheduling job
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
    # build the json file path from the parent data directory
    json_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "huda-budapest.json")
    masjid_data = parse_json(json_file)["rawdata"]
    
    # init the notification manager to send alerts
    notification_manager = NotificationManager()

    now = datetime.datetime.strptime("18:50", "%H:%M")
    month = 2 - 1  # note: months in the json are indexed 0-11
    day_str = "18" #"{:d}".format(now.day)
    
    # get today's prayer times from the json data
    try:
        prayer_times = masjid_data["calendar"][month][day_str]
    except KeyError:
        print(f"no data for today's date: month {now.month}, day {now.day}.")
        return 

    # lock file to prevent looping because of scheduler first run
    lock_file = os.path.join(os.path.dirname(__file__), "utils", "lock")
    if os.path.exists(lock_file):
        os.remove(lock_file)
        print("lock file removed.")
        return

    else:
        with open(lock_file, "w") as f:
            f.write("lock")
    
    # find the next prayer time
    for prayer_time in prayer_times:

        print(f"next prayer time: {prayer_time}")

        # parse the prayer time string into a datetime object and update to today's date
        prayer_parsed_time = datetime.datetime.strptime(prayer_time, "%H:%M")
        next_prayer_time = datetime.datetime.combine(now.date(), prayer_parsed_time.time())


        # check if the current time is before the prayer time
        if now < next_prayer_time:
            # calculate the time diff to next prayer
            time_diff = int((next_prayer_time - now).total_seconds())
            print(f"waiting {int(time_diff // 3600)} hours and {int((time_diff % 3600) // 60)} mins for prayer at {prayer_time} ...")
            
            # schedule a job timer for the next prayer
            schedule_next_job(time_diff)

            if next_prayer_time == datetime.datetime.combine(now.date(), datetime.datetime.strptime(prayer_times[0], "%H:%M").time()):
                # at day's start, print a welcome message with today’s date
                print("-------------------------")
                print("new day, may it be blessed .. date: ", datetime.datetime.now().date())

            # break after scheduling the next prayer
            break

        elif next_prayer_time == datetime.datetime.combine(now.date(), datetime.datetime.strptime(prayer_times[5], "%H:%M").time()):
            # no more prayers today, wait until midnight
            print("no upcoming prayer today. waiting until midnight...")
            schedule_next_job(60 * 60 * (24 - now.hour))

            break
            
        # if the current time is within 2 minutes of the prayer, due to scheduler imprecision, send a notification
        if next_prayer_time + datetime.timedelta(minutes=2) > now > next_prayer_time - datetime.timedelta(minutes=2):
            notification_manager.send_notification(
                title="prayer time",
                content=f"it's time for prayer at {prayer_time}."
            )

if __name__ == "__main__":
    main()