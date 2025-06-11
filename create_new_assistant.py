from openai import OpenAI
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_new_assistant():
    """Create a new assistant with the correct configuration"""
    try:
        # Create the assistant
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
            tools=[{"type": "file_search"}]
        )
        
        print(f"\nNew assistant created successfully!")
        print(f"Assistant ID: {assistant.id}")
        print(f"Name: {assistant.name}")
        print(f"Model: {assistant.model}")
        print(f"Tools: {assistant.tools}")
        
        print("\nPlease update your .env file with:")
        print(f"OPENAI_ASSISTANT_ID={assistant.id}")
        
        print("\nNext steps:")
        print("1. Go to the OpenAI Assistants dashboard")
        print("2. Select this new assistant")
        print("3. Upload your 'infobot information.pdf' file")
        print("4. Make sure the file is attached and the tool is set to 'file_search'")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    create_new_assistant() 