
function loadHomePage(){
    window.location.href = '/home';
}
function loadStudentPage(){
    console.log("load student page");
    window.location.href = '/student';
    fetchStudents();
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

});


// 14/09 10:21 modify
// write send email to student 
function SendEmailToStudents(){
    fetch('/send_timetable', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log("timetable(fake) sent");
            alert("Timetable had been sent");
        } 
        else {
            console.log("timetable failed to send");
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred');
    });
}

//Hover event for Home link
document.getElementById('home-link').addEventListener('click', function() {
    showPage('home');
});



document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var formData = new FormData(this);

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

// Function to handle logout
function logout() {
    window.location.href = '/logout';
}




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
    // Initialize counters for each section type
    const sectionCounters = {
        lecture: 0,
        tutorial: 0,
        lab: 0
    };

    // Populate the year dropdown with years from 2000 to current year + 1
    const yearSelect = document.getElementById('year');
    const currentYear = new Date().getFullYear();
    for (let year = 2000; year <= currentYear + 1; year++) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        yearSelect.appendChild(option);
    }

    // Function to generate time options
    function generateTimeOptions() {
        const times = [];
        for (let h = 7; h <= 22; h++) {
            for (let m = 0; m < 60; m += 15) {
                const hour = h.toString().padStart(2, '0');
                const minute = m.toString().padStart(2, '0');
                times.push(`${hour}:${minute}`);
            }
        }
        return times;
    }

    // Populate the time dropdowns
    function populateTimeDropdowns() {
        const times = generateTimeOptions();
        const timeSelects = document.querySelectorAll('.section .time-dropdown');
        timeSelects.forEach(select => {
            times.forEach(time => {
                const option = document.createElement('option');
                option.value = time;
                option.textContent = time;
                select.appendChild(option);
            });
        });
    }

    populateTimeDropdowns();

    // Handle "Add Section" button click
    document.getElementById('add-section').addEventListener('click', function () {
        const additionalSections = document.getElementById('additional-sections');
        const sectionType = prompt('Enter section type (lecture/tutorial/lab):').toLowerCase();
        
        if (sectionCounters.hasOwnProperty(sectionType)) {
            sectionCounters[sectionType]++;
            const sectionDiv = document.createElement('div');
            sectionDiv.className = 'section';
            sectionDiv.innerHTML = `
                <div class="section-title">${sectionType.charAt(0).toUpperCase() + sectionType.slice(1)} ${sectionCounters[sectionType]}</div>
                <div class="select-row">
                    <select id="${sectionType}-day" name="${sectionType}-day">
                        <option value="" disabled selected>Day</option>
                        <option value="monday">Monday</option>
                        <option value="tuesday">Tuesday</option>
                        <option value="wednesday">Wednesday</option>
                        <option value="thursday">Thursday</option>
                        <option value="friday">Friday</option>
                        <option value="saturday">Saturday</option>
                        <option value="sunday">Sunday</option>
                    </select>
                    <select id="${sectionType}-from" name="${sectionType}-from" class="time-dropdown">
                        <option value="" disabled selected>From</option>
                    </select>
                    <select id="${sectionType}-to" name="${sectionType}-to" class="time-dropdown">
                        <option value="" disabled selected>To</option>
                    </select>
                </div>
                <div class="select-row">
                    <input type="text" id="${sectionType}-name" name="${sectionType}-name" placeholder="${sectionType === 'lecture' ? 'Lecturer' : 'Tutor'}">
                    <input type="text" id="${sectionType}-location" name="${sectionType}-location" placeholder="Location">
                    <select id="${sectionType}-mode" name="${sectionType}-mode">
                        <option value="" disabled selected>Delivery Modes</option>
                        <option value="online">Online</option>
                        <option value="oncampus">On Campus</option>
                    </select>
                </div>
            `;
            
            additionalSections.appendChild(sectionDiv);
            populateTimeDropdowns(); // Populate time dropdowns after adding a new section
        } else {
            alert('Invalid section type');
        }
    });

    // Show the Create Subject page when "Add Subject" is clicked
    document.querySelector('button[onclick="addSubject()"]').addEventListener('click', function () {
        showPage('create-subject');
    });
});



function fetchStudents() {
    fetch('/students_timetable')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data); // 在控制台输出学生数据
            renderStudents(data); // 调用渲染函数，将数据渲染到页面上
        })
        .catch(error => {
            console.error('Error fetching students:', error);
        });
}
function renderStudents(students) {
    const studentContainer = document.getElementById('studentContainer'); // 假设你的容器 ID 是 studentContainer
    studentContainer.innerHTML = ''; // 清空容器

    students.forEach(student => {
        const studentDiv = document.createElement('div');
        studentDiv.textContent = `${student.id}: ${student.name}`; // 使用正确的属性
        studentContainer.appendChild(studentDiv);
    });
}