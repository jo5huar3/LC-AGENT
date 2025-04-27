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
from prompts import context, code_parser_template
from llama_index.core.tools import BaseTool, FunctionTool
import os
import ast
load_dotenv()
##############################################
# You can also directly import from llama_index.core, 
# though the top-level llama_index.* is the recommended approach in recent versions.
##############################################

# 2) Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# 3) Initialize LLM
llm = OpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)
Settings.llm = llm
Settings.embed_model = OpenAIEmbedding(model="text-embedding-ada-002", api_key=OPENAI_API_KEY)

#########################################
# 4) Attempt to load an existing vector index from “./storage/codebase”
#    If it doesn’t exist, build one from the folder “data/codebase”
#########################################
try:
    storage_context = StorageContext.from_defaults(persist_dir="./storage/codebase")
    vector_index = load_index_from_storage(storage_context)
    index_loaded = True
except:
    index_loaded = False

if not index_loaded:
    # Read documents (Python files, etc.) from "data/codebase" and build an index
    documents = SimpleDirectoryReader("data/codebase").load_data()
    vector_index = VectorStoreIndex.from_documents(documents)
    # Persist the index for future runs
    vector_index.storage_context.persist(persist_dir="./storage/codebase")

# 5) Create a query engine to retrieve code snippets or doc content
query_engine = vector_index.as_query_engine(llm=llm)

#########################################
# 6) Define Tools
#########################################
def file_reader(file_name: str) -> dict:
    """Given a filename relative to your workspace, return the file contents."""
    full_path = os.path.join("data", "codebase", file_name)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"file_content": content}
    except Exception as e:
        return {"error": f"Could not read file: {str(e)}"}

file_reader_tool = FunctionTool.from_defaults(
    fn=file_reader, 
    name="file_reader",
    description="Reads the contents of a file from the codebase."
)

def file_writer(file_name: str, file_content: str) -> dict:
    """Write the given content to a new file (or overwrite existing)."""
    full_path = os.path.join("data", "codebase", file_name)
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(file_content)
        return {"status": "success", "written_file": file_name}
    except Exception as e:
        return {"error": f"Could not write file: {str(e)}"}

file_writer_tool = FunctionTool.from_defaults(
    fn=file_writer,
    name="file_writer",
    description="Writes the given content to a specified file in the codebase."
)

def multiply(a: int, b: int) -> int:
    """Multiply two integers and return the result."""
    return a * b

multiply_tool = FunctionTool.from_defaults(
    fn=multiply, 
    name="multiply", 
    description="Multiply two integers."
)

def add(a: int, b: int) -> int:
    """Add two integers and return the result."""
    return a + b

add_tool = FunctionTool.from_defaults(
    fn=add, 
    name="add", 
    description="Add two integers."
)

# Provide a code snippet retrieval tool from your vector index
snippet_tool = QueryEngineTool(
    query_engine=query_engine,
    metadata=ToolMetadata(
        name="codebase_snippet_retriever",
        description=(
            "Given a programming-related query, retrieve relevant code from the codebase. "
            "Ideal for analyzing or referencing existing source code in 'data/codebase'."
        ),
    ),
)

#########################################
# 7) Assemble all Tools into a ReActAgent
#########################################
tools = [
    add_tool,
    multiply_tool,
    file_reader_tool,
    file_writer_tool,
    snippet_tool
]

agent = ReActAgent.from_tools(
    tools=tools,
    llm=llm,
    verbose=True,
    # Minimal "context" prompt: 
    context="You are a helpful coding assistant. You can read files, write files, and do math if asked."
)

#########################################
# 8) (Optional) a pipeline for specialized output
#    Here is just a short demonstration of how you
#    could parse a structured code output with Pydantic
#########################################
class CodeOutput(BaseModel):
    code: str
    description: str
    filename: str

code_parser_template = """
You are given a request to produce a Python script plus a short explanation.
Generate valid JSON that conforms to the schema:
"""


parser = PydanticOutputParser(CodeOutput)
json_prompt_str = parser.format(code_parser_template)
json_prompt = PromptTemplate(json_prompt_str)

output_pipeline = QueryPipeline(chain=[json_prompt, llm])

#########################################
# 9) Interactive loop
#########################################
def run_console():
    print("Welcome! Type your request, or q to quit.")
    while True:
        prompt = input("\nUser> ")
        if prompt.lower().strip() == "q":
            break
        try:
            # 1) Chat with the agent using the ReAct-based approach
            agent_response = agent.chat(prompt)
            print(f"Assistant (Agent) says:\n{agent_response}\n")
            
            # 2) (Optional) parse an instruction to create code in JSON form
            #    If you want the user to specifically say "Generate code" or something:
            if "generate code" in prompt.lower():
                # feed the agent's text to the pipeline
                pipeline_response = output_pipeline.run(response=agent_response)
                # parse it into a Pydantic model
                try:
                    # Because the LLM might not produce perfect JSON, do a small safety parse
                    pipeline_response = str(pipeline_response).strip()
                    pipeline_response = pipeline_response.replace("assistant:", "")
                    parsed = ast.literal_eval(pipeline_response)
                    
                    code_output = CodeOutput(**parsed)
                    print("\nProposed file content:\n", code_output.code)
                    print("Description:", code_output.description)
                    print("Suggested filename:", code_output.filename)
                    
                    # Optionally write out the file
                    file_writer_tool.run(
                        file_name=code_output.filename,
                        file_content=code_output.code
                    )
                    print(f"File '{code_output.filename}' written.\n")
                except Exception as parse_err:
                    print(f"Error parsing structured code output: {parse_err}")
        except Exception as e:
            print(f"Error occurred: {e}")

if __name__ == "__main__":
    run_console()
