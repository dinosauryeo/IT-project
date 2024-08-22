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

# Route to serve the reset password HTML file
@app.route('/reset_password')
def reset_page():
    return render_template('fgtpswd.html')

@app.route('/test-static')
def test_static():
    return app.send_static_file('styles.css')  

# Route to handle login requests
@app.route('/login', methods=['POST'])
def login():
    
    #get username and password
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    df = pd.DataFrame(pd.read_csv("loginDatabase.csv"))
    password_row = df[df['password'].astype(str) == password]
    
    print(type(password))
    print(password_row.empty)
    
    # Basic validation
    if not username or not password:
        return jsonify({"status": "fail", "message": "Username and password are required"})
    
    # Authenticate user
    if not password_row.empty:
        user_row = password_row[password_row['username'] == username]
        if not user_row.empty:
            # In a real application, you'd set a session or token here
            return jsonify({"status": "success", "message": "Login successful"})
    else:
        return jsonify({"status": "fail", "message": "Invalid username or password"})
        return "error"

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

