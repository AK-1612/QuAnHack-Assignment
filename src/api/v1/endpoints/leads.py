"""
Lead management endpoints for the dashboard.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from src.database.session import get_db
from src.models.database.lead import Lead, LeadStatus

router = APIRouter()

class LeadSchema(BaseModel):
    id: int
    phone_number: str
    name: Optional[str] = None
    destination: Optional[str] = None
    duration_days: Optional[int] = None
    budget_usd: Optional[float] = None
    status: LeadStatus
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[LeadSchema])
async def list_leads(db: Session = Depends(get_db)):
    """List all captured leads."""
    return db.query(Lead).order_by(Lead.created_at.desc()).all()

@router.get("/{lead_id}")
async def get_lead_details(lead_id: int, db: Session = Depends(get_db)):
    """Get full details for a lead, including conversations and itineraries."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return {
        "lead": lead,
        "conversations": lead.conversations,
        "itineraries": lead.itineraries
    }
