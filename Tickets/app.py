from flask import Flask, jsonify, request
from flasgger import Swagger
import yaml
import dataclasses
from database import DatabaseHandler
from managers import IncidentManager, TicketManager, ClientManager
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

with open("swagger.yml", "r", encoding="utf-8") as f:
    swagger_template = yaml.safe_load(f)
swagger = Swagger(app, template=swagger_template)

db = DatabaseHandler()
incident_manager = IncidentManager(db)
ticket_manager = TicketManager(db)
client_manager = ClientManager(db)

# ========================================
# Endpoints de incidentes
# ========================================
@app.route("/api/incidents/", methods=["GET"])
def show_incidents():
    """
    Lista todos los incidents registrados.
    ---
    tags:
      - Incidents
    """
    return jsonify([dataclasses.asdict(i) for i in incident_manager.show()])


@app.route("/api/incidents/", methods=["POST"])
def create_incident():
    """
    Crea un nuevo incident.
    ---
    tags:
      - Incidents
    """
    data = request.json
    incident = incident_manager.create(data["description"], data["incident_type"])
    return jsonify(dataclasses.asdict(incident)), 201


@app.route("/api/incidents/<int:incident_id>", methods=["GET"])
def get_incident(incident_id):
    """
    Obtiene un incident por su ID.
    ---
    tags:
      - Incidents
    """
    incident = incident_manager.get(incident_id)
    if incident:
        return jsonify(dataclasses.asdict(incident))
    return jsonify({"error": "Incident not found"}), 404


@app.route("/api/incidents/<int:incident_id>", methods=["PUT"])
def update_incident(incident_id):
    """
    Modifica un incident existente.
    ---
    tags:
      - Incidents
    """
    data = request.json
    incident = incident_manager.update(
        incident_id,
        description=data.get("description"),
        incident_type=data.get("incident_type")
    )
    if incident:
        return jsonify(dataclasses.asdict(incident))
    return jsonify({"error": "Incident not found"}), 404


# ========================================
# Endpoints de tickets
# ========================================
@app.route("/api/tickets/", methods=["GET"])
def show_tickets():
    """
    Lista todos los tickets registrados.
    ---
    tags:
      - Tickets
    """
    return jsonify([dataclasses.asdict(t) for t in ticket_manager.show()])


@app.route("/api/tickets/", methods=["POST"])
def create_ticket():
    """
    Crea un nuevo ticket.
    ---
    tags:
      - Tickets
    """
    data = request.json

    incident = incident_manager.get(data["incident_id"])
    if not incident:
        return jsonify({"error": "Incident is not valid"}), 400

    client_id = data.get("client_id")
    if not client_id:
        return jsonify({"error": "client_id is required"}), 400

    client = client_manager.get(client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404

    service = data.get("service") or "Unknown"

    ticket = ticket_manager.create(client, service, incident.id)
    return jsonify(dataclasses.asdict(ticket)), 201


@app.route("/api/tickets/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id):
    """
    Obtiene un ticket por su ID.
    ---
    tags:
      - Tickets
    """
    ticket = ticket_manager.get(ticket_id)
    if ticket:
        return jsonify(dataclasses.asdict(ticket))
    return jsonify({"error": "Ticket not found"}), 404


@app.route("/api/tickets/<int:ticket_id>/close", methods=["PUT"])
def close_ticket(ticket_id):
    """
    Cierra un ticket.
    ---
    tags:
      - Tickets
    """
    ticket = ticket_manager.close(ticket_id)
    if ticket:
        return jsonify(dataclasses.asdict(ticket))
    return jsonify({"error": "Ticket not found"}), 404


@app.route("/api/tickets/<int:ticket_id>", methods=["PUT"])
def update_ticket(ticket_id):
    data = request.json or {}

    incident_id = data.get("incident_id")
    if incident_id is not None and not incident_manager.get(incident_id):
        return jsonify({"error": "Invalid incident"}), 400

    client = None
    if "client_id" in data:
        client = client_manager.get(data["client_id"])
        if not client:
            return jsonify({"error": "Client not found"}), 404

    service = data.get("service")
    status = data.get("status")

    ticket = ticket_manager.update(
        ticket_id,
        client=client,
        service=service,
        incident_id=incident_id,
        status=status
    )

    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    return jsonify(dataclasses.asdict(ticket))


# ========================================
# Endpoints de clientes
# ========================================
@app.route("/api/clients/", methods=["GET"])
def show_clients():
    """
    Lista todos los clientes registrados.
    ---
    tags:
      - Clients
    """
    return jsonify([dataclasses.asdict(c) for c in client_manager.show()])


@app.route("/api/clients/<int:client_id>", methods=["GET"])
def get_client(client_id):
    """
    Obtiene un cliente por su ID.
    ---
    tags:
      - Clients
    """
    client = client_manager.get(client_id)
    if client:
        return jsonify(dataclasses.asdict(client))
    return jsonify({"error": "Client not found"}), 404


@app.route("/api/clients/", methods=["POST"])
def create_client():
    """
    Crea un nuevo cliente.
    ---
    tags:
      - Clients
    """
    data = request.json
    client = client_manager.create(
        name=data["name"],
        email=data["email"],
        phone_number=data["phone_number"]
    )
    return jsonify(dataclasses.asdict(client)), 201


@app.route("/api/clients/<int:client_id>", methods=["PUT"])
def update_client(client_id):
    """
    Modifica un cliente existente.
    ---
    tags:
      - Clients
    """
    data = request.json or {}
    client = client_manager.update(
        client_id,
        name=data.get("name"),
        email=data.get("email"),
        phone_number=data.get("phone_number")
    )
    if client:
        return jsonify(dataclasses.asdict(client))
    return jsonify({"error": "Client not found"}), 404


if __name__ == "__main__":
    app.run(debug=True, port=8000)
