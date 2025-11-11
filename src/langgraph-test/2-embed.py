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

chroma = chromadb.PersistentClient(path="data/chromadb")

COFFEE_KNOWLEDGE = """
Espresso is a concentrated form of coffee served in small, strong shots. It is made by forcing hot water under pressure through finely-ground coffee beans. Espresso forms the base for many coffee drinks.

Cappuccino is an espresso-based drink that's traditionally prepared with steamed milk, and milk foam. A traditional Italian cappuccino is generally a single shot of espresso topped with equal parts steamed milk and milk foam.

Latte is a coffee drink made with espresso and steamed milk. The word comes from the Italian 'caffè e latte' meaning 'coffee and milk'. A typical latte is made with one or two shots of espresso, steamed milk and a small layer of milk foam on top.

Cold Brew is coffee made by steeping coarse coffee grounds in cold water for 12-24 hours. This method creates a smooth, less acidic taste compared to hot brewed coffee. Cold brew can be served over ice or heated up.
"""


def main():

    coffeeChunker = RawTextChunkingStratedgy(size=128, overlap=5)
    coffeeChunks: List[RAGChunk] = coffeeChunker.process(COFFEE_KNOWLEDGE)

    efcoreChunker = MarkDownDirectoryChunkingStratedgy(
        input_dir="/home/scott/code/llm-things/src/langgraph-test/data/EntityFramework.Docs/entity-framework/core", 
        size=2048, 
        overlap=128)
    efcoreChunks = efcoreChunker.process()

    embedding_function: AmazonBedrockEmbeddingFunction = AmazonBedrockEmbeddingFunction(
        session=session,
        model_name="amazon.titan-embed-text-v2:0")

    # create collections
    coffee_collection: Collection = chroma.get_or_create_collection(
            name="coffee",
            embedding_function=embedding_function)   # type: ignore
    
    efcore_collection: Collection = chroma.get_or_create_collection(
        name="efcore",
        embedding_function=embedding_function)   # type: ignore


    # Add the chunks to the collection
    coffee_collection.add(
        ids=[chunk.id_ for chunk in coffeeChunks],
        documents=[chunk.text for chunk in coffeeChunks],
        metadatas=[chunk.metadata for chunk in coffeeChunks]
    )
    print(f"✅ Added {len(coffeeChunks)} chunks to collection {coffee_collection.name}")

    efcore_collection.add(
        ids=[chunk.id_ for chunk in efcoreChunks],
        documents=[chunk.text for chunk in efcoreChunks],
        metadatas=[chunk.metadata for chunk in efcoreChunks]
    )
    print(f"✅ Added {len(efcoreChunks)} chunks to collection {efcore_collection.name}")



if __name__ == "__main__":
    main()

