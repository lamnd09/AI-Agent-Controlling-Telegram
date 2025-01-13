import os
from dotenv import load_dotenv
from utils import send_telegram_message, receive_telegram_message

# Load environment variables from .env file
load_dotenv()

def test_send_telegram_message():
    print("Testing send_telegram_message...")
    text = "Hello! This is a test message from my bot."
    response = send_telegram_message(text)
    print(response)

def test_receive_telegram_message():
    print("Testing receive_telegram_message...")
    after_timestamp = 0  # Fetch all messages from the beginning
    new_messages = receive_telegram_message(after_timestamp)
    print(f"New messages since {after_timestamp}:")
    for message in new_messages:
        print(message)

if __name__ == "__main__":
    # Test sending a Telegram message
    test_send_telegram_message()

    # Test receiving Telegram messages
    test_receive_telegram_message()
