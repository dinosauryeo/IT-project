from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo
from datetime import datetime, timedelta
import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import gridfs
from datetime import datetime
import random

def login():
    uri = "mongodb+srv://dinosauryeo:6OHYa6vF6YUCk48K@cluster0.dajn796.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
    except Exception as e:
        print(e)
        
    return client

def access_user(client):
    # Create or access a database
    db = client['IT-project']
    # Create or access a collection (similar to a table in SQL databases)
    collection = db['User-data']
    
    return collection
    

#to verify login data
def verify(password, username):
    client = login()
    user_data = access_user(client)

    query={
        "$or":[{"username":username},{"email":username.lower()}],
        "password":password
    }
    result = user_data.find_one(query)
    
    if result is None:
        return False
    else:
        print(result)
        return result['access_level']

#to update a value in database
def input_user_data(email,destination,data):
    client = login()
    user_data = access_user(client)
    
    # Query to find the document to update
    query = {"email": email.lower()}

    # New values to update
    new_values = {"$set": {destination: data}}
    print("trying to update")

    # Update the document
    result = user_data.update_one(query, new_values)
    
#A function to check whether a specific value exists
def check_user_value(target_field,value):
    client = login()
    user_data = access_user(client)
    
    query = {target_field:value}
    
    result = user_data.find_one(query)
    
    if result is None:
        return False
    else:
        return True
    
#verify verification code
def veri_vericode(email,vericode,password):
    client = login()
    user_data = access_user(client)
    query = {"email":email.lower(),"verification_code":int(vericode)}
    
    result = user_data.find_one(query)
    
    #if no such vericode exists
    if result is None:
        return 2
    
    else:
        #check had the vericode expired yet
        time_limit = timedelta(minutes = 5)
        time_difference = abs(datetime.now() - result["vericode_date_sent"])
        
        if time_difference <= time_limit:
            # reset vericode value
            new_values = {"$set": {"password": password, "verification_code":None}}

            # Update the document
            result = user_data.update_one(query, new_values)
            return 1
        else:
            return 3
        




# Function to create a new collection or overwrite an existing one based on the course name and campus
def create_or_overwrite_collection(db, course_name, campus):
    # Search for existing collections that match the course name and campus
    existing_collections = [coll for coll in db.list_collection_names() if coll.startswith(f"Students-Enrollment-Details-{course_name}-{campus}")]

    if existing_collections:
        # If a matching collection exists, drop (delete) the old collection
        for collection_name in existing_collections:
            print(f"Collection {collection_name} found. Dropping it to overwrite with new data.")
            db[collection_name].drop()

    # Create a new collection with the course name, campus, and current timestamp
    collection_name = f"Students-Enrollment-Details-{course_name}-{campus}-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    collection = db[collection_name]
    
    return collection


def insert_student_data(file_path, year, semester):
    client = login()
    
    db = client[str(year) + "_" + str(semester)]
    
    # read CSV
    df = pd.read_csv(file_path)
    
    # 'Course Name' and 'Campus'
    course_name = df['Course Name'].iloc[0]
    campus = df['Campus'].iloc[0]

    # overwrite an existing one
    collection = create_or_overwrite_collection(db, course_name, campus)

    # insert
    for index, row in df.iterrows():
        student_data = row.to_dict()  
        collection.insert_one(student_data)  

    print(f"Data inserted into collection: {collection.name}")






def access_fs(client):
    db = client['Students-Enrollment-Details-DataBase']
    fs = gridfs.GridFS(db)
    return fs

#insert subject info to backend
def insert_subject(subject_data, year, semester):
    client = login()
    db = client[str(year) + "_" + str(semester)]
    
    try:
        if 'Subjects-Details' not in db.list_collection_names():
            db.create_collection('Subjects-Details')
        
        collection = db['Subjects-Details']
        result = collection.insert_one(subject_data)  
        print(f"Inserted document with ID: {result.inserted_id}")  
        return result.inserted_id  
    
    except Exception as e:
        print(f"An error occurred while inserting data: {e}")  
        return None

#insert subject info to backend
def insert_one(subject_data):
    client = login()
    db = client['IT-project']
    try:
        collection = db['Subjects-Details'] 
        result = collection.insert_one(subject_data)
        print(f"Inserted document with ID: {result.inserted_id}")  
        return result.inserted_id  
    except Exception as e:
        print(f"An error occurred while inserting data: {e}")  
        return None
    

def get_student_enrollment_details():
    client = login()
    db = client['Students-Enrollment-Details-DataBase']
    collection = db['Students-Enrollment-Details-20240905_150108'] 

    try:
        students_data = collection.find({})  

        student_courses = []

        for student in students_data:
            student_id = student.get('StudentID')  
            courses = []
            for course_id, status in student.items():
                if isinstance(status, str) and status == 'ENRL':  
                    courses.append(course_id)  

            if student_id and courses:
                student_courses.append({
                    'StudentID': student_id,
                    'EnrolledCourses': courses
                })

        return student_courses

    except Exception as e:
        print(f"Error: {str(e)}")
        return None






