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
function loadLocationPage() {
    window.location.href = '/location';
}
function loadRegistrationPage() {
    window.location.href = '/register';
}

function toggleMenu() {
    const sideMenu = document.getElementById('sideMenu');
    const overlay = document.getElementById('overlay');
    
    if (sideMenu.classList.contains('active')) {
        sideMenu.classList.remove('active');
        overlay.style.display = 'none';
    } else {
        sideMenu.classList.add('active');
        overlay.style.display = 'block';
    }
}

// Close menu when clicking outside
document.addEventListener('click', function(event) {
    const sideMenu = document.getElementById('sideMenu');
    const hamburgerMenu = document.querySelector('.hamburger-menu');
    
    if (!sideMenu.contains(event.target) && !hamburgerMenu.contains(event.target)) {
        sideMenu.classList.remove('active');
        document.getElementById('overlay').style.display = 'none';
    }
});

// Prevent clicks inside the menu from closing it
document.getElementById('sideMenu').addEventListener('click', function(event) {
    event.stopPropagation();
});

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
    const startYear = 2019;

    for (let year = startYear; year <= currentYear + 1; year++) {
        let option = document.createElement('option');
        option.value = year;
        option.text = year;
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
