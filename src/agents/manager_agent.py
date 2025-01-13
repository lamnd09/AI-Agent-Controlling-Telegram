import sqlite3
from typing import Annotated, Literal, TypedDict
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.graph.message import AnyMessage, add_messages
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from src.prompts.manager_agent_prompt import TELEGRAM_ASSISTANT_MANAGER_PROMPT
from src.agents.notion_agent import invoke_notion_agent, OllamaLlamaWrapper
from src.tools.delegate_tool import Delegate

# Initialize sqlite3 DB
conn = sqlite3.connect("db/checkpoints.sqlite", check_same_thread=False)

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

class ManagerAgent:
    def __init__(self, ollama_client):
        self.tools = [Delegate()]
        self.model = ollama_client  # Assign LLM directly
        self.checkpointer = SqliteSaver(conn)
        self.workflow = self.create_workflow()

    def create_workflow(self):
        workflow = StateGraph(State)
        
        workflow.add_node("telegram_agent", self.call_model)
        workflow.add_node("notion_agent", self.call_notion_agent)
        
        workflow.add_edge(START, "telegram_agent")
        
        workflow.add_conditional_edges(
            "telegram_agent",
            self.route_primary_assistant,
            {
                "notion_agent": "notion_agent",
                END: END,
            },
        )
        
        workflow.add_edge("notion_agent", 'telegram_agent')
        self.app = workflow.compile(self.checkpointer)
        return self.app 

    def call_model(self, state: State):
        print("[DEBUG] Calling Telegram agent")
        messages = state['messages']
        print(f"[DEBUG] Messages received by LLM: {messages}")
        response = self.model.invoke(messages)
        print(f"[DEBUG] Response from LLM: {response}")
        return {"messages": [response]}

    def route_primary_assistant(self, state: State) -> Literal["notion_agent", "__end__"]:
        route = tools_condition(state)
        #print(f"[DEBUG] Routing decision: {route}")
        if route == END:
            return END
        tool_calls = state["messages"][-1].tool_calls
        if tool_calls:
            if tool_calls[0]["name"] == Delegate.__name__:
                if tool_calls[0]['args']["agent_name"] == "Notion Agent":
                    return "notion_agent"
        raise ValueError("Invalid route")

    def call_notion_agent(self, state: State):
        print("[DEBUG] Calling Notion agent")
        last_manager_tool_calls = state["messages"][-1].tool_calls
        task = last_manager_tool_calls[0]['args']["task"]
        tool_call_id = last_manager_tool_calls[0]['id']
        #print(f"[DEBUG] Task passed to Notion Agent: {task}")
        response = invoke_notion_agent(task)
        #print(f"[DEBUG] Response from Notion Agent: {response}")
        return {"messages": [ToolMessage(content=response, name="Delegate", tool_call_id=tool_call_id)]}

    def invoke(self, message, config):
        #print(f"[DEBUG] Invoking ManagerAgent with message: {message}")
        if len(self.app.get_state(config=config).values.get("messages", [])) == 0:
            self.app.update_state(config, {"messages": [SystemMessage(content=TELEGRAM_ASSISTANT_MANAGER_PROMPT)]})
        sent_message = HumanMessage(content=message)
        final_state = self.app.invoke({"messages": [sent_message]}, config=config)
        #print(f"[DEBUG] Final state response: {final_state}")
        return final_state["messages"][-1].content
