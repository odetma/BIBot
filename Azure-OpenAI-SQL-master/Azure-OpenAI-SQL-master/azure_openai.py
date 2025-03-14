from openai import AzureOpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Azure OpenAI API
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_API_BASE")
)

def get_completion_from_messages(system_message, user_message, model="gpt-4o", temperature=0, max_tokens=500):
    """Calls Azure OpenAI's ChatGPT API and returns a response."""
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content

# Test the function
if __name__ == "__main__":
    system_message = "You are a helpful AI assistant."
    user_message = "Hello, what is the latest Power BI update?"
    print(get_completion_from_messages(system_message, user_message))
