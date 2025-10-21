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
    service: str      # hardcodeado
    incident_id: int
    status: str = "Open"
    creation_date: str 
    closing_date: Optional[str] = None

