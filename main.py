from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, PromptTemplate, StorageContext, load_index_from_storage
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from pydantic import BaseModel
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.query_pipeline import QueryPipeline
from specs.prompts import context, code_parser_template
from llama_index.core.tools import BaseTool, FunctionTool
import os
import ast
load_dotenv()


llm = OpenAI(model="gpt-4o")

try:
    storage_context = StorageContext.from_defaults(
        persist_dir="./storage/codebase"
    )
    vector_index = load_index_from_storage(storage_context)
    index_loaded = True
except:
    index_loaded = False
if not index_loaded:
    documents = SimpleDirectoryReader("data/codebase").load_data()
    vector_index = VectorStoreIndex.from_documents(documents)
    vector_index.storage_context.persist(persist_dir="./storage/codebase")
    
# print(vector_index)
Settings.llm = llm
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
query_engine = vector_index.as_query_engine(llm=llm)


def file_reader(file_name: str) -> str:
    """Take the file found using dir as a relative path and return the contents of the file as a string"""
    path = os.path.join("data", file_name)
    try:
        with open(file_name, "r") as f:
            content = f.read()
            return {"file_content": content}
    except Exception as e:
        return {"error": str(e)}
file_reader_tool = FunctionTool.from_defaults(fn=file_reader, name="file_reader")

def multiply(a: int, b: int) -> int:
    """Multiply two integers and returns the result integer"""
    return a * b
multiply_tool = FunctionTool.from_defaults(fn=multiply, name="multiply")

def add(a: int, b: int) -> int:
    """Add two integers and returns the result integer"""
    return a + b
add_tool = FunctionTool.from_defaults(fn=add, name="add")

tools = [
    add_tool,
    multiply_tool,
    file_reader_tool,
    QueryEngineTool(
            query_engine=query_engine,
            metadata=ToolMetadata(
                name="codebase_snippet_retriever",
                description="Given a single-step programming task, retrieves one relevant code \
                snippet from the codebase and a short explanation. Should be for python code inferences only.",
            ),
        ),
]

code_llm = OpenAI(model="gpt-4o")
agent = ReActAgent.from_tools(tools, llm=code_llm, verbose=True, context=context)


class CodeOutput(BaseModel):
    code: str
    description: str
    filename: str


parser = PydanticOutputParser(CodeOutput)
json_prompt_str = parser.format(code_parser_template)
json_prompt_tmpl = PromptTemplate(json_prompt_str)
output_pipeline = QueryPipeline(chain=[json_prompt_tmpl, llm])

while (prompt := input("Enter a prompt (q to quit): ")) != "q":
    try:
        response = agent.chat(prompt)
        #next_result = output_pipeline.run(response=result)
        #cleaned_json = ast.literal_eval(str(next_result).replace("assistant:", ""))
    except Exception as e:
        print(f"Error occured, retry:", e)