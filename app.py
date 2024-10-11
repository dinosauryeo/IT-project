from flask import Flask, render_template, request, jsonify, session 
import os
import pandas as pd
import random
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
import csv
from bson import ObjectId
import logging
import re
import traceback
from download import download_all,download_one
from flask_bcrypt import Bcrypt
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)

current_dir = os.path.dirname(os.path.abspath(__file__))

# Initialize the app with custom static and template folder paths
app = Flask(__name__, 
            static_folder=os.path.join(current_dir, 'templates','static'), 
            template_folder=os.path.join(current_dir, 'templates'))
app.secret_key="secret_key"

print("Static Folder:", app.static_folder)
print("Template Folder:", app.template_folder)

# Set upload folder path
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
bcrypt = Bcrypt(app)

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Route to serve the login HTML file
@app.route('/')
def login_page():
    return render_template('Login.html')

@app.route('/home', methods=['GET'])
def home_page():
    print(session)
    if "logged_in" in session:
        return render_template('home.html')
    else:
        return render_template('Login.html')

@app.route('/favicon.ico')

@app.route('/student')
def student_page():
    if "logged_in" in session:
        return render_template('student.html')
    else:
        return render_template('Login.html')

@app.route('/generate')
def generate_page():
    if "logged_in" in session:
        return render_template('generate.html')
    else:
        return render_template('Login.html')

# Route to serve the reset password HTML file
@app.route('/reset_page')
def reset_page():
    return render_template('fgtpswd.html')

@app.route('/logout')
def logout_page():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('accessLevel',None)
    return render_template('Login.html')

#10/10 15:42 last modify
@app.route('/register', methods=['GET', 'POST'])
def register():
    client = mongoDB.login()
    db = client['IT-project']
    users_collection = db['User-data']

    if request.method == 'POST':
        if(session.get('accessLevel') == 0):
            data = request.json
            existing_user = users_collection.find_one({'$or': [{'username': data['username']}, {'email': data['email']}]})
            
            if existing_user:
                return jsonify({'status': 'error', 'message': 'Username or email already exists'})
            
            #hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            new_user = {
                'username': data['username'],
                'email': data['email'],
                'password': data['password'],
                'accessLevel':"1",
                'verification_code': None,
                'vericode_date_sent':datetime(1900, 1, 1, 0, 0, 0)
            }
            users_collection.insert_one(new_user)
            return jsonify({'status': 'success', 'message': 'User registered successfully'})
        
        else:
            return jsonify({'status': 'error', 'message': 'unallowed for current access level'})
    
    return render_template('Registration.html')

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
    
    if success != False:
        # In a real application, you'd set a session or token here
        session['logged_in'] = True
        session['username'] = username_or_email
        session['accessLevel'] = success
        print(f"access level:{success}\n")
        return jsonify({"status": "success", "message": "Login successful"})
    else:
        return jsonify({"status": "fail", "message": "Invalid username or password"})
    
# 09/10 12:53 last modify
@app.route('/api/get-year-semesters')
def get_year_semesters():
    client = mongoDB.login()
    all_dbs = client.list_database_names()  # List all database names

    # Define the valid semester names
    valid_terms = ["Semester1", "Semester2", "Winter", "Summer"]
    
    # Filter database names that match the year_semester pattern
    filtered_dbs = [
        db_name for db_name in all_dbs
        if "_" in db_name and
           db_name.split('_')[0].isdigit() and
           db_name.split('_')[1] in valid_terms
    ]

    client.close()
    return jsonify(filtered_dbs)

