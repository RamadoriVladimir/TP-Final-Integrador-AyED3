import sqlite3

DB_NAME = "db.sqlite"

class DatabaseHandler:
    """Encapsula toda la lógica de base de datos."""

    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                incident_type TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client TEXT NOT NULL,
                service TEXT NOT NULL,
                incident_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                creation_date TEXT NOT NULL,
                closing_date TEXT,
                FOREIGN KEY (incident_id) REFERENCES incidents (id)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone_number TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    # ------------------------------
    # Metodos de consulta
    # ------------------------------
    def fetchall(self, query, params=()):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()

    def fetchone(self, query, params=()):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def execute(self, query, params=()):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    # ------------------------------
    # CRUD de incidents
    # ------------------------------
    def get_all_incidents(self):
        return self.fetchall("SELECT * FROM incidents")

    def get_incident(self, incident_id):
        return self.fetchone("SELECT * FROM incidents WHERE id=?", (incident_id,))

    def save_incident(self, incident_dict):
        if "id" not in incident_dict or incident_dict["id"] is None:
            incident_id = self.execute(
                "INSERT INTO incidents (description, incident_type) VALUES (?, ?)",
                (incident_dict["description"], incident_dict["incident_type"])
            )
            incident_dict["id"] = incident_id
        else:
            self.execute(
                "UPDATE incidents SET description=?, incident_type=? WHERE id=?",
                (incident_dict["description"], incident_dict["incident_type"], incident_dict["id"])
            )
        return incident_dict

    def delete_incident(self, incident_id):
        self.execute("DELETE FROM incidents WHERE id=?", (incident_id,))

    # ------------------------------
    # CRUD de tickets
    # ------------------------------
    def get_all_tickets(self):
        return self.fetchall("SELECT * FROM tickets")

    def get_ticket(self, ticket_id):
        return self.fetchone("SELECT * FROM tickets WHERE id=?", (ticket_id,))

    def save_ticket(self, ticket_dict):
        if "id" not in ticket_dict or ticket_dict["id"] is None:
            ticket_id = self.execute(
                """
                INSERT INTO tickets (client, service, incident_id, status, creation_date, closing_date)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    ticket_dict["client"],
                    ticket_dict["service"],
                    ticket_dict["incident_id"],
                    ticket_dict["status"],
                    ticket_dict["creation_date"],
                    ticket_dict["closing_date"]
                )
            )
            ticket_dict["id"] = ticket_id
        else:
            self.execute(
                """
                UPDATE tickets
                SET client=?, service=?, incident_id=?, status=?, creation_date=?, closing_date=?
                WHERE id=?
                """,
                (
                    ticket_dict["client"],
                    ticket_dict["service"],
                    ticket_dict["incident_id"],
                    ticket_dict["status"],
                    ticket_dict["creation_date"],
                    ticket_dict["closing_date"],
                    ticket_dict["id"]
                )
            )
        return ticket_dict

    def delete_ticket(self, ticket_id):
        self.execute("DELETE FROM tickets WHERE id=?", (ticket_id,))

    # ------------------------------
    # CRUD de cliente
    # ------------------------------
    def get_all_clients(self):
        return self.fetchall("SELECT * FROM clients")

    def get_client(self, client_id):
        return self.fetchone("SELECT * FROM clients WHERE id=?", (client_id,))

    def save_client(self, client_dict):
        if "id" not in client_dict or client_dict["id"] is None:
            client_id = self.execute(
                "INSERT INTO clients (name, email, phone_number) VALUES (?, ?, ?)",
                (
                client_dict["name"], 
                client_dict["email"], 
                client_dict["phone_number"]
                )
            )
            client_dict["id"] = client_id
        else:
            self.execute(
                "UPDATE clients SET name=?, email=?, phone_number=? WHERE id=?",
                (
                client_dict["name"], 
                client_dict["email"], 
                client_dict["phone_number"], 
                client_dict["id"]
                )
            )
        return client_dict

    def delete_client(self, client_id):
        self.execute("DELETE FROM clients WHERE id=?", (client_id,))

