function generateTimetable() {
    fetch('/generate_timetable', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})  // 不需要额外数据
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
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