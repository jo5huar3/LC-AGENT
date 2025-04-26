from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
#from BasicToolNode import BasicToolNode
import io
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.types import Command, interrupt
'''
Human assistant is not working in this file.
'''
class State(TypedDict):
    messages: Annotated[list, add_messages]
    name: str
    birthday: str

def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    assert len(message.tool_calls) <= 1
    return {"messages": [message]}

def RenderLangGraph(graph):
    try:
        png_bytes = graph.get_graph().draw_mermaid_png()
        buf = io.BytesIO(png_bytes)
        img_arr = mpimg.imread(buf, format='PNG')
        plt.imshow(img_arr)
        plt.axis('off')
        plt.show()
    except Exception:
        # This requires some extra dependencies and is optional
        print("exception occured")

@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    """Request assistance from a human."""
    human_response = interrupt(
        {
            "question": "Is this correct?",
            "name": name,
            "birthday": birthday,
        },
    )
    # If the information is correct, update the state as-is.
    if human_response.get("correct", "").lower().startswith("y"):
        verified_name = name
        verified_birthday = birthday
        response = "Correct"
    # Otherwise, receive information from the human reviewer.
    else:
        verified_name = human_response.get("name", name)
        verified_birthday = human_response.get("birthday", birthday)
        response = f"Made a correction: {human_response}"

    # This time we explicitly update the state with a ToolMessage inside
    # the tool.
    state_update = {
        "name": verified_name,
        "birthday": verified_birthday,
        "messages": [ToolMessage(response, tool_call_id=tool_call_id)],
    }
    # We return a Command object in the tool to update our state.
    return Command(update=state_update)

class CalculatorInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")

def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    print("multiply is called")
    return a * b

def route_tools(
    state: State,
):
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END

def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

calculator = StructuredTool.from_function(
    func=multiply,
    name="Calculator",
    description="multiply numbers",
    args_schema=CalculatorInput,
    return_direct=True,
)

graph_builder = StateGraph(State)

llm = ChatOpenAI(model="o1")

tools = [calculator, human_assistance]
llm_with_tools = llm.bind_tools(tools)
#tool_node = BasicToolNode(tools=tools)
tool_node = ToolNode(tools=[tool])

# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

# The `tools_condition` function returns "tools" if the chatbot asks to use a tool, and "END" if
# it is fine directly responding. This conditional routing defines the main agent loop.
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
    #{"tools": "tools", END: END},
)
# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)
# Display our LangGraph
#RenderLangGraph(graph)

config = {"configurable": {"thread_id": "main-thread"}}

while True:
    try:
        user_input = input("User (quit | exit | q to quit): ")

        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        #stream_graph_updates(user_input)
        events = graph.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            config,
            stream_mode="values",
        )
        for event in events:
            event["messages"][-1].pretty_print()
        #snapshot = graph.get_state(config)
        #print(snapshot)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break