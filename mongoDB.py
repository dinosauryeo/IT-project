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
        return True

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
        





"""
def insert_student_data(file_path):
    client = login()
    collection = create_new_collection(client, file_path)

    df = pd.read_csv(file_path)
    
    for index, row in df.iterrows():
        student_data = row.to_dict() 
        collection.insert_one(student_data)  
        

def create_new_collection(client, file_path):
    db = client['Students-Enrollment-Details-DataBase']
    
    collection_name = f"Students-Enrollment-Details-{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    collection = db[collection_name]
    
    return collection
    """
    
# def create_new_collection(year, semester):
#     client = login()
#     db = client[str(year)+"_"+str(semester)]
    
#     # Generate a unique collection name based on the year, semester, and current time
#     collection_name = f"Students-Enrollment-Details-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
#     # Create a new collection
#     collection = db[collection_name]
    
#     return collection

# def insert_student_data(file_path, year, semester):
#     client = login()
#     print(str(year)+"_"+str(semester))
#     db = client[str(year)+"_"+str(semester)]
#     collection_name = f"Students-Enrollment-Details-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
#     collection = db[collection_name]

#     # Read CSV file
#     df = pd.read_csv(file_path)
    
#     # Insert each row into MongoDB
#     for index, row in df.iterrows():
#         student_data = row.to_dict()  # Convert each row to a dictionary
#         collection.insert_one(student_data)  # Insert into MongoDB collection







# # Function to create a new collection based on the year, semester, and current time
# def create_new_collection(db, course_name, campus):
#     # Generate a unique collection name based on Course Name, Campus, and current timestamp
#     collection_name = f"Students-Enrollment-Details-{course_name}-{campus}-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
#     # Create a new collection in the specified database
#     collection = db[collection_name]
    
#     return collection

# # Function to insert student data from a CSV file into MongoDB
# def insert_student_data(file_path, year, semester):
#     client = login()
    
#     # Select the database based on the year and semester
#     db = client[str(year) + "_" + str(semester)]
    
#     # Read CSV file
#     df = pd.read_csv(file_path)
    
#     # Assuming 'Course Name' and 'Campus' are columns in your CSV
#     course_name = df['Course Name'].iloc[0]  # Get the first course name
#     campus = df['Campus'].iloc[0]  # Get the first campus name

#     # Create a new collection with the course name, campus, and current timestamp
#     collection = create_new_collection(db, course_name, campus)

#     # Insert each row from the CSV into the collection
#     for index, row in df.iterrows():
#         student_data = row.to_dict()  # Convert each row to a dictionary
#         collection.insert_one(student_data)  # Insert into MongoDB collection

#     print(f"Data inserted into collection: {collection.name}")
        

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

# Function to insert student data from a CSV file into MongoDB
def insert_student_data(file_path, year, semester):
    client = login()
    
    # Select the database based on the year and semester
    db = client[str(year) + "_" + str(semester)]
    
    # Read CSV file
    df = pd.read_csv(file_path)
    
    # Assuming 'Course Name' and 'Campus' are columns in your CSV
    course_name = df['Course Name'].iloc[0]  # Get the first course name
    campus = df['Campus'].iloc[0]  # Get the first campus name

    # Create a new collection or overwrite an existing one
    collection = create_or_overwrite_collection(db, course_name, campus)

    # Insert each row from the CSV into the collection
    for index, row in df.iterrows():
        student_data = row.to_dict()  # Convert each row to a dictionary
        collection.insert_one(student_data)  # Insert into MongoDB collection

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
        # Create the collection if it doesn't exist
        if 'Subjects-Details' not in db.list_collection_names():
            db.create_collection('Subjects-Details')
        
        collection = db['Subjects-Details']
        result = collection.insert_one(subject_data)  # Insert the subject data
        print(f"Inserted document with ID: {result.inserted_id}")  # Log the inserted document ID
        return result.inserted_id  # Return the ID of the inserted document
    
    except Exception as e:
        print(f"An error occurred while inserting data: {e}")  # Log any errors
        return None

