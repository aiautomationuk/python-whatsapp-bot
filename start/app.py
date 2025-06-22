from flask import Flask, request, jsonify
import json
import logging
import os
from dotenv import load_dotenv

# Import your OpenAI assistant functions
from openai_assistant import generate_response

# Map WhatsApp business numbers to OpenAI Assistant IDs AND Phone Number IDs
# IMPORTANT: Replace these with your ACTUAL Phone Number IDs from Facebook Developer Console
WHATSAPP_TO_ASSISTANT = {
    "447464177761": {
        "assistant_id": "asst_AS82w4Y1Nd6sSR8KhJbIodad",  # infobot
        "phone_number_id": "627065630497964"  
    },
    "447510698847": {
        "assistant_id": "asst_A2CqaZ1HO1qI6QwjyYIrmqeI",  # Copy of Natalie
        "phone_number_id": "659535307248611"   
    },
}

# Default configuration if no mapping is found
DEFAULT_CONFIG = {
    "assistant_id": "asst_AS82w4Y1Nd6sSR8KhJbIodad",
    "phone_number_id": os.getenv("WHATSAPP_PHONE_NUMBER_ID")  # Your default phone number ID
}

load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_assistant_config(business_number):
    """
    Get the appropriate assistant configuration for a given business number
    """
    logger.info(f"🔍 Looking up config for business number: {business_number}")
    logger.info(f"🗂️ Available mappings: {list(WHATSAPP_TO_ASSISTANT.keys())}")
    
    config = WHATSAPP_TO_ASSISTANT.get(business_number)
    if not config:
        logger.warning(f"❌ No assistant mapping found for {business_number}, using default")
        config = DEFAULT_CONFIG
        logger.info(f"📋 Using default config: {config}")
    else:
        logger.info(f"✅ Found config for {business_number}: {config}")
    
    return config

def process_whatsapp_message(webhook_data):
    """
    Process incoming WhatsApp message from webhook
    """
    try:
        # Extract the entry data
        entries = webhook_data.get("entry", [])
        
        for entry in entries:
            changes = entry.get("changes", [])
            
            for change in changes:
                value = change.get("value", {})
                
                # Check if this is a message (not a status update)
                if "messages" in value:
                    messages = value.get("messages", [])
                    contacts = value.get("contacts", [])
                    metadata = value.get("metadata", {})
                    
                    # Get business phone number from metadata
                    business_number = metadata.get("display_phone_number")
                    
                    logger.info(f"📱 Raw business number from metadata: {business_number}")
                    
                    # Remove any formatting (keep only digits)
                    if business_number:
                        business_number = ''.join(filter(str.isdigit, business_number))
                    
                    logger.info(f"📱 Cleaned business number: {business_number}")
                    
                    for message in messages:
                        sender_number = message.get("from")
                        message_id = message.get("id")
                        message_type = message.get("type")
                        timestamp = message.get("timestamp")
                        
                        logger.info(f"👤 Processing message from: {sender_number}")
                        logger.info(f"🏢 Business number: {business_number}")
                        logger.info(f"📝 Message type: {message_type}")
                        
                        # Check if this is NOT from our business number
                        if sender_number != business_number:
                            # Get sender's name if available
                            sender_name = None
                            for contact in contacts:
                                if contact.get("wa_id") == sender_number:
                                    sender_name = contact.get("profile", {}).get("name")
                                    break
                            
                            if not sender_name:
                                sender_name = f"User_{sender_number[-4:]}"  # Use last 4 digits as name
                            
                            # Get the appropriate assistant configuration for this business number
                            config = get_assistant_config(business_number)
                            
                            # Process different message types
                            if message_type == "text":
                                text_body = message.get("text", {}).get("body", "")
                                logger.info(f"💬 Text message: {text_body}")
                                
                                # Generate response using OpenAI Assistant
                                response = generate_response(
                                    message_body=text_body,
                                    wa_id=sender_number,
                                    name=sender_name,
                                    assistant_id=config["assistant_id"]
                                )
                                
                                # Send response back to user using the correct phone number ID
                                logger.info(f"📤 About to send response using phone_number_id: {config['phone_number_id']}")
                                send_whatsapp_message(
                                    to_number=sender_number, 
                                    message_text=response, 
                                    phone_number_id=config["phone_number_id"]
                                )
                                
                            elif message_type == "image":
                                logger.info("🖼️ Received image message")
                                response = generate_response(
                                    message_body="I received an image. How can I help you with it?",
                                    wa_id=sender_number,
                                    name=sender_name,
                                    assistant_id=config["assistant_id"]
                                )
                                send_whatsapp_message(
                                    to_number=sender_number, 
                                    message_text=response, 
                                    phone_number_id=config["phone_number_id"]
                                )
                                
                            else:
                                logger.info(f"❓ Received unsupported message type: {message_type}")
                                response = "I received your message but I can only respond to text messages at the moment."
                                send_whatsapp_message(
                                    to_number=sender_number, 
                                    message_text=response, 
                                    phone_number_id=config["phone_number_id"]
                                )
                        else:
                            logger.info("🤖 Ignoring message from our own business number")
                
    except Exception as e:
        logger.error(f"💥 Error processing WhatsApp message: {str(e)}")
        raise


