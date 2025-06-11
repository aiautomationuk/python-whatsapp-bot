import os
from openai import OpenAI
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def check_assistant():
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        assistant_id = os.getenv('OPENAI_ASSISTANT_ID')
        
        if not assistant_id:
            raise ValueError("OPENAI_ASSISTANT_ID not found in environment variables")
            
        # Get assistant details
        assistant = client.beta.assistants.retrieve(assistant_id)
        
        print("\nAssistant Configuration:")
        print("-" * 50)
        print(f"Assistant ID: {assistant.id}")
        print(f"Name: {assistant.name}")
        print(f"Model: {assistant.model}")
        print(f"Instructions: {assistant.instructions}")
        print("\nTools:")
        for tool in assistant.tools:
            print(f"- {tool.type}")
            if hasattr(tool, 'file_search'):
                print(f"  Vector Store IDs: {tool.file_search.vector_store_ids}")
        
        # Check if the assistant is using the correct vector store
        vector_store_id = "vs_68495a806e9c8191838cccc8c2ba66a3"
        is_using_correct_store = False
        
        for tool in assistant.tools:
            if hasattr(tool, 'file_search') and hasattr(tool.file_search, 'vector_store_ids'):
                if vector_store_id in tool.file_search.vector_store_ids:
                    is_using_correct_store = True
                    break
        
        print("\nVector Store Status:")
        print("-" * 50)
        if is_using_correct_store:
            print("✅ Assistant is using the correct vector store")
        else:
            print("❌ Assistant is NOT using the correct vector store")
            print(f"Expected vector store ID: {vector_store_id}")
        
    except Exception as e:
        logger.error(f"Error checking assistant: {str(e)}")
        raise

if __name__ == "__main__":
    check_assistant() 