import os
from openai import OpenAI
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def update_instructions():
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        assistant_id = os.getenv('OPENAI_ASSISTANT_ID')
        
        if not assistant_id:
            raise ValueError("OPENAI_ASSISTANT_ID not found in environment variables")
            
        # Update the assistant with strict instructions
        updated_assistant = client.beta.assistants.update(
            assistant_id=assistant_id,
            instructions="""You are a specialized AI assistant for Infobot Technologies. Your responses MUST follow these rules:

1. ONLY use information from the attached knowledge base file (infobot_info.txt)
2. NEVER guess or make up information
3. If the information is not in the file, respond with: "I don't have that information. Please contact info@infobot.co.uk for assistance."
4. Do not add any additional details or context that is not explicitly stated in the file
5. Keep responses concise and to the point
6. If asked about anything not related to Infobot Technologies, politely explain that you can only assist with questions about Infobot Technologies

Remember: Your primary source of information is the attached file. Do not use any other knowledge or make assumptions."""
        )
        
        logger.info(f"Assistant instructions updated successfully!")
        logger.info(f"Assistant ID: {updated_assistant.id}")
        logger.info(f"Assistant name: {updated_assistant.name}")
        logger.info(f"Assistant model: {updated_assistant.model}")
        logger.info(f"Assistant tools: {updated_assistant.tools}")
        
    except Exception as e:
        logger.error(f"Error updating assistant instructions: {str(e)}")
        raise

if __name__ == "__main__":
    update_instructions() 