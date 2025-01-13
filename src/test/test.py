import requests
import json

url = "http://localhost:11434/api/generate"
data = { "model": "llama3.2", "prompt": "What is water made of?" }
response = requests.post(url, json=data, stream=True)

full_response = ""
for line in response.iter_lines(decode_unicode=True):
    if line:
        try:
            chunk = json.loads(line)
            full_response += chunk.get("response", "")
            if chunk.get("done", False):
                break
        except json.JSONDecodeError:
            continue

print("Complete response:", full_response)
