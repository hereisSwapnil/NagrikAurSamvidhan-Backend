from fastapi import FastAPI, HTTPException
from app.config import Config
from app.utils.loader import create_prompt_template_legal_expert, create_prompt_template_educational_expert, tokenizer, model, llm
from app.services.embedding_service import create_embeddings
from app.services.response_service import get_response_from_chain
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prompt_template_legal_expert = create_prompt_template_legal_expert()
prompt_template_educational_expert = create_prompt_template_educational_expert()

# Initialize embeddings at startup for efficiency
vectors = create_embeddings()


def translate_text(text, target_lang):
    tokenizer.src_lang = "en"
    encoded_text = tokenizer(text, return_tensors="pt")
    generated_tokens = model.generate(
        **encoded_text, forced_bos_token_id=tokenizer.get_lang_id(target_lang))
    translated_text = tokenizer.batch_decode(
        generated_tokens, skip_special_tokens=True)
    return translated_text


@app.post("/get_educational")
async def get_response(user_prompt: str):
    if vectors is None:
        raise HTTPException(
            status_code=400, detail="Embeddings not activated. Please activate embeddings first."
        )
    try:
        answer = get_response_from_chain(
            llm, prompt_template_educational_expert, vectors, user_prompt)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get_legal")
async def get_response(user_prompt: str):
    if vectors is None:
        raise HTTPException(
            status_code=400, detail="Embeddings not activated. Please activate embeddings first."
        )
    try:
        answer = get_response_from_chain(
            llm, prompt_template_legal_expert, vectors, user_prompt)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/translate")
async def translate(text: str, target_lang: str):
    try:
        translation = translate_text(text, target_lang)
        return {"translation": translation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the application using: uvicorn app.main:app --reload
