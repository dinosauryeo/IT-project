function generateTimetable() {
    fetch('/generate_timetable', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // Adding a body with empty object as your Flask route doesn’t need specific data
        body: JSON.stringify({})
    })
    .then(response => {
        // Check if the response is OK (status code 200-299)
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            console.log('Timetable generated and saved with ID:', data.id);
            alert('Timetable generated and saved successfully!');
        } else {
            alert('Failed to generate timetable: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error generating timetable:', error);
        alert('An error occurred while generating the timetable. Please try again later.');
    });
}
