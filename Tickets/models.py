from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Client:
    id: int
    name: str
    email: str
    phone_number: str

@dataclass
class Incident:
    id: int
    description: str
    incident_type: str

@dataclass
class Ticket:
    id: int
    client: Client      
    service: str      
    incident_id: int
    creation_date: str 
    status: str = "Open"
    closing_date: Optional[str] = None