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

# ✅ Define Table Relationships (Dimension tables linked to Fact tables)
TABLE_RELATIONSHIPS = {
    "FactInternetSales": {
        "DimCustomer": "CustomerKey",
        "DimDate": {"fact_column": "OrderDate", "dim_column": "Date"},
        "DimProduct": "ProductKey"
    },
    "FactResellerSales": {
        "DimDate": {"fact_column": "OrderDate", "dim_column": "Date"}
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

def search_schema(query_text, top_k=5, min_score=0.5):
    """Search ChromaDB for relevant schema (fact table + columns, then related dim tables)."""
    embedding_function = get_azure_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    print(f"\n🔍 Searching for: {query_text}\n")

    # ✅ Step 1: Perform similarity search
    results = db.similarity_search_with_relevance_scores(query_text, k=top_k)

    if not results:
        return "❌ No relevant schema found."

    # ✅ Step 2: Extract the highest-ranked fact table
    fact_table = None
    fact_columns = []
    table_scores = {}

    for doc, score in results:
        if score >= min_score:
            table_column_pair = doc.page_content.replace("Table: ", "").split(", Column: ")
            if len(table_column_pair) == 2:
                table, column = table_column_pair
                table_scores[table] = max(table_scores.get(table, 0), score)  # Track the highest score per table

    # ✅ Select the top fact table
    sorted_tables = sorted(table_scores, key=table_scores.get, reverse=True)
    for table in sorted_tables:
        if table.startswith("Fact"):  # Prioritize fact tables
            fact_table = table
            break

    if not fact_table:
        return "⚠️ No relevant fact table found."

    # ✅ Retrieve all columns for the selected fact table
    for doc, score in results:
        if score >= min_score and doc.page_content.startswith(fact_table):
            _, column = doc.page_content.split(", Column: ")
            fact_columns.append(column)

    # ✅ Step 3: Retrieve related dimension tables with key columns
    related_tables = {}
    # ✅ Step 3: Retrieve related dimension tables with key columns
    related_tables = {}
    if fact_table in TABLE_RELATIONSHIPS:
        for dim_table, mapping in TABLE_RELATIONSHIPS[fact_table].items():
            if isinstance(mapping, dict):  # If it's a dictionary, it's a mapped field
                fact_column = mapping["fact_column"]
                dim_column = mapping["dim_column"]
                related_tables[dim_table] = [f"{fact_column} → {dim_column}"]  # Make the relationship explicit

            else:
                related_tables[dim_table] = [mapping]  # Normal key relationships


    # ✅ Step 4: Format output for OpenAI (Avoid NULL Issues)
    formatted_schema = f"Fact Table:\n- {fact_table}: {', '.join(fact_columns)}\n\nRelated Dimension Tables:\n"
    for table, columns in related_tables.items():
        if isinstance(columns, dict):
            formatted_schema += f"- {table}: {', '.join(columns.values())}\n"
        else:
            formatted_schema += f"- {table}: {', '.join(columns)}\n"

    return formatted_schema


if __name__ == "__main__":
    query = input("🔍 Enter your schema-related query: ")
    print(search_schema(query))
