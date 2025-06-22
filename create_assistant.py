from app.services.openai_service import create_new_assistant
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def main():
    try:
        assistant_id = create_new_assistant()
        print("\n" + "="*50)
        print(f"NEW ASSISTANT ID: {assistant_id}")
        print("="*50)
        print("\nPlease update your OPENAI_ASSISTANT_ID environment variable with this ID")
    except Exception as e:
        print(f"Error creating assistant: {str(e)}")

if __name__ == "__main__":
    main() 

    