from openai import OpenAI
import shelve
from dotenv import load_dotenv
import os
import time

load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=OPEN_AI_API_KEY)


# --------------------------------------------------------------
# Upload file
# --------------------------------------------------------------
def upload_file(path):
    # Upload a file with an "assistants" purpose
    file = client.files.create(file=open(path, "rb"), purpose="assistants")
    return file


# --------------------------------------------------------------
# Create assistant function (you can run this separately to create assistants)
# --------------------------------------------------------------
def create_assistant(name, instructions, file_path=None):
    """
    Create a new assistant with optional file upload
    """
    tools = []
    file_ids = []
    
    if file_path and os.path.exists(file_path):
        file = upload_file(file_path)
        file_ids = [file.id]
        tools = [{"type": "file_search"}]  # Updated for newer API
    
    assistant = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        tools=tools,
        model="gpt-4-turbo-preview",
        file_ids=file_ids,
    )
    
    print(f"Created assistant: {assistant.id}")
    return assistant


# --------------------------------------------------------------
# Thread management
# --------------------------------------------------------------
def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)


def store_thread(wa_id, thread_id):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id


# --------------------------------------------------------------
# Generate response - UPDATED to handle assistant_id properly
# --------------------------------------------------------------
def generate_response(message_body, wa_id, name, assistant_id=None):
    # Use default assistant if none provided
    if assistant_id is None:
        assistant_id = os.getenv("DEFAULT_ASSISTANT_ID", "asst_7Wx2nQwoPWSf710jrdWTDlfE")
    
    # Check if there is already a thread_id for the wa_id
    thread_id = check_if_thread_exists(wa_id)

    # If a thread doesn't exist, create one and store it
    if thread_id is None:
        print(f"Creating new thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.create()
        store_thread(wa_id, thread.id)
        thread_id = thread.id
    else:
        print(f"Retrieving existing thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.retrieve(thread_id)

    # Add message to thread
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_body,
    )

    # Run the assistant and get the new message
    new_message = run_assistant(thread, assistant_id)
    print(f"To {name}:", new_message)
    return new_message


# --------------------------------------------------------------
# Run assistant - UPDATED to use the passed assistant_id
# --------------------------------------------------------------
def run_assistant(thread, assistant_id):
    try:
        # Retrieve the Assistant
        assistant = client.beta.assistants.retrieve(assistant_id)

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        # Wait for completion with timeout
        max_wait_time = 60  # 60 seconds timeout
        start_time = time.time()
        
        while run.status not in ["completed", "failed", "cancelled", "expired"]:
            if time.time() - start_time > max_wait_time:
                print("Assistant run timed out")
                return "I'm sorry, I'm taking too long to respond. Please try again."
            
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            print(f"Run status: {run.status}")

        if run.status == "completed":
            # Retrieve the Messages
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            new_message = messages.data[0].content[0].text.value
            print(f"Generated message: {new_message}")
            return new_message
        else:
            print(f"Assistant run failed with status: {run.status}")
            return "I'm sorry, I encountered an error. Please try again."
            
    except Exception as e:
        print(f"Error running assistant: {str(e)}")
        return "I'm sorry, I encountered an error. Please try again."


# --------------------------------------------------------------
# Helper function to create multiple assistants
# --------------------------------------------------------------
def setup_assistants():
    """
    Run this function once to create your different assistants
    """
    
    # Assistant 1: AirBnb Support
    airbnb_assistant = create_assistant(
        name="WhatsApp AirBnb Assistant",
        instructions="You're a helpful WhatsApp assistant that can assist guests staying in our Paris AirBnb. Use your knowledge base to best respond to customer queries. If you don't know the answer, say simply that you cannot help with the question and advise to contact the host directly. Be friendly and funny.",
        file_path="../data/airbnb-faq.pdf"  # Update path as needed
    )
    
    # Assistant 2: Customer Support
    support_assistant = create_assistant(
        name="Customer Support Assistant",
        instructions="You're a professional customer support assistant. Help customers with their inquiries, be polite, helpful, and efficient. If you cannot resolve an issue, escalate to human support.",
        file_path=None
    )
    
    # Assistant 3: Sales Assistant
    sales_assistant = create_assistant(
        name="Sales Assistant",
        instructions="You're a friendly sales assistant. Help potential customers understand our products and services. Be enthusiastic but not pushy. Guide them through the sales process naturally.",
        file_path=None
    )
    
    print("\nAssistant IDs created:")
    print(f"AirBnb Assistant: {airbnb_assistant.id}")
    print(f"Support Assistant: {support_assistant.id}")
    print(f"Sales Assistant: {sales_assistant.id}")
    
    return {
        "airbnb": airbnb_assistant.id,
        "support": support_assistant.id,
        "sales": sales_assistant.id
    }


# Uncomment and run this once to create your assistants
# if __name__ == "__main__":
#     assistants = setup_assistants()