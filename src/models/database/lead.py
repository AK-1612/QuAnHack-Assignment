"""
SQLAlchemy ORM model for Lead data.
Tracks prospect information and journey.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from src.database.base import Base

class LeadStatus(str, PyEnum):
    INITIAL = "initial"
    INTERESTED = "interested"
    FOLLOWING_UP = "following_up"
    QUALIFIED = "qualified"
    BOOKED = "booked"
    LOST = "lost"

class Lead(Base):
    __tablename__ = "leads"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Contact Information
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    
    # Travel Preferences
    destination = Column(String(255), nullable=True)
    duration_days = Column(Integer, nullable=True)
    budget_usd = Column(Float, nullable=True)
    interests = Column(Text, nullable=True)  # Stored as comma-separated or JSON string
    travel_dates = Column(String(255), nullable=True)
    number_of_people = Column(Integer, default=1)
    
    # Lead Status
    status = Column(Enum(LeadStatus), default=LeadStatus.INITIAL, index=True)
    source = Column(String(50), default="whatsapp")
    
    # Engagement Metrics
    messages_sent = Column(Integer, default=0)
    messages_received = Column(Integer, default=0)
    last_interaction = Column(DateTime, nullable=True)
    
    # Follow-up Tracking
    follow_up_1_sent = Column(Boolean, default=False)
    follow_up_2_sent = Column(Boolean, default=False)
    follow_up_3_sent = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    conversations = relationship("Conversation", back_populates="lead", cascade="all, delete-orphan")
    itineraries = relationship("Itinerary", back_populates="lead", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Lead {self.phone_number} - {self.destination}>"
