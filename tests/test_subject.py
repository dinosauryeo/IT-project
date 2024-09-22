import pytest
from unittest import mock
from app import app

# Setup for test client
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

### Test cases for /editsubject (POST)
@mock.patch('app.MongoClient')  # Mock MongoDB connection
def test_edit_subject_success(mock_mongo, client):
    mock_collection = mock_mongo.return_value['2023_Semester1']['Subjects-Details']
    mock_collection.update_one.return_value.matched_count = 1

    # Prepare the payload
    data = {
        'year': '2023',
        'semester': 'Semester1',
        'subjectCode': 'CS101',
        'subjectName': 'Computer Science'
    }

    # Act: Send a POST request to /editsubject
    response = client.post('/editsubject', json=data)

    # Assert: Check if the response is successful
    assert response.status_code == 200
    assert response.get_json() == {'status': 'success', 'message': 'Subject updated successfully'}
    mock_collection.update_one.assert_called_once_with(
        {'subjectCode': 'CS101'},
        {'$set': data}
    )

@mock.patch('app.MongoClient')  # Mock MongoDB connection
def test_edit_subject_not_found(mock_mongo, client):
    mock_collection = mock_mongo.return_value['2023_Semester1']['Subjects-Details']
    mock_collection.update_one.return_value.matched_count = 0

    # Prepare the payload
    data = {
        'year': '2023',
        'semester': 'Semester1',
        'subjectCode': 'CS101',
        'subjectName': 'Computer Science'
    }

    # Act: Send a POST request to /editsubject
    response = client.post('/editsubject', json=data)

    # Assert: Check if the response is a subject not found
    assert response.status_code == 404
    assert response.get_json() == {'status': 'error', 'message': 'Subject not found'}
    mock_collection.update_one.assert_called_once_with(
        {'subjectCode': 'CS101'},
        {'$set': data}
    )

### Test cases for /createsubject (POST)
@mock.patch('app.mongoDB')  # Mock the mongoDB interaction
def test_create_subject_success(mock_mongoDB, client):
    # Mock the insert_subject method
    mock_mongoDB.insert_subject.return_value = 'some_document_id'

    # Prepare the payload
    data = {
        'year': '2023',
        'semester': 'Semester1',
        'campus': 'Main',
        'coordinator': 'Dr. Smith',
        'subjectName': 'Math 101',
        'subjectCode': 'MTH101',
        'sections': ['A', 'B', 'C']
    }

    # Act: Send a POST request to /createsubject
    response = client.post('/createsubject', json=data)

    # Assert: Check if the response is successful
    assert response.status_code == 200
    assert response.get_json() == {'status': 'success'}
    mock_mongoDB.insert_subject.assert_called_once_with(data, '2023', 'Semester1')

@mock.patch('app.mongoDB')  # Mock the mongoDB interaction
def test_create_subject_failure(mock_mongoDB, client):
    # Mock insert_subject to raise an exception
    mock_mongoDB.insert_subject.side_effect = Exception("Insert failed")

    # Prepare the payload
    data = {
        'year': '2023',
        'semester': 'Semester1',
        'campus': 'Main',
        'coordinator': 'Dr. Smith',
        'subjectName': 'Math 101',
        'subjectCode': 'MTH101',
        'sections': ['A', 'B', 'C']
    }

    # Act: Send a POST request to /createsubject
    response = client.post('/createsubject', json=data)

    # Assert: Check if the response indicates failure
    assert response.status_code == 500
    assert response.get_json() == {'status': 'error', 'message': 'Failed to create subject'}
    mock_mongoDB.insert_subject.assert_called_once_with(data, '2023', 'Semester1')

### Test cases for /getsubjects (GET)
@mock.patch('app.MongoClient')  # Mock MongoDB connection
def test_get_subjects_success(mock_mongo, client):
    mock_collection = mock_mongo.return_value['2023_Semester1']['Subjects-Details']
    mock_collection.find.return_value = [
        {'subjectCode': 'CS101', 'subjectName': 'Computer Science', 'coordinator': 'Dr. Smith', 'campus': 'Main'},
        {'subjectCode': 'MTH101', 'subjectName': 'Math 101', 'coordinator': 'Dr. Jones', 'campus': 'Main'}
    ]

    # Act: Send a GET request to /getsubjects
    response = client.get('/getsubjects?year_semester=2023_Semester1')

    # Assert: Check if the response is successful
    assert response.status_code == 200
    assert response.get_json() == [
        {'subjectString': 'CS101 - Computer Science', 'subjectCode': 'CS101', 'coordinator': 'Dr. Smith', 'campus': 'Main'},
        {'subjectString': 'MTH101 - Math 101', 'subjectCode': 'MTH101', 'coordinator': 'Dr. Jones', 'campus': 'Main'}
    ]
    mock_collection.find.assert_called_once()

@mock.patch('app.MongoClient')  # Mock MongoDB connection
def test_get_subjects_missing_year_semester(mock_mongo, client):
    # Act: Send a GET request to /getsubjects without year_semester
    response = client.get('/getsubjects')

    # Assert: Check if the response indicates a bad request
    assert response.status_code == 400
    assert response.get_json() == {'status': 'error', 'message': 'Year and semester are required'}

### Test cases for /getsubjectdetails (GET)
@mock.patch('app.MongoClient')  # Mock MongoDB connection
def test_get_subject_details_success(mock_mongo, client):
    mock_collection = mock_mongo.return_value['2023_Semester1']['Subjects-Details']
    mock_collection.find_one.return_value = {
        'subjectCode': 'CS101',
        'subjectName': 'Computer Science',
        'coordinator': 'Dr. Smith',
        'campus': 'Main'
    }

    # Act: Send a GET request to /getsubjectdetails
    response = client.get('/getsubjectdetails?subject_code=CS101&year_semester=2023_Semester1')

    # Assert: Check if the response is successful
    assert response.status_code == 200
    assert response.get_json() == {
        'subjectCode': 'CS101',
        'subjectName': 'Computer Science',
        'coordinator': 'Dr. Smith',
        'campus': 'Main'
    }
    mock_collection.find_one.assert_called_once_with({'subjectCode': 'CS101'}, {'_id': 0})

@mock.patch('app.MongoClient')  # Mock MongoDB connection
def test_get_subject_details_not_found(mock_mongo, client):
    mock_collection = mock_mongo.return_value['2023_Semester1']['Subjects-Details']
    mock_collection.find_one.return_value = None

    # Act: Send a GET request to /getsubjectdetails with a subject that doesn't exist
    response = client.get('/getsubjectdetails?subject_code=CS101&year_semester=2023_Semester1')

    # Assert: Check if the response indicates subject not found
    assert response.status_code == 404
    assert response.get_json() == {'status': 'error', 'message': 'Subject not found'}
    mock_collection.find_one.assert_called_once_with({'subjectCode': 'CS101'}, {'_id': 0})