def get_subject_details():
    client = login()
    db = client['IT-project']
    collection = db['Subjects-Details']
    try:
        subjects_data = collection.find({}) 

        subjects_details = []

        for subject in subjects_data:
            subject_code = subject.get('subjectCode')  
            subject_sections = {
                'subjectCode': subject_code,
                'sections': []
            }

            sections = subject.get('sections', {})  

            for section_type, section_objects in sections.items():
                for section_object in section_objects:
                    title = section_object.get('title')  

                    section_details = {
                        'type': section_type,
                        'title': title,
                        'modules': []
                    }

                    modules = section_object.get('modules', [])
                    for module in modules:
                        module_info = {
                            'day': module.get('day'),
                            'from': module.get('from'),
                            'to': module.get('to'),
                            'location': module.get('location'),
                            'mode': module.get('mode')
                        }
                        section_details['modules'].append(module_info)

                    subject_sections['sections'].append(section_details)

            subjects_details.append(subject_sections)

        return subjects_details

    except Exception as e:
        print(f"Error: {str(e)}")
        return None



def check_time_conflict(assigned_times, day, from_time, to_time):
    for time_slot in assigned_times:
        if time_slot['day'] == day:
            if not (to_time <= time_slot['from'] or from_time >= time_slot['to']):
                return True  # conflict
    return False  # no conflict



def generate_timetable_for_students(database_name):
    client = MongoClient("mongodb+srv://dinosauryeo:6OHYa6vF6YUCk48K@cluster0.dajn796.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", server_api=ServerApi('1'))

    students_db = client[database_name]
    
    student_collections = [coll for coll in students_db.list_collection_names() if coll.startswith('Students-Enrollment-Details-')]
    
    subjects_collection = students_db['Subjects-Details']
    error_messages = []

    try:
        for student_collection_name in student_collections:
            students_collection = students_db[student_collection_name]
            students_data = students_collection.find({})

            parts = student_collection_name.split('-')
            if len(parts) >= 4:
                course_name = parts[3]  
                campus_name = parts[4]  
            else:
                course_name = 'UnknownCourse'
                campus_name = 'UnknownCampus'

            timetable_collection_name = f"Timetable-{course_name}-{campus_name}"
            if timetable_collection_name in students_db.list_collection_names():
                print(f"Found existing timetable collection: {timetable_collection_name}. Dropping it.")
                students_db[timetable_collection_name].drop()  # drop the old collection if it exists
                print(f"Successfully dropped {timetable_collection_name}.")

            # course details from 'Subjects-Details'
            subjects_data = list(subjects_collection.find({}))
            
            student_timetables = [] 

            for student in students_data:
                student_id = student.get('StudentID')
                student_name = student.get('Student Name')
                personal_email = student.get('Personal Email')

                for attempt in range(10):  # attempt to generate a timetable up to 10 times
                    enrolled_courses = []
                    assigned_times = []
                    conflict = False

                    for course_id, status in student.items():
                        if isinstance(status, str) and status == 'ENRL':
                            matching_subject = next((sub for sub in subjects_data if sub['subjectCode'] == course_id), None)

                            if matching_subject:
                                subject_code = matching_subject['subjectCode']
                                sections = matching_subject.get('sections', {})

                                for section_type, section_objects in sections.items():
                                    for section_object in section_objects:
                                        title = section_object.get('title')
                                        modules = section_object.get('modules', [])
                                        random.shuffle(modules)

                                        module_assigned = False
                                        for module in modules:
                                            day = module.get('day')
                                            from_time = module.get('from')
                                            to_time = module.get('to')
                                            name = module.get('name')
                                            location = module.get('location')
                                            limit = module.get('limit', None)

                                            current_enrollment = module.get('current_enrollment', 0)
                                            if limit is not None:
                                                limit = int(limit)
                                                if current_enrollment >= limit:
                                                    continue  # skip this module if the limit is reached

                                            if not check_time_conflict(assigned_times, day, from_time, to_time):
                                                assigned_times.append({
                                                    'day': day,
                                                    'from': from_time,
                                                    'to': to_time
                                                })

                                                enrolled_courses.append({
                                                    'SubjectCode': subject_code,
                                                    'SectionType': section_type,
                                                    'Title': title,
                                                    'Day': day,
                                                    'From': from_time,
                                                    'To': to_time,
                                                    'Name': name,
                                                    'Location': location,
                                                    'Location': module.get('location'),
                                                    'Mode': module.get('mode')
                                                })

                                                if limit is not None:
                                                    module['current_enrollment'] = current_enrollment + 1

                                                module_assigned = True
                                                break

                                        if not module_assigned:
                                            conflict = True
                                            break

                                    if conflict:
                                        break

                            if conflict:
                                break

                    if not conflict:
                        student_timetables.append({
                            'StudentID': student_id,
                            'StudentName': student_name,
                            'PersonalEmail': personal_email,
                            'Timetable': enrolled_courses
                        })
                        break

                    if attempt == 9:
                        error_message = f"Error: Student {student_id} Courses cannot be scheduled without conflicts"
                        error_messages.append(error_message)

            # after generating timetables for students in this collection, save them to a new collection
            timetable_collection = students_db[timetable_collection_name]

            # insert each timetable into the new collection
            for timetable in student_timetables:
                timetable_collection.insert_one(timetable)

        return student_timetables, error_messages

    except Exception as e:
        print(f"Error: {str(e)}")
        return None, [f"An error occurred: {str(e)}"]








