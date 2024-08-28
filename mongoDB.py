
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo
from datetime import datetime, timedelta

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
        "$or":[{"username":username},{"email":username}],
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
    query = {"email": email}

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
    query = {"email":email,"verification_code":int(vericode)}
    
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
        