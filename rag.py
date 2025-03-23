from dotenv import load_dotenv
import os
import pandas as pd

from llama_index.core.query_engine import PandasQueryEngine

from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI

load_dotenv()

from index_builder import wheat_engine, cotton_engine, rice_engine, sugarcane_engine, maize_engine, spinach_engine

tools = [
    QueryEngineTool(
        query_engine=wheat_engine,
        metadata=ToolMetadata(
            name="wheat_data",
            description="this gives detailed information about the wheat crop in Pakistan",
        ),
    ),
    QueryEngineTool(
        query_engine=rice_engine,
        metadata=ToolMetadata(
            name="rice_data",
            description="this gives detailed information about the rice crop in Pakistan",
        ),
    ),
    QueryEngineTool(
        query_engine=cotton_engine,
        metadata=ToolMetadata(
            name="cotton_data",
            description="this gives detailed information about the cotton crop in Pakistan",
        ),
    ),
    QueryEngineTool(
        query_engine=sugarcane_engine,
        metadata=ToolMetadata(
            name="sugarcane_data",
            description="this gives detailed information about the sugarcane crop in Pakistan",
        ),
    ),
    QueryEngineTool(
        query_engine=maize_engine,
        metadata=ToolMetadata(
            name="maize_data",
            description="this gives detailed information about the maize crop in Pakistan",
        ),
    ),
    QueryEngineTool(
        query_engine=spinach_engine,
        metadata=ToolMetadata(
            name="spinach_data",
            description="this gives detailed information about the spinach crop in Pakistan",
        ),
    )
    
]

context = """Purpose: The primary role of this agent is to assist users by providing accurate 
            information about punjabs agriculture statistics and details. """

llm = OpenAI(model="gpt-4o")
agent = ReActAgent.from_tools(tools, llm=llm, verbose=True, context=context)