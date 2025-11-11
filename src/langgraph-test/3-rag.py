import boto3
import os
import chromadb
from chromadb import Collection, QueryResult
from chromadb.utils.embedding_functions import AmazonBedrockEmbeddingFunction
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
from utils.rag_utils import RAGChunk, RawTextChunkingStratedgy, MarkDownDirectoryChunkingStratedgy

load_dotenv()

MODEL = "amazon.nova-micro-v1:0"

session = boto3.Session(region_name="us-east-1")
bedrock_client = session.client(
    service_name="bedrock-runtime",
)

llm = ChatBedrockConverse(
    model=MODEL,
    client=bedrock_client,
    #region_name="us-east-1",
    # aws_access_key_id=...,
    # aws_secret_access_key=...,
    # aws_session_token=session,
    temperature=0,
    max_tokens=500,
    # other params...
)

chroma = chromadb.PersistentClient(path="data/chromadb")
embedding_function: AmazonBedrockEmbeddingFunction = AmazonBedrockEmbeddingFunction(
session=session,
model_name="amazon.titan-embed-text-v2:0")

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

RAG_PROMPT_TEMPLATE: str = """
    Using the context below, answer the question.

    <context>
    {context}
    </context>

    <question>
    {question}
    </question>

    Remember, if the context doesn't contain the answer, say "I don't know".
    """

def ask(question: str, collection: str, n_results: int):
    # create collections
    coffee_collection: Collection = chroma.get_or_create_collection(
            name=collection,
            embedding_function=embedding_function)   # type: ignore
    
    qr: QueryResult = coffee_collection.query(
        query_texts=[question],
        n_results=n_results,
        include=['embeddings', 'documents', 'metadatas', 'distances']
    )

    if collection == "efcore":
        i = 0
        for hit in qr['documents'][0]:
            print(qr['metadatas'][0][i]['file_path'])
            i += 1

    context: str = "\n\n".join(qr['documents'][0])
    rag_prompt: str = RAG_PROMPT_TEMPLATE.format(question=question, context=context)
    
    # Call Bedrock with the RAG prompt
    user_message = HumanMessage(content=rag_prompt)
    user_message.pretty_print()

    answer = llm.invoke([user_message])
    answer.pretty_print()

def main():

    ask("how is cold brew made?", "coffee", 1)

    ask("How do I bulk delete rows?", "efcore", 3)

    # # create collections
    # coffee_collection: Collection = chroma.get_or_create_collection(
    #         name="coffee",
    #         embedding_function=embedding_function)   # type: ignore
    
    # efcore_collection: Collection = chroma.get_or_create_collection(
    #     name="efcore",
    #     embedding_function=embedding_function)   # type: ignore

    # # Question 1
    # question = "how is cold brew made?"
    # qr: QueryResult = coffee_collection.query(
    #     query_texts=[question],
    #     n_results=1,
    #     include=['embeddings', 'documents', 'metadatas', 'distances']
    # )

    # context: str = "\n\n".join(qr['documents'][0])
    # rag_prompt: str = RAG_PROMPT_TEMPLATE.format(question=question, context=context)
    
    # # Call Bedrock with the RAG prompt
    # user_message = HumanMessage(content=rag_prompt)
    # user_message.pretty_print()

    # answer = llm.invoke([user_message])
    # answer.pretty_print()

if __name__ == "__main__":
    main()

