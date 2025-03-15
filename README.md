# BI Bot: AI-Powered DAX Query Generator

This project integrates Azure OpenAI, ChromaDB, and Streamlit to generate DAX (Data Analysis Expressions) queries based on natural language input. Users can describe their data needs in plain English, and the system will retrieve the most relevant schema and generate an appropriate DAX query to be executed against a Power BI XMLA endpoint.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Contributing](#contributing)
- [License](#license)

## Features

- Natural Language to DAX: Converts user queries into DAX using Azure OpenAI (GPT-4o).
- Schema-Based Query Generation: Dynamically selects the most relevant fact and dimension tables using ChromaDB.
- Streamlit UI: Provides an intuitive web interface for users to input their queries.
- Power BI XMLA Execution: Runs the generated DAX query against a Power BI dataset and returns the results.

## Prerequisites

- Python 3.8 or above
- An Azure OpenAI API key
- A Power BI dataset that supports XMLA queries
- Virtual Environment (recommended)

## Installation

1. Clone the Repository:
    ```bash
    git clone https://github.com/odetma/BIBot.git
    cd bi-bot
    ```

2. Set up a Virtual Environment (optional but recommended):
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3. Install Dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up Environment Variables:

   Create a `.env` file in the root directory and add the following credentials:
   ```
   AZURE_OPENAI_API_KEY=your-api-key
   AZURE_OPENAI_API_BASE=your-api-endpoint
   AZURE_OPENAI_API_VERSION=2023-06-01-preview
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your-deployment-name
   ```

## Usage

1. Run the Streamlit App:
    ```bash
    python -m streamlit run main_app_streamlit.py
    ```

2. Open the displayed URL (usually `http://localhost:8501`).

3. Enter your query in natural language, such as:
   ```
   Show me total sales by product.
   ```

4. The app will:
   - Retrieve the most relevant schema using ChromaDB embeddings.
   - Generate a DAX query using Azure OpenAI.
   - Execute the query against the Power BI XMLA endpoint.
   - Display the results in a table.

## How It Works

### 1. Schema Retrieval (ChromaDB)
   - The system stores Power BI table and column metadata in ChromaDB.
   - When a user enters a query, the system retrieves the most relevant fact and dimension tables based on vector similarity search.

### 2. DAX Query Generation (Azure OpenAI)
   - The system formats the schema and sends it to GPT-4o along with the user query.
   - The AI generates a DAX query in JSON format.

### 3. Query Execution (Power BI XMLA)
   - The generated DAX query is executed against a Power BI dataset using ADOMD.NET.
   - Results are displayed in the Streamlit app.

## Contributing

Feel free to fork this repository, create a feature branch, and submit a pull request if you have improvements or fixes.

## License

This project is open source and licensed under the MIT license.
