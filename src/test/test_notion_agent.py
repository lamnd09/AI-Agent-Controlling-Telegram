#from src.agents.notion_agent import invoke_notion_agent
import sys
import os 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from src.agents.notion_agent import invoke_notion_agent

# Test adding a task
def test_add_task():
    task_description = "Add a task named 'Test Task' with due date 2025-01-15."
    response = invoke_notion_agent(task_description)
    print("Add Task Response:", response)

# Test retrieving tasks
def test_get_tasks():
    task_description = "Retrieve all tasks for 2025-01-15."
    response = invoke_notion_agent(task_description)
    print("Get Tasks Response:", response)

if __name__ == "__main__":
    print("Testing Notion Agent...")
    test_add_task()
    test_get_tasks()
