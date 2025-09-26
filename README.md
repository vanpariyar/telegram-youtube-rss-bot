# telegram-youtube-rss-bot
Telegram RSS bot


Here's a complete step-by-step guide.

-----

## Step 1: Get Your Telegram Credentials 📜

First, you need a Telegram bot and the ID of the group where it will post notifications.

1.  **Create a Bot with BotFather**:

      * Open Telegram and search for the user `@BotFather`.
      * Start a chat and send the `/newbot` command.
      * Follow the prompts to name your bot. BotFather will give you a **Bot Token**. Save this token—it's like a password for your bot.

2.  **Create a Telegram Group**:

      * Create a new group for your notifications.
      * Add the bot you just created as a member of the group. **Important**: You must also promote the bot to be an **administrator** so it has permission to send messages.

3.  **Get the Group Chat ID**:

      * Add the `@userinfobot` to your group.
      * As soon as it joins, it will post a message with the group's information.
      * Find the **Chat ID** (it's a negative number, like `-1001234567890`) and save it. You can remove `@userinfobot` from the group afterward.

-----

## Step 2: Get the YouTube Channel RSS Feed URL 📡

You need the RSS feed URL for the YouTube channel you want to track. The format is: `https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID`

To find the `CHANNEL_ID`:

1.  Go to the YouTube channel's main page.
2.  Right-click anywhere on the page and select "View Page Source".
3.  Press `Ctrl + F` (or `Cmd + F` on Mac) and search for `"channel_id"`.
4.  You'll find a value like `"UCXXXXXXXXXXXXXXXXXXXXXX"`. Copy this ID and place it in the URL above.

Save the full RSS feed URL.

-----

## Step 3: Set Up the GitHub Repository 📂

This is where your bot's code and logic will live.

1.  **Create a new repository** on GitHub. You can name it something like `telegram-rss-bot`. It can be public or private.

2.  In your new repository, create the following four files:

      * `requirements.txt`
      * `main.py`
      * `last_video_link.txt`
      * `.github/workflows/rss_bot.yml` (You'll need to create the `.github` and `workflows` folders first).

Leave the files empty for now. We will add the code in the next step. Your initial `last_video_link.txt` file should be completely empty.

-----

## Step 4: Add the Code 💻

Now, let's add the code to the files you created.

### 1\. `requirements.txt`

This file lists the Python libraries our script needs.

```txt
feedparser
requests
```

### 2\. `last_video_link.txt`

This file will store the link of the last video that was sent to Telegram. **Make sure this file is created and is initially empty.** The script will manage its contents.

### 3\. `main.py`

This is the core Python script that does the work.

```python
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
```

### 4\. `.github/workflows/rss_bot.yml`

This is the GitHub Actions workflow file. It automates the process of running the Python script on a schedule.

```yaml
name: Check for New Videos

on:
  # Runs on a schedule (every 15 minutes)
  schedule:
    - cron: '*/15 * * * *'
  # Allows you to run this workflow manually from the Actions tab
  workflow_dispatch:

jobs:
  check-videos:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run script to check for new videos
        # Pass secrets as environment variables to the Python script
        env:
          RSS_FEED_URL: ${{ secrets.RSS_FEED_URL }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: python main.py

      - name: Commit and push updated last video link
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add last_video_link.txt
          # Commit only if there are changes
          if git diff-index --quiet HEAD; then
            echo "No changes to commit."
          else
            git commit -m "Update last video link"
            git push
          fi
```

-----

## Step 5: Add Secrets to GitHub 🤫

To keep your bot token and chat ID secure, you should store them as encrypted secrets in GitHub.

1.  In your GitHub repository, go to **Settings** \> **Secrets and variables** \> **Actions**.
2.  Click **New repository secret**.
3.  Create the following three secrets:
      * `RSS_FEED_URL`: The full RSS feed URL you got in Step 2.
      * `TELEGRAM_BOT_TOKEN`: Your bot's token from BotFather.
      * `TELEGRAM_CHAT_ID`: Your group's chat ID.

-----

## Step 6: Run and Verify ✅

Your bot is now fully configured\! The GitHub Action will automatically run every 15 minutes.

To test it immediately:

1.  Go to the **Actions** tab in your GitHub repository.
2.  In the left sidebar, click on the "Check for New Videos" workflow.
3.  Click the **Run workflow** dropdown, then click the green **Run workflow** button.

The action will now run. On its first run, it will find the latest video, send a notification to your Telegram group, and save the video's link to `last_video_link.txt`. On all future runs, it will only send a notification if a newer video link appears in the RSS feed. You can click on the workflow run to see the logs and check for any errors.