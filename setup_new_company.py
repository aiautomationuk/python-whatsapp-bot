import os
import json
import shutil
from datetime import datetime
from dotenv import load_dotenv
import openai
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_new_company(company_name, company_info_file, meta_token=None, meta_phone_id=None):
    """
    Set up a new company instance with its own configuration
    
    Args:
        company_name (str): Name of the company
        company_info_file (str): Path to the company's information file
        meta_token (str, optional): Meta Business API token
        meta_phone_id (str, optional): Meta Phone Number ID
    """
    try:
        # Create company directory
        company_dir = f"companies/{company_name.lower().replace(' ', '_')}"
        os.makedirs(company_dir, exist_ok=True)
        
        # Copy template files
        template_files = [
            'app',
            'start',
            'requirements.txt',
            'gunicorn.conf.py',
            'render.yaml'
        ]
        
        for file in template_files:
            if os.path.isdir(file):
                shutil.copytree(file, f"{company_dir}/{file}", dirs_exist_ok=True)
            else:
                shutil.copy2(file, f"{company_dir}/{file}")
        
        # Create company-specific .env file
        env_template = """
# OpenAI Configuration
OPENAI_API_KEY={openai_api_key}
OPENAI_ASSISTANT_ID={assistant_id}

# Meta WhatsApp Configuration
META_TOKEN={meta_token}
META_PHONE_ID={meta_phone_id}

# Company Configuration
COMPANY_NAME={company_name}
COMPANY_INFO_FILE={company_info_file}
"""
        
        # Create new assistant for the company
        client = openai.OpenAI()
        
        # Create assistant
        assistant = client.beta.assistants.create(
            name=f"{company_name} Assistant",
            instructions=f"""You are a customer service assistant for {company_name}. 
            You should only use information from the provided knowledge base file.
            If you don't know something, say "I don't have that information. Please contact {company_name} directly."
            Keep responses concise and professional.""",
            model="gpt-4-turbo-preview",
            tools=[{"type": "retrieval"}]
        )
        
        # Create vector store
        vector_store = client.beta.vector_stores.create(
            name=f"{company_name} Knowledge Base"
        )
        
        # Upload company info file
        with open(company_info_file, 'rb') as file:
            file_data = client.files.create(
                file=file,
                purpose='assistants'
            )
        
        # Update assistant with vector store
        client.beta.assistants.update(
            assistant_id=assistant.id,
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
        )
        
        # Write .env file
        with open(f"{company_dir}/.env", 'w') as f:
            f.write(env_template.format(
                openai_api_key=os.getenv('OPENAI_API_KEY'),
                assistant_id=assistant.id,
                meta_token=meta_token or os.getenv('META_TOKEN'),
                meta_phone_id=meta_phone_id or os.getenv('META_PHONE_ID'),
                company_name=company_name,
                company_info_file=company_info_file
            ))
        
        # Create setup instructions
        setup_instructions = f"""
# Setup Instructions for {company_name}

1. Environment Setup:
   - Navigate to {company_dir}
   - Copy .env.example to .env and fill in the values
   - Install dependencies: pip install -r requirements.txt

2. Meta WhatsApp Setup:
   - Create a Meta Business account if not already done
   - Set up WhatsApp Business API
   - Update META_TOKEN and META_PHONE_ID in .env

3. Deployment:
   - Update render.yaml with company-specific settings
   - Deploy to Render.com or your preferred platform

4. Testing:
   - Run test_assistant.py to verify assistant responses
   - Test WhatsApp integration using the provided phone number

For support, contact: support@infobot.tech
"""
        
        with open(f"{company_dir}/SETUP.md", 'w') as f:
            f.write(setup_instructions)
        
        logger.info(f"Successfully set up new company instance for {company_name}")
        logger.info(f"Company directory: {company_dir}")
        logger.info(f"Assistant ID: {assistant.id}")
        logger.info(f"Vector Store ID: {vector_store.id}")
        
        return {
            "company_dir": company_dir,
            "assistant_id": assistant.id,
            "vector_store_id": vector_store.id
        }
        
    except Exception as e:
        logger.error(f"Error setting up new company: {str(e)}")
        raise

if __name__ == "__main__":
    load_dotenv()
    
    # Example usage
    company_name = input("Enter company name: ")
    company_info_file = input("Enter path to company info file: ")
    meta_token = input("Enter Meta Business API token (optional): ") or None
    meta_phone_id = input("Enter Meta Phone Number ID (optional): ") or None
    
    setup_new_company(company_name, company_info_file, meta_token, meta_phone_id) 