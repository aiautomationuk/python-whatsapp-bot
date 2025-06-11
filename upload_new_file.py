import os
from openai import OpenAI
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def upload_and_update():
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        assistant_id = os.getenv('OPENAI_ASSISTANT_ID')
        
        if not assistant_id:
            raise ValueError("OPENAI_ASSISTANT_ID not found in environment variables")
            
        # Upload the new file
        with open("infobot_info.txt", "rb") as file:
            uploaded_file = client.files.create(
                file=file,
                purpose="assistants"
            )
        logger.info(f"File uploaded successfully with ID: {uploaded_file.id}")
        
        # Update the assistant with the new file
        updated_assistant = client.beta.assistants.update(
            assistant_id=assistant_id,
            file_ids=[uploaded_file.id]
        )
        
        logger.info(f"Assistant updated successfully!")
        logger.info(f"Assistant ID: {updated_assistant.id}")
        logger.info(f"Assistant name: {updated_assistant.name}")
        logger.info(f"Assistant model: {updated_assistant.model}")
        logger.info(f"Assistant tools: {updated_assistant.tools}")
        
    except Exception as e:
        logger.error(f"Error during upload and update: {str(e)}")
        raise

if __name__ == "__main__":
    upload_and_update() 