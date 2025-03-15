import streamlit as st
from query_data import search_schema  # Import function to retrieve relevant schema
from azure_openai import get_completion_from_messages  # Import function to call Azure OpenAI
from xmla import execute_dax_query  # Import function to run DAX queries
import json
import base64

# ✅ Set Streamlit page settings
st.set_page_config(page_title="BI Bot", page_icon="🤖", layout="wide")

# ✅ Function to load external CSS
def load_css(file_name):
    """Loads CSS from an external file and applies it to the Streamlit app."""
    with open(file_name, "r", encoding="utf-8") as f:
        css_content = f.read()
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

# ✅ Load CSS
load_css("styles.css")

# ✅ Load the logo image and convert it to Base64
LOGO_PATH = "OdetMaimoniLogo.png"  # Ensure this file exists

def get_base64_of_image(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

image_base64 = get_base64_of_image(LOGO_PATH)

# ✅ Display the logo and title
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

# ✅ User Input
user_message = st.text_input("🔍 Enter your query:", placeholder="Example: Show me total sales by product")

if user_message:
    # ✅ Retrieve the most relevant schema using embeddings (Top 1 match)
    relevant_schema_results = search_schema(user_message)
    
    if "❌" in relevant_schema_results:
        st.warning("⚠️ No relevant schema found. Try rephrasing your query.")
    else:
        # ✅ Extract only the top match instead of the full schema list
        top_match = relevant_schema_results.split("\n\n---\n\n")[0]

        st.markdown("### 📄 Top Matching Schema:")
        st.text(top_match)

        # ✅ Format prompt for Azure OpenAI (GPT-4o)
        formatted_prompt = f"""
        You are an AI specialized in generating DAX (Data Analysis Expressions) queries based on the provided schema. Adhere to the following guidelines to ensure optimal performance and accuracy:

        ### General Guidelines:
        - Valid JSON Output: Always return the DAX query encapsulated within a JSON object as the value for the "query" key.
        - No Explanations: Provide only the JSON-formatted DAX query without additional commentary.

        ### DAX Best Practices:

        - When filtering, always use dimension tables (`DimTable`) instead of fact tables (`FactTable`) for example FILTER('FactInternetSales',YEAR('DimDate'[Date]) = 2011)

        - Begin every DAX query with the `EVALUATE` statement to execute the table expression.

        - Do not use `RELATED()` inside `FILTER()`. Instead, apply filters directly on the related dimension tables.

        - For grouped aggregations, prefer `SUMMARIZECOLUMNS()` over `SUMMARIZE()`.

        - When retrieving specific columns without grouping, use `SELECTCOLUMNS()`.

        - Use `DISTINCT()` and `VALUES()` appropriately to retrieve unique values and ensure accuracy.

        ### Schema
        {top_match}

        ### Example Query Format
        Respond in valid JSON:
        ```json
        {{
            "query": "EVALUATE SUMMARIZECOLUMNS('DimDate'[Date], \"Total Sales\", SUM('FactInternetSales'[SalesAmount]))"
        }}

        """

        # ✅ Get AI-generated DAX query
        try:
            response = get_completion_from_messages(formatted_prompt, user_message)
            cleaned_response = response.strip().lstrip("```json").rstrip("```").strip()

            # ✅ Parse and display the generated query
            try:
                json_response = json.loads(cleaned_response)
                dax_query = json_response.get('query', '❌ No valid query found.')

                st.markdown("### 🔹 Generated DAX Query")
                st.code(dax_query, language="sql")

                # ✅ Execute the DAX Query on XMLA
                st.markdown("### 🚀 Query Results")
                try:
                    dax_results = execute_dax_query(dax_query)
                    if dax_results is not None and not dax_results.empty:
                        st.dataframe(dax_results)  # Display query results in Streamlit
                    else:
                        st.write("No results returned from the DAX query.")
                except Exception as e:
                    st.error(f"⚠️ Error executing DAX query: {e}")

            except json.JSONDecodeError:
                 st.error(f"❌ JSON Parsing Error: {str(e)}")
                 st.text(f"Raw response:\n{cleaned_response}")  # Show the problematic response

        except Exception as e:
            st.error(f"❌ Error generating DAX query: {str(e)}")
