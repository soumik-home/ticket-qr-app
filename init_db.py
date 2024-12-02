import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')  # Create the database file
    cursor = conn.cursor()

    # Create the tickets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        );
    ''')

    # Enable WAL mode for better concurrency
    cursor.execute('PRAGMA journal_mode=WAL;')
    conn.commit()
    conn.close()

# Call the function to initialize the database
if __name__ == '__main__':
    init_db()
    print("Database initialized with WAL mode enabled.")