#09/10 1:40 last modify
@app.route('/get-enrolled-students', methods=['GET'])
def get_enrolled_students():
    try:
        subject_code = request.args.get('subject_code')
        year = request.args.get('year')
        semester = request.args.get('semester')
        campus = request.args.get('campus')
        folder_prefix = request.args.get('folder_prefix')

        print(f"Received request with parameters: subject_code={subject_code}, year={year}, semester={semester}, campus={campus}, folder_prefix={folder_prefix}")

        # Connect to MongoDB
        client = mongoDB.login()

        # Find the correct database
        db_name = f'{year}_{semester}'
        db = client[db_name]
        print(f"Accessing database: {db_name}")

        # Find the correct collection (folder)
        folder_pattern = re.compile(f"^{re.escape(folder_prefix)}.*{re.escape(campus)}.*")
        collections = db.list_collection_names()
        matching_collections = [coll for coll in collections if folder_pattern.match(coll)]

        if not matching_collections:
            print(f"No collection found matching pattern: {folder_pattern}")
            return jsonify({"count": 0, "students": []})

        collection_name = matching_collections[0]
        collection = db[collection_name]
        print(f"Found collection: {collection_name}")

        # Get all students from the collection
        students = list(collection.find({}))
        print(f"Number of students in collection: {len(students)}")

        # Filter students enrolled in the subject
        enrolled_students = [
            student for student in students
            if student.get(subject_code) == "ENRL"
        ]
        enrolled_count = len(enrolled_students)
        print(f"Number of enrolled students for subject {subject_code}: {enrolled_count}")

        # Return only necessary information
        result = [
            {
                "StudentID": student.get("StudentID"),
                "Student_Name": student.get("Student Name")
            }
            for student in enrolled_students
        ]

        print(f"Returning {enrolled_count} students")
        return jsonify({"count": enrolled_count, "students": result})
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/location')
def location_page():
    if "logged_in" in session:
        return render_template('location.html')
    else:
        return render_template('Login.html')

@app.route('/get_buildings/<campus>', methods=['GET'])
def get_buildings(campus):
    client = mongoDB.login()
    db = client['IT-project']
    campus_collection = db[f'{campus}_Locations']
    buildings = list(campus_collection.distinct('building'))
    return jsonify(buildings)

@app.route('/add_buildings', methods=['POST'])
def add_buildings():
    client = mongoDB.login()
    db = client['IT-project']
    data = request.json
    campus = data['campus']
    buildings = data['buildings']
    campus_collection = db[f'{campus}_Locations']
    
    for building in buildings:
        existing_building = campus_collection.find_one({'building': building})
        if not existing_building:
            campus_collection.insert_one({'campus': campus, 'building': building})
    
    return jsonify({'success': True}), 201

@app.route('/add_classrooms', methods=['POST'])
def add_classrooms():
    client = mongoDB.login()
    db = client['IT-project']
    data = request.json
    campus = data['campus']
    building = data['building']
    classroom_data = data['classroomData']
    campus_collection = db[f'{campus}_Locations']
    
    for level_data in classroom_data:
        level = level_data['level']
        classrooms = level_data['classrooms']
        for classroom in classrooms:
            campus_collection.insert_one({
                'campus': campus,
                'building': building,
                'level': level,
                'classroom': classroom
            })
    
    return jsonify({'success': True}), 201

@app.route('/get_locations', methods=['GET'])
def get_locations():
    client = mongoDB.login()
    db = client['IT-project']
    locations = []
    for campus in ['Melbourne', 'Geelong', 'Adelaide', 'Sydney']:
        campus_collection = db[f'{campus}_Locations']
        campus_locations = list(campus_collection.find({'classroom': {'$exists': True}}))
        for loc in campus_locations:
            loc['_id'] = str(loc['_id'])  # Convert ObjectId to string
        locations.extend(campus_locations)
    return jsonify(locations)


@app.route('/delete_location/<location_id>', methods=['DELETE'])
def delete_location(location_id):
    client = mongoDB.login()
    db = client['IT-project']
    for campus in ['Melbourne', 'Geelong', 'Adelaide', 'Sydney']:
        campus_collection = db[f'{campus}_Locations']
        result = campus_collection.delete_one({'_id': ObjectId(location_id)})
        if result.deleted_count > 0:
            return jsonify({'success': True}), 200
    return jsonify({'success': False, 'error': 'Location not found'}), 404

