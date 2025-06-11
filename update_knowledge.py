from app.services.knowledge_base import knowledge_base
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)

def main():
    try:
        # Update the knowledge base with correct information
        new_info = {
            "name": "Infobot Technologies",
            "address": "Your actual business address",  # Replace with actual address
            "contact": {
                "email": "info@infobot.co.uk",
                "phone": "Your actual phone number"  # Replace with actual phone
            },
            "services": [
                "WhatsApp Business API Integration",
                "Custom Chatbot Development",
                "AI-Powered Customer Service Solutions"
            ],
            "business_hours": "Your actual business hours"  # Replace with actual hours
        }
        
        knowledge_base.update_knowledge(new_info)
        print("\nKnowledge base updated successfully!")
        print("\nCurrent knowledge base contents:")
        print(json.dumps(knowledge_base.knowledge, indent=2))
        
    except Exception as e:
        print(f"Error updating knowledge base: {str(e)}")

if __name__ == "__main__":
    main() 