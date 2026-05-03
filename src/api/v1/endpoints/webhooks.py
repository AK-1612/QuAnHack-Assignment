"""
WhatsApp webhook endpoints for receiving and processing messages.
"""
from fastapi import APIRouter, Request, Response, Depends, BackgroundTasks
import logging
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.handlers.message_handler import MessageHandler

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/whatsapp/incoming")
async def handle_whatsapp_message(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Handle incoming WhatsApp messages from Twilio.
    """
    try:
        # Parse form data
        form_data = await request.form()
        phone_number = form_data.get("From", "").replace("whatsapp:", "")
        message_text = form_data.get("Body", "").strip()
        
        logger.info(f"Webhook Received: Inbound message from {phone_number}")
        
        # Process message through handler
        handler = MessageHandler(db)
        response = await handler.handle_message(phone_number, message_text, background_tasks)
        
        # Return TwiML response
        return Response(
            content=response.to_xml(),
            media_type="application/xml"
        )
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return Response(content="<Response></Response>", media_type="application/xml")
