# Install the Telethon library
!pip install telethon

from telethon.sync import TelegramClient
import re
import asyncio
from google.colab import files
from telethon.errors import PhoneCodeInvalidError
import time

# === Your Telegram API credentials ===
api_id = 22687862
api_hash = '8963bd790810ee30eaf234fa97788cc5'
phone_number = '+9647503898085'

# === List of Telegram video message links and custom names ===
video_links = [
    ('https://t.me/c/2156135894/26', 'Lesson-5'),  # Example 1 with custom name
    ('https://t.me/c/2156135894/31', 'Lesson-6'),
    ('https://t.me/c/2156135894/35', 'Lesson-7'),  # Example 2 with custom name
    ('https://t.me/c/2156135894/37', 'Lesson-8'),
    ('https://t.me/c/2156135894/40', 'Lesson-9'),  # Example 3 with custom name
    # Add more video links and custom names here
]

# === Extract channel ID and message ID from link ===
def extract_video_details(video_link):
    match = re.match(r'https://t\.me/c/(\d+)/(\d+)', video_link)
    if not match:
        raise ValueError("Invalid Telegram message link format")
    channel_id = int('-100' + match.group(1))
    message_id = int(match.group(2))
    return channel_id, message_id

# === Progress callback ===
def progress_callback(current, total):
    percent = int(current * 100 / total)
    print(f"\r⏬ Downloading: {percent}%", end='')

# === Login function with error handling ===
async def login(client):
    try:
        if not await client.is_user_authorized():
            await client.send_code_request(phone_number)
            code = input("Enter the code sent to your Telegram app: ")
            await client.sign_in(phone_number, code)
    except PhoneCodeInvalidError:
        print("❌ Invalid code entered. Please try again.")
        await login(client)  # Prompt again for the code

# === Main async function ===
async def main():
    # Create a new client for the first video to avoid session conflicts
    client = TelegramClient('session_all_videos', api_id, api_hash)

    await client.connect()
    
    # Attempt to log in with error handling (only once)
    await login(client)

    # Loop through all the video links and process them
    for video_link, custom_name in video_links:
        print(f"\n🔗 Processing video link: {video_link}")
        
        channel_id, message_id = extract_video_details(video_link)

        print(f"📥 Getting message {message_id} from channel {channel_id}...")
        message = await client.get_messages(channel_id, ids=message_id)

        if message and message.video:
            file_path = f'{custom_name}.mp4'  # Custom name for the file
            print("⏳ Downloading video in full quality...")
            await client.download_media(message, file=file_path, progress_callback=progress_callback)
            print(f"\n✅ Video {message_id} downloaded successfully as {file_path}")

            # Offer to download manually in Colab
            files.download(file_path)
        else:
            print("⚠️ No video found in the specified message.")

        # Add a delay to avoid overwhelming the server with requests (e.g., 5 seconds)
        time.sleep(5)  # Adjust the delay as needed

    # Disconnect the client after processing all videos
    await client.disconnect()

# === Run the async function in Colab ===
await main()
