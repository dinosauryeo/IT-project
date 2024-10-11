import pytest
from unittest import mock
from app import app

# Setup for test client
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

### Test cases for /generate_timetable (POST)

@mock.patch('app.MongoClient')  # Mock MongoDB connection
@mock.patch('app.generate_timetable_for_students')  # Mock timetable generation function
def test_generate_timetable_success(mock_generate_timetable, mock_mongo, client):
    # Mock the timetable generation function to return some timetables
    mock_generate_timetable.return_value = (
        [{'student_id': '123', 'timetable': 'some_data'}],  # Generated timetables
        []  # No error messages
    )

    # Mock the MongoDB insert_one function
    mock_collection = mock_mongo.return_value['Students-Timetable']['Timetables']
    mock_collection.insert_one.return_value = None

    # Act: Send a POST request to /generate_timetable
    response = client.post('/generate_timetable')

    # Assert: Check if the response is successful
    assert response.status_code == 200
    assert response.get_json() == {'status': 'success', 'message': 'Timetable generated and saved successfully!'}
    mock_generate_timetable.assert_called_once()
    mock_collection.insert_one.assert_called_once_with({'student_id': '123', 'timetable': 'some_data'})


@mock.patch('app.MongoClient')  # Mock MongoDB connection
@mock.patch('app.generate_timetable_for_students')  # Mock timetable generation function
def test_generate_timetable_failure(mock_generate_timetable, mock_mongo, client):
    # Mock the timetable generation function to return no timetables
    mock_generate_timetable.return_value = ([], [])  # No timetables, no error messages

    # Act: Send a POST request to /generate_timetable
    response = client.post('/generate_timetable')

    # Assert: Check if the response indicates a failure
    assert response.status_code == 200
    assert response.get_json() == {'status': 'error', 'message': 'Failed to generate timetable'}
    mock_generate_timetable.assert_called_once()


@mock.patch('app.MongoClient')  # Mock MongoDB connection
@mock.patch('app.generate_timetable_for_students')  # Mock timetable generation function
def test_generate_timetable_exception(mock_generate_timetable, mock_mongo, client):
    # Mock the timetable generation function to raise an exception
    mock_generate_timetable.side_effect = Exception('Something went wrong')

    # Act: Send a POST request to /generate_timetable
    response = client.post('/generate_timetable')

    # Assert: Check if the response indicates an error occurred
    assert response.status_code == 200
    assert response.get_json() == {'status': 'error', 'message': 'An error occurred while generating the timetable'}
    mock_generate_timetable.assert_called_once()
