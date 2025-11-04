from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from contextlib import contextmanager

DB_NAME = "db.sqlite"
Base = declarative_base()

class IncidentModel(Base):
    __tablename__ = 'incidents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text, nullable=False)
    incident_type = Column(String(100), nullable=False)
    
    # Relación 1:N con tickets
    tickets = relationship("TicketModel", back_populates="incident")


class TicketModel(Base):
    __tablename__ = 'tickets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    client = Column(Text, nullable=False)  
    service = Column(String(100), nullable=False)
    incident_id = Column(Integer, ForeignKey('incidents.id'), nullable=False)
    status = Column(String(20), nullable=False, default='Open')
    creation_date = Column(String(50), nullable=False)
    closing_date = Column(String(50), nullable=True)
    
    # Relación N:1 con incident
    incident = relationship("IncidentModel", back_populates="tickets")


class ClientModel(Base):
    __tablename__ = 'clients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    phone_number = Column(String(50), nullable=False)


class DatabaseHandler:
    """Encapsula toda la lógica de base de datos usando SQLAlchemy."""

    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self.engine = create_engine(f'sqlite:///{db_name}', echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.init_db()

    def init_db(self):
        """Crea todas las tablas si no existen."""
        Base.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self):
        """Context manager para manejar sesiones de SQLAlchemy."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ========================================
    # CRUD de Incidentes
    # ========================================
    def get_all_incidents(self):
        with self.get_session() as session:
            incidents = session.query(IncidentModel).all()
            return [
                {
                    "id": i.id,
                    "description": i.description,
                    "incident_type": i.incident_type
                }
                for i in incidents
            ]

    def get_incident(self, incident_id):
        with self.get_session() as session:
            incident = session.query(IncidentModel).filter_by(id=incident_id).first()
            if incident:
                return {
                    "id": incident.id,
                    "description": incident.description,
                    "incident_type": incident.incident_type
                }
            return None

    def save_incident(self, incident_dict):
        with self.get_session() as session:
            if "id" not in incident_dict or incident_dict["id"] is None:
                new_incident = IncidentModel(
                    description=incident_dict["description"],
                    incident_type=incident_dict["incident_type"]
                )
                session.add(new_incident)
                session.flush()  # Para obtener el ID
                incident_dict["id"] = new_incident.id
            else:
                incident = session.query(IncidentModel).filter_by(
                    id=incident_dict["id"]
                ).first()
                if incident:
                    incident.description = incident_dict["description"]
                    incident.incident_type = incident_dict["incident_type"]
            
            return incident_dict

    def delete_incident(self, incident_id):
        with self.get_session() as session:
            incident = session.query(IncidentModel).filter_by(id=incident_id).first()
            if incident:
                session.delete(incident)

    # ========================================
    # CRUD de Tickets
    # ========================================
    def get_all_tickets(self):
        with self.get_session() as session:
            tickets = session.query(TicketModel).all()
            return [
                {
                    "id": t.id,
                    "client": t.client,
                    "service": t.service,
                    "incident_id": t.incident_id,
                    "status": t.status,
                    "creation_date": t.creation_date,
                    "closing_date": t.closing_date
                }
                for t in tickets
            ]

    def get_ticket(self, ticket_id):
        with self.get_session() as session:
            ticket = session.query(TicketModel).filter_by(id=ticket_id).first()
            if ticket:
                return {
                    "id": ticket.id,
                    "client": ticket.client,
                    "service": ticket.service,
                    "incident_id": ticket.incident_id,
                    "status": ticket.status,
                    "creation_date": ticket.creation_date,
                    "closing_date": ticket.closing_date
                }
            return None

    def save_ticket(self, ticket_dict):
        with self.get_session() as session:
            if "id" not in ticket_dict or ticket_dict["id"] is None:
                new_ticket = TicketModel(
                    client=ticket_dict["client"],
                    service=ticket_dict["service"],
                    incident_id=ticket_dict["incident_id"],
                    status=ticket_dict["status"],
                    creation_date=ticket_dict["creation_date"],
                    closing_date=ticket_dict["closing_date"]
                )
                session.add(new_ticket)
                session.flush()
                ticket_dict["id"] = new_ticket.id
            else:
                ticket = session.query(TicketModel).filter_by(
                    id=ticket_dict["id"]
                ).first()
                if ticket:
                    ticket.client = ticket_dict["client"]
                    ticket.service = ticket_dict["service"]
                    ticket.incident_id = ticket_dict["incident_id"]
                    ticket.status = ticket_dict["status"]
                    ticket.creation_date = ticket_dict["creation_date"]
                    ticket.closing_date = ticket_dict["closing_date"]
            
            return ticket_dict

    def delete_ticket(self, ticket_id):
        with self.get_session() as session:
            ticket = session.query(TicketModel).filter_by(id=ticket_id).first()
            if ticket:
                session.delete(ticket)

    # ========================================
    # CRUD de Clientes
    # ========================================
    def get_all_clients(self):
        with self.get_session() as session:
            clients = session.query(ClientModel).all()
            return [
                {
                    "id": c.id,
                    "name": c.name,
                    "email": c.email,
                    "phone_number": c.phone_number
                }
                for c in clients
            ]

    def get_client(self, client_id):
        with self.get_session() as session:
            client = session.query(ClientModel).filter_by(id=client_id).first()
            if client:
                return {
                    "id": client.id,
                    "name": client.name,
                    "email": client.email,
                    "phone_number": client.phone_number
                }
            return None

    def save_client(self, client_dict):
        with self.get_session() as session:
            if "id" not in client_dict or client_dict["id"] is None:
                new_client = ClientModel(
                    name=client_dict["name"],
                    email=client_dict["email"],
                    phone_number=client_dict["phone_number"]
                )
                session.add(new_client)
                session.flush()
                client_dict["id"] = new_client.id
            else:
                client = session.query(ClientModel).filter_by(
                    id=client_dict["id"]
                ).first()
                if client:
                    client.name = client_dict["name"]
                    client.email = client_dict["email"]
                    client.phone_number = client_dict["phone_number"]
            
            return client_dict

    def delete_client(self, client_id):
        with self.get_session() as session:
            client = session.query(ClientModel).filter_by(id=client_id).first()
            if client:
                session.delete(client)