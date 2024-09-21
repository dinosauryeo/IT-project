import csv
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

def format_time(time_str):
    return time_str.lstrip('0') if time_str.startswith('0') else time_str


def calculate_duration(start_time, end_time):
    """calculate time interval for lecture/lab/tutorial"""
    time_format = "%H:%M" 
    start = datetime.strptime(start_time, time_format)
    end = datetime.strptime(end_time, time_format)

    # calculate duriation
    duration = end - start
    total_minutes = duration.total_seconds() // 60
    hours = total_minutes // 60
    minutes = total_minutes % 60
    if minutes == 0:
        return (str(hours)+'h').replace('.0', '')
    else:
        return (str(hours)+'h'+ str(minutes) +'min').replace('.0', '')


def csv_to_excel(csv_file, excel_file):
    # create a Excelwritter 
    with pd.ExcelWriter(excel_file, engine = 'openpyxl') as writer:
        workbook = writer.book
        #create new work sheet
        worksheet = workbook.create_sheet(title = 'Timetable') 
        worksheet.column_dimensions['C'].width = 87.67
        worksheet.column_dimensions['B'].width = 29.67
        worksheet.column_dimensions['A'].width = 11.5
        worksheet.column_dimensions['D'].width = 25.67
        worksheet.column_dimensions['E'].width = 14.33
        worksheet.column_dimensions['E'].width = 14.33
        worksheet.column_dimensions['G'].width = 24.5
        # import title
        worksheet.append(['']*1 + ["Victorian Institute of Technology Pty Ltd"])
        worksheet.append(['']*1 + ["ABN: 41 085 128 525 RTO No: 20829 TEQSA ID: PRV14007 CRICOS Provider Code: 02044E"])
        worksheet.append(['']*1 + ["Master of Information Technology and Systems"])
        worksheet.append(['Timetable: ']*1 + ["Venue: 123 & 235 Queens Street, Melbourne"])
        worksheet.append(["Note: (a) This is a Master Timetable. You are required to refer to your Unit Allocation (i.e., your enrolled units) to know which units/sessions are applicable to you."])
        worksheet.append(["(b) Time Table may change in the event of some exigencies.(c) Units have additional consulting sessions (based on unit requirements) which is not reflected below including online guided learning"])
        worksheet.append(["(d) L- Lecture (2hr), P- Practical (1hr), T - Tutorial/Lab/Guided Learning (1hr) (e) TA -Teaching Assistant as Rostered."])
        worksheet.append([])  
        data = pd.read_csv(csv_file)
        worksheet.append(list(data.columns))
        #read data into excel
        for row in data.itertuples(index=False):
            # append each line into excel
            worksheet.append(row) 
        worksheet.merge_cells('B1:G1') 
        worksheet.merge_cells('B2:G2') 
        worksheet.merge_cells('B3:G3') 
        worksheet.merge_cells('B4:G4')
        worksheet.merge_cells('A5:G5')
        worksheet.merge_cells('A6:G6')
        worksheet.merge_cells('A7:G7')
        for row in range(1, 8):
            if row < 3:
                merged_cell = worksheet[f'B{row}']
                merged_cell.alignment = Alignment(horizontal='center', vertical='center')
                #blue color
                merged_cell.font = Font(color="0000FF", bold = True) 
            elif 2 < row < 5:
                merged_cell = worksheet[f'B{row}']
                merged_cell.alignment = Alignment(horizontal='center', vertical='center')
                merged_cell.font = Font(color="000000", bold = True) 
            else:
                #red color
                merged_cell = worksheet[f'A{row}']
                merged_cell.alignment = Alignment(horizontal='left', vertical='center')
                merged_cell.font = Font(color="FF0000", bold = True) 





def download():
    client = MongoClient('mongodb+srv://dinosauryeo:6OHYa6vF6YUCk48K@cluster0.dajn796.mongodb.net/')
    db = client['Students-Timetable']  
    collection = db['Timetables']
    days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

    # extract each student timetable
    for document in collection.find():
        student_id = document['StudentID']
        timetables = document.get('Timetable', [])
        sorted_timetables = sorted(timetables, key=lambda x: (days_order.index(x['Day']), datetime.strptime(x['From'], '%H:%M')))
        # create each students' csv
        filename = f'{student_id}_timetable.csv'
        with open(filename, 'w', newline = '', encoding = 'utf-8') as file:
            fieldnames = ['Day', 'Time', 'Unit', 'Classroom Level/ Room/ Venue', 'Lecturer', 'Tutor', 'Delivery Mode']
            writer = csv.DictWriter(file, fieldnames = fieldnames)
            writer.writeheader()

            if sorted_timetables:
                for timetable in sorted_timetables:
                    row = {
                        'Day': timetable.get('Day', ''),
                        'Time': format_time(timetable.get('From', '')) + ' to ' + format_time(timetable.get('To', '')) + "(L + T)",
                        'Unit': timetable.get('SubjectCode', '') + '-' + timetable.get('SubjectName', '') + '(' + calculate_duration(format_time(timetable.get('From', '')) , format_time(timetable.get('To', ''))) +' ' +timetable.get('Title', '') + ')',
                        'Classroom Level/ Room/ Venue': timetable.get('Location', ''),
                        'Lecturer': timetable.get('Lecturer', ''),
                        'Tutor': timetable.get('Tutor', ''),
                        'Delivery Mode': timetable.get('Mode', '')
                    }
                    writer.writerow(row)
            else:
                print(f"No timetable found for StudentID: {student_id}")
        csv_to_excel(filename, f'{student_id}_timetable.xlsx')
if __name__ == "__main__":
    download()