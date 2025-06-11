from openai import OpenAI
import shelve
from dotenv import load_dotenv
import os
import time
import logging
from flask import current_app
from app.services.knowledge_base import knowledge_base
import json

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

client = OpenAI(
    api_key=OPENAI_API_KEY,
    default_headers={"OpenAI-Beta": "assistants=v2"}
)

# Thread storage file path
THREAD_DB_PATH = "threads.db"


def upload_file(file_path):
    """
    Upload a file with an "assistants" purpose
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, "rb") as file:
            uploaded_file = client.files.create(
                file=file, 
                purpose="assistants"
            )
        logging.info(f"File uploaded successfully: {uploaded_file.id}")
        return uploaded_file
    except Exception as e:
        logging.error(f"Error uploading file: {str(e)}")
        raise


def create_assistant(file_ids=None):
    """
    Create a new OpenAI Assistant with specific instructions.
    """
    try:
        assistant_config = {
            "name": "infobot",
            "instructions": """You are a specialized AI assistant for Infobot Technologies. Your role is strictly limited to:

1. Answering questions about Infobot Technologies' services and products
2. Providing information about our business hours, location, and contact details
3. Handling basic customer service inquiries
4. Explaining our service offerings and pricing

You must:
1. ONLY use information provided in the knowledge base
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
            "model": "gpt-4-turbo-preview"
        }
        
        # Add file IDs if provided
        if file_ids:
            assistant_config["file_ids"] = file_ids
        
        assistant = client.beta.assistants.create(**assistant_config)
        logging.info(f"Assistant created successfully: {assistant.id}")
        return assistant
    except Exception as e:
        logging.error(f"Error creating assistant: {str(e)}")
        raise


def get_or_create_thread(user_id):
    """
    Get an existing thread for a user or create a new one.
    """
    try:
        # Check if thread exists in storage
        thread_id = check_if_thread_exists(user_id)
        if thread_id:
            try:
                thread = client.beta.threads.retrieve(thread_id)
                return thread
            except Exception as e:
                logging.warning(f"Could not retrieve thread {thread_id}: {str(e)}")
                # If thread doesn't exist on OpenAI side, remove from storage and create new
                remove_thread(user_id)
        
        # Create new thread if none exists
        thread = client.beta.threads.create()
        store_thread(user_id, thread.id)
        logging.info(f"New thread created for user {user_id}: {thread.id}")
        return thread
    except Exception as e:
        logging.error(f"Error in get_or_create_thread: {str(e)}")
        raise


def check_if_thread_exists(user_id):
    """
    Check if a thread exists for the given user ID.
    """
    try:
        with shelve.open(THREAD_DB_PATH) as shelf:
            return shelf.get(str(user_id))
    except Exception as e:
        logging.error(f"Error checking thread existence: {str(e)}")
        return None


def store_thread(user_id, thread_id):
    """
    Store the thread ID for a user.
    """
    try:
        with shelve.open(THREAD_DB_PATH) as shelf:
            shelf[str(user_id)] = thread_id
        logging.info(f"Thread {thread_id} stored for user {user_id}")
    except Exception as e:
        logging.error(f"Error storing thread: {str(e)}")


def remove_thread(user_id):
    """
    Remove thread ID for a user from storage.
    """
    try:
        with shelve.open(THREAD_DB_PATH) as shelf:
            if str(user_id) in shelf:
                del shelf[str(user_id)]
                logging.info(f"Thread removed for user {user_id}")
    except Exception as e:
        logging.error(f"Error removing thread: {str(e)}")


def generate_response(message, user_id, user_name=None):
    """
    Generate a response using OpenAI's Assistant API.
    """
    try:
        # Get or create thread for this user
        thread = get_or_create_thread(user_id)
        
        # Add user message to thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message
        )
        
        # Get assistant ID from environment variable
        assistant_id = OPENAI_ASSISTANT_ID
        if not assistant_id:
            raise ValueError("OPENAI_ASSISTANT_ID not found in environment variables")
        
        # Log assistant details
        try:
            assistant = client.beta.assistants.retrieve(assistant_id)
            logging.info(f"Using assistant: {assistant.name} (ID: {assistant.id})")
            logging.info(f"Assistant model: {assistant.model}")
            logging.info(f"Assistant instructions: {assistant.instructions[:200]}...")
        except Exception as e:
            logging.error(f"Error retrieving assistant details: {str(e)}")
        
        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        
        # Wait for the run to complete with timeout
        max_wait_time = 60  # 60 seconds timeout
        wait_time = 0
        
        while wait_time < max_wait_time:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            
            if run_status.status == 'completed':
                break
            elif run_status.status in ['failed', 'cancelled', 'expired']:
                logging.error(f"Run failed with status: {run_status.status}")
                return "I apologize, but I encountered an error while processing your request."
            elif run_status.status == 'requires_action':
                logging.info("Run requires action - function calls needed")
                
            time.sleep(1)
            wait_time += 1
        
        if wait_time >= max_wait_time:
            logging.error("Run timed out")
            return "I apologize, but the request is taking too long to process. Please try again."
        
        # Get the latest message from the assistant
        messages = client.beta.threads.messages.list(
            thread_id=thread.id,
            order='desc',
            limit=1
        )
        
        if messages.data and messages.data[0].content:
            response = messages.data[0].content[0].text.value
            logging.info(f"Generated response for user {user_id}: {response[:100]}...")
            return response
            
        return "I apologize, but I couldn't generate a response at this time."
        
    except Exception as e:
        logging.error(f"Error generating response for user {user_id}: {str(e)}")
        return "I apologize, but I encountered an error while processing your request."


def get_thread_messages(user_id, limit=10):
    """
    Get conversation history for a user.
    """
    try:
        thread_id = check_if_thread_exists(user_id)
        if not thread_id:
            return []
        
        messages = client.beta.threads.messages.list(
            thread_id=thread_id,
            order='desc',
            limit=limit
        )
        
        return messages.data
    except Exception as e:
        logging.error(f"Error getting thread messages: {str(e)}")
        return []


def clear_user_thread(user_id):
    """
    Clear the thread for a user (start fresh conversation).
    """
    try:
        remove_thread(user_id)
        logging.info(f"Thread cleared for user {user_id}")
        return True
    except Exception as e:
        logging.error(f"Error clearing thread for user {user_id}: {str(e)}")
        return False


def create_new_assistant():
    """
    Create a new assistant with the latest instructions and return its ID.
    """
    try:
        assistant = create_assistant()
        logging.info(f"Created new assistant with ID: {assistant.id}")
        logging.info("Please update your OPENAI_ASSISTANT_ID environment variable with this ID")
        return assistant.id
    except Exception as e:
        logging.error(f"Error creating new assistant: {str(e)}")
        raise