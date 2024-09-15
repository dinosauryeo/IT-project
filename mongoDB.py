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



"""
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
    """
    
def create_new_collection(year, semester):
    client = login()
    db = client[str(year)+"_Sem"+str(semester)]
    
    # Generate a unique collection name based on the year, semester, and current time
    collection_name = f"Students-Enrollment-Details-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create a new collection
    collection = db[collection_name]
    
    return collection

def insert_student_data(file_path, year, semester):
    client = login()
    db = client[str(year)+"_Sem"+str(semester)]
    collection_name = f"Students-Enrollment-Details-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    collection = db[collection_name]

    # Read CSV file
    df = pd.read_csv(file_path)
    
    # Insert each row into MongoDB
    for index, row in df.iterrows():
        student_data = row.to_dict()  # Convert each row to a dictionary
        collection.insert_one(student_data)  # Insert into MongoDB collection
        
def access_fs(client):
    db = client['Students-Enrollment-Details-DataBase']
    fs = gridfs.GridFS(db)
    return fs

#insert subject info to backend
def insert_subject(subject_data,year, semester):
    client = login()
    db = client[str(year)+"_Sem"+str(semester)]
    try:
        collection = db['Subjects-Details'] 
        result = collection.insert_one(subject_data)
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
        # 查询集合中的所有学生记录
        students_data = collection.find({})  # 获取所有学生数据

        student_courses = []

        for student in students_data:
            student_id = student.get('StudentID')  # 获取 StudentID
            courses = []

            # 遍历所有的课程ID和状态
            for course_id, status in student.items():
                if isinstance(status, str) and status == 'ENRL':  # 找到状态为 "ENRL" 的课程
                    courses.append(course_id)  # 记录课程ID

            if student_id and courses:
                student_courses.append({
                    'StudentID': student_id,
                    'EnrolledCourses': courses
                })

        return student_courses

    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# # 调用函数并输出结果
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
        # 查询所有课程的详细信息
        subjects_data = collection.find({})  # 获取所有课程数据

        subjects_details = []

        for subject in subjects_data:
            subject_code = subject.get('subjectCode')  # 获取课程的 subjectCode

            # 初始化用于存储 section 详细信息的列表
            subject_sections = {
                'subjectCode': subject_code,
                'sections': []
            }

            sections = subject.get('sections', {})  # 获取课程的 sections

            for section_type, section_objects in sections.items():
                # 遍历每种 section（如 lecture、tutorial、lab）
                for section_object in section_objects:
                    title = section_object.get('title')  # 获取 section 的 title

                    # 初始化用于存储该 section 的数据
                    section_details = {
                        'type': section_type,
                        'title': title,
                        'modules': []
                    }

                    # 获取 modules 里面的时间段信息
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

                    # 将每个 section 及其模块信息添加到课程的 sections 列表中
                    subject_sections['sections'].append(section_details)

            subjects_details.append(subject_sections)

        return subjects_details

    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# # 调用函数并输出结果
# subject_details = get_subject_details()
# if subject_details:
#     for subject in subject_details:
#         print(f"Subject Code: {subject['subjectCode']}")
#         for section in subject['sections']:
#             print(f"  Section Type: {section['type']}, Title: {section['title']}")
#             for module in section['modules']:
#                 print(f"    Day: {module['day']}, From: {module['from']}, To: {module['to']}, Location: {module['location']}, Mode: {module['mode']}")







# def check_time_conflict(assigned_times, day, from_time, to_time):
#     """
#     检查给定的时间段是否与已分配的时间段冲突。
#     """
#     for time_slot in assigned_times:
#         if time_slot['day'] == day:
#             # 如果在同一天，检查时间是否重叠
#             if not (to_time <= time_slot['from'] or from_time >= time_slot['to']):
#                 return True
#     return False



# def generate_timetable_for_students():
#     client = login()
#     students_db = client['Students-Enrollment-Details-DataBase']
#     students_collection = students_db['Students-Enrollment-Details-20240905_150108']

