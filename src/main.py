import os
import time
import datetime
from notify import NotificationManager
from utils.parse_json import parse_json

def main():
    # Build the path to the JSON file 
    json_file = os.path.join("..","data", "huda-budapest.json")
    masjid_data = parse_json(json_file)["rawdata"]
    
    # Initialize the notification manager
    notification_manager = NotificationManager()

    while True:
        print("-------------------------")
        print("New day, May it be blessed .. date: ", datetime.datetime.now())

        now = datetime.datetime.now()
        month = now.month - 1  # months are just 0-11 in the JSON data
        day_str = "{:d}".format(now.day)
        
        # Access the prayer times for today from JSON data
        try:
            prayer_times = masjid_data["calendar"][month][day_str]
        except KeyError:
            print(f"No data for today's date: month {now.month}, day {now.day}.")
            break
        
        # 
        next_prayer = None
        next_prayer_str = None

        # Find the next upcoming prayer time
        for prayer_time in prayer_times:

            # Parse the prayer time string into a datetime object
            parsed_time = datetime.datetime.strptime(prayer_time, "%H:%M")
            # the date part is irrelevant, so we replace it with the current date
            current_prayer = datetime.datetime.combine(now.date(), parsed_time.time())

            # Check if the prayer time has already passed
            if now < current_prayer:
                next_prayer = current_prayer
                next_prayer_str = prayer_time
                break
        
        # If there is an upcoming prayer today, wait until then
        if next_prayer:
            # Calculate the time difference between now and the next prayer
            time_diff = (next_prayer - now).total_seconds()
            print(f"Waiting {time_diff // 3600} hours and {(time_diff % 3600) // 60} mins for prayer at {next_prayer_str}...")
            
            # Sleep to save resources
            time.sleep(time_diff)

            # Send a notification when it's time for prayer
            notification_manager.send_notification(
                title="Prayer Time",
                content=f"It's time for prayer at {next_prayer_str}.",
                image="https://example.com/prayer_image.png"  # Replace as needed
            )
            
        else:
            # No upcoming prayer today; wait until midnight to check again
            print("No upcoming prayer today. Waiting until midnight...")
            time.sleep(60 * 60 * (24 - now.hour)) # Sleep until midnight
            

if __name__ == "__main__":
    main()