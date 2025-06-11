import os
from openai import OpenAI
from dotenv import load_dotenv
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_assistant():
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        assistant_id = os.getenv('OPENAI_ASSISTANT_ID')
        
        if not assistant_id:
            raise ValueError("OPENAI_ASSISTANT_ID not found in environment variables")
            
        # Verify assistant configuration
        logger.info(f"Testing assistant with ID: {assistant_id}")
        assistant = client.beta.assistants.retrieve(assistant_id)
        logger.info(f"Assistant name: {assistant.name}")
        logger.info(f"Assistant model: {assistant.model}")
        logger.info(f"Assistant tools: {assistant.tools}")
        
        # Test questions
        test_questions = [
            "What is Infobot Technologies' phone number?",
            "What are Infobot Technologies' business hours?",
            "What services does Infobot Technologies offer?",
            "Where is Infobot Technologies located?"
        ]
        
        for question in test_questions:
            print(f"\nTesting question: {question}")
            print("-" * 50)
            
            # Create a new thread for each question
            thread = client.beta.threads.create()
            logger.info(f"Created new thread: {thread.id}")
            
            # Send the question
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=question
            )
            
            # Run the assistant
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant_id
            )
            
            # Wait for the response
            while True:
                run_status = client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                
                if run_status.status == 'completed':
                    break
                elif run_status.status == 'failed':
                    raise Exception(f"Run failed: {run_status.last_error}")
                    
                print("Waiting for response...")
                time.sleep(2)
            
            # Get the response
            messages = client.beta.threads.messages.list(
                thread_id=thread.id,
                limit=1,
                order='desc'
            )
            
            print("\nAssistant's response:")
            print("-" * 50)
            print(messages.data[0].content[0].text.value)
            print("-" * 50)
            
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        raise

if __name__ == "__main__":
    test_assistant() 