"""
Itinerary storage model for tracking generated plans.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database.base import Base

class Itinerary(Base):
    __tablename__ = "itineraries"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), index=True)
    
    # Itinerary Details
    destination = Column(String(255), nullable=False)
    duration_days = Column(Integer, nullable=False)
    budget_usd = Column(Float, nullable=False)
    
    # Structured Data
    itinerary_data = Column(JSON, nullable=True)  # Day-by-day breakdown
    
    # Generated Content
    full_text = Column(Text, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    lead = relationship("Lead", back_populates="itineraries")
    
    def __repr__(self):
        return f"<Itinerary {self.destination} for Lead {self.lead_id}>"
