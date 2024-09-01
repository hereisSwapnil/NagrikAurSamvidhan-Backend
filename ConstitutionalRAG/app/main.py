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
