from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os
import google.generativeai as genai
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Config class

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    PDF_DIRECTORY = './data'
    EMBEDDING_MODEL = "models/embedding-001"


# Initialize ChatGroq LLM
llm = ChatGroq(model="llama3-70b-8192")

# Function to create embeddings


def create_embeddings(pdf_dir: str = Config.PDF_DIRECTORY, model_name: str = Config.EMBEDDING_MODEL):
    embeddings = GoogleGenerativeAIEmbeddings(model=model_name)
    loader = PyPDFDirectoryLoader(pdf_dir)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200)
    final_documents = text_splitter.split_documents(documents)
    vectors = FAISS.from_documents(final_documents, embeddings)
    return vectors

# Function to get response from chain


def get_response_from_chain(llm, prompt_template, vectors, user_prompt, language):
    document_chain = create_stuff_documents_chain(llm, prompt_template)
    retriever = vectors.as_retriever()
    retriever_chain = create_retrieval_chain(retriever, document_chain)
    response = retriever_chain.invoke(
        {'input': user_prompt, 'language': language})
    return response.get('answer')

# Define prompt templates


def create_prompt_template_legal_expert():
    return ChatPromptTemplate.from_template(
        '''
        You are an expert legal assistant with deep knowledge of legal intricacies, skilled at referencing and applying relevant laws, regulations, sections, and articles. Users will seek your guidance on various legal incidents or issues, and you should provide clear, concise, and actionable advice based on the law.

        If a query falls outside the legal domain or if you are unsure of the answer, it's essential to maintain integrity by either advising the user to consult a relevant professional or by saying 'I don't know.'

        In your response, focus on the specific legal aspects, referencing the appropriate sections, articles, and regulations that apply to the situation. Provide practical advice on the steps the user can take to address their issue.

        Below is a snippet of context from the relevant legal texts, though this context will not be shown to users.
        <context>
        Context: {context}
        Question: {input}
        <context>
        Your response should be precise, focusing solely on the legal advice needed to resolve the issue at hand.
        You should response in {language} only.
        
        Legal advice:
        '''
    )


def create_prompt_template_educational_expert():
    return ChatPromptTemplate.from_template(
        '''
        You are an expert educational assistant with a deep understanding of various subjects, particularly in interpreting and explaining complex articles, cases, and incidents. Your role is to help users comprehend difficult concepts, summarize content, and provide suggestions for further study or understanding.

        When a user asks a question, provide clear, concise explanations that break down complex information into understandable terms. Your goal is to make learning easier and more accessible by summarizing the key points, offering relevant examples, and suggesting additional resources if necessary.

        Your responses should be supportive, educational, and aimed at helping users understand the material better.

        Below is a snippet of the relevant content for your internal reference to help craft your response. This content will not be shown to users.
        <context>
        Context: {context}
        Question: {input}
        <context>
        Your response should focus on teaching and clarifying the topic at hand be concise in what you are saying.
        You should response in {language} only.

        Educational guidance:
        '''
    )


# Initialize embeddings
vectors = create_embeddings()

# FastAPI application
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load prompt templates
prompt_template_legal_expert = create_prompt_template_legal_expert()
prompt_template_educational_expert = create_prompt_template_educational_expert()

# Educational endpoint


@app.post("/get_educational")
async def get_response(user_prompt: str, language: str):
    try:
        answer = get_response_from_chain(
            llm, prompt_template_educational_expert, vectors, user_prompt, language)
        answer = answer.replace("\n", "<br>")
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Legal endpoint


@app.post("/get_legal")
async def get_response(user_prompt: str, language: str):
    try:
        answer = get_response_from_chain(
            llm, prompt_template_legal_expert, vectors, user_prompt, language)
        answer = answer.replace("\n", "<br>")
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# To run the application use: uvicorn chatbot:app --reload
