import streamlit as st
from query_data import search_schema  # Retrieve relevant schema based on user query
from azure_openai import get_completion_from_messages  # Call Azure OpenAI for generating responses
from xmla import execute_dax_query  # Execute DAX queries via XMLA
import json
import base64

# Configure Streamlit page settings
st.set_page_config(page_title="BI Bot", page_icon="🤖", layout="wide")

# Load external CSS to style the Streamlit app
def load_css(file_name):
    """Loads CSS from an external file and applies it to the Streamlit app."""
    with open(file_name, "r", encoding="utf-8") as f:
        css_content = f.read()
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

# Apply external styles
load_css("styles.css")

# Convert logo image to Base64 for embedding in HTML
LOGO_PATH = "OdetMaimoniLogo.png"   # Ensure the file exists

def get_base64_of_image(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

image_base64 = get_base64_of_image(LOGO_PATH)

# Display logo and application title
st.markdown(
    f"""
    <div class="logo-container">
        <img src="data:image/png;base64,{image_base64}" alt="BI Bot Logo">
    </div>
    <p class="title">BI Bot</p>
    <p class="subtitle">Ask me questions about your data</p>
    """,
    unsafe_allow_html=True
)

# Input field for user queries
user_message = st.text_input("🔍 Enter your query:", placeholder="Example: Show me total sales by product")

if user_message:
   # Retrieve the most relevant schema based on embeddings
    relevant_schema_results = search_schema(user_message)
    
    if "❌" in relevant_schema_results:
        st.warning("⚠️ No relevant schema found. Try rephrasing your query.")
    else:
        # Extract only the top schema match
        top_match = relevant_schema_results.split("\n\n---\n\n")[0]

        st.markdown("### 📄 Top Matching Schema:")
        st.text(top_match)

        # Format prompt for Azure OpenAI to generate DAX queries
        formatted_prompt = f"""
        You are an AI specialized in generating accurate DAX (Data Analysis Expressions) queries based on the provided schema. Follow these guidelines:

        ### General Instructions
        - Output Format: Return only the DAX query within a JSON object as the value for the `"query"` key.
        - Schema Compliance: Use only tables and columns specified in the schema below.
        - No Additional Text: Do not include explanations or comments.

        ### DAX Query Guidelines
        - Aggregation: Use `SUMMARIZECOLUMNS()` for grouping and aggregating results.
        - Filtering: Apply filters using `CALCULATE()`; avoid using `FILTER()` inside `SUMMARIZECOLUMNS()`.
        - Context Management: Ensure proper context by filtering on dimension tables, not directly on fact tables.
        - Scalar Values: For scalar outputs, wrap calculations in `ROW()`.

        ### Schema
        {top_match}

        ### Example Output
        ```json
        {{
            "query": "EVALUATE SUMMARIZECOLUMNS('DimDate'[Year], \"Total Sales\", SUM('FactInternetSales'[SalesAmount]))"
        }}


        """

        # Generate the DAX query
        try:
            response = get_completion_from_messages(formatted_prompt, user_message)
            cleaned_response = response.strip().lstrip("```json").rstrip("```").strip()

           
            try:
                json_response = json.loads(cleaned_response)
                dax_query = json_response.get('query', '❌ No valid query found.')

                 # Display generated DAX query
                st.markdown("### 🔹 Generated DAX Query")
                st.code(dax_query, language="sql")

                # Execute the generated DAX query
                st.markdown("### 🚀 Query Results")
                try:
                    dax_results = execute_dax_query(dax_query)
                    if dax_results is not None and not dax_results.empty:
                        st.dataframe(dax_results)   # Display query results
                    else:
                        st.write("No results returned from the DAX query.")
                except Exception as e:
                    st.error(f"⚠️ Error executing DAX query: {e}")

            except json.JSONDecodeError:
                 st.error(f"❌ JSON Parsing Error: {str(e)}")
                 st.text(f"Raw response:\n{cleaned_response}")  # Show raw output for debugging

        except Exception as e:
            st.error(f"❌ Error generating DAX query: {str(e)}")