#     subjects_db = client['IT-project']
#     subjects_collection = subjects_db['Subjects-Details']
#     try:
#         # 获取学生选课信息
#         students_data = students_collection.find({})
#         # 获取所有课程的详细信息
#         subjects_data = list(subjects_collection.find({}))

#         student_timetables = []

#         for student in students_data:
#             student_id = student.get('StudentID')
#             enrolled_courses = []  # 记录该学生的timetable
#             assigned_times = []  # 记录该学生已分配的时间段
            
#             for course_id, status in student.items():
#                 if isinstance(status, str) and status == 'ENRL':  # 如果课程状态是 "ENRL"
#                     # 在课程详细信息中找到对应的课程
#                     matching_subject = next((sub for sub in subjects_data if sub['subjectCode'] == course_id), None)
                    
#                     if matching_subject:
#                         subject_code = matching_subject['subjectCode']
#                         sections = matching_subject.get('sections', {})

#                         for section_type, section_objects in sections.items():
#                             for section_object in section_objects:
#                                 title = section_object.get('title')
                                
#                                 # 尝试随机选择一个 module
#                                 modules = section_object.get('modules', [])
#                                 if modules:
#                                     available_modules = modules.copy()  # 复制一份可用模块列表
#                                     selected_module = None

#                                     while available_modules:
#                                         potential_module = random.choice(available_modules)
#                                         from_time = potential_module.get('from')
#                                         to_time = potential_module.get('to')
#                                         day = potential_module.get('day')

#                                         # 检查是否与已分配时间冲突
#                                         if not check_time_conflict(assigned_times, day, from_time, to_time):
#                                             selected_module = potential_module
#                                             # 如果没有冲突，将该时间段加入已分配时间的列表
#                                             assigned_times.append({
#                                                 'day': day,
#                                                 'from': from_time,
#                                                 'to': to_time
#                                             })
#                                             break
#                                         else:
#                                             # 如果冲突，从可用模块中移除
#                                             available_modules.remove(potential_module)

#                                     # 如果找到没有冲突的时间段
#                                     if selected_module:
#                                         enrolled_courses.append({
#                                             'SubjectCode': subject_code,
#                                             'SectionType': section_type,
#                                             'Title': title,
#                                             'Day': selected_module.get('day'),
#                                             'From': selected_module.get('from'),
#                                             'To': selected_module.get('to'),
#                                             'Location': selected_module.get('location'),
#                                             'Mode': selected_module.get('mode')
#                                         })
#                                     else:
#                                         print(f"Warning: 无法为学生 {student_id} 的课程 {subject_code} 安排无冲突的时间段")

#             # 将该学生的timetable保存
#             student_timetables.append({
#                 'StudentID': student_id,
#                 'Timetable': enrolled_courses
#             })

#         return student_timetables

#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return None

# # 生成学生的timetable
# timetables = generate_timetable_for_students()

# # 输出生成的timetable
# if timetables:
#     for student_timetable in timetables:
#         print(f"StudentID: {student_timetable['StudentID']}")
#         for course in student_timetable['Timetable']:
#             print(f"  Subject: {course['SubjectCode']}, Section: {course['SectionType']}, Title: {course['Title']}")
#             print(f"    Day: {course['Day']}, From: {course['From']}, To: {course['To']}, Location: {course['Location']}, Mode: {course['Mode']}")



import random

def check_time_conflict(assigned_times, day, from_time, to_time):
    """
    检查给定的时间段是否与已分配的时间段冲突。
    """
    for time_slot in assigned_times:
        if time_slot['day'] == day:
            # 如果在同一天，检查时间是否重叠
            if not (to_time <= time_slot['from'] or from_time >= time_slot['to']):
                return True  # 发生冲突
    return False  # 无冲突


