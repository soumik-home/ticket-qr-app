import sqlite3
from flask import Flask, request, render_template, g

app = Flask(__name__)

DATABASE = 'database.db'

# Database initialization function
def init_db():
    """Initializes the database and creates the tickets table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE)  # Create or open the database file
    cursor = conn.cursor()

    # Create the tickets table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        );
    ''')

    # Enable WAL mode for better concurrency
    cursor.execute('PRAGMA journal_mode=WAL;')
    conn.commit()  # Commit the changes
    conn.close()   # Close the database connection

# Initialize the database when the app starts
init_db()

# Database connection setup with WAL mode enabled
def get_db():
    """Open a new database connection if none exists yet."""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(DATABASE, check_same_thread=False)
        g.sqlite_db.row_factory = sqlite3.Row  # Allows access by column name
        # Enable WAL mode for better concurrency
        g.sqlite_db.execute('PRAGMA journal_mode=WAL;')
        g.sqlite_db.commit()
    return g.sqlite_db

# Route to view all tickets (for debugging purposes)
@app.route('/')
def home():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets;")
    result = cursor.fetchall()
    conn.close()
    return render_template('index.html', result=result)

# Route to create a new ticket (POST)
@app.route('/create-ticket', methods=['POST'])
def create_ticket():
    # Get the data from the form
    name = request.form['name']
    email = request.form['email']
    
    # Insert the ticket info into the database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tickets (name, email) VALUES (?, ?)", (name, email))
    conn.commit()  # Commit the transaction
    conn.close()
    
    return render_template('ticket.html', name=name)

# Close the database connection after each request
@app.teardown_appcontext
def close_db(error):
    """Closes the database after each request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

if __name__ == '__main__':
    app.run(debug=True)
