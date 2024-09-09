
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




// Function to handle logout
function logout() {
    window.location.href = '/logout';
}



document.addEventListener('DOMContentLoaded', function () {
    fetch('/getsubjects')
        .then(response => response.json())
        .then(data => {
            if (Array.isArray(data)) {
                const subjectDropdown = document.getElementById('subject-dropdown');
                subjectDropdown.innerHTML = '';  // Clear existing options

                // Populate the dropdown with subjects
                data.forEach(subject => {
                    const option = document.createElement('option');
                    option.value = subject.subjectCode;
                    option.textContent = `${subject.subjectCode} - ${subject.subjectName}`;
                    subjectDropdown.appendChild(option);
                });

                // Optionally, load details of the first subject
                if (data.length > 0) {
                    loadSubjectDetails(data[0]);
                }
            } else {
                alert('Error fetching subjects: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error fetching subjects.');
        });
});

function loadSubjectDetails(subject) {
    // Set subject code and title
    document.getElementById('subject-code-title').textContent = `${subject.subjectCode} - ${subject.subjectName}`;
    
    // Set delivery mode
    if (subject.sections.lecture.length > 0 && subject.sections.lecture[0].modules.length > 0) {
        document.getElementById('delivery-mode').textContent = subject.sections.lecture[0].modules[0].mode;
    } else {
        document.getElementById('delivery-mode').textContent = 'N/A';
    }

    const lectureTutorialLabList = document.getElementById('lecture-tutorial-list');
    lectureTutorialLabList.innerHTML = '';  // Clear existing list

    // Example for lecture times
    subject.sections.lecture.forEach(lecture => {
        lecture.modules.forEach(module => {
            const li = document.createElement('li');
            li.textContent = `Lecture - ${module.day}: ${module.from} - ${module.to} (${module.name})`;
            lectureTutorialLabList.appendChild(li);
        });
    });

    // Example for tutorial times
    subject.sections.tutorial.forEach(tutorial => {
        tutorial.modules.forEach(module => {
            const li = document.createElement('li');
            li.textContent = `Tutorial - ${module.day}: ${module.from} - ${module.to} (${module.name})`;
            lectureTutorialLabList.appendChild(li);
        });
    });

    // Example for lab times
    subject.sections.lab.forEach(lab => {
        lab.modules.forEach(module => {
            const li = document.createElement('li');
            li.textContent = `Lab - ${module.day}: ${module.from} - ${module.to} (${module.name})`;
            lectureTutorialLabList.appendChild(li);
        });
    });
}

document.getElementById('subject-dropdown').addEventListener('change', function () {
    const selectedSubjectCode = this.value;

    fetch('/getsubjects')
        .then(response => response.json())
        .then(data => {
            const selectedSubject = data.find(subject => subject.subjectCode === selectedSubjectCode);
            if (selectedSubject) {
                loadSubjectDetails(selectedSubject);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error loading subject details.');
        });
});
