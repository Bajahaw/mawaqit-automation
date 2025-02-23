import subprocess
import json
import time

class NotificationManager:
    def __init__(self):
        # Initialize notification settings if needed
        pass

    def send_notification(self, title, content):

        # Get the current volume levels
        media_vol = self.get_volume("music")
        notify_vol = self.get_volume("notification")

        subprocess.run([termux-volume, "music", str(notify_vol)])

        # Implement notification logic using Termux API.
        subprocess.run([
            'termux-notification',
            '--title', title,
            '--content', content,
            '--priority', 'low'
        ])

        # Play a notification sound
        subprocess.run([
            'termux-media-player',
            'play',
            '../resources/notification_sound.mp3'
        ])

        time.sleep(18)
        
        # Restore the volume levels
        subprocess.run([termux-volume, "music", str(media_vol)])

    def get_volume(self, stream):
        # Get the current volume level for the specified stream
        output = subprocess.check_output(["termux-volume"], text=True)
        volumes = json.loads(output)
        for volume in volumes:
            if volume["stream"] == stream:
                return volume["volume"]
        return None 