from typing import Annotated
import io
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from typing_extensions import TypedDict
from tools.uRLTool import *
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt

'''
Human assistance and state modification.
'''

class State(TypedDict):
    messages: Annotated[list, add_messages]

def RenderLangGraph(graph):
    try:
        png_bytes = graph.get_graph().draw_mermaid_png()
        buf = io.BytesIO(png_bytes)
        img_arr = mpimg.imread(buf, format='PNG')
        plt.imshow(img_arr)
        plt.axis('off')
        plt.show()
    except Exception:
        print("exception occured")

def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    assert(len(message.tool_calls) <= 1)
    return {"messages": [message]}

tools = [ extractUrlContent ]
llm = ChatOpenAI(model="o1")
llm_with_tools = llm.bind_tools(tools)

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

RenderLangGraph(graph)

