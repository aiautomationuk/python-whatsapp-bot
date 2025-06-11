from openai import OpenAI
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_vector_store():
    """Create a vector store for Infobot's information"""
    try:
        # Create a vector store
        vector_store = client.vector_stores.create(
            name="infobot information"
        )
        print(f"\nVector store created successfully!")
        print(f"Vector Store ID: {vector_store.id}")
        print(f"Name: {vector_store.name}")
        
        # Upload the PDF file
        print("\nUploading files...")
        with open("infobot information.pdf", "rb") as file:
            file_batch = client.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store.id,
                files=[file]
            )
        
        print("\nFile upload status:")
        print(f"Status: {file_batch.status}")
        print(f"File counts: {file_batch.file_counts}")
        
        print("\nNext steps:")
        print("1. Go to the OpenAI Assistants dashboard")
        print("2. Select your assistant")
        print("3. In the Knowledge section, select this vector store")
        print("4. Save the changes")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    create_vector_store() 