from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from extract_tmdl_schema import load_all_tmdls
from dotenv import load_dotenv
import os
import shutil

# Load environment variables
load_dotenv()

# Azure OpenAI API details
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_BASE = os.getenv("AZURE_OPENAI_API_BASE")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

CHROMA_PATH = "chroma"

# ✅ Define Important Key Columns (To Ensure They're Always Embedded)
IMPORTANT_COLUMNS = {
    "DimDate": ["Date", "Year", "Month", "MonthName"],
    "DimCustomer": ["CustomerKey", "FirstName", "LastName", "EmailAddress"],
    "DimProduct": ["ProductKey", "ProductName", "Category"],
    "FactInternetSales": ["OrderDate", "SalesAmount", "CustomerKey", "ProductKey"]
}

def get_azure_embedding_function():
    """Returns an Azure OpenAI embedding function."""
    return AzureOpenAIEmbeddings(
        azure_endpoint=AZURE_OPENAI_API_BASE,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    )

def generate_data_store():
    """Loads Power BI schema and saves it to ChromaDB, ensuring related tables have key columns."""
    schema = load_all_tmdls("./")  # Load Power BI schema

    documents = []

    for table, columns in schema.items():
        # ✅ Add missing key columns for related tables
        if table in IMPORTANT_COLUMNS:
            for key_col in IMPORTANT_COLUMNS[table]:
                if key_col not in columns:
                    columns.append(key_col)  # Ensure these columns are embedded

        for column in columns:  # Store each column separately
            doc_text = f"{table}, Column: {column}"
            documents.append(doc_text)

    save_to_chroma(documents)

def save_to_chroma(documents):
    """Saves schema documents (table + column pairs) to ChromaDB."""
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)  # Clear existing database

    embedding_function = get_azure_embedding_function()

    db = Chroma.from_texts(documents, embedding_function, persist_directory=CHROMA_PATH)
    db.persist()
    print(f"✅ Saved {len(documents)} schema entries (table + column) to {CHROMA_PATH} using Azure OpenAI Embeddings.")

if __name__ == "__main__":
    generate_data_store()