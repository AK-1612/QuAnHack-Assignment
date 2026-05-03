# Travel Agencies - An AI-powered Travel Itinerary Assistant

An enterprise-grade, AI-driven travel assistant that transforms natural language WhatsApp conversations into structured travel leads and luxury itineraries.

## Overview

This system provides a seamless bridge between travelers and travel agencies. Using **Google Gemini 1.5/2.0**, it parses conversational inputs, identifies travel parameters (destination, duration, budget, interests), and generates premium day-by-day itineraries—all delivered via **Twilio WhatsApp**.

### Key Features
- **Conversational Parameter Extraction**: Identifies missing trip details and prompts the user naturally.
- **Background Itinerary Generation**: Uses FastAPI background tasks to prevent timeouts during complex LLM generation.
- **Multi-Model Fallback**: Automatically switches between Gemini models (Flash, Pro) to ensure 100% uptime.
- **Agency Dashboard**: A real-time, glassmorphic UI to monitor leads, budgets, and chat history.
- **WhatsApp Optimization**: Automatically segments long itineraries to fit within WhatsApp's 1600-character limit.

## Technology Stack
- **Backend**: FastAPI (Python 3.9+)
- **AI**: Google Gemini (generative-ai SDK)
- **Database**: SQLite (SQLAlchemy ORM)
- **Messaging**: Twilio WhatsApp API
- **Frontend**: Vanilla JS / Tailwind CSS (Glassmorphism design)

## Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone <repo-url>
   cd QuAnHack
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**
   Create a `.env` file in the root directory (see `.env.example` for reference):
   ```env
   GEMINI_API_KEY=your_gemini_key
   TWILIO_ACCOUNT_SID=your_sid
   TWILIO_AUTH_TOKEN=your_token
   TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
   ```

4. **Run the Application**
   ```bash
   python3 -m uvicorn src.main:app --reload
   ```

## Dashboard
Access the agency dashboard by opening `dashboard/index.html` in any modern web browser. The dashboard connects to the local API on port 8000 and refreshes every 30 seconds.

## Architecture
- `src/api/`: FastAPI routers and endpoints.
- `src/handlers/`: Core business logic and message orchestration.
- `src/services/`: Specialized services for AI parsing and generation.
- `src/llm/`: LLM client wrappers with resilience logic.
- `src/models/`: SQLAlchemy database models.
