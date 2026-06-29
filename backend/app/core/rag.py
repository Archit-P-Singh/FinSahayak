import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Initialize lightweight open-source embeddings (runs locally)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

CHROMA_DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_db")

def get_vector_store():
    """
    Returns the ChromaDB vector store instance for RAG.
    """
    return Chroma(
        collection_name="financial_knowledge",
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_DIR
    )

def add_documents_to_db(docs):
    """
    Adds a list of LangChain Document objects to the vector store.
    """
    vector_store = get_vector_store()
    vector_store.add_documents(docs)