@app.route('/delete_all_buildings_in_campus/<campus>', methods=['DELETE'])
def delete_all_buildings_in_campus(campus):
    client = mongoDB.login()
    db = client['IT-project']
    campus_collection = db[f'{campus}_Locations']
    
    result = campus_collection.delete_many({})
    
    if result.deleted_count > 0:
        return jsonify({'success': True, 'message': f'Deleted {result.deleted_count} documents'}), 200
    else:
        return jsonify({'success': False, 'message': 'No documents found to delete'}), 404

@app.route('/delete_all_classrooms_in_building/<campus>/<building>', methods=['DELETE'])
def delete_all_classrooms_in_building(campus, building):
    client = mongoDB.login()
    db = client['IT-project']
    campus_collection = db[f'{campus}_Locations']
    
    result = campus_collection.delete_many({'building': building, 'classroom': {'$exists': True}})
    
    if result.deleted_count > 0:
        return jsonify({'success': True, 'message': f'Deleted {result.deleted_count} classrooms'}), 200
    else:
        return jsonify({'success': False, 'message': 'No classrooms found to delete'}), 404


@app.route('/editsubject', methods=['GET'])
def editsubject_page():
    return render_template('EditSubjects.html')

@app.route('/get_subject_data', methods=['GET'])
def get_subject_data():
    client = mongoDB.login()
    
    year = request.args.get('year')
    semester = request.args.get('semester')
    subject_code = request.args.get('code')
    campus = request.args.get('campus')

    logging.debug(f"Fetching subject data: year={year}, semester={semester}, code={subject_code}, campus={campus}")

    if not all([year, semester, subject_code, campus]):
        return jsonify({'status': 'error', 'message': 'Missing required parameters'}), 400

    year_semester = f"{year}_{semester}"
    db = client[year_semester]
    collection = db['Subjects-Details']

    subject = collection.find_one({'subjectCode': subject_code, 'campus': campus})
    if subject:
        # Convert ObjectId to string for JSON serialization
        subject['_id'] = str(subject['_id'])
        logging.debug(f"Subject found: {subject}")
        return jsonify(subject), 200
    else:
        logging.warning(f"Subject not found: year={year}, semester={semester}, code={subject_code}, campus={campus}")
        return jsonify({'status': 'error', 'message': 'Subject not found'}), 404
    

