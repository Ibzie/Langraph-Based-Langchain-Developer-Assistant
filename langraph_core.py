from typing import List
from typing_extensions import TypedDict
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain import hub

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents
    """
    question: str
    generation: str
    documents: List[str]

# Prompts
def get_prompt_template(template_str, input_vars):
    return PromptTemplate(template=template_str, input_variables=input_vars)

def get_llm(model, format="json", temperature=0):
    return ChatOllama(model=model, format=format, temperature=temperature)

# Chains
def get_retrieval_grader(llm, prompt):
    return prompt | llm | JsonOutputParser()

def get_rag_chain(prompt, llm):
    return prompt | llm | StrOutputParser()

def get_question_rewriter(prompt, llm):
    return prompt | llm | StrOutputParser()

# State management functions
def retrieve(state, retriever):
    question = state["question"]
    documents = retriever.get_relevant_documents(question)
    return {"documents": documents, "question": question}

def generate(state, rag_chain):
    question = state["question"]
    documents = state["documents"]
    document_texts = "\n-------\n".join([doc.page_content for doc in documents])
    generation = rag_chain.invoke({"document": document_texts, "question": question})
    return {"documents": documents, "question": question, "generation": generation}



def grade_documents(state, retrieval_grader):
    question = state["question"]
    documents = state["documents"]
    filtered_docs = []

    for d in documents:
        score = retrieval_grader.invoke({"question": question, "document": d.page_content})
        if score["score"] == "yes":
            filtered_docs.append(d)

    return {"documents": filtered_docs, "question": question}

def transform_query(state, question_rewriter):
    question = state["question"]
    documents = state["documents"]
    better_question = question_rewriter.invoke({"question": question})
    return {"documents": documents, "question": better_question}

def decide_to_generate(state):
    filtered_documents = state["documents"]
    if not filtered_documents:
        return "transform_query"
    else:
        return "generate"

def grade_generation_v_documents_and_question(state, hallucination_grader, answer_grader):
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader.invoke({"documents": documents, "generation": generation})
    if score["score"] == "yes":
        score = answer_grader.invoke({"question": question, "generation": generation})
        if score["score"] == "yes":
            return "useful"
        else:
            return "not useful"
    else:
        return "not supported"