#insert subject info to backend
def insert_one(subject_data):
    client = login()
    db = client['IT-project']
    try:
        collection = db['Subjects-Details'] 
        result = collection.insert_one(subject_data)
        print(f"Inserted document with ID: {result.inserted_id}")  # Log the inserted document ID
        return result.inserted_id  # Return the ID of the inserted document
    except Exception as e:
        print(f"An error occurred while inserting data: {e}")  # Log any errors
        return None
    

def get_student_enrollment_details():
    client = login()
    db = client['Students-Enrollment-Details-DataBase']
    #select sample student enrollment file
    collection = db['Students-Enrollment-Details-20240905_150108'] 

    try:
        # Query all student records in the collection
        students_data = collection.find({})  # Get all student data

        student_courses = []

        for student in students_data:
            student_id = student.get('StudentID')  # Get StudentID
            courses = []

            # Iterate through all course IDs and statuses
            for course_id, status in student.items():
                if isinstance(status, str) and status == 'ENRL':  # Find courses with status "ENRL"
                    courses.append(course_id)  # Record the course ID

            if student_id and courses:
                student_courses.append({
                    'StudentID': student_id,
                    'EnrolledCourses': courses
                })

        return student_courses

    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# enrollment_details = get_student_enrollment_details()
# if enrollment_details:
#     for detail in enrollment_details:
#         print(f"StudentID: {detail['StudentID']}, Enrolled Courses: {detail['EnrolledCourses']}")
    




def get_subject_details():
    client = login()
    db = client['IT-project']
    #select sample subject file
    collection = db['Subjects-Details']
    try:
        # Get detailed information on all courses
        subjects_data = collection.find({})  # Get all course data

        subjects_details = []

        for subject in subjects_data:
            subject_code = subject.get('subjectCode')  # Get the subjectCode of the course

            # Initializes a list for storing section details
            subject_sections = {
                'subjectCode': subject_code,
                'sections': []
            }

            sections = subject.get('sections', {})  # Get the sections of a course

            for section_type, section_objects in sections.items():
                # Go through each section (such as lecture, tutorial, lab)
                for section_object in section_objects:
                    title = section_object.get('title')  # Get the section title

                    # Initialize the data used to store this section
                    section_details = {
                        'type': section_type,
                        'title': title,
                        'modules': []
                    }

                    # Get the time period information in modules
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

                    # Add each section and its module information to the course's sections list
                    subject_sections['sections'].append(section_details)

            subjects_details.append(subject_sections)

        return subjects_details

    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# subject_details = get_subject_details()
# if subject_details:
#     for subject in subject_details:
#         print(f"Subject Code: {subject['subjectCode']}")
#         for section in subject['sections']:
#             print(f"  Section Type: {section['type']}, Title: {section['title']}")
#             for module in section['modules']:
#                 print(f"    Day: {module['day']}, From: {module['from']}, To: {module['to']}, Location: {module['location']}, Mode: {module['mode']}")




import random

def check_time_conflict(assigned_times, day, from_time, to_time):
    """
    Checks whether the given time slot conflicts with an already allocated time slot
    """
    for time_slot in assigned_times:
        if time_slot['day'] == day:
            # If it is on the same day, check if the times overlap
            if not (to_time <= time_slot['from'] or from_time >= time_slot['to']):
                return True  # Conflict
    return False  # no Conflict


# def generate_timetable_for_students():
#     client = login()
#     students_db = client['Students-Enrollment-Details-DataBase']
#     students_collection = students_db['Students-Enrollment-Details-20240905_150108']

#     subjects_db = client['IT-project']
#     subjects_collection = subjects_db['Subjects-Details']

#     error_messages = []  # Used to collect error information

#     try:
#         # Get student course selection information
#         students_data = students_collection.find({})
#         # Get detailed information on all courses
#         subjects_data = list(subjects_collection.find({}))

