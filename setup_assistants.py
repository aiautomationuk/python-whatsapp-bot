#!/usr/bin/env python3
"""
Setup script to create multiple OpenAI assistants for different WhatsApp numbers
Run this script once to create your assistants, then update app.py with the returned IDs
"""

from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=OPEN_AI_API_KEY)


def create_assistant(name, instructions, file_path=None, model="gpt-4-turbo-preview"):
    """
    Create a new assistant with optional file upload
    """
    try:
        tools = []
        file_ids = []
        
        if file_path and os.path.exists(file_path):
            print(f"Uploading file: {file_path}")
            file = client.files.create(
                file=open(file_path, "rb"), 
                purpose="assistants"
            )
            file_ids = [file.id]
            tools = [{"type": "file_search"}]
            print(f"File uploaded with ID: {file.id}")
        
        print(f"Creating assistant: {name}")
        assistant = client.beta.assistants.create(
            name=name,
            instructions=instructions,
            tools=tools,
            model=model,
            file_ids=file_ids if file_ids else None,
        )
        
        print(f"✅ Created assistant: {assistant.id}")
        return assistant
        
    except Exception as e:
        print(f"❌ Error creating assistant {name}: {str(e)}")
        return None


def setup_all_assistants():
    """
    Create all your different assistants
    """
    assistants = {}
    
    # Assistant 1: AirBnb Support (with PDF file)
    print("\n" + "="*50)
    print("Creating AirBnb Assistant...")
    airbnb_assistant = create_assistant(
        name="WhatsApp AirBnb Assistant",
        instructions="""You're a helpful WhatsApp assistant that can assist guests staying in our Paris AirBnb. 
        Use your knowledge base to best respond to customer queries. If you don't know the answer, 
        say simply that you cannot help with the question and advise to contact the host directly. 
        Be friendly and funny. Keep responses concise for WhatsApp.""",
        file_path="data/airbnb-faq.pdf"  # Update this path to your actual file
    )
    if airbnb_assistant:
        assistants["airbnb"] = airbnb_assistant.id

    # Assistant 2: Customer Support
    print("\n" + "="*50)
    print("Creating Customer Support Assistant...")
    support_assistant = create_assistant(
        name="Customer Support Assistant",
        instructions="""You're a professional customer support assistant. Help customers with their inquiries, 
        be polite, helpful, and efficient. If you cannot resolve an issue, escalate to human support. 
        Keep responses brief and actionable for WhatsApp messaging."""
    )
    if support_assistant:
        assistants["support"] = support_assistant.id

    # Assistant 3: Sales Assistant
    print("\n" + "="*50)
    print("Creating Sales Assistant...")
    sales_assistant = create_assistant(
        name="Sales Assistant",
        instructions="""You're a friendly sales assistant. Help potential customers understand our products and services. 
        Be enthusiastic but not pushy. Guide them through the sales process naturally. 
        Ask qualifying questions and provide clear next steps. Keep messages concise for WhatsApp."""
    )
    if sales_assistant:
        assistants["sales"] = sales_assistant.id

    # Assistant 4: General Chatbot
    print("\n" + "="*50)
    print("Creating General Chatbot Assistant...")
    general_assistant = create_assistant(
        name="General Chatbot Assistant",
        instructions="""You're a helpful general purpose assistant. Answer questions, provide information, 
        and assist users with various topics. Be friendly, informative, and concise. 
        Perfect for WhatsApp conversations."""
    )
    if general_assistant:
        assistants["general"] = general_assistant.id

    return assistants


def generate_config_code(assistants):
    """
    Generate the configuration code to paste into app.py
    """
    print("\n" + "="*70)
    print("🎉 SETUP COMPLETE!")
    print("="*70)
    
    print("\n📋 ASSISTANT IDS CREATED:")
    for name, assistant_id in assistants.items():
        print(f"  {name.upper()}: {assistant_id}")
    
    print("\n📝 UPDATE YOUR app.py FILE:")
    print("Replace the WHATSAPP_TO_ASSISTANT dictionary with:")
    print("\n" + "-"*50)
    
    config_code = """WHATSAPP_TO_ASSISTANT = {
    # Replace these phone numbers with your actual WhatsApp business numbers
    # Remove country code prefix, keep only digits"""
    
    # Example mappings - user needs to update with real numbers
    example_numbers = [
        "447464177761",  # UK number from their code
        "447510698847",  # Another UK number from their code
        "1234567890",    # Example US number
        "9876543210"     # Another example number
    ]
    
    assistant_list = list(assistants.values())
    
    for i, number in enumerate(example_numbers[:len(assistant_list)]):
        assistant_id = assistant_list[i]
        assistant_name = list(assistants.keys())[i]
        config_code += f'\n    "{number}": "{assistant_id}",  # {assistant_name.title()} Assistant'
    
    config_code += "\n}"
    
    print(config_code)
    print("-"*50)
    
    print("\n🔧 ALSO UPDATE:")
    if assistants:
        first_assistant = list(assistants.values())[0]
        print(f'DEFAULT_ASSISTANT_ID = "{first_assistant}"')
    
    print("\n💡 NEXT STEPS:")
    print("1. Copy the configuration above into your app.py file")
    print("2. Replace the example phone numbers with your actual WhatsApp Business numbers")
    print("3. Make sure your phone numbers are in the format shown (digits only, no + or spaces)")
    print("4. Restart your Flask application")
    print("5. Test by sending messages to your WhatsApp numbers")
    
    # Save to file for reference
    with open("assistant_config.json", "w") as f:
        json.dump(assistants, f, indent=2)
    print(f"\n💾 Assistant IDs saved to assistant_config.json for reference")


def main():
    print("🚀 Setting up multiple OpenAI Assistants for WhatsApp...")
    print("This will create different assistants for different use cases.")
    
    # Check if API key is available
    if not OPEN_AI_API_KEY:
        print("❌ Error: OPEN_AI_API_KEY not found in environment variables")
        print("Please add your OpenAI API key to your .env file")
        return
    
    print(f"✅ OpenAI API key found")
    
    # Create all assistants
    assistants = setup_all_assistants()
    
    if not assistants:
        print("\n❌ No assistants were created successfully")
        return
    
    # Generate configuration code
    generate_config_code(assistants)


if __name__ == "__main__":
    main()