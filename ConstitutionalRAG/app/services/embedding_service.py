from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def create_embeddings(pdf_dir: str, model_name: str = "models/embedding-001"):
    embeddings = GoogleGenerativeAIEmbeddings(model=model_name)
    loader = PyPDFDirectoryLoader(pdf_dir)
    text = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200)
    final_documents = text_splitter.split_documents(text)
    vectors = FAISS.from_documents(final_documents, embeddings)
    return vectors
