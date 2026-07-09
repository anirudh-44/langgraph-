from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage,HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
import sqlite3

load_dotenv()

llm  = HuggingFaceEndpoint(
        repo_id = "Qwen/Qwen2.5-72B-Instruct",
        task = "text-generation"
)

model = ChatHuggingFace(llm=llm)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}

conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
# Checkpointer
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    unique_threads = set()
    for checkpoint in checkpointer.list(None): # looping over the generator that returns all the checkpointers
        #print(checkpoint)
        unique_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(unique_threads)

#print(chatbot.get_state(config={'configurable':{'thread_id':'thread-1'}}))



