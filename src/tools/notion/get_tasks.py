import os
from datetime import datetime
from typing import Optional, Type
from langchain_core.callbacks import CallbackManagerForToolRun
from langsmith import traceable
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from notion_client import Client

# Notion API token and database ID
NOTION_TOKEN = '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'
NOTION_DATABASE_ID = '1782eb16a9c380ecae16dc885bc4c71b'

# Initialize the Notion client
notion = Client(auth=NOTION_TOKEN)

print(f"Using Notion Token: {NOTION_TOKEN[:5]}...{NOTION_TOKEN[-5:]}")
print(f"Database ID: {NOTION_DATABASE_ID}")

class GetMyTodoListInput(BaseModel):
    date: str = Field(description="Date for which to retrieve tasks (YYYY-MM-DD)")

class GetMyTodoList(BaseTool):
    name: str = "GetMyTodoList"
    description: str = "Use this to retrieve tasks from your Notion to-do list for a specific date"
    args_schema: Type[BaseModel] = GetMyTodoListInput

    def get_tasks_for_date(self, target_date: str):
        try:
            # Parse the target date string into a datetime object
            try:
                target_datetime = datetime.strptime(target_date, "%Y-%m-%d")
            except ValueError:
                return f"Error: Invalid date format. Please use YYYY-MM-DD."

            # Query the database with a filter for tasks due on the target date
            results = notion.databases.query(
                database_id=NOTION_DATABASE_ID,
                filter={
                    "property": "Due date",  # Match the exact property name from your database schema
                    "date": {"equals": target_date},
                }
            )

            # Parse the query results
            tasks = []
            for page in results["results"]:
                # Extract task details
                task_name = page["properties"]["Task name"]["title"][0]["text"]["content"]
                status = page["properties"]["Status"]["status"]["name"]
                due_date = page["properties"]["Due date"]["date"]["start"]

                tasks.append({
                    "id": page["id"],
                    "title": task_name,
                    "status": status,
                    "due_date": due_date,
                })

            if tasks:
                return f"Todo list for {target_date}:\n" + "\n".join(
                    [f"- {task['title']} (Status: {task['status']}, Due: {task['due_date']})" for task in tasks]
                )
            else:
                return f"No tasks found in Todo list for {target_date}."

        except Exception as e:
            return f"An error occurred: {str(e)}"

    @traceable(run_type="tool", name="GetMyTodoList")
    def _run(
        self,
        date: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        return self.get_tasks_for_date(date)

# Test the tool
if __name__ == "__main__":
    tool = GetMyTodoList()

    # Define test input
    test_date = datetime.now().strftime("%Y-%m-%d")  # Today's date

    # Retrieve tasks for the test date
    response = tool._run(date=test_date)
    print(response)
