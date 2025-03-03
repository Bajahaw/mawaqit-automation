import os
import time
import datetime
import subprocess
from notify import NotificationManager
from utils.parse_json import parse_json

def schedule_next_job(delay_seconds):
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

    # lock file to prevent looping because of scheduler first run
    lock_file = os.path.join(os.path.dirname(__file__), "utils", "lock")
    if os.path.exists(lock_file):
        os.remove(lock_file)
        print("lock file removed")
        return

    else:
        with open(lock_file, "w") as f:
            print("lock file created")
            f.write("lock")

    # build the json file path from the parent data directory
    json_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "huda-budapest.json")
    masjid_data = parse_json(json_file)["rawdata"]
    
    # init the notification manager to send alerts
    notification_manager = NotificationManager()

    now = datetime.datetime.now()
    month = now.month - 1  # note: months in the json are indexed 0-11
    day_str = "{:d}".format(now.day)
    
    # get today's prayer times from the json data
    try:
        prayer_times = masjid_data["calendar"][month][day_str]
    except KeyError:
        print(f"no data for today's date: month {now.month}, day {now.day}.")
        return 

    prayers = ["Fajr", "Shorouq", "Dhuhr", "Asr", "Maghrib", "Ishaa"]
    prayer_index = 0

    # find the next prayer time
    for i in range(len(prayer_times)):

        prayer_time = prayer_times[i]
        prayer_index = i
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

            if i == 0:
                # at day's start, print a welcome message with today’s date
                print("-------------------------")
                print("new day, may it be blessed .. date: ", datetime.datetime.now().date())

            # break after scheduling the next prayer
            break

        elif i == len(prayer_times) - 1: # Ishaa prayer
            # no more prayers today, wait until midnight
            print("no upcoming prayer today. waiting until midnight...")
            prayer_index = i + 1
            schedule_next_job(60 * 60 * (24 - now.hour))
        
    prayer_index = prayer_index - 1
    prayer_name = prayers[max(0, prayer_index)]
    notification_manager.send_notification(
        title="Prayer Time",
        content=f"It is time for {prayer_name} prayer, at {prayer_times[max(0, prayer_index)]}"
    )
    print(f"notification sent: upcoming prayer at {prayer_times[i-1]}")


if __name__ == "__main__":
    main()