#         student_timetables = []

#         for student in students_data:
#             student_id = student.get('StudentID')
#             personal_email = student.get('Personal Email')  # Read personal mailbox

#             for attempt in range(10):  # Maximum 10 attempts
#                 enrolled_courses = []  # Record the student's timetable
#                 assigned_times = []  # Record the allocated time periods
#                 conflict = False  # Is there a conflict?

#                 # Traverse all the courses selected by the student
#                 for course_id, status in student.items():
#                     if isinstance(status, str) and status == 'ENRL':  # If the course status is "ENRL"
#                         # Find the corresponding course in the course details
#                         matching_subject = next((sub for sub in subjects_data if sub['subjectCode'] == course_id), None)

#                         if matching_subject:
#                             subject_code = matching_subject['subjectCode']
#                             sections = matching_subject.get('sections', {})

#                             # Traverse all section types of the course (Lecture, Tutorial, Lab, etc.)
#                             for section_type, section_objects in sections.items():
#                                 for section_object in section_objects:
#                                     title = section_object.get('title')
                                    
#                                     # Randomly shuffle the order of modules so that the order is different each time you try
#                                     modules = section_object.get('modules', [])
#                                     random.shuffle(modules)  # Shuffle the order of the modules to ensure that each selection is different

#                                     module_assigned = False  # Indicates whether the current section is allocated successfully.

#                                     # Try to allocate each time module
#                                     for module in modules:
#                                         day = module.get('day')
#                                         from_time = module.get('from')
#                                         to_time = module.get('to')
#                                         limit = module.get('limit', None)  # Get the number of people limit, if not set, the default is None

#                                         # Get the number of people assigned to the current module
#                                         current_enrollment = module.get('current_enrollment', 0)

#                                         # Check if there is a limit and convert it to int
#                                         if limit is not None:
#                                             limit = int(limit)  # Convert limit from a string to an integer
                                            
#                                             # Check if the limit has been reached
#                                             if current_enrollment >= limit:
#                                                 continue  # Skip this module

#                                         # Check if there is a conflict with the allocated time
#                                         if not check_time_conflict(assigned_times, day, from_time, to_time):
#                                             # If there is no conflict, assign the time slot and update the number of people
#                                             assigned_times.append({
#                                                 'day': day,
#                                                 'from': from_time,
#                                                 'to': to_time
#                                             })

#                                             enrolled_courses.append({
#                                                 'SubjectCode': subject_code,
#                                                 'SectionType': section_type,
#                                                 'Title': title,
#                                                 'Day': module.get('day'),
#                                                 'From': module.get('from'),
#                                                 'To': module.get('to'),
#                                                 'Location': module.get('location'),
#                                                 'Mode': module.get('mode')
#                                             })

#                                             # If `limit` is given, update the number of allocated users for the module
#                                             if limit is not None:
#                                                 module['current_enrollment'] = current_enrollment + 1
                                            
#                                             module_assigned = True  # Successful allocation
#                                             break  # After success, jump out of the module loop

#                                     # If the section is not allocated successfully, mark the conflict
#                                     if not module_assigned:
#                                         conflict = True
#                                         break  # Break out of section loop

#                                 # If a conflict occurs, end the course early
#                                 if conflict:
#                                     break

#                             # If a conflict occurs, end the course traversal early
#                             if conflict:
#                                 break

#                 # If all courses are assigned successfully, save the timetable
#                 if not conflict:
#                     student_timetables.append({
#                         'StudentID': student_id,
#                         'PersonalEmail': personal_email,  # Add personal email addresses to the results
#                         'Timetable': enrolled_courses
#                     })
#                     break  # Successfully generated schedule, exiting the try loop

#                 # If you still fail after 10 attempts
#                 if attempt == 9:
#                     error_message = f"Error: Student {student_id} Courses cannot be scheduled without conflicts"
#                     error_messages.append(error_message)  # Collecting error information
        
