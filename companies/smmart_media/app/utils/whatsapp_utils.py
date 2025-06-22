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
        
        # Try to find matching business number by phone_number_id
        for key in os.environ:
            if key.startswith("WHATSAPP_PHONE_NUMBER_ID_"):
                business_number = key.replace("WHATSAPP_PHONE_NUMBER_ID_", "")
                if os.getenv(key) == phone_number_id:
                    logger.info(f"Found business number {business_number} for phone_number_id {phone_number_id}")
                    return business_number
        
        # If no match found, log available configurations
        logger.warning(f"No business number found for phone_number_id: {phone_number_id}")
        logger.info(f"Available business configurations: {list_configured_businesses()}")
        
        # Return None to indicate no match found
        return None
        
    except (KeyError, IndexError) as e:
        logger.error(f"Error extracting business number from webhook: {e}")
        logger.error(f"Webhook body structure: {json.dumps(body, indent=2)}")
        return None

def validate_credentials(business_number):
    """Validate that all required credentials exist for a business number"""
    if not business_number:
        return False, "No business number provided"
    
    access_token = os.getenv(f"WHATSAPP_ACCESS_TOKEN_{business_number}")
    phone_number_id = os.getenv(f"WHATSAPP_PHONE_NUMBER_ID_{business_number}")
    
    if not access_token:
        return False, f"Missing WHATSAPP_ACCESS_TOKEN_{business_number}"
    
    if not phone_number_id:
        return False, f"Missing WHATSAPP_PHONE_NUMBER_ID_{business_number}"
    
    return True, "Credentials valid"

def send_whatsapp_message(to_number, message_text, business_number=None):
    """Send WhatsApp message using business-specific credentials"""
    try:
        # Validate credentials first
        if business_number:
            is_valid, error_msg = validate_credentials(business_number)
            if not is_valid:
                logger.error(f"Credential validation failed: {error_msg}")
                return False
            
            access_token = os.getenv(f"WHATSAPP_ACCESS_TOKEN_{business_number}")
            phone_number_id = os.getenv(f"WHATSAPP_PHONE_NUMBER_ID_{business_number}")
        else:
            # Fallback to generic credentials
            access_token = os.getenv("WHATSAPP_ACCESS_TOKEN") or os.getenv("ACCESS_TOKEN")
            phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID") or os.getenv("PHONE_NUMBER_ID")
            
            if not access_token or not phone_number_id:
                logger.error("Missing fallback WhatsApp credentials")
                return False
        
        version = os.getenv("VERSION", "v18.0")
        
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
        
        response = requests.post(url, data=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"Message sent successfully to {to_number} via business {business_number}")
            return True
        else:
            logger.error(f"Failed to send message: {response.status_code} - {response.text}")
            return False
            
    except requests.Timeout:
        logger.error("Timeout occurred while sending WhatsApp message")
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
        # Validate credentials first
        is_valid, error_msg = validate_credentials(business_number)
        if not is_valid:
            logger.error(f"Credential validation failed: {error_msg}")
            return jsonify({"status": "error", "message": error_msg}), 500

        access_token = os.getenv(f"WHATSAPP_ACCESS_TOKEN_{business_number}")
        phone_number_id = os.getenv(f"WHATSAPP_PHONE_NUMBER_ID_{business_number}")
        version = os.getenv("VERSION", "v23.0")

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
    try:
        wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
        name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
        
        # Get the business number from the webhook
        business_number = get_business_number_from_webhook(body)
        
        if not business_number:
            logger.error("Could not determine business number from webhook")
            logger.error(f"Available businesses: {list_configured_businesses()}")
            return False
        
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
        result = send_message(data, business_number)
        
        return True
        
    except (KeyError, IndexError) as e:
        logger.error(f"Error processing WhatsApp message: {e}")
        logger.error(f"Message body: {json.dumps(body, indent=2)}")
        return False

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

def debug_credentials():
    """Debug function to check credential configuration"""
    businesses = list_configured_businesses()
    logger.info(f"Found {len(businesses)} configured businesses: {businesses}")
    
    for business in businesses:
        token = os.getenv(f"WHATSAPP_ACCESS_TOKEN_{business}")
        phone_id = os.getenv(f"WHATSAPP_PHONE_NUMBER_ID_{business}")
        
        token_status = "✓" if token else "✗"
        phone_status = "✓" if phone_id else "✗"
        
        logger.info(f"Business {business}: Token {token_status}, Phone ID {phone_status}")
        
        if token:
            logger.debug(f"  Token preview: {token[:20]}...")
        if phone_id:
            logger.debug(f"  Phone ID: {phone_id}")

# Only run debug in development
if os.getenv("FLASK_ENV") == "development":
    debug_credentials()