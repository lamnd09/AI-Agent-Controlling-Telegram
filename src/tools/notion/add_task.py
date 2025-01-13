import os
from enum import Enum
from typing import Optional, Type
from langchain_core.callbacks import CallbackManagerForToolRun
from langsmith import traceable
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from notion_client import Client
from datetime import datetime
from random import randint

# Notion API token and database ID
NOTION_TOKEN = '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'
NOTION_DATABASE_ID = '1782eb16a9c380ecae16dc885bc4c71b'

# Initialize the Notion client
notion = Client(auth=NOTION_TOKEN)

print(f"Using Notion Token: {NOTION_TOKEN[:5]}...{NOTION_TOKEN[-5:]}")
print(f"Database ID: {NOTION_DATABASE_ID}")

# Define task status as an Enum
class TaskStatus(Enum):
    NOT_STARTED = "Not started"
    IN_PROGRESS = "In progress"
    COMPLETED = "Done"

# Define input schema for adding tasks
class AddTaskInTodoListInput(BaseModel):
    task: str = Field(description="Task to be added")
    date: str = Field(description="Date and time for the task (YYYY-MM-DDTHH:MM:SS)")

# Define the tool for adding tasks
class AddTaskInTodoList(BaseTool):
    name: str = "AddTaskInTodoList"
    description: str = "Use this to add a new task to your Notion to-do list"
    args_schema: Type[BaseModel] = AddTaskInTodoListInput

    def add_task(self, task: str, due_date: Optional[str] = None):
        print(f"[DEBUG] Attempting to add task: {task} with due date: {due_date}")
        try:
            new_task = {
                "Task name": {"title": [{"text": {"content": task}}]},
                "Status": {"status": {"name": TaskStatus.NOT_STARTED.value}},
            }
            if due_date:
                new_task["Due date"] = {"date": {"start": due_date}}

            response = notion.pages.create(
                parent={"database_id": NOTION_DATABASE_ID},
                properties=new_task
            )
            print(f"[DEBUG] Notion API response: {response}")
            return f"Task '{task}' added successfully to the Todo list for {due_date}."
        except Exception as e:
            print(f"[DEBUG] Error in add_task: {str(e)}")
            return f"An error occurred: {str(e)}"

    @traceable(run_type="tool", name="AddTaskInTodoList")
    def _run(
        self,
        task: str,
        date: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        print(f"[DEBUG] _run called with task: {task}, date: {date}")
        return self.add_task(task, date)

