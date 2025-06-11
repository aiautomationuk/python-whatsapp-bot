from openai import OpenAI
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def test_assistant():
    """Test the assistant with a simple question"""
    try:
        # Get assistant ID from environment
        assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
        if not assistant_id:
            print("Error: OPENAI_ASSISTANT_ID not found in environment variables")
            return

        # Create a new thread
        thread = client.beta.threads.create()
        print(f"Created new thread: {thread.id}")

        # Add a test message
        message = "What is Infobot Technologies' phone number?"
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message
        )
        print(f"\nSent message: {message}")

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        print(f"Started run: {run.id}")

        # Wait for completion
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == 'completed':
                break
            elif run_status.status in ['failed', 'cancelled', 'expired']:
                print(f"Run failed with status: {run_status.status}")
                return
            print("Waiting for response...")
            import time
            time.sleep(1)

        # Get the response
        messages = client.beta.threads.messages.list(
            thread_id=thread.id,
            order='desc',
            limit=1
        )
        
        if messages.data and messages.data[0].content:
            response = messages.data[0].content[0].text.value
            print("\nAssistant's response:")
            print("-" * 50)
            print(response)
            print("-" * 50)
        else:
            print("No response received")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_assistant() 