#         return student_timetables, error_messages  # Return timeline and error messages

#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return None

# def generate_timetable_for_students(database_name):
#     client = MongoClient("mongodb+srv://dinosauryeo:6OHYa6vF6YUCk48K@cluster0.dajn796.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", server_api=ServerApi('1'))
    
#     # Use the dynamically passed database name for subjects and students
#     students_db = client[database_name]
    
#     # Find collections that start with 'Students-Enrollment-Details-'
#     student_collections = [coll for coll in students_db.list_collection_names() if coll.startswith('Students-Enrollment-Details-')]
    
#     subjects_collection = students_db['Subjects-Details']

#     error_messages = []
#     student_timetables = []

#     try:
#         # Iterate through all student enrollment collections
#         for student_collection_name in student_collections:
#             students_collection = students_db[student_collection_name]
#             students_data = students_collection.find({})

#             # Get course details from 'Subjects-Details'
#             subjects_data = list(subjects_collection.find({}))

#             for student in students_data:
#                 student_id = student.get('StudentID')
#                 personal_email = student.get('Personal Email')

#                 for attempt in range(10):
#                     enrolled_courses = []
#                     assigned_times = []
#                     conflict = False

#                     for course_id, status in student.items():
#                         if isinstance(status, str) and status == 'ENRL':
#                             matching_subject = next((sub for sub in subjects_data if sub['subjectCode'] == course_id), None)

#                             if matching_subject:
#                                 subject_code = matching_subject['subjectCode']
#                                 sections = matching_subject.get('sections', {})

#                                 for section_type, section_objects in sections.items():
#                                     for section_object in section_objects:
#                                         title = section_object.get('title')
#                                         modules = section_object.get('modules', [])
#                                         random.shuffle(modules)

#                                         module_assigned = False
#                                         for module in modules:
#                                             day = module.get('day')
#                                             from_time = module.get('from')
#                                             to_time = module.get('to')
#                                             limit = module.get('limit', None)

#                                             current_enrollment = module.get('current_enrollment', 0)
#                                             if limit is not None:
#                                                 limit = int(limit)  # Convert limit from a string to an integer
#                                                 # Check if the limit has been reached
#                                                 if current_enrollment >= limit:
#                                                     continue  # Skip this module

#                                             # if limit is not None and current_enrollment >= limit:
#                                             #     continue

#                                             if not check_time_conflict(assigned_times, day, from_time, to_time):
#                                                 assigned_times.append({
#                                                     'day': day,
#                                                     'from': from_time,
#                                                     'to': to_time
#                                                 })

#                                                 enrolled_courses.append({
#                                                     'SubjectCode': subject_code,
#                                                     'SectionType': section_type,
#                                                     'Title': title,
#                                                     'Day': day,
#                                                     'From': from_time,
#                                                     'To': to_time,
#                                                     'Location': module.get('location'),
#                                                     'Mode': module.get('mode')
#                                                 })

#                                                 if limit is not None:
#                                                     module['current_enrollment'] = current_enrollment + 1

#                                                 module_assigned = True
#                                                 break

#                                         if not module_assigned:
#                                             conflict = True
#                                             break

#                                     if conflict:
#                                         break

#                             if conflict:
#                                 break

#                     if not conflict:
#                         student_timetables.append({
#                             'StudentID': student_id,
#                             'PersonalEmail': personal_email,
#                             'Timetable': enrolled_courses
#                         })
#                         break

#                     if attempt == 9:
#                         error_message = f"Error: Student {student_id} Courses cannot be scheduled without conflicts"
#                         error_messages.append(error_message)

#         return student_timetables, error_messages

#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return None









# def generate_timetable_for_students(database_name):
#     client = MongoClient("mongodb+srv://dinosauryeo:6OHYa6vF6YUCk48K@cluster0.dajn796.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", server_api=ServerApi('1'))
    
