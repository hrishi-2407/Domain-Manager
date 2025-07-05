from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import logging

from app.database import engine, get_db
from app.models import Domain, Base

from datetime import datetime, timezone, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Initializing database tables...")
try:
    Base.metadata.create_all(bind=engine)

    logger.info("Database tables initialized successfully")
except Exception as e:
    logger.error(f"Error initializing database: {e}")
    
app = FastAPI(title="Domain Manager")

class DomainSchema(BaseModel):
    name: str
    tld: str

    class Config:
        orm_mode = True
        from_attributes = True  

@app.post("/domains/create", response_model=DomainSchema)
def create_domain(domain: DomainSchema, db: Session = Depends(get_db)):
    """Create a new domain with optional registration_date and auto expiration_date"""
    db_domain = Domain(name=domain.name, 
                       tld=domain.tld)
    db.add(db_domain)
    db.commit()
    db.refresh(db_domain)
    return db_domain

@app.get("/domains/getall", response_model=List[DomainSchema])
def read_domains(db: Session = Depends(get_db)):
    """Get all domains"""
    return db.query(Domain).all()

@app.get("/domains/get/{domain_id}", response_model=DomainSchema)
def read_domain(domain_id: int, db: Session = Depends(get_db)):
    """Get a specific domain by ID"""
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    return domain

@app.put("/domains/update/{domain_id}", response_model=DomainSchema)
def update_domain(domain_id: int, domain: DomainSchema, db: Session = Depends(get_db)):
    """Update a domain"""
    db_domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if db_domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    db_domain.name = Domain.name
    db_domain.tld = Domain.tld
    db.commit()
    db.refresh(db_domain)
    return db_domain

@app.delete("/domains/delete/{domain_id}")
def delete_domain(domain_id: int, db: Session = Depends(get_db)):
    """Delete a domain"""
    db_domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if db_domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    db.delete(db_domain)
    db.commit()
    return {"message": "Domain deleted successfully"}

@app.get("/")
def read_root():
    return {"message": "Welcome to Domain Manager API", 
            "docs": "Visit /docs for the API documentation"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
