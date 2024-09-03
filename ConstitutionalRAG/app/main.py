from dotenv import load_dotenv
import os
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
from fastapi import FastAPI, HTTPException
from app.config import Config
from app.utils.loader import create_prompt_template
from app.services.embedding_service import create_embeddings
from app.services.response_service import get_response_from_chain
from langchain_groq import ChatGroq

app = FastAPI()

# Initialize the language model
llm = ChatGroq(model="llama3-70b-8192")

# Load prompt template
prompt_template = create_prompt_template()

# Create vector embeddings
vectors = create_embeddings('./data')

# Load environment variables
load_dotenv()

# Get API key from environment variables (not needed if using local model)
api_key = os.getenv("HUGGINGFACE_API_KEY")

# Define the repository ID
repo_id = "facebook/m2m100_418M"

# Initialize the model and tokenizer
model = M2M100ForConditionalGeneration.from_pretrained(repo_id)
tokenizer = M2M100Tokenizer.from_pretrained(repo_id)


def translate_text(text, target_lang):
    tokenizer.src_lang = "en"
    encoded_text = tokenizer(text, return_tensors="pt")
    generated_tokens = model.generate(
        **encoded_text, forced_bos_token_id=tokenizer.get_lang_id(target_lang))
    translated_text = tokenizer.batch_decode(
        generated_tokens, skip_special_tokens=True)
    return translated_text


@app.post("/get_response/")
async def get_response(user_prompt: str):
    if vectors is None:
        raise HTTPException(
            status_code=400, detail="Embeddings not activated. Please activate embeddings first."
        )
    try:
        answer = get_response_from_chain(
            llm, prompt_template, vectors, user_prompt)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the application using: uvicorn app.main:app --reload