def send_whatsapp_message(to_number, message_text, phone_number_id):
    """
    Send a WhatsApp message using the WhatsApp Business API
    Updated to use the specific phone_number_id for each WhatsApp number
    """
    try:
        # Import requests here to avoid circular imports
        import requests
        
        # WhatsApp Business API endpoint - now using the passed phone_number_id
        access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        
        logger.info(f"📞 Sending message to: {to_number}")
        logger.info(f"🆔 Using phone_number_id: {phone_number_id}")
        logger.info(f"🔐 Access token exists: {bool(access_token)}")
        
        if not phone_number_id or not access_token:
            logger.error("❌ Missing WhatsApp credentials")
            return False
        
        # Check if phone_number_id looks like a placeholder
        if "REPLACE_WITH_ACTUAL" in phone_number_id:
            logger.error(f"❌ Phone Number ID appears to be a placeholder: {phone_number_id}")
            logger.error("❌ You need to replace this with your actual Phone Number ID from Facebook Developer Console")
            return False
            
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
        logger.info(f"🌐 API URL: {url}")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {
                "body": message_text
            }
        }
        
        logger.info(f"📦 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, headers=headers, json=payload)
        
        logger.info(f"📊 Response status: {response.status_code}")
        logger.info(f"📊 Response body: {response.text}")
        
        if response.status_code == 200:
            logger.info(f"✅ Message sent successfully to {to_number} from phone number ID {phone_number_id}")
            return True
        else:
            logger.error(f"❌ Failed to send message: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"💥 Error sending WhatsApp message: {str(e)}")
        return False


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """
    WhatsApp webhook endpoint
    """
    if request.method == 'GET':
        # Webhook verification
        verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode == 'subscribe' and token == verify_token:
            logger.info("✅ Webhook verified successfully")
            return challenge
        else:
            logger.error("❌ Webhook verification failed")
            return "Verification failed", 403
    
    elif request.method == 'POST':
        # Process incoming webhook
        try:
            webhook_data = request.get_json()
            logger.info(f"📥 Received webhook body: {json.dumps(webhook_data, indent=2)}")
            
            if webhook_data and webhook_data.get("object") == "whatsapp_business_account":
                process_whatsapp_message(webhook_data)
                return jsonify({"status": "success"}), 200
            else:
                logger.warning("⚠️ Invalid webhook data received")
                return jsonify({"status": "invalid"}), 400
                
        except Exception as e:
            logger.error(f"💥 Error processing webhook: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        "status": "healthy", 
        "configured_numbers": list(WHATSAPP_TO_ASSISTANT.keys()),
        "default_phone_number_id": os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    }), 200


@app.route('/debug', methods=['GET'])
def debug_config():
    """
    Debug endpoint to check configuration
    """
    return jsonify({
        "whatsapp_mappings": WHATSAPP_TO_ASSISTANT,
        "default_config": DEFAULT_CONFIG,
        "env_vars": {
            "WHATSAPP_ACCESS_TOKEN": bool(os.getenv("WHATSAPP_ACCESS_TOKEN")),
            "WHATSAPP_PHONE_NUMBER_ID": os.getenv("WHATSAPP_PHONE_NUMBER_ID"),
            "WHATSAPP_VERIFY_TOKEN": bool(os.getenv("WHATSAPP_VERIFY_TOKEN"))
        }
    }), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
