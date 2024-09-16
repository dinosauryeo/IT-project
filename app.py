from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
import random
import sqlite3  # Example using SQLite for database
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import yagmail
import mongoDB
from datetime import datetime
from mongoDB import insert_student_data
from mongoDB import generate_timetable_for_students
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


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

@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/student')
def student_page():
    return render_template('student.html')

@app.route('/generate')
def generate_page():
    return render_template('generate.html')

# Route to serve the reset password HTML file
@app.route('/reset_page')
def reset_page():
    return render_template('fgtpswd.html')

@app.route('/logout')
def logout_page():
    return render_template('login.html')

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
    


@app.route('/createsubject', methods=['GET', 'POST'])
def createsubject_page():
    if request.method == 'GET':
        return render_template('create_subject.html')

    data = request.json
    print(f"Received data: {data}")  # Log received data

    year = data.get('year')
    semester = data.get('semester')
    campus = data.get('campus')
    coordinator = data.get('coordinator')
    subject_name = data.get('subjectName')
    subject_code = data.get('subjectCode')
    sections = data.get('sections')
    
    subject_data = {
        'year': year,
        'semester': semester,
        'campus': campus,
        'coordinator': coordinator,
        'subjectName': subject_name,
        'subjectCode': subject_code,
        'sections': sections
    }

    try:
        inserted_id = mongoDB.insert_subject(subject_data,year, semester)
        print(f"Inserted document ID: {inserted_id}")  # Log inserted document ID
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(f"Error inserting subject: {e}")  # Log error message
        return jsonify({'status': 'error', 'message': 'Failed to create subject'}), 500

    
@app.route('/getsubjects', methods=['GET'])
def get_subjects():
    try:
        client = login()  # Connect to MongoDB
        db = client['IT-project']
        collection = db['Subjects-Details']  # Collection where your subjects are stored

        # Fetch all subjects from the collection
        subjects = list(collection.find({}, {'_id': 0, 'year': 1, 'semester': 1, 'campus': 1, 'coordinator': 1, 'subjectName': 1, 'subjectCode': 1, 'sections': 1}))
        
        # Debugging output to check the structure
        print("Subjects fetched from MongoDB:", subjects)

        return jsonify(subjects), 200  # Return JSON data
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to fetch subjects'}), 500


# 14/09 10:06 last modify
# Route to handle file upload
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return render_template('upload.html')
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    year = request.form.get('year')  # Get the year from the form data
    semester = request.form.get('semester')  # Get the semester from the form data

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        # Create a directory with year and semester if it doesn't exist
        folder_name = f"{year}_{semester}"
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        # Save the file to the server inside the year_semester folder
        filepath = os.path.join(folder_path, file.filename)
        file.save(filepath)

        # Process the file as needed (e.g., store data in database)
        if file.filename.endswith('.csv'):
            # Call the function to insert data into MongoDB
            insert_student_data(filepath, year, semester)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(filepath)
            # Optionally handle Excel files here
        else:
            return jsonify({'error': 'Invalid file format'}), 400

        return jsonify({'message': 'File uploaded and data stored successfully'})

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
    
    #genereate the verification code
    verification_code = random.randint(100000, 999999)
    
    respons = send_email({user_email:["Verification code to reset password", "Your verification code is " + str(verification_code) +" ,please use this within one minute"]})
    
    if respons == 1:
        #store the verification code in the system
        mongoDB.input_user_data(user_email,"verification_code",verification_code)
        mongoDB.input_user_data(user_email,"vericode_date_sent",datetime.now())
        return jsonify({"status": "success","message": "Verification code sent successfully, please use it within one minute"})
    
    else:
        print(f"Failed to send email: {respons}")
        return jsonify({"status": "fail","message": "Failed to send email"})
    
#route to handle sending verification email
@app.route('/send_timetable', methods=['POST'])    
def send_timetable():
    #have to add logic to combine the timetable with student's email(work to be done)
    respons = send_email({"jetng111@gmail.com":["student timetable", "this would be the student timetable", "excel_sample.xlsx"]})
    
    if respons == 1:
        return jsonify({"status": "success","message": "timetable sent to student!"})
    
    else:
        print(f"Failed to send email: {respons}")
        return jsonify({"status": "fail","message": "Failed to send email"})
    

#to send email out to a list of email, using a dictionary structure where the key would be receiver email and the value would be a list where the first element
#would be the email subject, second element would be the email body and possibiliy a third element which would be a excel file to send
def send_email(email_list):
    #setup information required to send the email
    server = 'smtp.gmail.com'
    port = 587
    username = "dinosauryeo@gmail.com"
    password = "jucvnvbkwtgcehjo"
    
    for key in email_list.keys():
        print(key)
        #construct the email body
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = key
        msg['Subject'] = email_list[key][0]
        body = email_list[key][1]
        msg.attach(MIMEText(body, 'plain'))
        
        #attch the excel file if it exists
        if(len(email_list[key]) == 3):
            file_path = email_list[key][2] 
            with open(file_path, "rb") as attachment:
                # Create a MIMEBase object and set its payload to the file content
                mime_base = MIMEBase('application', 'octet-stream')
                mime_base.set_payload(attachment.read())
            
                # Encode the payload in base64
                encoders.encode_base64(mime_base)
                
                # Add a header to the attachment
                mime_base.add_header('Content-Disposition', f'attachment; filename="{file_path.split("/")[-1]}"')
                
                # Attach the Excel file to the message
                msg.attach(mime_base)
            

        try:
            with smtplib.SMTP(server, port) as server:
                #create connection
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls() 
                
                #login and send the mail
                server.login(username, password)
                server.sendmail(username, key, msg.as_string())
        
        except Exception as e:
            return e
    
    return 1

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
    
# if __name__ == '__main__':
#     app.run(debug=True)


@app.route('/generate_timetable', methods=['POST'])
def generate_timetable():
    try:
        client = MongoClient("mongodb+srv://dinosauryeo:6OHYa6vF6YUCk48K@cluster0.dajn796.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", server_api=ServerApi('1'))
        timetable_db = client['Students-Timetable']
        timetable_collection = timetable_db['Timetables']
        # 调用生成timetable的函数
        timetables, error_messages = generate_timetable_for_students()

        if not timetables:
            return jsonify({'status': 'error', 'message': 'Failed to generate timetable'})
        
        if error_messages:
            return jsonify({'status': 'error', 'message': error_messages})

        # 存储到 MongoDB 的 Timetables 集合
        for timetable in timetables:
            timetable_collection.insert_one(timetable)

        return jsonify({'status': 'success', 'message': 'Timetable generated and saved successfully!'})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'An error occurred while generating the timetable'})
    

if __name__ == '__main__':
    app.run(debug=True)
    