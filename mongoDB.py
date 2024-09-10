from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo
from datetime import datetime, timedelta
import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import gridfs
from datetime import datetime

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
        



# def insert_student_data(file_path):
#     client = login()
#     collection = access_enrollment(client)

#     # 读取CSV文件
#     df = pd.read_csv(file_path)
    
#     # 将每一行数据插入到 MongoDB
#     for index, row in df.iterrows():
#         student_data = row.to_dict()  # 将每一行转换为字典
#         collection.insert_one(student_data)  # 插入到 MongoDB 集合中
# def access_enrollment(client):
#     # 修改数据库和集合名称
#     db = client['Students-Enrollment-Details-DataBase']
#     collection = db['Students-Enrollment-Details-1']
#     return collection

# def access_fs(client):
#     db = client['Students-Enrollment-Details-DataBase']
#     fs = gridfs.GridFS(db)
#     return fs




def insert_student_data(file_path):
    client = login()
    collection = create_new_collection(client, file_path)

    # 读取CSV文件
    df = pd.read_csv(file_path)
    
    # 将每一行数据插入到 MongoDB
    for index, row in df.iterrows():
        student_data = row.to_dict()  # 将每一行转换为字典
        collection.insert_one(student_data)  # 插入到 MongoDB 集合中
        

def create_new_collection(client, file_path):
    db = client['Students-Enrollment-Details-DataBase']
    
    # 使用当前时间生成唯一集合名
    collection_name = f"Students-Enrollment-Details-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 创建新的集合
    collection = db[collection_name]
    
    return collection

def access_fs(client):
    db = client['Students-Enrollment-Details-DataBase']
    fs = gridfs.GridFS(db)
    return fs

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
    

def read_studet_enrollment_from_mongo():
    client = login()
    db = client['Students-Enrollment-Details-DataBase']
    #select sample student enrollment file
    collection = db['Students-Enrollment-Details-20240905_150108'] 

    try:
        #read all data
        data = collection.find()
        
        #store student enrollment data in to a list
        student_enroll_list = []
        for document in data:
            student_dict={}
            for key in document.keys():
                # if the condition fit
                if key in ["StudentID", "Course Start Date", "Student Name"]:
                    student_dict[key] = document.get(key)
                elif document.get(key) == "ENRL":
                    student_dict[key] = document.get(key)


            #if the student dictionary is not empty, add the data
            if student_dict:
                student_enroll_list .append(student_dict)
                
        return student_enroll_list 

    except Exception as e:
        print(f"An error occurred while reading data: {e}")
        return None
    
def read_subject_info_from_mongo():
    client = login()
    db = client['IT-project']
    #select sample subject file
    collection = db['Subjects-Details']
    try:
        #read all data
        data = collection.find()
        #store subject data in to a list
        subject_list = []
        for document in data:
            subject_dict={}
            for key in document.keys():
                # if the condition fit
                if key in ["year", "semester", "subjectName","subjectCode"]:
                    subject_dict[key] = document.get(key)
                elif key in ["sections"]:
                    #lab/lecture/tutorial
                    section = document.get(key)
                    mode_dict = {}
                    for j in section.keys():
                        #have lab/lecture/tutorial
                        if section.get(j) is not None:
                            #displayMode
                            mode_dict[j] = section.get(j)
                    subject_dict[key] = mode_dict

            #if the student dictionary is not empty, add the data
            if subject_dict:
                subject_list .append(subject_dict)
                
        return subject_list 
    
    except Exception as e:
        print(f"An error occurred while reading data: {e}")
        return None
    
subjects = read_subject_info_from_mongo()
for subject in subjects:
    print(subject)