#     # Use the dynamically passed database name for subjects and students
#     students_db = client[database_name]
    
#     # Find collections that start with 'Students-Enrollment-Details-'
#     student_collections = [coll for coll in students_db.list_collection_names() if coll.startswith('Students-Enrollment-Details-')]
    
#     subjects_collection = students_db['Subjects-Details']
#     error_messages = []
#     student_timetables = []

#     try:
#         # Iterate through all student enrollment collections
#         for student_collection_name in student_collections:
#             students_collection = students_db[student_collection_name]
#             students_data = students_collection.find({})

#             # Extract course name and campus name from the collection name
#             parts = student_collection_name.split('-')
#             if len(parts) >= 4:
#                 course_name = parts[3]  # Assuming course name is the 3rd part
#                 campus_name = parts[4]  # Assuming campus name is the 4th part
#             else:
#                 course_name = 'UnknownCourse'
#                 campus_name = 'UnknownCampus'

#             # Get course details from 'Subjects-Details'
#             subjects_data = list(subjects_collection.find({}))

#             for student in students_data:
#                 student_id = student.get('StudentID')
#                 personal_email = student.get('Personal Email')

#                 for attempt in range(10):  # Attempt to generate a timetable up to 10 times
#                     enrolled_courses = []
#                     assigned_times = []
#                     conflict = False

#                     for course_id, status in student.items():
#                         if isinstance(status, str) and status == 'ENRL':
#                             matching_subject = next((sub for sub in subjects_data if sub['subjectCode'] == course_id), None)

#                             if matching_subject:
#                                 subject_code = matching_subject['subjectCode']
#                                 sections = matching_subject.get('sections', {})

#                                 for section_type, section_objects in sections.items():
#                                     for section_object in section_objects:
#                                         title = section_object.get('title')
#                                         modules = section_object.get('modules', [])
#                                         random.shuffle(modules)

#                                         module_assigned = False
#                                         for module in modules:
#                                             day = module.get('day')
#                                             from_time = module.get('from')
#                                             to_time = module.get('to')
#                                             limit = module.get('limit', None)

#                                             current_enrollment = module.get('current_enrollment', 0)
#                                             if limit is not None:
#                                                 limit = int(limit)
#                                                 if current_enrollment >= limit:
#                                                     continue  # Skip this module if the limit is reached

#                                             if not check_time_conflict(assigned_times, day, from_time, to_time):
#                                                 assigned_times.append({
#                                                     'day': day,
#                                                     'from': from_time,
#                                                     'to': to_time
#                                                 })

#                                                 enrolled_courses.append({
#                                                     'SubjectCode': subject_code,
#                                                     'SectionType': section_type,
#                                                     'Title': title,
#                                                     'Day': day,
#                                                     'From': from_time,
#                                                     'To': to_time,
#                                                     'Location': module.get('location'),
#                                                     'Mode': module.get('mode')
#                                                 })

#                                                 if limit is not None:
#                                                     module['current_enrollment'] = current_enrollment + 1

#                                                 module_assigned = True
#                                                 break

#                                         if not module_assigned:
#                                             conflict = True
#                                             break

#                                     if conflict:
#                                         break

#                             if conflict:
#                                 break

#                     if not conflict:
#                         student_timetables.append({
#                             'StudentID': student_id,
#                             'PersonalEmail': personal_email,
#                             'Timetable': enrolled_courses
#                         })
#                         break

#                     if attempt == 9:
#                         error_message = f"Error: Student {student_id} Courses cannot be scheduled without conflicts"
#                         error_messages.append(error_message)

#             # After generating timetables for students in this collection, save them to a new collection
#             new_collection_name = f"Timetable-{course_name}-{campus_name}"
#             timetable_collection = students_db[new_collection_name]

#             # Insert each timetable into the new collection
#             for timetable in student_timetables:
#                 timetable_collection.insert_one(timetable)

#         return student_timetables, error_messages

