function loadHomePage(){
    window.location.href = '/home';
}
function loadStudentPage(){
    window.location.href = '/student';
}
function loadUploadPage(){
    window.location.href = '/upload';
}
function loadGeneratePage(){
    window.location.href = '/generate';
}
function addSubject() {
    window.location.href = '/createsubject';
}
// Function to handle logout
function logout() {
    window.location.href = '/logout';
}

function showPage(pageId) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.style.display = 'none';
    });

    // Show the selected page
    document.getElementById(pageId).style.display = 'block';
    // Update active class for navbar items
    document.querySelectorAll('.navbar li').forEach(item => {
        item.classList.remove('active');
    });
    const activeItem = document.getElementById(`${pageId}-link`);
    if (activeItem) {
        activeItem.classList.add('active');
    }
}

//Hover event for Home link
document.getElementById('home-link').addEventListener('click', function() {
    showPage('home');
});

document.addEventListener('DOMContentLoaded', function () {
    // Get all the navbar items
    var navbarItems = document.querySelectorAll('.navbar li');

    // Loop through each item
    navbarItems.forEach(function (item) {
        item.addEventListener('click', function () {
            // Remove 'active' class from all items
            navbarItems.forEach(function (el) {
                el.classList.remove('active');
            });
            // Add 'active' class to the clicked item
            this.classList.add('active');
        });
    });

    // Dynamic Year dropdown population
    const yearSelect = document.getElementById('yearSelect');
    const currentYear = new Date().getFullYear();

    for (let i = 0; i < 5; i++) {  // Example: add 5 years ahead
        let option = document.createElement('option');
        option.value = currentYear + i;
        option.text = currentYear + i;
        yearSelect.appendChild(option);
    }
});

function generateTimetable() {
    // 获取选中的年份和学期
    const year = document.getElementById('yearSelect').value;
    const semester = document.getElementById('semesterSelect').value;

    // 将Year和Semester数据发送到后端
    fetch('/generate_timetable', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ year: year, semester: semester })  // 传递year和semester数据
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
