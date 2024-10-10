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
    // Populate the Year dropdown with past 5 years and 1 year ahead
    const yearSelect = document.getElementById('yearSelect');
    const currentYear = new Date().getFullYear();
    for (let i = currentYear - 5; i <= currentYear + 1; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = i;
        yearSelect.appendChild(option);
    }

    // Handle form submission
    document.getElementById('uploadForm').addEventListener('submit', function(event) {
        event.preventDefault();

        // Get selected year and semester
        const year = document.getElementById('yearSelect').value;
        const semester = document.getElementById('semesterSelect').value;

        // Create a new FormData object and append year and semester
        const formData = new FormData(this);
        formData.append('year', year);
        formData.append('semester', semester);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
            } else if (data.error) {
                alert(data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred');
        });
    });
});
