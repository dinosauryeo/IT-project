import pytest  # For writing and running tests
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock  # For mocking dependencies like MongoDB, ObjectId, etc.
from flask import Flask  # Needed for the Flask client used in the tests
from app import app  # Import your Flask app from the application module

# Test client setup
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Mocking MongoClient to prevent actual database interaction
@pytest.fixture
def mock_mongo_client():
    with patch('app.MongoClient') as mock_client:
        yield mock_client

@patch('app.mongoDB.login')
def test_add_buildings_success(mock_mongo_login, client):
    # Mock the MongoDB client and collection
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()

    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    # Mock find_one to return None (building does not exist)
    mock_collection.find_one.return_value = None

    mock_mongo_login.return_value = mock_client

    # Mock data for buildings
    data = {
        'campus': 'Melbourne',
        'buildings': ['Building A', 'Building B']
    }

    # Make a POST request to add buildings
    response = client.post('/add_buildings', json=data)

    # Assert that the response is successful
    assert response.status_code == 201
    assert b'success' in response.data

    # Ensure insert_one was called twice (for each building)
    assert mock_collection.insert_one.call_count == 2

@patch('app.mongoDB.login')
def test_add_buildings_already_exist(mock_mongo_login, client):
    # Mock the MongoDB client and collection
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()

    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    # Mock find_one to return a value (building already exists)
    mock_collection.find_one.return_value = {'building': 'Building A'}

    mock_mongo_login.return_value = mock_client

    # Mock data for buildings
    data = {
        'campus': 'Melbourne',
        'buildings': ['Building A']
    }

    # Make a POST request to add buildings
    response = client.post('/add_buildings', json=data)

    # Assert that the response is successful, but no insertions were made
    assert response.status_code == 201
    assert b'success' in response.data

    # Ensure insert_one was not called because the building already exists
    mock_collection.insert_one.assert_not_called()

@patch('app.mongoDB.login')
def test_add_classrooms_success(mock_mongo_login, client):
    # Mock the MongoDB client and collection
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()

    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    mock_mongo_login.return_value = mock_client

    # Mock data for classrooms
    data = {
        'campus': 'Melbourne',
        'building': 'Building A',
        'classroomData': [
            {
                'level': '1',
                'classrooms': ['Room 101', 'Room 102']
            }
        ]
    }

    # Make a POST request to add classrooms
    response = client.post('/add_classrooms', json=data)

    # Assert that the response is successful
    assert response.status_code == 201
    assert b'success' in response.data

    # Ensure insert_one was called twice (for each classroom)
    assert mock_collection.insert_one.call_count == 2

@patch('app.mongoDB.login')
@patch('app.ObjectId')
def test_delete_location_success(mock_objectid, mock_mongo_login, client):
    # Mock the MongoDB client and collection
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()

    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    # Mock delete_one to return a successful deletion (deleted_count = 1)
    mock_collection.delete_one.return_value.deleted_count = 1

    mock_mongo_login.return_value = mock_client

    # Mock ObjectId conversion
    mock_objectid.return_value = 'fake_location_id'

    # Make a DELETE request to remove the location
    response = client.delete('/delete_location/fake_location_id')

    # Assert that the response is successful
    assert response.status_code == 200
    assert b'success' in response.data

    # Ensure delete_one was called
    mock_collection.delete_one.assert_called_once_with({'_id': 'fake_location_id'})

