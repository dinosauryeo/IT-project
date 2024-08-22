from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
import sqlite3  # Example using SQLite for database

current_dir = os.path.dirname(os.path.abspath(__file__))

# Initialize the app with custom static and template folder paths
app = Flask(__name__, 
            static_folder=os.path.join(current_dir, 'templates','static'), 
            template_folder=os.path.join(current_dir, 'templates'))

print("Static Folder:", app.static_folder)
print("Template Folder:", app.template_folder)

# Set upload folder path
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Route to serve the login HTML file
@app.route('/')
def login_page():
    return render_template('login.html')

# Route to serve the file upload HTML file
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/test-static')
def test_static():
    return app.send_static_file('styles.css')  

# Route to handle login requests
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Connect to your database
    conn = sqlite3.connect('login_database.db')
    cursor = conn.cursor()

    # Query to check credentials
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({'status': 'success', 'message': 'Login successful'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

# Route to handle file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        # Save the file to the server
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Process the file as needed (e.g., store data in database)
        if file.filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(filepath)
        else:
            return jsonify({'error': 'Invalid file format'}), 400

        # Process the dataframe or store it as needed
        # For example, you might save data to a database or perform some analysis

        return jsonify({'message': 'File uploaded successfully'})

if __name__ == '__main__':
    app.run(debug=True)

