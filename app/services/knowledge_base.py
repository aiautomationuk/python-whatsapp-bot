from openai import OpenAI
import os
from dotenv import load_dotenv
import logging
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class KnowledgeBase:
    def __init__(self):
        self.knowledge_file = "knowledge_base.json"
        self.load_knowledge()

    def load_knowledge(self):
        """Load knowledge base from JSON file"""
        try:
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, 'r') as f:
                    self.knowledge = json.load(f)
                logging.info("Knowledge base loaded successfully")
            else:
                self.knowledge = {
                    "company_info": {
                        "name": "Infobot Technologies",
                        "address": "Manchester, UK",
                        "contact": {
                            "email": "info@infobot.co.uk",
                            "phone": "+447464177761"
                        },
                        "services": [
                            "WhatsApp Business API Integration",
                            "Custom Chatbot Development",
                            "AI-Powered Customer Service Solutions"
                        ],
                        "business_hours": "Monday - Friday, 9:00 AM - 5:00 PM"
                    }
                }
                self.save_knowledge()
                logging.info("Created new knowledge base with default values")
        except Exception as e:
            logging.error(f"Error loading knowledge base: {str(e)}")
            self.knowledge = {}

    def save_knowledge(self):
        """Save knowledge base to JSON file"""
        try:
            with open(self.knowledge_file, 'w') as f:
                json.dump(self.knowledge, f, indent=4)
            logging.info("Knowledge base saved successfully")
        except Exception as e:
            logging.error(f"Error saving knowledge base: {str(e)}")

    def get_relevant_info(self, query):
        """Get relevant information from knowledge base based on query"""
        try:
            # For now, return all company info
            # In the future, we can implement semantic search here
            return self.knowledge.get("company_info", {})
        except Exception as e:
            logging.error(f"Error getting relevant info: {str(e)}")
            return {}

    def update_knowledge(self, new_info):
        """Update knowledge base with new information"""
        try:
            self.knowledge["company_info"].update(new_info)
            self.save_knowledge()
            logging.info("Knowledge base updated successfully")
        except Exception as e:
            logging.error(f"Error updating knowledge base: {str(e)}")

# Create a singleton instance
knowledge_base = KnowledgeBase() 