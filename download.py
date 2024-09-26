import csv
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.drawing.image import Image
from openpyxl.styles import Border, Side


TIME = 60
COLUMN_C = 87.67
COLUMN_B = 29.67
COLUMN_A = 11.5
COLUMN_D = 25.67
COLUMN_E = 14.33
COLUMN_G = 24.5
ROW = 9
TITLE = 3
HEADER = 5
SIZE = 11
ROW_HEIGHT = 30
BLUE = "0000FF"
BLACK = "000000"
RED = "FF0000"
GREY = "C0C0C0"
LIGHT_BLUE = "E0FFFF"
HORIZONTAL = 'center'
LEFT = 'left'
TAHOMA = 'Tahoma'


'''change the time format'''
def format_time(time_str):
    return time_str.lstrip('0') if time_str.startswith('0') else time_str


'''calculate class time interval'''
def calculate_duration(start_time, end_time):
    """calculate time interval for lecture/lab/tutorial"""
    time_format = "%H:%M" 
    start = datetime.strptime(start_time, time_format)
    end = datetime.strptime(end_time, time_format)

    # calculate duriation
    duration = end - start
    total_minutes = duration.total_seconds() // TIME
    hours = total_minutes // TIME
    minutes = total_minutes % TIME
    if minutes == 0:
        return (str(hours)+'h').replace('.0', '')
    else:
        return (str(hours)+'h'+ str(minutes) +'min').replace('.0', '')



'''translate csv timetable into excel
with well structured format and meet target output design '''
def csv_to_excel(csv_file, excel_file):
    # create border feature
    thin_border = Border(left=Side(style='thin'),
                     right=Side(style='thin'),
                     top=Side(style='thin'),
                     bottom=Side(style='thin'))
    tahoma_font = Font(name = TAHOMA, size = SIZE)
    # create a Excelwritter 
    with pd.ExcelWriter(excel_file, engine = 'openpyxl') as writer:
        workbook = writer.book
        #create new work sheet
        worksheet = workbook.create_sheet(title = 'Timetable') 
        worksheet.column_dimensions['A'].width = COLUMN_A
        worksheet.column_dimensions['B'].width = COLUMN_B
        worksheet.column_dimensions['C'].width = COLUMN_C
        worksheet.column_dimensions['D'].width = COLUMN_D
        worksheet.column_dimensions['E'].width = COLUMN_E
        worksheet.column_dimensions['F'].width = COLUMN_E
        worksheet.column_dimensions['G'].width = COLUMN_G
        # image add
        img = Image('templates/static/images/uniphoto.png')  
        worksheet.add_image(img, 'A1')
        
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
        for row in range(1, ROW - 1):
            if row < TITLE:
                merged_cell = worksheet[f'B{row}']
                merged_cell.alignment = Alignment(horizontal=HORIZONTAL, vertical=HORIZONTAL)
                #blue color
                merged_cell.font = Font(color = BLUE, bold = True, name=TAHOMA,size = SIZE) 
            elif TITLE <= row < HEADER:
                merged_cell = worksheet[f'B{row}']
                merged_cell.alignment = Alignment(horizontal= HORIZONTAL, vertical= HORIZONTAL)
                merged_cell.font = Font(color = BLACK, bold = True, name=TAHOMA,size = SIZE) 
            else:
                #red color
                merged_cell = worksheet[f'A{row}']
                merged_cell.alignment = Alignment(horizontal = LEFT, vertical = HORIZONTAL)
                merged_cell.font = Font(color = RED, bold = True, name=TAHOMA, size = SIZE)    

            
        # grey back ground and font
        header_fill = PatternFill(start_color= GREY , end_color = GREY, fill_type="solid")  
        header_font = Font(bold=True, color = BLACK, name = TAHOMA)
        columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        for column in columns:
            cell = worksheet[f'{column}9']
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal = HORIZONTAL, vertical = HORIZONTAL)
            cell.border = thin_border
        #set data background into light blue color
        for row_index, row in data.iterrows():
            for col_index in range(len(row)):
                cell = worksheet.cell(row = row_index + ROW + 1, column = col_index + 1)
                cell.fill = PatternFill(start_color = LIGHT_BLUE, end_color = LIGHT_BLUE, fill_type = "solid")
                cell.font = tahoma_font
                cell.border = thin_border
        worksheet.row_dimensions[ROW].height = ROW_HEIGHT
        worksheet['D9'].alignment = Alignment(horizontal = HORIZONTAL, vertical = HORIZONTAL, wrap_text = True)






'''
The method is to download each student timetable file from MongoDB 
transfer into csv with student id _timetable
'''
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
            fieldnames = ['Day', 'Time', 'Unit', 'Classroom\nLevel/ Room/ Venue', 'Lecturer', 'Tutor', 'Delivery Mode']
            writer = csv.DictWriter(file, fieldnames = fieldnames)
            writer.writeheader()
            if sorted_timetables:
                for timetable in sorted_timetables:
                    row = {
                        'Day': timetable.get('Day', '').capitalize(),
                        'Time': format_time(timetable.get('From', '')) + ' to ' + format_time(timetable.get('To', '')) + "(L + T)",
                        'Unit': timetable.get('SubjectCode', '') + '-' + timetable.get('SubjectName', '') + '(' + calculate_duration(format_time(timetable.get('From', '')) , format_time(timetable.get('To', ''))) +' ' +timetable.get('Title', '') + ')',
                        'Classroom\nLevel/ Room/ Venue': timetable.get('Location', ''),
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