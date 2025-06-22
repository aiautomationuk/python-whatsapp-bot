import logging
import os
import requests
import json
import re
from flask import current_app, jsonify
from app.services.openai_service import generate_response as openai_generate_response

logger = logging.getLogger(__name__)

def get_business_number_from_webhook(body):
    """Extract business phone number from webhook payload"""
    try:
        # Get the phone number ID from the webhook
        phone_number_id = body["entry"][0]["changes"][0]["value"]["metadata"]["phone_number_id"]
        
        # You might need to maintain a mapping of phone_number_id to business_number
        # For now, we'll try to extract from environment variables
        for key in os.environ:
            if key.startswith("WHATSAPP_PHONE_NUMBER_ID_") and os.getenv(key) == phone_number_id:
                return key.replace("WHATSAPP_PHONE_NUMBER_ID_", "")
        
        # Fallback: return the phone_number_id itself
        return phone_number_id
    except (KeyError, IndexError) as e:
        logger.error(f"Error extracting business number: {e}")
        return None

def send_whatsapp_message(to_number, message_text, business_number=None):
    """Send WhatsApp message using business-specific credentials"""
    try:
        if business_number:
            access_token = os.getenv(f"WHATSAPP_ACCESS_TOKEN_{business_number}")
            phone_number_id = os.getenv(f"WHATSAPP_PHONE_NUMBER_ID_{business_number}")
        else:
            # Fallback to generic credentials
            access_token = os.getenv("WHATSAPP_ACCESS_TOKEN") or os.getenv("ACCESS_TOKEN")
            phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID") or os.getenv("PHONE_NUMBER_ID")
        
        version = os.getenv("VERSION", "v18.0")
        
        if not access_token or not phone_number_id:
            logger.error(f"Missing WhatsApp credentials for business {business_number}")
            return False
        
        headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        
        data = json.dumps({
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "text",
            "text": {"preview_url": False, "body": message_text},
        })
        
        url = f"https://graph.facebook.com/{version}/{phone_number_id}/messages"
        
        response = requests.post(url, data=data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Message sent successfully to {to_number} via business {business_number}")
            return True
        else:
            logger.error(f"Failed to send message: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        return False

def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")

def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )

def send_message(data, business_number):
    try:
        access_token = os.getenv(f"WHATSAPP_ACCESS_TOKEN_{business_number}")
        phone_number_id = os.getenv(f"WHATSAPP_PHONE_NUMBER_ID_{business_number}")
        version = os.getenv("VERSION", "v23.0")
        
        if not access_token or not phone_number_id:
            logger.error(f"Missing WhatsApp credentials for {business_number}")
            return jsonify({"status": "error", "message": f"Missing WhatsApp credentials for {business_number}"}), 500

        headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

        url = f"https://graph.facebook.com/{version}/{phone_number_id}/messages"
        logger.info(f"Sending message to URL: {url} for business {business_number}")

        response = requests.post(url, data=data, headers=headers, timeout=10)
        if response.status_code != 200:
            logger.error(f"Failed to send message. Status: {response.status_code}, Response: {response.text}")
            return jsonify({"status": "error", "message": f"Failed to send message: {response.text}"}), response.status_code
            
        log_http_response(response)
        return response
    except requests.Timeout:
        logger.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except requests.RequestException as e:
        logger.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": f"Failed to send message: {str(e)}"}), 500

def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text

def process_whatsapp_message(body):
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
    
    # Get the business number from the webhook
    business_number = get_business_number_from_webhook(body)
    
    logging.info(f"Processing message from {name} ({wa_id}) for business {business_number}")

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_body = message["text"]["body"]
    logging.info(f"Message content: {message_body}")

    # Generate response using OpenAI Assistant
    response = openai_generate_response(message_body, wa_id, name)
    logging.info(f"OpenAI response: {response}")
    
    response = process_text_for_whatsapp(response)
    logging.info(f"Processed response for WhatsApp: {response}")

    data = get_text_message_input(wa_id, response)
    send_message(data, business_number)

def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )

def list_configured_businesses():
    """Helper function to list all configured business numbers"""
    businesses = []
    for key in os.environ:
        if key.startswith("WHATSAPP_ACCESS_TOKEN_"):
            business_number = key.replace("WHATSAPP_ACCESS_TOKEN_", "")
            businesses.append(business_number)
    return businesses

# Debug function - remove in production
def debug_credentials():
    businesses = list_configured_businesses()
    for business in businesses:
        token = os.getenv(f"WHATSAPP_ACCESS_TOKEN_{business}")
        phone_id = os.getenv(f"WHATSAPP_PHONE_NUMBER_ID_{business}")
        print(f"Business {business}: Token exists: {bool(token)}, Phone ID exists: {bool(phone_id)}")

# Only run debug in development
if os.getenv("FLASK_ENV") == "development":
    debug_credentials()