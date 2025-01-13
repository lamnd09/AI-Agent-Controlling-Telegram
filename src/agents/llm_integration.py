import requests
from langchain_core.runnables.base import Runnable

class OllamaLlamaWrapper(Runnable):
    """
    Wrapper for the Ollama server to serve LLaMA-based models.
    """

    def __init__(self, server_url="http://localhost:11434", model_name="llama3.2"):
        self.server_url = server_url
        self.model_name = model_name
        self.tools = []

    def generate(self, prompt: str) -> str:
        """
        Calls Ollama's /generate endpoint with the given prompt and returns the text.
        """
        data = {
            "prompt": prompt,
            "model": self.model_name,
        }
        try:
            r = requests.post(f"{self.server_url}/generate", json=data)
            r.raise_for_status()
            resp_json = r.json()
            return resp_json.get("response", "")
        except requests.RequestException as e:
            return f"Ollama request failed: {str(e)}"

    def bind_tools(self, tools):
        """
        Binds tools to the model.
        """
        self.tools = tools
        return self

    def __call__(self, inputs: dict) -> dict:
        """
        Makes the class callable by implementing the Runnable interface.
        """
        prompt = inputs.get("prompt", "")
        response = self.generate(prompt)
        return {"response": response}
