"""
Message processing pipeline for WhatsApp interactions.
Coordinates parsing, state management, and itinerary generation.
"""
import logging
from sqlalchemy.orm import Session
from twilio.twiml.messaging_response import MessagingResponse

from src.models.database.lead import Lead, LeadStatus
from src.models.database.conversation import Conversation, MessageRole
from src.models.database.itinerary import Itinerary
from src.services.message_parser_service import MessageParserService
from src.services.itinerary_generator_service import ItineraryGeneratorService
from src.llm.clients.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

from fastapi import BackgroundTasks
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

from src.models.database.lead import Lead, LeadStatus
from src.models.database.conversation import Conversation, MessageRole
from src.models.database.itinerary import Itinerary
from src.services.message_parser_service import MessageParserService
from src.services.itinerary_generator_service import ItineraryGeneratorService
from src.llm.clients.gemini_client import GeminiClient
from src.config import settings
from src.database.session import SessionLocal

logger = logging.getLogger(__name__)

class MessageHandler:
    def __init__(self, db: Session):
        self.db = db
        self.gemini = GeminiClient()
        self.parser = MessageParserService(self.gemini)
        self.generator = ItineraryGeneratorService(self.gemini)
        self.twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    async def handle_message(self, phone_number: str, message_text: str, background_tasks: BackgroundTasks) -> MessagingResponse:
        """
        Main entry point for processing a WhatsApp message.
        """
        # 1. Get or create lead
        lead = self.db.query(Lead).filter(Lead.phone_number == phone_number).first()
        if not lead:
            lead = Lead(phone_number=phone_number, status=LeadStatus.INITIAL)
            self.db.add(lead)
            self.db.commit()
            self.db.refresh(lead)

        # 2. Log incoming message
        incoming = Conversation(lead_id=lead.id, role=MessageRole.USER, content=message_text)
        self.db.add(incoming)
        lead.messages_received += 1
        
        # 3. Get recent conversation history for context
        history = [
            {"role": c.role.value, "content": c.content} 
            for c in self.db.query(Conversation).filter(Conversation.lead_id == lead.id).order_by(Conversation.created_at.desc()).limit(5)
        ][::-1]

        # 4. Parse message for travel parameters
        params = await self.parser.parse_message(message_text, history)
        
        # 5. Update lead info if params found
        if params.destination: lead.destination = params.destination
        if params.duration_days: lead.duration_days = params.duration_days
        if params.budget_usd: lead.budget_usd = params.budget_usd
        if params.interests: lead.interests = ", ".join(params.interests)
        
        response = MessagingResponse()
        reply_text = ""

        # 6. Logic for reply
        if params.is_complete:
            # Generate itinerary in background to prevent webhook timeout
            reply_text = f"Preparing your personalized itinerary for {lead.destination}. You will receive it shortly."
            background_tasks.add_task(
                self._generate_and_send_itinerary, 
                lead.id, 
                phone_number,
                lead.destination, 
                lead.duration_days, 
                lead.budget_usd, 
                lead.interests
            )
        else:
            # Prompt for missing trip parameters
            if not lead.destination:
                reply_text = "Welcome to the Travel Assistant. What destination are you considering for your next trip?"
            elif not lead.duration_days:
                reply_text = f"Acknowledged. What is the intended duration of your stay in {lead.destination}?"
            elif not lead.budget_usd:
                reply_text = "Please provide an estimated total budget (in USD) for this trip."
            elif not lead.interests:
                reply_text = "What activities or interests should be prioritized in your itinerary? (e.g. food, history, nature)"
            else:
                reply_text = "Thank you. Is there any additional information you would like to include before I generate the itinerary?"

        # 7. Persist outgoing conversation record
        outgoing = Conversation(lead_id=lead.id, role=MessageRole.ASSISTANT, content=reply_text)
        self.db.add(outgoing)
        lead.messages_sent += 1
        
        self.db.commit()
        
        response.message(reply_text)
        return response

    async def _generate_and_send_itinerary(self, lead_id: int, phone_number: str, destination: str, duration: int, budget: float, interests: str):
        """Background worker to generate and transmit itinerary via Twilio REST API."""
        try:
            # Initialize new database session for background task
            db = SessionLocal()
            
            logger.info(f"Background Process: Generating itinerary for Lead ID {lead_id}")
            itinerary_text = await self.generator.generate_itinerary(
                destination, duration, budget, interests
            )
            
            # Persist generated itinerary
            itinerary = Itinerary(
                lead_id=lead_id,
                destination=destination,
                duration_days=duration,
                budget_usd=budget,
                full_text=itinerary_text
            )
            db.add(itinerary)
            
            # Update lead lifecycle status
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            if lead:
                lead.status = LeadStatus.QUALIFIED
                conv = Conversation(lead_id=lead_id, role=MessageRole.ASSISTANT, content=itinerary_text)
                db.add(conv)
                lead.messages_sent += 1

            db.commit()
            
            # Transmit via Twilio REST API with character limit handling
            char_limit = 1500
            if len(itinerary_text) <= char_limit:
                self.twilio_client.messages.create(
                    from_=settings.TWILIO_WHATSAPP_FROM,
                    body=itinerary_text,
                    to=f"whatsapp:{phone_number}"
                )
            else:
                # Segment long itineraries into multiple messages
                chunks = [itinerary_text[i:i+char_limit] for i in range(0, len(itinerary_text), char_limit)]
                for i, chunk in enumerate(chunks):
                    self.twilio_client.messages.create(
                        from_=settings.TWILIO_WHATSAPP_FROM,
                        body=f"[{i+1}/{len(chunks)}]\n\n{chunk}",
                        to=f"whatsapp:{phone_number}"
                    )
            
            logger.info(f"Transmission Success: Itinerary delivered to {phone_number}")
            db.close()
            
        except Exception as e:
            logger.error(f"Background Generation Error: {str(e)}")
