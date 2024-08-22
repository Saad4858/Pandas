from dotenv import load_dotenv
import os
import pandas as pd

from llama_index.core.query_engine import PandasQueryEngine

from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI

load_dotenv()

from pdf import wheat_engine, cotton_engine, rice_engine, sugercane_engine, blackberry_engine




# population_path = os.path.join("data", "population.csv")
# population_df = pd.read_csv(population_path)

# population_query_engine = PandasQueryEngine(
#     df=population_df, verbose=True, instruction_str=instruction_str
# )

# population_query_engine.update_prompts({"pandas_prompt": new_prompt})

tools = [
    # note_engine,
    # QueryEngineTool(
    #     query_engine=population_query_engine,
    #     metadata=ToolMetadata(
    #         name="population_data",
    #         description="this gives information at the world population and demographics",
    #     ),
    # ),
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
        query_engine=sugercane_engine,
        metadata=ToolMetadata(
            name="sugercane_data",
            description="this gives detailed information about the sugercane crop in Pakistan",
        ),
    ),
    QueryEngineTool(
        query_engine=blackberry_engine,
        metadata=ToolMetadata(
            name="blackberry_data",
            description="this gives detailed information about the blackberry crop in general and specifically of it being grown in Pakistan",
        ),
    ),
    # QueryEngineTool(
    #     query_engine=mnfsr_engine,
    #     metadata=ToolMetadata(
    #         name="agricultural_data",
    #         description="this gives detailed all encompassing information and statistics about all things agricultural in Pakistan",
    #     ),
    # ),
]

context = """Purpose: The primary role of this agent is to assist users by providing accurate 
            information about punjabs agriculture statistics and details. """

llm = OpenAI(model="gpt-4o")
agent = ReActAgent.from_tools(tools, llm=llm, verbose=True, context=context)

def getRagResponse(query):
    result = agent.query(query)
    return result


while (prompt := input("Enter a prompt (q to quit): ")) != "q":
    result = agent.query(prompt)
    print(result)