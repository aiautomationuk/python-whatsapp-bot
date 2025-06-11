from openai import OpenAI
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def check_assistant():
    """Check assistant configuration and attached files"""
    try:
        assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
        if not assistant_id:
            print("Error: OPENAI_ASSISTANT_ID not found in environment variables")
            return

        # Get assistant details
        assistant = client.beta.assistants.retrieve(assistant_id)
        print("\nAssistant Configuration:")
        print("=" * 50)
        print(f"Name: {assistant.name}")
        print(f"ID: {assistant.id}")
        print(f"Model: {assistant.model}")
        print(f"Tools: {assistant.tools}")
        print("\nInstructions:")
        print("-" * 50)
        print(assistant.instructions)
        
        # Get attached files
        files = client.beta.assistants.files.list(assistant_id=assistant_id)
        print("\nAttached Files:")
        print("=" * 50)
        if files.data:
            for file in files.data:
                print(f"File ID: {file.id}")
                # Get file details
                file_details = client.files.retrieve(file.id)
                print(f"Filename: {file_details.filename}")
                print(f"Purpose: {file_details.purpose}")
                print("-" * 30)
        else:
            print("No files attached to the assistant!")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    check_assistant() 