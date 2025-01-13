import time
from src.agents.manager_agent import ManagerAgent
from src.agents.notion_agent import OllamaLlamaWrapper  # Import the wrapper
from src.utils import send_telegram_message, receive_telegram_message
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Initialize our Ollama Llama wrapper
ollama_client = OllamaLlamaWrapper(model_name="llama3.2")

# Create the manager agent with the LLM wrapper
telegram_assistant = ManagerAgent(ollama_client)

def monitor_bot(after_timestamp, config):
    while True:
        new_messages = receive_telegram_message(after_timestamp)
        if new_messages:
            for message in new_messages:
                sent_message = (f"Message: {message['text']}\n"
                                f"Current Date/time: {message['date']}")
                answer = telegram_assistant.invoke(sent_message, config)
                send_telegram_message(answer)
        after_timestamp = int(time.time())
        time.sleep(5)  # Sleep for 5 seconds before checking again

if __name__ == "__main__":
    print("Telegram Assistant Manager is running")
    config = {"configurable": {"thread_id": 42}}
    initial_timestamp = int(time.time())
    monitor_bot(initial_timestamp, config)
