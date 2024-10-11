import pytest
from unittest import mock
from app import app
import io
from werkzeug.datastructures import FileStorage

# Test for rendering the upload form (GET request)
def test_render_upload_form():
    with app.test_client() as client:
        # Act: Send a GET request to the /upload endpoint
        response = client.get('/upload')
        
        # Assert: Check that the status code is 200 and the response contains 'Upload Form'
        assert response.status_code == 200
        assert b'uploadForm' in response.data  # Check if the form is rendered

# Test for handling missing file in POST request
def test_post_request_without_file():
    with app.test_client() as client:
        # Act: Send a POST request without a file
        data = {'year': '2023', 'semester': 'Semester1'}
        response = client.post('/upload', data=data)
        
        # Assert: Check for 400 response and correct error message
        assert response.status_code == 400
        assert response.get_json() == {'error': 'No file part'}

# Test for handling an empty filename in POST request
def test_post_request_with_empty_filename():
    with app.test_client() as client:
        # Act: Send a POST request with an empty filename
        data = {
            'year': '2023', 
            'semester': 'Semester1',
            'file': (io.BytesIO(b"test data"), '')  # Empty filename
        }
        response = client.post('/upload', content_type='multipart/form-data', data=data)
        
        # Assert: Check for 400 response and correct error message
        assert response.status_code == 400
        assert response.get_json() == {'error': 'No selected file'}

# Test for successfully uploading a CSV file
@mock.patch('app.insert_student_data')  # Mock the insert_student_data function
def test_post_request_with_valid_csv(mock_insert_student_data):
    with app.test_client() as client:
        # Arrange: Simulate a CSV file wrapped in FileStorage
        csv_data = io.BytesIO(b"csv,data,content")
        file = FileStorage(stream=csv_data, filename="test.csv", content_type="text/csv")
        
        data = {
            'year': '2023', 
            'semester': 'Fall',
            'file': file  # Simulate CSV file upload wrapped in FileStorage
        }

        # Act: Send the POST request
        with mock.patch.object(FileStorage, 'save', return_value=None) as mock_save_file:
            response = client.post('/upload', content_type='multipart/form-data', data={
                'year': '2023',
                'semester': 'Semester1',
                'file': (file.stream, file.filename)  # This mimics file upload form data
            })

            # Assert: Check that the file was saved and processed correctly
            mock_save_file.assert_called_once()  # Ensure file.save was called
            mock_insert_student_data.assert_called_once_with(mock.ANY, '2023', 'Semester1')
            assert response.status_code == 200
            assert response.get_json() == {'message': 'File uploaded and data stored successfully'}

# Test for invalid file format (e.g., .txt)
def test_post_request_with_invalid_file_format():
    with app.test_client() as client:
        # Arrange: Create a simulated invalid file format
        data = {
            'year': '2023', 
            'semester': 'Semester1',
            'file': (io.BytesIO(b"some data"), 'test.txt')  # Simulate invalid file upload
        }

        # Act: Send the POST request
        response = client.post('/upload', content_type='multipart/form-data', data=data)
        
        # Assert: Check for 400 response and correct error message
        assert response.status_code == 400
        assert response.get_json() == {'error': 'Invalid file format'}
