from models import Incident, Ticket, Client
from datetime import datetime
import json
import dataclasses

class IncidentManager:
    def __init__(self, db):
        self.db = db

    def show(self):
        return [Incident(**i) for i in self.db.get_all_incidents()]

    def create(self, description, incident_type):
        incident_dict = {"id": None, "description": description, "incident_type": incident_type}
        saved = self.db.save_incident(incident_dict)
        return Incident(**saved)

    def get(self, incident_id):
        row = self.db.get_incident(incident_id)
        return Incident(**row) if row else None

    def update(self, incident_id, description=None, incident_type=None):
        incident = self.get(incident_id)
        if not incident:
            return None
        if description is not None:
            incident.description = description
        if incident_type is not None:
            incident.incident_type = incident_type
        saved = self.db.save_incident(vars(incident))
        return Incident(**saved)


class TicketManager:
    def __init__(self, db):
        self.db = db

    def show(self):
        tickets = self.db.get_all_tickets()
        result = []
        for t in tickets:
            t["client"] = Client(**json.loads(t["client"]))
            result.append(Ticket(**t))
        return result

    def create(self, client, service, incident_id):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ticket_dict = {
            "id": None,
            "client": json.dumps(dataclasses.asdict(client)),
            "service": service,
            "incident_id": incident_id,
            "status": "Open",
            "creation_date": date,
            "closing_date": None
        }
        saved = self.db.save_ticket(ticket_dict) 
        saved["client"] = Client(**json.loads(saved["client"]))
        return Ticket(**saved)

    def get(self, ticket_id):
        row = self.db.get_ticket(ticket_id)
        if not row:
            return None
        row["client"] = Client(**json.loads(row["client"]))
        return Ticket(**row)

    def close(self, ticket_id):
        ticket = self.get(ticket_id)
        if not ticket:
            return None
        ticket.status = "Closed"
        ticket.closing_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ticket_dict = vars(ticket).copy()
        ticket_dict["client"] = json.dumps(dataclasses.asdict(ticket.client))
        saved = self.db.save_ticket(ticket_dict)
        saved["client"] = Client(**json.loads(saved["client"]))

        return Ticket(**saved)

    def update(self, ticket_id, client=None, service=None, incident_id=None, status=None):
        ticket = self.get(ticket_id)
        if not ticket:
            return None
        if client is not None:
            ticket.client = client
        if service is not None:
            ticket.service = service
        if incident_id is not None:
            ticket.incident_id = incident_id
        if status is not None:
            ticket.status = status
            if status == "Closed" and ticket.closing_date is None:
                ticket.closing_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            elif status == "Open":
                ticket.closing_date = None

        ticket_dict = vars(ticket).copy()
        ticket_dict["client"] = json.dumps(dataclasses.asdict(ticket.client))
        saved = self.db.save_ticket(ticket_dict)
        saved["client"] = Client(**json.loads(saved["client"]))
        return Ticket(**saved)

class ClientManager:
    def __init__(self, db):
        self.db = db
    
    def show(self):
        return [Client(**c) for c in self.db.get_all_clients()]
    
    def get(self, client_id):
        row = self.db.get_client(client_id)
        return Client(**row) if row else None
    
    def create(self, name, email, phone_number):
        client_dict = {"id": None, "name": name, "email": email, "phone_number": phone_number}
        saved = self.db.save_client(client_dict)
        return Client(**saved)

    def update(self, client_id, name=None, email=None, phone_number=None):
        client = self.get(client_id)
        if not client:
            return None
        if name is not None:
            client.name = name
        if email is not None:
            client.email = email
        if phone_number is not None:
            client.phone_number = phone_number
        saved = self.db.save_client(vars(client))
        return Client(**saved)

