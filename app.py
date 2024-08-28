from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
import random
import sqlite3  # Example using SQLite for database
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yagmail
import mongoDB
from datetime import datetime

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



# Route to serve the reset password HTML file
@app.route('/reset_page')
def reset_page():
    return render_template('fgtpswd.html')

# Route to handle login requests
@app.route('/login', methods=['POST'])
def login():
    
    #get username and password
    data = request.get_json()
    username_or_email = data.get('username')
    password = data.get('password')
    

    # Basic validation
    if not username_or_email or not password:
        return jsonify({"status": "fail", "message": "Username and password are required"})
    
    success = mongoDB.verify(password,username_or_email)
    
    if success:
        # In a real application, you'd set a session or token here
        return jsonify({"status": "success", "message": "Login successful"})
    else:
        return jsonify({"status": "fail", "message": "Invalid username or password"})
    

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

#route to handle sending verification email
@app.route('/send_vericode', methods=['POST'])
def send_vericode():
    #fetch user data
    data = request.get_json()
    user_email = data.get('email')
    
    #check does the email exists
    email_exists = mongoDB.check_user_value("email",user_email)
    if not email_exists:
        return jsonify({"status": "fail","message": "email doesnt exists"})
    
    #setup information required to send the email
    server = 'smtp.gmail.com'
    port = 587
    username = "dinosauryeo@gmail.com"
    password = "jucvnvbkwtgcehjo"
    
    #genereate the verification code
    verification_code = random.randint(100000, 999999)
    
    #construct the email body
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = user_email
    msg['Subject'] = "Verification code to reset password"
    body = "Your verification code is " + str(verification_code) +" ,please use this within one minute"
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(server, port) as server:
            #create connection
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls() 
            
            #login and send the mail
            server.login(username, password)
            server.sendmail(username, user_email, msg.as_string())
            
            #store the verification code in the system
            mongoDB.input_user_data(user_email,"verification_code",verification_code)
            mongoDB.input_user_data(user_email,"vericode_date_sent",datetime.now())
            return jsonify({"status": "success","message": "Verification code sent successfully, please use it within one minute"})
    
    except Exception as e:
        print(f"Failed to send email: {e}")
        return jsonify({"status": "fail","message": "Failed to send email"})
    
#route to handle reseting and relogin 
@app.route('/reset_password', methods=['POST'])
def relogin():
    data = request.get_json()
    email = data.get('email')
    vericode = data.get('vericode')
    resetpassword = data.get('resetpassword')
    confirmpassword = data.get('confirmpassword')
    
    #check all field exists
    if not email or not vericode or not resetpassword or not confirmpassword:
        return jsonify({"status": "fail","message": "please enter all field"})
    print("all field exists")
    
    #check does the two password match up
    if resetpassword == confirmpassword:
        print("two password match")
        
        response = mongoDB.veri_vericode(email,vericode,resetpassword)
        #check does the vericode match up with any email in the database
        if response == 1:
            print("reset successful")
            return jsonify({"status": 'success',"message": "success"})
        elif response == 2:
            print("vericode doesn't match")
            return jsonify({"status": "fail","message": "vericode doesn't match"})
        elif response == 3:
            print("vericode expired")
            return jsonify({"status": "fail","message": "vericode expired"})
    else:
        return jsonify({"status": "fail","message": "password doesn't match"})
    
if __name__ == '__main__':
    app.run(debug=True)


