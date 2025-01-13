from langchain.llms.base import LLM
from langgraph.prebuilt import create_react_agent
from langsmith import traceable
from langchain.schema import HumanMessage  # Import HumanMessage
from src.tools.notion import GetMyTodoList, AddTaskInTodoList
from src.prompts import NOTION_AGENT_PROMPT
from src.utils import print_agent_output
from dotenv import load_dotenv
import requests
import json  # For manual JSON parsing

# Load environment variables from .env file
load_dotenv()

class OllamaLlamaWrapper(LLM):
    # Define fields for Pydantic compatibility
    server_url: str = "http://localhost:11434/api"
    model_name: str = "llama3.2"

    @property
    def _llm_type(self) -> str:
        return "custom_ollama_llama"

    def _call(self, prompt: str, stop: list[str] | None = None) -> str:
        """
        Sends a prompt to the Ollama server and retrieves the full streamed response.
        """
        data = {"prompt": prompt, "model": self.model_name}
        try:
            # Enable streaming
            response = requests.post(f"{self.server_url}/generate", json=data, stream=True)
            response.raise_for_status()

            full_response = ""
            # Iterate over the streamed lines
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue  # Skip lines that aren't valid JSON
                    # Accumulate text from each chunk
                    full_response += chunk.get("response", "")
                    # Optional: Break early if done signal received
                    if chunk.get("done", False):
                        break

            return full_response.strip() or "No response received."
        except requests.RequestException as e:
            raise RuntimeError(f"Error communicating with Ollama server: {e}") from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Error parsing JSON response: {e}") from e
            
    def invoke(self, messages, *args, **kwargs):
        """
        Combine a list of messages into a single prompt and get the response.
        Additional arguments are accepted to maintain compatibility with external calls.
        """
        # Combine messages into a single prompt text.
        combined_prompt = "\n".join([msg.content for msg in messages])
        response_text = self._call(combined_prompt)
        # Wrap the response text into a HumanMessage (or appropriate message type).
        return HumanMessage(content=response_text)

            
    def bind_tools(self, tool_classes):
        """Dummy implementation of bind_tools to satisfy agent requirements."""
        return self

# Initialize the LLM wrapper
llm = OllamaLlamaWrapper(
    server_url="http://localhost:11434/api",
    model_name="llama3.2"
)

tools = [GetMyTodoList(), AddTaskInTodoList()]

notion_agent = create_react_agent(
    model=llm,
    tools=tools,
    state_modifier=NOTION_AGENT_PROMPT
)
@traceable(run_type="llm", name="Notion Agent")
def invoke_notion_agent(task: str) -> str:
    try:
        inputs = {"messages": [HumanMessage(content=task)]}
        output = notion_agent.invoke(inputs)

        # Dynamically fetch tasks after adding
        updated_tasks = GetMyTodoList()._run(date="2025-01-15")  # Replace with your date logic
        return f"{output['messages'][1].content}\n\nUpdated Notion Tasks:\n{updated_tasks}"
    except Exception as e:
        return f"Failed to process task: {str(e)}"