#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return None, [f"An error occurred: {str(e)}"]



# def generate_timetable_for_students(database_name):
#     client = MongoClient("mongodb+srv://dinosauryeo:6OHYa6vF6YUCk48K@cluster0.dajn796.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", server_api=ServerApi('1'))
    
#     # Use the dynamically passed database name for subjects and students
#     students_db = client[database_name]
    
#     # Find collections that start with 'Students-Enrollment-Details-'
#     student_collections = [coll for coll in students_db.list_collection_names() if coll.startswith('Students-Enrollment-Details-')]
    
#     subjects_collection = students_db['Subjects-Details']
#     error_messages = []

#     try:
#         # Iterate through all student enrollment collections
#         for student_collection_name in student_collections:
#             students_collection = students_db[student_collection_name]
#             students_data = students_collection.find({})

#             # Extract course name and campus name from the collection name
#             parts = student_collection_name.split('-')
#             if len(parts) >= 4:
#                 course_name = parts[3]  # Assuming course name is the 3rd part
#                 campus_name = parts[4]  # Assuming campus name is the 4th part
#             else:
#                 course_name = 'UnknownCourse'
#                 campus_name = 'UnknownCampus'

#             # Get course details from 'Subjects-Details'
#             subjects_data = list(subjects_collection.find({}))
            
#             # **Reset the student_timetables list for each collection**
#             student_timetables = []  # Move this line here to reset for each student collection

#             for student in students_data:
#                 student_id = student.get('StudentID')
#                 personal_email = student.get('Personal Email')

#                 for attempt in range(10):  # Attempt to generate a timetable up to 10 times
#                     enrolled_courses = []
#                     assigned_times = []
#                     conflict = False

#                     for course_id, status in student.items():
#                         if isinstance(status, str) and status == 'ENRL':
#                             matching_subject = next((sub for sub in subjects_data if sub['subjectCode'] == course_id), None)

#                             if matching_subject:
#                                 subject_code = matching_subject['subjectCode']
#                                 sections = matching_subject.get('sections', {})

#                                 for section_type, section_objects in sections.items():
#                                     for section_object in section_objects:
#                                         title = section_object.get('title')
#                                         modules = section_object.get('modules', [])
#                                         random.shuffle(modules)

#                                         module_assigned = False
#                                         for module in modules:
#                                             day = module.get('day')
#                                             from_time = module.get('from')
#                                             to_time = module.get('to')
#                                             limit = module.get('limit', None)

#                                             current_enrollment = module.get('current_enrollment', 0)
#                                             if limit is not None:
#                                                 limit = int(limit)
#                                                 if current_enrollment >= limit:
#                                                     continue  # Skip this module if the limit is reached

#                                             if not check_time_conflict(assigned_times, day, from_time, to_time):
#                                                 assigned_times.append({
#                                                     'day': day,
#                                                     'from': from_time,
#                                                     'to': to_time
#                                                 })

#                                                 enrolled_courses.append({
#                                                     'SubjectCode': subject_code,
#                                                     'SectionType': section_type,
#                                                     'Title': title,
#                                                     'Day': day,
#                                                     'From': from_time,
#                                                     'To': to_time,
#                                                     'Location': module.get('location'),
#                                                     'Mode': module.get('mode')
#                                                 })

#                                                 if limit is not None:
#                                                     module['current_enrollment'] = current_enrollment + 1

#                                                 module_assigned = True
#                                                 break

#                                         if not module_assigned:
#                                             conflict = True
#                                             break

#                                     if conflict:
#                                         break

#                             if conflict:
#                                 break

#                     if not conflict:
#                         student_timetables.append({
#                             'StudentID': student_id,
#                             'PersonalEmail': personal_email,
#                             'Timetable': enrolled_courses
#                         })
#                         break

#                     if attempt == 9:
#                         error_message = f"Error: Student {student_id} Courses cannot be scheduled without conflicts"
#                         error_messages.append(error_message)

