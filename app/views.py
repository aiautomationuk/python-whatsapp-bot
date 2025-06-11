import logging
import json

from flask import Blueprint, request, jsonify, current_app

from .decorators.security import signature_required
from .utils.whatsapp_utils import (
    process_whatsapp_message,
    is_valid_whatsapp_message,
)

webhook_blueprint = Blueprint("webhook", __name__)


def handle_message():
    """
    Handle incoming webhook events from the WhatsApp API.

    This function processes incoming WhatsApp messages and other events,
    such as delivery statuses. If the event is a valid message, it gets
    processed. If the incoming payload is not a recognized WhatsApp event,
    an error is returned.

    Every message send will trigger 4 HTTP requests to your webhook: message, sent, delivered, read.

    Returns:
        response: A tuple containing a JSON response and an HTTP status code.
    """
    body = request.get_json()
    logging.info(f"Received webhook body: {json.dumps(body, indent=2)}")
    
    # Check if it's a WhatsApp status update
    if (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    ):
        logging.info("Received a WhatsApp status update.")
        return jsonify({"status": "ok"}), 200

    # Check if it's a message from a user (not a status update)
    if (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("messages")
    ):
        message = body["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = message.get("from")
        logging.info(f"Received message from: {from_number}")
        
        # Get the bot's number from metadata
        bot_number = body["entry"][0]["changes"][0]["value"]["metadata"]["display_phone_number"].replace("+", "")
        
        if from_number != bot_number:  # Ignore messages from our own number
            try:
                if is_valid_whatsapp_message(body):
                    logging.info("Processing valid WhatsApp message")
                    process_whatsapp_message(body)
                    return jsonify({"status": "ok"}), 200
                else:
                    logging.info("Invalid WhatsApp message format")
            except json.JSONDecodeError:
                logging.error("Failed to decode JSON")
                return jsonify({"status": "error", "message": "Invalid JSON provided"}), 400
        else:
            logging.info("Ignoring message from our own number")
    
    # If it's not a status update or a valid user message, return ok but don't process
    logging.info("No valid message to process")
    return jsonify({"status": "ok"}), 200


# Required webhook verifictaion for WhatsApp
def verify():
    # Parse params from the webhook verification request
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == current_app.config["VERIFY_TOKEN"]:
            # Respond with 200 OK and challenge token from the request
            logging.info("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            logging.info("VERIFICATION_FAILED")
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        logging.info("MISSING_PARAMETER")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400


@webhook_blueprint.route("/webhook", methods=["GET"])
def webhook_get():
    return verify()

@webhook_blueprint.route("/webhook", methods=["POST"])
@signature_required
def webhook_post():
    return handle_message()