def generate_timetable_for_students():
    client = login()
    students_db = client['Students-Enrollment-Details-DataBase']
    students_collection = students_db['Students-Enrollment-Details-20240905_150108']

    subjects_db = client['IT-project']
    subjects_collection = subjects_db['Subjects-Details']

    error_messages = []  # 用于收集错误信息

    try:
        # 获取学生选课信息
        students_data = students_collection.find({})
        # 获取所有课程的详细信息
        subjects_data = list(subjects_collection.find({}))

        student_timetables = []

        for student in students_data:
            student_id = student.get('StudentID')
            personal_email = student.get('Personal Email')  # 读取个人邮箱

            for attempt in range(10):  # 最多尝试10次
                enrolled_courses = []  # 记录该学生的时间表
                assigned_times = []  # 记录已分配的时间段
                conflict = False  # 是否发生冲突

                # 遍历该学生选的所有课程
                for course_id, status in student.items():
                    if isinstance(status, str) and status == 'ENRL':  # 如果课程状态是 "ENRL"
                        # 在课程详细信息中找到对应的课程
                        matching_subject = next((sub for sub in subjects_data if sub['subjectCode'] == course_id), None)

                        if matching_subject:
                            subject_code = matching_subject['subjectCode']
                            sections = matching_subject.get('sections', {})

                            # 遍历课程的所有 section 类型（Lecture, Tutorial, Lab等）
                            for section_type, section_objects in sections.items():
                                for section_object in section_objects:
                                    title = section_object.get('title')
                                    
                                    # 随机打乱模块顺序，每次尝试时顺序不同
                                    modules = section_object.get('modules', [])
                                    random.shuffle(modules)  # 打乱模块的顺序，确保每次选择不同

                                    module_assigned = False  # 标识当前 section 是否分配成功

                                    # 尝试分配每一个时间模块
                                    for module in modules:
                                        day = module.get('day')
                                        from_time = module.get('from')
                                        to_time = module.get('to')

                                        # 检查是否与已分配的时间冲突
                                        if not check_time_conflict(assigned_times, day, from_time, to_time):
                                            # 如果没有冲突，分配该时间段
                                            assigned_times.append({
                                                'day': day,
                                                'from': from_time,
                                                'to': to_time
                                            })
                                            enrolled_courses.append({
                                                'SubjectCode': subject_code,
                                                'SectionType': section_type,
                                                'Title': title,
                                                'Day': module.get('day'),
                                                'From': module.get('from'),
                                                'To': module.get('to'),
                                                'Location': module.get('location'),
                                                'Mode': module.get('mode')
                                            })
                                            module_assigned = True  # 成功分配
                                            break  # 成功后跳出 module 循环

                                    # 如果该 section 没有分配成功，标记冲突
                                    if not module_assigned:
                                        conflict = True
                                        # print("aaaaaaaaaaaaaa")
                                        break  # 跳出 section 循环

                                # 如果发生冲突，提前结束该课程的处理
                                if conflict:
                                    break

                            # 如果发生冲突，提前结束课程遍历
                            if conflict:
                                break

                # 如果所有课程都成功分配，则保存时间表
                if not conflict:
                    student_timetables.append({
                        'StudentID': student_id,
                        'PersonalEmail': personal_email,  # 将个人邮箱添加到结果中
                        'Timetable': enrolled_courses
                    })
                    break  # 成功生成时间表，退出尝试循环
                else:
                    attempt+1
                    # 每次冲突重新开始时，打印失败信息
                    # print(f"Attempt {attempt + 1} failed for student {student_id}")

                # 如果10次尝试仍然失败
                if attempt == 9:
                    error_message = f"Error: 学生 {student_id} 的课程无法安排无冲突的时间表"
                    error_messages.append(error_message)  # 收集错误信息
        
        return student_timetables, error_messages  # 返回时间表和错误信息

    except Exception as e:
        print(f"Error: {str(e)}")
        return None

"""
# 生成时间表
timetables, error_messages = generate_timetable_for_students()


# 输出生成的时间表
if timetables:
    for student_timetable in timetables:
        print(f"StudentID: {student_timetable['StudentID']}, PersonalEmail: {student_timetable['PersonalEmail']}")
        for course in student_timetable['Timetable']:
            print(f"  Subject: {course['SubjectCode']}, Section: {course['SectionType']}, Title: {course['Title']}")
            print(f"    Day: {course['Day']}, From: {course['From']}, To: {course['To']}, Location: {course['Location']}, Mode: {course['Mode']}")

# 把错误信息传递到前端显示
if error_messages:
    for error in error_messages:
        print(f"前端显示: {error}")
"""