#             # After generating timetables for students in this collection, save them to a new collection
#             new_collection_name = f"Timetable-{course_name}-{campus_name}"
#             timetable_collection = students_db[new_collection_name]

#             # Insert each timetable into the new collection
#             for timetable in student_timetables:
#                 timetable_collection.insert_one(timetable)

#         return student_timetables, error_messages

#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return None, [f"An error occurred: {str(e)}"]



def generate_timetable_for_students(database_name):
    client = MongoClient("mongodb+srv://dinosauryeo:6OHYa6vF6YUCk48K@cluster0.dajn796.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", server_api=ServerApi('1'))
    
    # Use the dynamically passed database name for subjects and students
    students_db = client[database_name]
    
    # Find collections that start with 'Students-Enrollment-Details-'
    student_collections = [coll for coll in students_db.list_collection_names() if coll.startswith('Students-Enrollment-Details-')]
    
    subjects_collection = students_db['Subjects-Details']
    error_messages = []

    try:
        # Iterate through all student enrollment collections
        for student_collection_name in student_collections:
            students_collection = students_db[student_collection_name]
            students_data = students_collection.find({})

            # Extract course name and campus name from the collection name
            parts = student_collection_name.split('-')
            if len(parts) >= 4:
                course_name = parts[3]  # Assuming course name is the 3rd part
                campus_name = parts[4]  # Assuming campus name is the 4th part
            else:
                course_name = 'UnknownCourse'
                campus_name = 'UnknownCampus'

            # Check if a timetable for this course and campus already exists
            timetable_collection_name = f"Timetable-{course_name}-{campus_name}"
            if timetable_collection_name in students_db.list_collection_names():
                # print(f"Timetable for {course_name} at {campus_name} already exists. Dropping the old collection to create a new one.")
                print(f"Found existing timetable collection: {timetable_collection_name}. Dropping it.")
                students_db[timetable_collection_name].drop()  # Drop the old collection if it exists
                print(f"Successfully dropped {timetable_collection_name}.")

            # Get course details from 'Subjects-Details'
            subjects_data = list(subjects_collection.find({}))
            
            # **Reset the student_timetables list for each collection**
            student_timetables = []  # Reset for each student collection

            for student in students_data:
                student_id = student.get('StudentID')
                personal_email = student.get('Personal Email')

                for attempt in range(10):  # Attempt to generate a timetable up to 10 times
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
                                            limit = module.get('limit', None)

                                            current_enrollment = module.get('current_enrollment', 0)
                                            if limit is not None:
                                                limit = int(limit)
                                                if current_enrollment >= limit:
                                                    continue  # Skip this module if the limit is reached

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
                            'PersonalEmail': personal_email,
                            'Timetable': enrolled_courses
                        })
                        break

                    if attempt == 9:
                        error_message = f"Error: Student {student_id} Courses cannot be scheduled without conflicts"
                        error_messages.append(error_message)

            # After generating timetables for students in this collection, save them to a new collection
            timetable_collection = students_db[timetable_collection_name]

            # Insert each timetable into the new collection
            for timetable in student_timetables:
                timetable_collection.insert_one(timetable)

        return student_timetables, error_messages

    except Exception as e:
        print(f"Error: {str(e)}")
        return None, [f"An error occurred: {str(e)}"]











# timetables, error_messages = generate_timetable_for_students()

# if timetables:
#     for student_timetable in timetables:
#         print(f"StudentID: {student_timetable['StudentID']}, PersonalEmail: {student_timetable['PersonalEmail']}")
#         for course in student_timetable['Timetable']:
#             print(f"  Subject: {course['SubjectCode']}, Section: {course['SectionType']}, Title: {course['Title']}")
#             print(f"    Day: {course['Day']}, From: {course['From']}, To: {course['To']}, Location: {course['Location']}, Mode: {course['Mode']}")

# if error_messages:
#     for error in error_messages:
#         print(f"front end: {error}")
