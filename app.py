import sqlite3
import qrcode
from flask import Flask, render_template, request, redirect, url_for, send_file
from io import BytesIO

app = Flask(__name__)

DATABASE = 'database.db'

# Database initialization function
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        );
    ''')
    cursor.execute('PRAGMA journal_mode=WAL;')
    conn.commit()
    conn.close()

# Initialize the database when the app starts
init_db()

# Function to generate QR code for the "create ticket" page
def generate_qr_code():
    # URL of the create-ticket page (this would be dynamic based on your setup)
    create_ticket_url = url_for('create_ticket', _external=True)  # _external generates a full URL

    # Generate the QR code
    img = qrcode.make(create_ticket_url)

    # Save the image to a BytesIO object so it can be sent directly as a response
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return img_io

@app.route('/')
def home():
    # Generate the QR code for the create ticket URL
    img_io = generate_qr_code()

    # Display the QR code and provide a link to create the ticket
    return render_template('index.html', qr_code=img_io)

@app.route('/create-ticket', methods=['GET', 'POST'])
def create_ticket():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']

        # Insert the ticket data into the database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tickets (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
        conn.close()

        # Return a confirmation message
        return render_template('ticket.html', name=name)

    # Display the ticket creation form
    return render_template('create_ticket.html')

@app.route('/qr-code')
def qr_code():
    # Generate and send QR code image for download
    img_io = generate_qr_code()
    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='ticket_qr_code.png')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
