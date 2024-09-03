from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import Config


def create_embeddings(pdf_dir: str = Config.PDF_DIRECTORY, model_name: str = Config.EMBEDDING_MODEL):
    embeddings = GoogleGenerativeAIEmbeddings(model=model_name)
    loader = PyPDFDirectoryLoader(pdf_dir)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200)
    final_documents = text_splitter.split_documents(documents)
    vectors = FAISS.from_documents(final_documents, embeddings)
    return vectors
