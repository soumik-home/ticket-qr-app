from flask import Flask, render_template, request, redirect, url_for, send_file
import qrcode
from io import BytesIO
import uuid

app = Flask(__name__)

# In-memory storage for simplicity (not production-safe)
users = {}

@app.route('/')
def home():
    """Homepage with a QR code."""
    unique_id = str(uuid.uuid4())
    link = url_for('create_ticket', unique_id=unique_id, _external=True)
    
    # Generate QR code
    qr = qrcode.QRCode(box_size=10, border=5)
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code as bytes
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

@app.route('/create-ticket/<unique_id>', methods=['GET', 'POST'])
def create_ticket(unique_id):
    """Page to input user details and generate a ticket."""
    if request.method == 'POST':
        # Save user details
        name = request.form['name']
        email = request.form['email']
        users[unique_id] = {'name': name, 'email': email}
        
        # Redirect to the ticket page
        return redirect(url_for('ticket', unique_id=unique_id))
    
    return render_template('create_ticket.html')

@app.route('/ticket/<unique_id>')
def ticket(unique_id):
    """Display the personalized ticket."""
    user = users.get(unique_id)
    if not user:
        return "Invalid ticket ID!", 404
    
    name = user['name']
    email = user['email']
    
    return render_template('ticket.html', name=name, email=email)

if __name__ == '__main__':
    app.run(debug=True)
