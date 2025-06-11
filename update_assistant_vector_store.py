from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
vector_store_id = "vs_68495a806e9c8191838cccc8c2ba66a3"

if not assistant_id:
    print("Error: OPENAI_ASSISTANT_ID not found in environment variables")
    exit(1)

assistant = client.beta.assistants.update(
    assistant_id=assistant_id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}}
)

print(f"Assistant updated! Now using vector store: {vector_store_id}") 