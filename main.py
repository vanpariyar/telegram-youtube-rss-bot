import os
import feedparser
import requests

# --- Configuration ---
# Get secrets from GitHub Actions environment variables
RSS_URL = os.environ.get("RSS_FEED_URL")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# File to store the link of the last processed video
LAST_VIDEO_FILE = "last_video_link.txt"

def get_last_video_link():
    """Reads the last video link from the file."""
    try:
        with open(LAST_VIDEO_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def set_last_video_link(link):
    """Writes the new last video link to the file."""
    with open(LAST_VIDEO_FILE, "w") as f:
        f.write(link)

def send_telegram_message(message):
    """Sends a message to the specified Telegram chat."""
    api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(api_url, data=payload)
        print(f"Telegram API Response: {response.json()}")
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

def check_for_new_video():
    """Checks the RSS feed for a new video and sends a notification."""
    print("Checking for new videos...")
    feed = feedparser.parse(RSS_URL)

    if not feed.entries:
        print("RSS feed is empty or could not be parsed.")
        return

    # Get the latest video from the feed
    latest_video = feed.entries[0]
    latest_video_link = latest_video.link
    last_video_link = get_last_video_link()

    print(f"Latest video found: {latest_video_link}")
    print(f"Last video processed: {last_video_link}")

    if latest_video_link != last_video_link:
        print("New video found! Sending notification...")
        video_title = latest_video.title
        channel_title = feed.feed.title

        # Construct the message
        message = (
            f"📢 <b>New Video from {channel_title}!</b>\n\n"
            f"<b>Title:</b> {video_title}\n"
            f"<b>Link:</b> {latest_video_link}"
        )

        send_telegram_message(message)
        set_last_video_link(latest_video_link)
    else:
        print("No new videos found.")

if __name__ == "__main__":
    check_for_new_video()