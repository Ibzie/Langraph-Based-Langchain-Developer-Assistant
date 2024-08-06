import os
from dotenv import load_dotenv

load_dotenv()

local_llm = 'llama3.1'
START_URL = "https://python.langchain.com/v0.2/docs/tutorials/"
MAX_DEPTH = 2

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
LANGCHAIN = os.getenv("LANGCHAIN_API")
os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN
