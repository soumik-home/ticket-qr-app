from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import uuid
import qrcode
import io

app = Flask(__name__)
DATABASE = 'tickets.db'


# Database setup and connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # To return rows as dictionaries
    return conn


def init_db():
    """Initialize the database with the tickets table."""
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                ticket_id TEXT UNIQUE NOT NULL
            )
        ''')
        conn.commit()


# Helper to generate a unique ticket ID
def generate_ticket_id():
    return str(uuid.uuid4())


# Routes
@app.route('/')
def home():
    """Homepage to display the QR code for /create-ticket."""
    # Generate a QR code for the /create-ticket URL
    qr_url = request.url_root + 'create-ticket'  # e.g., http://127.0.0.1:5000/create-ticket
    qr = qrcode.make(qr_url)

    # Save the QR code to a BytesIO stream for rendering
    qr_stream = io.BytesIO()
    qr.save(qr_stream, 'PNG')
    qr_stream.seek(0)

    return render_template('home.html', qr_code=qr_stream)


@app.route('/create-ticket', methods=['GET', 'POST'])
def create_ticket():
    """Handle ticket creation and prevent duplicates."""
    if request.method == 'GET':
        # Display the form
        return render_template('create_ticket.html')

    elif request.method == 'POST':
        # Handle form submission
        name = request.form['name']
        email = request.form['email']
        ticket_id = generate_ticket_id()

        # Store in the database
        db = get_db()
        try:
            db.execute(
                'INSERT INTO tickets (name, email, ticket_id) VALUES (?, ?, ?)',
                (name, email, ticket_id)
            )
            db.commit()
            return render_template('ticket.html', name=name, ticket_id=ticket_id)
        except sqlite3.IntegrityError:
            return "Error: This email has already been used to create a ticket."


@app.route('/list-tickets')
def list_tickets():
    """Display all stored tickets."""
    db = get_db()
    tickets = db.execute('SELECT * FROM tickets').fetchall()
    return render_template('list_tickets.html', tickets=tickets)


# Initialize the database on app startup
with app.app_context():
    init_db()


if __name__ == '__main__':
    app.run(debug=True)
