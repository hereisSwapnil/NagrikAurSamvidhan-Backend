from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi import FastAPI, HTTPException, Request
from app.config import Config
from fastapi.middleware.cors import CORSMiddleware
import requests
from langchain_community.document_loaders import UnstructuredURLLoader
import os
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = FastAPI()


@app.get("/generate_case_study")
async def get_news(request: Request):
    # Define the base URL and parameters
    url = 'https://newsapi.org/v2/everything'
    now = datetime.now()
    six_days_ago = now - timedelta(days=6)
    params = {
        'q': 'crimes in Kolkata',
        'from': six_days_ago.strftime('%Y-%m-%d'),
        'to': now.strftime('%Y-%m-%d'),
        'pageSize': 1,
        'apiKey': os.getenv('NEWS_API_KEY')  # Fetch API key from environment
    }

    # Modify parameters based on query parameters from the request
    for key in params.keys():
        if key in request.query_params:
            params[key] = request.query_params[key]

    # Make the GET request to the external API
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code != 200:
        return JSONResponse(status_code=response.status_code, content={"error": "Failed to fetch news"})

    # Parse the JSON response
    data = response.json()

    # Ensure there are articles in the response
    if 'articles' not in data or not data['articles']:
        return JSONResponse(status_code=404, content={"error": "No articles found"})

    # Extract the URL from the first article
    url_data = data['articles'][0]['url']

    # Load the news data synchronously
    loader = UnstructuredURLLoader(urls=[url_data])
    news_data = loader.load()[0]

    # Extract the page content from the Document object
    news_text = news_data.page_content

    prompt = (
        'You are an AI simulating a human who crafts engaging and interactive case studies based on real news events. '
        'These case studies should delve into the Indian Constitution, specifically highlighting instances where fundamental rights and laws have been violated. '
        'Your task is to integrate relevant data and legal aspects from the Constitution and provide detailed analysis without summarizing the case study. '
        'Ensure the case study is immersive, guiding the reader through an interactive exploration of the situation, encouraging critical thinking, '
        'and prompting discussion on the constitutional violations involved.'
    )

    # Generate case study content using the Generative AI model
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([prompt, news_text])

    result = response.to_dict()
    # Extract the content from the generated response
    # Adjust according to the structure of the response
    case_study_text = result['candidates'][0]['content']['parts'][0]['text']

    print(case_study_text)

    res = {
        'description': str(case_study_text)
    }
    return JSONResponse(content=res)


# def translate_text(text, target_lang):
#     tokenizer.src_lang = "en"
#     encoded_text = tokenizer(text, return_tensors="pt")
#     generated_tokens = model.generate(
#         **encoded_text, forced_bos_token_id=tokenizer.get_lang_id(target_lang))
#     translated_text = tokenizer.batch_decode(
#         generated_tokens, skip_special_tokens=True)
#     return translated_text


# @app.post("/get_educational")
# async def get_response(user_prompt: str):
#     if vectors is None:
#         raise HTTPException(
#             status_code=400, detail="Embeddings not activated. Please activate embeddings first."
#         )
#     try:
#         answer = get_response_from_chain(
#             llm, prompt_template_educational_expert, vectors, user_prompt)
#         return {"answer": answer}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/get_legal")
# async def get_response(user_prompt: str):
#     if vectors is None:
#         raise HTTPException(
#             status_code=400, detail="Embeddings not activated. Please activate embeddings first."
#         )
#     try:
#         answer = get_response_from_chain(
#             llm, prompt_template_legal_expert, vectors, user_prompt)
#         return {"answer": answer}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/translate")
# async def translate(text: str, target_lang: str):
#     try:
#         translation = translate_text(text, target_lang)
#         return {"translation": translation}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# Run the application using: uvicorn app.main:app --reload
