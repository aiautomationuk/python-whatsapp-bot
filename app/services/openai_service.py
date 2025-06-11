from openai import OpenAI
import shelve
from dotenv import load_dotenv
import os
import time
import logging
from flask import current_app

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
client = OpenAI(
    api_key=OPENAI_API_KEY,
    default_headers={"OpenAI-Beta": "assistants=v2"}
)


def upload_file(path):
    # Upload a file with an "assistants" purpose
    file = client.files.create(
        file=open("../../data/infobot knowledge.pdf", "rb"), purpose="assistants"
    )


def create_assistant(file):
    """
    You currently cannot set the temperature for Assistant via the API.
    """
    assistant = client.beta.assistants.create(
        name="infobot",
        instructions="You are a helpful and professional AI assistant for Infobot Technologies. Your primary goal is to provide accurate, concise, and helpful responses to user inquiries. Key Guidelines:
1. Always maintain a professional and friendly tone
2. Keep responses concise and to the point
3. If you're unsure about something, direct users to contact info@infobot.co.uk
4. Use bullet points for lists to improve readability
5. Include relevant links when appropriate
6. Always use English from the united kingdom.",
        tools=[{"type": "retrieval"}],
        model="gpt-4o",
        file_ids=[file.id],
    )
    return assistant


def get_or_create_thread(user_id):
    """
    Get an existing thread for a user or create a new one.
    """
    try:
        # Check if thread exists in storage
        thread_id = check_if_thread_exists(user_id)
        if thread_id:
            return client.beta.threads.retrieve(thread_id)
        
        # Create new thread if none exists
        thread = client.beta.threads.create()
        store_thread(user_id, thread.id)
        return thread
    except Exception as e:
        logging.error(f"Error in get_or_create_thread: {str(e)}")
        raise


def check_if_thread_exists(user_id):
    """
    Check if a thread exists for the given user ID.
    """
    # TODO: Implement thread storage and retrieval
    return None


def store_thread(user_id, thread_id):
    """
    Store the thread ID for a user.
    """
    # TODO: Implement thread storage
    pass


def run_assistant(thread, name):
    # Retrieve the Assistant
    assistant = client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    # Wait for completion
    while run.status != "completed":
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Retrieve the Messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value
    logging.info(f"Generated message: {new_message}")
    return new_message


def generate_response(message, user_id, user_name):
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
        
        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=current_app.config["OPENAI_ASSISTANT_ID"]
        )
        
        # Wait for the run to complete
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == 'completed':
                break
            elif run_status.status in ['failed', 'cancelled', 'expired']:
                raise Exception(f"Run failed with status: {run_status.status}")
            time.sleep(1)
        
        # Get the latest message from the assistant
        messages = client.beta.threads.messages.list(
            thread_id=thread.id,
            order='desc',
            limit=1
        )
        
        if messages.data and messages.data[0].content:
            return messages.data[0].content[0].text.value
        return "I apologize, but I couldn't generate a response at this time."
        
    except Exception as e:
        logging.error(f"Error generating response: {str(e)}")
        return "I apologize, but I encountered an error while processing your request."
