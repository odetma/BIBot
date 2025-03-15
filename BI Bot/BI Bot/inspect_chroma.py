from langchain_community.vectorstores import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Azure OpenAI API details
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_BASE = os.getenv("AZURE_OPENAI_API_BASE")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

CHROMA_PATH = "chroma"

def get_azure_embedding_function():
    """Returns an Azure OpenAI embedding function."""
    return AzureOpenAIEmbeddings(
        azure_endpoint=AZURE_OPENAI_API_BASE,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    )

def inspect_chroma():
    """Loads and displays stored schema entries and their embeddings from ChromaDB."""
    embedding_function = get_azure_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Retrieve all stored documents and embeddings
    stored_data = db.get(include=["documents", "embeddings"])

    if stored_data:
        print("✅ Stored Schema Entries in ChromaDB:\n")
        for i, (doc, vector) in enumerate(zip(stored_data['documents'], stored_data['embeddings'])):
            print(f"🔹 Entry {i+1}:")
            print(doc)
            print("\n📌 Embedding Vector (first 5 values):", vector[:5])  # Display first 5 numbers for readability
            print("-" * 80)
    else:
        print("❌ No data found in ChromaDB.")

if __name__ == "__main__":
    inspect_chroma()
