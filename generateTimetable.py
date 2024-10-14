import mongoDB
from datetime import datetime, time


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



#find all enrolled subjects timetable combination here
def find_subject(subject, subject_file):
    one_subject_timetable={}
    for queue in subject_file:
        #find subject same id
        if subject == queue.get("subjectCode"):
            subject_time_list=[]
            #loop how many lectures in week
            if queue.get("sections").get("lecture") != []:
                subject_time_list.append(lecture_section(queue.get("sections").get("lecture")))
                #print(subject_time_list)
            if queue.get("sections").get("tutorial") != []:
                subject_time_list.append(tutorial_section(queue.get("sections").get("tutorial")))
            if queue.get("sections").get("lab") != []:
                subject_time_list.append(lab_section(queue.get("sections").get("lab")))
        one_subject_timetable[subject] = subject_time_list
    return one_subject_timetable

def lecture_section(lecture):
    lec = {}
    for lecture_num in lecture:
        title = lecture_num.get("title")
        lec[title] = []
        
        # Process each module for the lecture
        for time in lecture_num.get("modules"):
            # Create a new dictionary for each time slot
            section = {}
            day = time.get("day")
            start = time.get("from")
            end = time.get("to")
            section["day"] = day
            section["start"] = start
            section["end"] = end
            # Append the new dictionary to the lecture's list
            lec[title].append(section)
    return lec
def tutorial_section(tutorial):
    tut = {}
    for tutorial_num in tutorial:
        title = tutorial_num.get("title")
        tut[title] = []
        
        # Process each module for the tutorial
        for time in tutorial_num.get("modules"):
            # Create a new dictionary for each time slot
            section = {}
            day = time.get("day")
            start = time.get("from")
            end = time.get("to")
            section["day"] = day
            section["start"] = start
            section["end"] = end
            # Append the new dictionary to the lecture's list
            tut[title].append(section)
    return tut
    

def lab_section(lab):
    lab_time = {}
    for lab_num in lab:
        title = lab_num.get("title")
        lab_time[title] = []
        # Process each module for the lab
        for time in lab_num.get("modules"):
            # Create a new dictionary for each time slot
            section = {}
            day = time.get("day")
            start = time.get("from")
            end = time.get("to")
            section["day"] = day
            section["start"] = start
            section["end"] = end
            # Append the new dictionary to the lecture's list
            lab_time[title].append(section)
    return lab_time

def parse_time(time_str):
    #transfer from string to time
    return datetime.strptime(time_str, "%H:%M").time()


def is_time_overlapping(start1, end1, start2, end2):
    start1 = parse_time(start1)
    end1 = parse_time(end1)
    start2 = parse_time(start2)
    end2 = parse_time(end2)
    
    # check if the time overlap
    return not (end1 <= start2 or end2 <= start1)

#check whether the schedule is conflict or not
def check_schedule_conflicts(new_schedule, existing_schedules):
    #check whether the overlap for new and existing schedules
    conflicts = []
    for existing in existing_schedules:
        for new in new_schedule:
            if new['day'] == existing['day']:
                if is_time_overlapping(new['start'], new['end'], existing['start'], existing['end']):
                    conflicts.append((new, existing))
    return conflicts

generateTimetable()





