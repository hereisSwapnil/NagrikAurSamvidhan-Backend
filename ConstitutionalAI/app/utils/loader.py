from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
from dotenv import load_dotenv
import os

load_dotenv()

# Load Hugging Face model and tokenizer only once
api_key = os.getenv("HUGGINGFACE_API_KEY")
repo_id = "facebook/m2m100_418M"
model = M2M100ForConditionalGeneration.from_pretrained(repo_id)
tokenizer = M2M100Tokenizer.from_pretrained(repo_id)

llm = ChatGroq(model="llama3-70b-8192")


def create_prompt_template():
    return ChatPromptTemplate.from_template(
        '''
        As a seasoned legal advisor, you possess deep knowledge of legal intricacies and are skilled in referencing relevant laws and regulations. Users will seek guidance on various legal matters.

        If a question falls outside the scope of legal expertise, kindly inform the user that your specialization is limited to legal advice.

        In cases where you're uncertain of the answer, it's important to uphold integrity by admitting 'I don't know' rather than providing potentially erroneous information.

        Below is a snippet of context from the relevant section of the constitution, although it will not be disclosed to users.
        <context>
        Context: {context}
        Question: {input}
        <context>
        Your response should consist solely of helpful advice without any extraneous details.

        Helpful advice:
        '''
    )
