import csv
from pymongo import MongoClient

client = MongoClient('mongodb+srv://dinosauryeo:6OHYa6vF6YUCk48K@cluster0.dajn796.mongodb.net/')
db = client['IT-project']  
collection = db['User-data']

data = list(collection.find({}))

if data:
    fieldnames = data[0].keys()
    with open('output.csv', 'w', newline='', encoding = 'utf-8') as file:
        writer = csv.DictWriter(file, fieldnames = fieldnames)
        writer.writeheader()
        for document in data:
            writer.writerow(document)
else:
    print("No data found.")