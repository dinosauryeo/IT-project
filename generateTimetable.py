import mongoDB


def generateTimetable():
    timetable = {}
    student_file = mongoDB.read_student_enrollment_from_mongo()
    subject_file= mongoDB.read_subject_info_from_mongo()
    #print(student_file)
    #print(subject_file)
    #loop each student info
    for student in student_file:
        subeject_enroll = student["Enroll"]
        #loop each enrolled subject
        for subject in subeject_enroll:
            find_subject(subject, subject_file)






