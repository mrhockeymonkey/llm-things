import boto3
import json
from dotenv import load_dotenv
from typing import Dict, List, TypedDict, Any
from langgraph.graph import START, END, StateGraph
from langchain_aws import ChatBedrockConverse
from types_boto3_bedrock_runtime import BedrockRuntimeClient
from types_boto3_bedrock_runtime.type_defs import MessageTypeDef, ConverseResponseTypeDef
# from langchain.messages import AnyMessage
from typing_extensions import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, SystemMessage
from langchain_aws import ChatBedrockConverse

load_dotenv()

MODEL = "amazon.nova-micro-v1:0"


llm = ChatBedrockConverse(
    model=MODEL,
    region_name="us-east-1",
    # aws_access_key_id=...,
    # aws_secret_access_key=...,
    # aws_session_token=...,
    temperature=0,
    max_tokens=500,
    # other params...
)

class State(TypedDict):
    """Type definition for our conversation state"""
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int

def call_llm(state: State) -> State:
    """Call Bedrock with the current conversation state"""
    
    response = llm.invoke(state['messages'])
    
    return {
        "messages": [response],
        "llm_calls": state.get('llm_calls', 0) + 1
    }

def main():

    workflow = StateGraph(State)
    workflow.add_node("llm", call_llm)
    workflow.add_edge(START, "llm")  # First, call the LLM
    workflow.add_edge("llm", END)    # Then end the workflow
    agent = workflow.compile()

    messages : List[AnyMessage] = [
        HumanMessage(content="Say hi in french")
    ]

    initial_state: State = {"messages": messages, "llm_calls": 0}
    
    result: Dict[str, Any] = agent.invoke(initial_state)
    
    for m in result["messages"]:
        m.pretty_print()

if __name__ == "__main__":
    main()

