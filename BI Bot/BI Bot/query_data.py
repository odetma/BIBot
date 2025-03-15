from langchain_community.vectorstores import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Retrieve Azure OpenAI API credentials
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_BASE = os.getenv("AZURE_OPENAI_API_BASE")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

CHROMA_PATH = "chroma"  # Path for ChromaDB storage

# Define relationships between fact and dimension tables
TABLE_RELATIONSHIPS = {
    "FactInternetSales": {
        "DimCustomer": "CustomerKey",
        "DimDate": {"fact_column": "OrderDate", "dim_column": "Date"},
        "DimProduct": "ProductKey"
    },
    "FactSurveyResponse": {
        "DimDate": "Date",
        "DimCustomer": "CustomerKey"
    }
}

def get_azure_embedding_function():
    """Returns an Azure OpenAI embedding function."""
    return AzureOpenAIEmbeddings(
        azure_endpoint=AZURE_OPENAI_API_BASE,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    )

def search_schema(query_text, top_k=10, min_score=0.5, max_columns=3):
    """Search ChromaDB for relevant schema (fact table + columns, then related dim tables and their attributes)."""
    embedding_function = get_azure_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    print(f"\n🔍 Searching for: {query_text}\n")

    # Perform similarity search based on embeddings
    results = db.similarity_search_with_relevance_scores(query_text, k=top_k)

    if not results:
        return "❌ No relevant schema found."

    # Identify the most relevant fact table and its columns
    fact_table = None
    fact_columns = []
    table_scores = {}

    for doc, score in results:
        if score >= min_score:
            table_column_pair = doc.page_content.replace("Table: ", "").split(", Column: ")
            if len(table_column_pair) == 2:
                table, column = table_column_pair
                table_scores[table] = max(table_scores.get(table, 0), score)  # Track highest score

    # Select the best-matching fact table based on the highest score
    sorted_tables = sorted(table_scores, key=table_scores.get, reverse=True)
    for table in sorted_tables:
        if table.startswith("Fact"):  # Prioritize fact tables
            fact_table = table
            break

    if not fact_table:
        return "⚠️ No relevant fact table found."

    # Extract relevant columns for the selected fact table
    fact_column_scores = {}
    for doc, score in results:
        if score >= min_score and doc.page_content.startswith(fact_table):
            _, column = doc.page_content.split(", Column: ")
            fact_column_scores[column] = score

    # Get the top N columns for the fact table
    fact_columns = sorted(fact_column_scores, key=fact_column_scores.get, reverse=True)[:max_columns]

    # Retrieve related dimension tables and key columns
    related_tables = {}
    dim_table_columns = {}  # Dictionary to store extracted columns for each dimension table

    if fact_table in TABLE_RELATIONSHIPS:
        for dim_table, mapping in TABLE_RELATIONSHIPS[fact_table].items():
            if isinstance(mapping, dict):  # If dictionary, map columns explicitly
                fact_column = mapping["fact_column"]
                dim_column = mapping["dim_column"]
                related_tables[dim_table] = [f"[{fact_table}]{fact_column} → [{dim_table}]{dim_column}"]
            else:
                related_tables[dim_table] = [mapping]

            # Ensure the dimension table has a list for attributes
            if dim_table not in dim_table_columns:
                dim_table_columns[dim_table] = {}

    # Retrieve **ALL** stored columns from related dimension tables
    stored_data = db.get(include=["documents"])  # Get all stored table-column pairs

    # Create a dictionary to store scores
    dim_column_scores = {table: {} for table in related_tables}

    for doc in stored_data["documents"]:
        table_column_pair = doc.replace("Table: ", "").split(", Column: ")
        if len(table_column_pair) == 2:
            stored_table, stored_column = table_column_pair
            if stored_table in related_tables:
                dim_column_scores[stored_table][stored_column] = 0  # Initialize with score 0

    # Update scores based on similarity search
    for doc, score in results:
        table_column_pair = doc.page_content.replace("Table: ", "").split(", Column: ")
        if len(table_column_pair) == 2:
            table, column = table_column_pair
            if table in dim_column_scores:
                dim_column_scores[table][column] = score  # Assign similarity score

    # Limit to top N columns per dimension table
    for table in dim_column_scores.keys():
        sorted_columns = sorted(dim_column_scores[table], key=dim_column_scores[table].get, reverse=True)
        dim_table_columns[table] = sorted_columns[:max_columns]

    # Format schema output
    formatted_schema = f"Fact Table:\n- {fact_table}: {', '.join(fact_columns)}\n\nRelated Dimension Tables:\n"
    for table, columns in related_tables.items():
        formatted_schema += f"- {table}: {', '.join(columns)}\n"
        if table in dim_table_columns:
            formatted_schema += f"  * Attributes: {', '.join(dim_table_columns[table])}\n"

    return formatted_schema

if __name__ == "__main__":
    query = input("🔍 Enter your schema-related query: ")
    print(search_schema(query))
