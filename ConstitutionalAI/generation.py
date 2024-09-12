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
