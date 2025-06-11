from openai import OpenAI
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def upload_company_info():
    """Upload company information file to OpenAI"""
    try:
        with open("company_info.txt", "rb") as file:
            uploaded_file = client.files.create(
                file=file,
                purpose="assistants"
            )
        logging.info(f"File uploaded successfully: {uploaded_file.id}")
        return uploaded_file.id
    except Exception as e:
        logging.error(f"Error uploading file: {str(e)}")
        raise

def create_assistant_with_knowledge(file_id):
    """Create a new assistant with the knowledge base file (OpenAI v2 pattern)"""
    try:
        assistant = client.beta.assistants.create(
            name="infobot",
            instructions="""You are a specialized AI assistant for Infobot Technologies. Your role is strictly limited to:

1. Answering questions about Infobot Technologies' services and products
2. Providing information about our business hours, location, and contact details
3. Handling basic customer service inquiries
4. Explaining our service offerings and pricing

You must:
1. ONLY use information from the provided knowledge base file
2. If you don't know something or if the information isn't in the knowledge base, say "I don't have that information in my knowledge base. Please contact info@infobot.co.uk for more details."
3. Never make up or guess information
4. Always be honest about what you know and don't know

You must NOT:
1. Write or debug code
2. Answer general questions unrelated to Infobot Technologies
3. Provide technical support for non-Infobot products
4. Generate creative content or stories
5. Answer questions about other companies or services
6. Make up information that isn't in the knowledge base

If asked about anything outside these boundaries, politely explain that you can only assist with questions about Infobot Technologies and our services.

For any technical or complex inquiries, direct the user to contact our support team.""",
            model="gpt-4-turbo-preview",
            tools=[{"type": "retrieval"}]
        )
        logging.info(f"Assistant created successfully: {assistant.id}")
        # Attach the file to the assistant
        client.beta.assistants.files.create(
            assistant_id=assistant.id,
            file_id=file_id
        )
        logging.info(f"File {file_id} attached to assistant {assistant.id}")
        return assistant.id
    except Exception as e:
        logging.error(f"Error creating assistant: {str(e)}")
        raise

def main():
    try:
        # Upload company information
        print("Uploading company information...")
        file_id = upload_company_info()
        
        # Create new assistant with the knowledge base
        print("\nCreating new assistant...")
        assistant_id = create_assistant_with_knowledge(file_id)
        
        print("\n" + "="*50)
        print(f"NEW ASSISTANT ID: {assistant_id}")
        print("="*50)
        print("\nPlease update your OPENAI_ASSISTANT_ID environment variable with this ID")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 