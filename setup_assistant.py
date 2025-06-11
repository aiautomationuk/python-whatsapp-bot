from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.openai.com/v2")

def create_assistant():
    """
    Create a new OpenAI Assistant with custom instructions and tools.
    """
    assistant = client.beta.assistants.create(
        name="WhatsApp AI Assistant",
        instructions="""You are a helpful WhatsApp assistant that can engage in natural conversations with users. 
        Your responses should be:
        1. Conversational and friendly
        2. Concise and to the point
        3. Helpful and informative
        4. Professional but warm
        
        If you don't know the answer to something, be honest and say so.
        Always maintain a helpful and positive tone.""",
        tools=[{"type": "retrieval"}],
        model="gpt-4-1106-preview"
    )
    
    print(f"Created new assistant with ID: {assistant.id}")
    print("Please add this ID to your .env file as OPENAI_ASSISTANT_ID")
    return assistant

if __name__ == "__main__":
    create_assistant() 