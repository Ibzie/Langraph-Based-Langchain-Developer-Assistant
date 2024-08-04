from config import local_llm, START_URL, MAX_DEPTH
from utils import scrape_urls
from ai_core import load_documents, split_documents, create_vectorstore
from langraph_core import (
    GraphState, get_prompt_template, get_llm, get_retrieval_grader, get_rag_chain, get_question_rewriter,
    retrieve, generate, grade_documents, transform_query,
    decide_to_generate, grade_generation_v_documents_and_question
)
from langgraph.graph import END, StateGraph, START
from pprint import pprint

# Step 1: Scrape URLs
urls = scrape_urls(START_URL, 0, MAX_DEPTH, START_URL)
urls = list(set(urls))
print(f"Scraped URLs: {urls}")

# Step 2: Load and split documents
docs_list = load_documents(urls)
doc_splits = split_documents(docs_list)

# Step 3: Create vectorstore
vectorstore = create_vectorstore(doc_splits)
retriever = vectorstore.as_retriever()

# Step 4: Set up prompts and LLMs
retrieval_template = """You are a grader assessing relevance of a retrieved document to a user question. \n 
Here is the retrieved document: \n\n {document} \n\n
Here is the user question: {question} \n
If the document contains keywords related to the user question, grade it as relevant. \n
It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question. \n
Provide the binary score as a JSON with a single key 'score' and no preamble or explanation."""

hallucination_template = """You are a grader assessing whether an answer is grounded in / supported by a set of facts. \n 
Here are the facts:
\n ------- \n
{documents} 
\n ------- \n
Here is the answer: {generation}
Give a binary score 'yes' or 'no' score to indicate whether the answer is grounded in / supported by a set of facts. \n
Provide the binary score as a JSON with a single key 'score' and no preamble or explanation."""

answer_template = """You are a grader assessing whether an answer is useful to resolve a question. \n 
Here is the answer:
\n ------- \n
{generation} 
\n ------- \n
Here is the question: {question}
Give a binary score 'yes' or 'no' to indicate whether the answer is useful to resolve a question. \n
Provide the binary score as a JSON with a single key 'score' and no preamble or explanation."""

question_rewrite_template = """You are a question re-writer that converts an input question to a better version that is optimized \n 
 for vectorstore retrieval. Look at the initial and formulate an improved question. \n
 Here is the initial question: \n\n {question}. Improved question with no preamble: \n """

retrieval_prompt = get_prompt_template(retrieval_template, ["question", "document"])
hallucination_prompt = get_prompt_template(hallucination_template, ["generation", "documents"])
answer_prompt = get_prompt_template(answer_template, ["generation", "question"])
question_rewrite_prompt = get_prompt_template(question_rewrite_template, ["question"])

llm = get_llm(local_llm)
retrieval_grader = get_retrieval_grader(llm, retrieval_prompt)
hallucination_grader = get_retrieval_grader(llm, hallucination_prompt)
answer_grader = get_retrieval_grader(llm, answer_prompt)
question_rewriter = get_question_rewriter(question_rewrite_prompt, llm)

# Define the RAG prompt template
rag_template = """You are a RAG model combining retrieved documents to generate an answer. 
Here are the documents: \n ------- \n {document} \n ------- \n
Here is the question: {question} 
Generate a concise and accurate answer to the question using the information from the documents."""

rag_prompt = get_prompt_template(rag_template, ["document", "question"])
rag_chain = get_rag_chain(rag_prompt, llm)

# Step 5: Define state graph
workflow = StateGraph(GraphState)

workflow.add_node("retrieve", lambda state: retrieve(state, retriever))
workflow.add_node("grade_documents", lambda state: grade_documents(state, retrieval_grader))
workflow.add_node("generate", lambda state: generate(state, rag_chain))
workflow.add_node("transform_query", lambda state: transform_query(state, question_rewriter))

workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "transform_query": "transform_query",
        "generate": "generate",
    },
)
workflow.add_edge("transform_query", "retrieve")
workflow.add_conditional_edges(
    "generate",
    lambda state: grade_generation_v_documents_and_question(state, hallucination_grader, answer_grader),
    {
        "not supported": "generate",
        "useful": END,
        "not useful": "transform_query",
    },
)

app = workflow.compile()

# Step 6: Run the application
question = "Hello!"
while(question!="\q" or question!="\Q"):
    inputs = {"question": "Eample Query: Explain what is Langchain as best as you can?"}
    for output in app.stream(inputs, {"recursion_limit": 500}):
        for key, value in output.items():
            pprint(f"Node '{key}':")
            pprint(value)
        pprint("\n---\n")
    
    question = input("Enter your next query: ")

    # Final generation
    pprint(value["generation"])