@app.route('/editsubject', methods=['POST'])
def update_subject():
    client = mongoDB.login()
    
    try:
        subject_data = request.get_json()
        year = subject_data.get('year')
        semester = subject_data.get('semester')
        subject_code = subject_data.get('subjectCode')
        campus = subject_data.get('campus')

        logging.debug(f"Updating subject: year={year}, semester={semester}, code={subject_code}, campus={campus}")

        year_semester = f"{year}_{semester}"
        db = client[year_semester]
        collection = db['Subjects-Details']

        result = collection.update_one(
            {'subjectCode': subject_code, 'campus': campus},
            {'$set': subject_data}
        )

        if result.matched_count == 0:
            logging.warning(f"Subject not found for update: year={year}, semester={semester}, code={subject_code}, campus={campus}")
            return jsonify({'status': 'error', 'message': 'Subject not found'}), 404
        else:
            logging.info(f"Subject updated successfully: year={year}, semester={semester}, code={subject_code}, campus={campus}")
            return jsonify({'status': 'success', 'message': 'Subject updated successfully'}), 200

    except Exception as e:
        logging.error(f"Error updating subject: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to update subject'}), 500
    
    
@app.route('/get_campus_locations/<campus>', methods=['GET'])
def get_campus_locations(campus):
    client = mongoDB.login()
    db = client['IT-project']
    campus_collection = db[f'{campus}_Locations']
    locations = list(campus_collection.find({}, {'_id': 0}))
    return jsonify(locations)

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



# 08/10 7:30 last modify
@app.route('/getsubjects', methods=['GET'])
def get_subjects():
    year_semester = request.args.get('year_semester')
    campus = request.args.get('campus')

    if not year_semester or not campus:
        return jsonify({'status': 'error', 'message': 'Year/semester and campus are required'}), 400

    try:
        client = mongoDB.login()
        db = client[year_semester]  # Connect to the specific year and semester database
        collection = db['Subjects-Details']  # Collection where your subjects are stored
        
        # Fetch subjects for the specified campus
        subjects = list(collection.find({'campus': campus}, {'_id': 0, 'subjectName': 1, 'subjectCode': 1, 'coordinator': 1, 'campus': 1}))
        
        subject_list = [
            {
                'subjectString': f"{subject.get('subjectCode', 'N/A')} - {subject.get('subjectName', 'N/A')}",
                'subjectCode': subject.get('subjectCode', 'N/A'),
                'coordinator': subject.get('coordinator', 'N/A'),
                'campus': subject.get('campus', 'N/A')
            }
            for subject in subjects
        ]
        
        return jsonify(subject_list), 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to fetch subjects'}), 500
    

# 08/10 6:59 last modify
@app.route('/getsubjectdetails', methods=['GET'])
def get_subject_details():
    subject_code = request.args.get('subject_code')
    year = request.args.get('year')
    semester = request.args.get('semester')
    campus = request.args.get('campus')

    print(f"Received subject_code: {subject_code}")
    print(f"Received year: {year}")
    print(f"Received semester: {semester}")
    print(f"Received campus: {campus}")

    if not all([subject_code, year, semester, campus]):
        return jsonify({'status': 'error', 'message': 'Subject code, year, semester, and campus are required'}), 400

    try:
        client = mongoDB.login()
        db = client[f"{year}_{semester}"]  # Connect to the specific year and semester database
        collection = db['Subjects-Details']  # Collection where your subjects are stored
        
        subject = collection.find_one({'subjectCode': subject_code, 'campus': campus}, {'_id': 0})
        
        print(f"Found subject: {subject}")  # Check if the subject is found
        
        if subject:
            return jsonify(subject), 200
        else:
            return jsonify({'status': 'error', 'message': 'Subject not found'}), 404
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to fetch subject details'}), 500

# 08/10 4:10 last modify
@app.route('/inherit_subjects', methods=['POST'])
def inherit_subjects():
    data = request.json
    from_year_semester = f"{data['fromYear']}_{data['fromSemester']}"
    to_year_semester = f"{data['toYear']}_{data['toSemester']}"

    try:
        client = mongoDB.login()
        # Source database and collection
        from_db = client[from_year_semester]
        from_collection = from_db['Subjects-Details']

        # Destination database and collection
        to_db = client[to_year_semester]
        to_collection = to_db['Subjects-Details']

        # Fetch all documents from the source collection
        subjects = list(from_collection.find({}, {'_id': 0}))  # Exclude MongoDB _id

        # Update year and semester in each document
        for subject in subjects:
            subject['year'] = data['toYear']
            subject['semester'] = data['toSemester']

        # Insert the modified documents into the destination collection
        if subjects:
            to_collection.insert_many(subjects)

        return jsonify({'status': 'success', 'message': f'Inherited {len(subjects)} subjects'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

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
    
    respons = send_email([user_email, "Verification code to reset password", "Your verification code is " + str(verification_code) +" ,please use this within one minute"])
    
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
    
"""
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
"""

def send_email(email_list):
    #setup information required to send the email
    server = 'smtp.gmail.com'
    port = 587
    username = "dinosauryeo@gmail.com"
    password = "jucvnvbkwtgcehjo"
    
    try:
        with smtplib.SMTP(server, port) as server:
            #create connection
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls() 
                
            #login and send the mail
            server.login(username, password)
            
            email = email_list[0]
            
            #construct the email body
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = email
            msg['Subject'] = email_list[1]
            body = email_list[2]
            msg.attach(MIMEText(body, 'plain'))
                
            #attch the excel file if it exists
            if(len(email_list) == 4):
                file_path = email_list[3] 
                print(f"file path:{file_path}\n")
                
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
            
            server.sendmail(username, email, msg.as_string())
        
    except Exception as e:
        return False
    
    return True

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
    


# @app.route('/generate_timetable', methods=['POST'])
# def generate_timetable():
#     try:
#         client = MongoClient("mongodb+srv://dinosauryeo:6OHYa6vF6YUCk48K@cluster0.dajn796.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", server_api=ServerApi('1'))
#         timetable_db = client['Students-Timetable']
#         timetable_collection = timetable_db['Timetables']
#         # Call the function that generates the timetable
#         timetables, error_messages = generate_timetable_for_students()

#         if not timetables:
#             return jsonify({'status': 'error', 'message': 'Failed to generate timetable'})
        
#         if error_messages:
#             return jsonify({'status': 'error', 'message': error_messages})

#         # Stored in MongoDB's Timetables collection
#         for timetable in timetables:
#             timetable_collection.insert_one(timetable)

#         return jsonify({'status': 'success', 'message': 'Timetable generated and saved successfully!'})

#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return jsonify({'status': 'error', 'message': 'An error occurred while generating the timetable'})

# @app.route('/generate_timetable', methods=['POST'])
# def generate_timetable():
#     try:
#         # Get year and semester from the request body
#         data = request.get_json()
#         year = data.get('year')
#         semester = data.get('semester')
        
#         if not year or not semester:
#             return jsonify({'status': 'error', 'message': 'Year and semester are required'})

#         # Dynamically select the database based on year and semester
#         database_name = f"{year}_{semester}"
        
#         client = MongoClient("mongodb+srv://dinosauryeo:6OHYa6vF6YUCk48K@cluster0.dajn796.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", server_api=ServerApi('1'))
#         timetable_db = client[database_name]
#         timetable_collection = timetable_db['Timetables']

#         # Call the function that generates the timetable
#         timetables, error_messages = generate_timetable_for_students(database_name)

#         if not timetables:
#             return jsonify({'status': 'error', 'message': 'Failed to generate timetable'})
        
#         if error_messages:
#             return jsonify({'status': 'error', 'message': error_messages})

#         # Store the generated timetables in the dynamically selected database
#         for timetable in timetables:
#             course_name = timetable.get('CourseName', 'UnknownCourse')
#             campus_name = timetable.get('Campus', 'UnknownCampus')
#             file_name = f"Timetable-{course_name}-{campus_name}.json"
            
#             # Log the file name or save it as part of the database entry if needed
#             print(f"Generated file name: {file_name}")
            
#             # Insert the timetable into the MongoDB collection
#             timetable_collection.insert_one(timetable)

#         return jsonify({'status': 'success', 'message': 'Timetable generated and saved successfully!'})

#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return jsonify({'status': 'error', 'message': 'An error occurred while generating the timetable'})

@app.route('/generate_timetable', methods=['POST'])
def generate_timetable():
    try:
        # 从请求体中获取年份和学期
        data = request.get_json()
        year = data.get('year')
        semester = data.get('semester')

        # 验证年份和学期是否提供
        if not year or not semester:
            return jsonify({'status': 'error', 'message': 'Year and semester are required'})

        # 动态选择基于年份和学期的数据库
        database_name = f"{year}_{semester}"

        # 调用生成时间表的函数
        timetables, error_messages = generate_timetable_for_students(database_name)

        if not timetables:
            return jsonify({'status': 'error', 'message': 'Failed to generate timetable'})

        if error_messages:
            return jsonify({'status': 'error', 'message': error_messages})

        return jsonify({'status': 'success', 'message': 'Timetable generated and saved successfully!'})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'An error occurred while generating the timetable'})




@app.route('/api/get-degrees', methods=['GET'])
def get_degrees():
    client = mongoDB.login()
    db = client["IT-project"]
    degrees_collection = db["Degrees"]
    degrees = list(degrees_collection.find({}, {"_id": 0, "name": 1}))
    return jsonify(degrees)

@app.route('/api/add-degree', methods=['POST'])
def add_degree():
    client = mongoDB.login()
    db = client["IT-project"]
    degrees_collection = db["Degrees"]
    try:
        new_degree = request.json.get('name')
        if new_degree:
            if degrees_collection.find_one({"name": new_degree}):
                return jsonify({"success": False, "message": "Degree already exists"})
            degrees_collection.insert_one({"name": new_degree})
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Invalid degree name"})
    except Exception as e:
        print(f"Error in add_degree: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "message": "Server error occurred"}), 500

@app.route('/api/remove-degree', methods=['POST'])
def remove_degree():
    client = mongoDB.login()
    db = client["IT-project"]
    degrees_collection = db["Degrees"]
    try:
        degree_to_remove = request.json.get('name')
        if degree_to_remove:
            result = degrees_collection.delete_one({"name": degree_to_remove})
            if result.deleted_count > 0:
                return jsonify({"success": True})
            return jsonify({"success": False, "message": "Degree not found"})
        return jsonify({"success": False, "message": "Invalid degree name"})
    except Exception as e:
        print(f"Error in remove_degree: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "message": "Server error occurred"}), 500

#09/10 4.47 last modify
@app.route('/get-enrolled-students-timetable', methods=['GET'])
def get_enrolled_students_timetable():
    try:
        year = request.args.get('year')
        semester = request.args.get('semester')
        campus = request.args.get('campus')
        folder_prefix = request.args.get('folder_prefix')
        degree_name = request.args.get('degree_name')
        sort_method = request.args.get('sort_method', 'alphabetical')

        print(f"Received request with parameters: year={year}, semester={semester}, campus={campus}, folder_prefix={folder_prefix}, degree_name={degree_name}, sort_method={sort_method}")

        # Check if all required parameters are provided
        if not all([year, semester, campus, folder_prefix, degree_name]):
            return jsonify({"error": "Missing required parameters"}), 400

        # Connect to MongoDB
        client = mongoDB.login()

        # Find the correct database
        db_name = f'{year}_{semester}'
        db = client[db_name]
        print(f"Accessing database: {db_name}")

        # Find the correct collection (folder)
        folder_pattern = re.compile(f"^{re.escape(folder_prefix)}.*{re.escape(degree_name)}.*{re.escape(campus)}.*")
        collections = db.list_collection_names()
        matching_collections = [coll for coll in collections if folder_pattern.match(coll)]

        if not matching_collections:
            print(f"No collection found matching pattern: {folder_pattern}")
            return jsonify({"count": 0, "students": []})

        collection_name = matching_collections[0]
        collection = db[collection_name]
        print(f"Found collection: {collection_name}")

        # Get all students from the collection
        students = list(collection.find({}))
        print(f"Number of students in collection: {len(students)}")

        # Extract necessary information
        result = []
        for student in students:
            student_data = {
                "StudentID": student.get("StudentID"),
                "Student_Name": student.get("Student Name"),
                "Course Start Date": student.get("Course Start Date"),
                "Course End Date": student.get("Course End Date"),
                "Enrolled_Subjects": [key for key, value in student.items() if value == "ENRL"]
            }
            result.append(student_data)

        # Apply sorting based on the sort_method
        if sort_method == 'alphabetical':
            result.sort(key=lambda x: x['Student_Name'])
        elif sort_method == 'reverse-alphabetical':
            result.sort(key=lambda x: x['Student_Name'], reverse=True)
        elif sort_method == 'id-ascending':
            result.sort(key=lambda x: x['StudentID'])
        elif sort_method == 'id-descending':
            result.sort(key=lambda x: x['StudentID'], reverse=True)
        elif sort_method == 'random':
            random.shuffle(result)

        print(f"Returning {len(result)} students")
        return jsonify({"count": len(result), "students": result})
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
'''
return student id and student name and send it to front end
'''
# @app.route('/students_timetable', methods=['GET'])
# def get_students():
#     client = mongoDB.login()
#     db = client['2019_Semester1']  # 选择数据库
#     collection = db['Students-Enrollment-Details-20240915_190953']  # 选择集合
#     try:
#         # 查询MongoDB中的所有学生数据
#         students = collection.find()
#         # 将查询结果转换为JSON格式
#         student_list = []
#         for student in students:
#             print(student['Student Name'])
#             student_list.append({
#                 'name': student.get('Student Name', 'No Name'),
#                 'id': student.get('StudentID', 'No ID'),
#                 'course': student.get('Course Name', 'No Course Name'),
#                 'campus': student.get('Campus', 'No Campus')
#             })
        
#         return jsonify(student_list), 200  # 返回JSON响应，状态码200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500  # 返回错误信息，状态码500'''
    
@app.route('/get-student-timetable')
def get_student_timetable():
    year = request.args.get('year')
    semester = request.args.get('semester')
    campus = request.args.get('campus')
    folder_prefix = request.args.get('folder_prefix')
    degree_name = request.args.get('degree_name')
    student_id = request.args.get('student_id')

    print(f"Received parameters: year={year}, semester={semester}, campus={campus}, folder_prefix={folder_prefix}, degree_name={degree_name}, student_id={student_id}")

    client = mongoDB.login()
    db_name = f'{year}_{semester}'
    db = client[db_name]

    print(f"Connected to database: {db_name}")

    folder_pattern = re.compile(f"^{re.escape(folder_prefix)}.*{re.escape(degree_name)}.*{re.escape(campus)}.*")
    collections = db.list_collection_names()
    print(f"Available collections: {collections}")

    timetable_collection = next((coll for coll in collections if folder_pattern.match(coll)), None)
    print(f"Matched timetable collection: {timetable_collection}")

    if timetable_collection:
        print(f"Searching for StudentID: {student_id}")
        student_data = db[timetable_collection].find_one({"StudentID": int(student_id)})
        print(f"Found student data: {student_data is not None}")
        if student_data and "Timetable" in student_data:
            print("Timetable found in student data")
            return jsonify({"timetable": student_data["Timetable"]})
        else:
            print("Timetable not found in student data")
    else:
        print("No matching timetable collection found")

    print("Returning 404 error")
    return jsonify({"error": "Timetable not found"}), 404



'''
export all student timetables when the export-all button clicked
'''
@app.route('/export-all-student-timetable')
def export_all_student_timetable():
    # Convert student_id to integer
    try:
        year = request.args.get('year')
        semester = request.args.get('semester')
        campus = request.args.get('campus')
        folder_prefix = request.args.get('folder_prefix')
        degree_name = request.args.get('degree_name')
        print(f"Received parameters: year={year}, semester={semester}, campus={campus}, folder_prefix={folder_prefix}, degree_name={degree_name}")
        result = download_all(year,semester,campus,folder_prefix,degree_name)  
        # Check if download was successful
        if result == False:
            return jsonify({"error": "Failed to export timetable"}), 500
        else:
            return jsonify({"message": "Timetable exported successfully"}), 200

    except Exception as e:
        print(f"Error in export_all_student_timetable: {str(e)}")
        return jsonify({"error": str(e)}), 500


'''
export the specific student timetable when the export button clicked
'''
@app.route('/export-one-student-timetable')
def export_one_student_timetable():
    try:
        year = request.args.get('year')
        semester = request.args.get('semester')
        campus = request.args.get('campus')
        folder_prefix = request.args.get('folder_prefix')
        degree_name = request.args.get('degree_name')
        student_id = request.args.get('student_id')
        
        print(f"Received parameters: year={year}, semester={semester}, campus={campus}, folder_prefix={folder_prefix}, degree_name={degree_name}, student_id={student_id}")
        
        # Convert student_id to integer
        try:
            student_id_int = int(student_id)
        except ValueError:
            return jsonify({"error": "Invalid student ID format"}), 400

        # Call the download function
        result = download_one(year, semester, campus, folder_prefix, degree_name, student_id_int)
        
        # Check if download was successful
        if result == False:
            return jsonify({"error": "Failed to export timetable"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    file_path = os.path.join("student_timetable", student_id+"_timetable.xlsx") 
    success = send_email([result, "student timetable","this is your timetable", file_path])
    
    if success:
        csv_file_path = os.path.join("student_timetable", student_id+"_timetable.csv") 
        
        os.remove(file_path)
        os.remove(csv_file_path)
        print("file remvoed")
        return jsonify({"message":"successful sent timetable"})
    else:
        print("failed to send\n")
        return jsonify({"error": "failed to send"}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
    