import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import NomicEmbeddings


load_dotenv()
local_llm = 'llama3.1'



os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
LANGCHAIN = os.getenv("LANGCHAIN_API")
os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN


# Constants
START_URL = "https://python.langchain.com/v0.2/docs/tutorials/"
MAX_DEPTH = 2

def fetch_page(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

def scrape_urls(url, depth, max_depth):
    if depth > max_depth:
        return []

    page_content = fetch_page(url)
    if not page_content:
        return []

    soup = BeautifulSoup(page_content, 'html.parser')
    links = soup.find_all('a', href=True)
    urls = [urljoin(url, link['href']) for link in links if link['href'].startswith('/')]

    all_urls = []
    for link_url in urls:
        if link_url.startswith(START_URL):
            all_urls.append(link_url)
            all_urls.extend(scrape_urls(link_url, depth + 1, max_depth))

    return all_urls

# Step 2: Scrape URLs
urls = scrape_urls(START_URL, 0, MAX_DEPTH)
urls = list(set(urls))  # Remove duplicates
print(f"Scraped URLs: {urls}")

# Step 3: Use LangChain's WebBaseLoader to scrape content from the URLs
docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]

# Step 4: Split the documents into chunks
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=250, chunk_overlap=0
)
doc_splits = text_splitter.split_documents(docs_list)

# Step 5: Add to vectorDB
vectorstore = Chroma.from_documents(
    documents=doc_splits,
    collection_name="rag-chroma",
    embedding=NomicEmbeddings(model="nomic-embed-text-v1.5", inference_mode="local"),
)
retriever = vectorstore.as_retriever()


from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import JsonOutputParser

llm = ChatOllama(model=local_llm, format="json", temperature=0)

prompt = PromptTemplate(
    template="""You are a grader assessing relevance of a retrieved document to a user question. \n 
    Here is the retrieved document: \n\n {document} \n\n
    Here is the user question: {question} \n
    If the document contains keywords related to the user question, grade it as relevant. \n
    It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question. \n
    Provide the binary score as a JSON with a single key 'score' and no premable or explanation.""",
    input_variables=["question", "document"],
)

retrieval_grader = prompt | llm | JsonOutputParser()
question = "agent memory"
docs = retriever.get_relevant_documents(question)
doc_txt = docs[1].page_content
print(retrieval_grader.invoke({"question": question, "document": doc_txt}))