@patch('app.mongoDB.login')
@patch('app.ObjectId')
def test_delete_location_not_found(mock_objectid, mock_mongo_login, client):
    # Mock the MongoDB client and a single database
    mock_client = MagicMock()
    mock_db = MagicMock()

    mock_client.__getitem__.return_value = mock_db
    
    # Mock the four collections for the different campuses
    mock_collection_melbourne = MagicMock()
    mock_collection_geelong = MagicMock()
    mock_collection_adelaide = MagicMock()
    mock_collection_sydney = MagicMock()

    mock_db.__getitem__.side_effect = [
        mock_collection_melbourne,
        mock_collection_geelong,
        mock_collection_adelaide,
        mock_collection_sydney
    ]
    
    # Mock the delete_one method and its deleted_count attribute for each collection
    mock_collection_melbourne.delete_one.return_value.deleted_count = 0
    mock_collection_geelong.delete_one.return_value.deleted_count = 0
    mock_collection_adelaide.delete_one.return_value.deleted_count = 0
    mock_collection_sydney.delete_one.return_value.deleted_count = 0

    mock_mongo_login.return_value = mock_client

    # Mock ObjectId conversion
    mock_objectid.return_value = 'fake_location_id'

    # Make a DELETE request to remove the location
    response = client.delete('/delete_location/fake_location_id')

    # Assert that the response is a 404 error
    assert response.status_code == 404
    assert b'Location not found' in response.data

    # Ensure delete_one was called on all campus collections
    mock_collection_melbourne.delete_one.assert_called_once_with({'_id': 'fake_location_id'})
    mock_collection_geelong.delete_one.assert_called_once_with({'_id': 'fake_location_id'})
    mock_collection_adelaide.delete_one.assert_called_once_with({'_id': 'fake_location_id'})
    mock_collection_sydney.delete_one.assert_called_once_with({'_id': 'fake_location_id'})



@patch('app.mongoDB.login')
def test_delete_all_buildings_in_campus_success(mock_mongo_login, client):
    # Mock the MongoDB client and collection
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()

    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    # Mock delete_many to return a successful deletion (deleted_count > 0)
    mock_collection.delete_many.return_value.deleted_count = 5

    mock_mongo_login.return_value = mock_client

    # Make a DELETE request to remove all buildings in a campus
    response = client.delete('/delete_all_buildings_in_campus/Melbourne')

    # Assert that the response is successful
    assert response.status_code == 200
    assert b'Deleted 5 documents' in response.data

    # Ensure delete_many was called
    mock_collection.delete_many.assert_called_once_with({})

@patch('app.mongoDB.login')
def test_delete_all_buildings_in_campus_not_found(mock_mongo_login, client):
    # Mock the MongoDB client and collection
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()

    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    # Mock delete_many to return no deletion (deleted_count = 0)
    mock_collection.delete_many.return_value.deleted_count = 0

    mock_mongo_login.return_value = mock_client

    # Make a DELETE request to remove all buildings in a campus
    response = client.delete('/delete_all_buildings_in_campus/Melbourne')

    # Assert that the response is a 404 error
    assert response.status_code == 404
    assert b'No documents found to delete' in response.data

    # Ensure delete_many was called
    mock_collection.delete_many.assert_called_once_with({})

@patch('app.mongoDB.login')
def test_delete_all_classrooms_in_building_success(mock_mongo_login, client):
    # Mock the MongoDB client and collection
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()

    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    # Mock delete_many to return a successful deletion (deleted_count > 0)
    mock_collection.delete_many.return_value.deleted_count = 3

    mock_mongo_login.return_value = mock_client

    # Make a DELETE request to remove all classrooms in a building
    response = client.delete('/delete_all_classrooms_in_building/Melbourne/BuildingA')

    # Assert that the response is successful
    assert response.status_code == 200
    assert b'Deleted 3 classrooms' in response.data

    # Ensure delete_many was called with the correct filter
    mock_collection.delete_many.assert_called_once_with({'building': 'BuildingA', 'classroom': {'$exists': True}})

@patch('app.mongoDB.login')
def test_delete_all_classrooms_in_building_not_found(mock_mongo_login, client):
    # Mock the MongoDB client and collection
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()

    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    # Mock delete_many to return no deletion (deleted_count = 0)
    mock_collection.delete_many.return_value.deleted_count = 0

    mock_mongo_login.return_value = mock_client

    # Make a DELETE request to remove all classrooms in a building
    response = client.delete('/delete_all_classrooms_in_building/Melbourne/BuildingA')

    # Assert that the response is a 404 error
    assert response.status_code == 404
    assert b'No classrooms found to delete' in response.data

    # Ensure delete_many was called with the correct filter
    mock_collection.delete_many.assert_called_once_with({'building': 'BuildingA', 'classroom': {'$exists': True}})



