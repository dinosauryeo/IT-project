function loadHomePage(){
    window.location.href = '/home';
}
function loadStudentPage(){
    alert("load student page");
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

document.addEventListener('DOMContentLoaded', function() {
    const homeLink = document.getElementById('home-link');
    if (homeLink) {
        homeLink.addEventListener('click', function() {
            showPage('home');
        });
    }
});


// Hover event for Home link
document.getElementById('home-link').addEventListener('click', function() {
    showPage('home');
});

document.getElementById('shuffle-select').addEventListener('change', function() {
    this.size = 0; // Collapse the dropdown after selection
});

document.addEventListener('click', function(event) {
    var shuffleSelect = document.getElementById('shuffle-select');
    if (!shuffleSelect.contains(event.target)) {
        shuffleSelect.size = 0; // Collapse the dropdown when clicking outside
    }
});




document.addEventListener('DOMContentLoaded', function () {
    // Initialize variables
    const yearSemesterSelect = document.getElementById('year-semester');
    const campusSelect = document.getElementById('campus-select');
    const degreeSelect = document.getElementById('degree-select');
    const studentList = document.getElementById('student-list');
    const shuffleSelect = document.getElementById('shuffle-select');
    const studentDetails = document.querySelector('.student-details');
    const searchInput = document.getElementById('search-student');
    const searchContainer = searchInput.parentNode;
    const searchButton = document.createElement('button');
    const clearButton = document.createElement('button');
    
    searchButton.textContent = 'Search';
    searchButton.id = 'search-button';
    clearButton.textContent = 'Clear';
    clearButton.id = 'clear-button';
    
    // Add both buttons to the search container
    searchContainer.appendChild(searchButton);
    searchContainer.appendChild(clearButton);

    let currentStudents = [];

    // Initialize page
    initializePage();

    function initializePage() {
        fetchYearSemester();
        fetchDegrees();
        setupEventListeners();
    }

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

    function setupEventListeners() {
        yearSemesterSelect.addEventListener('change', checkFetchStudents);
        campusSelect.addEventListener('change', checkFetchStudents);
        degreeSelect.addEventListener('change', checkFetchStudents);
        shuffleSelect.addEventListener('change', handleShuffleChange);
        searchButton.addEventListener('click', performSearch);
        clearButton.addEventListener('click', clearSearchAndReload);
    }

    function checkFetchStudents() {
        if (yearSemesterSelect.value && campusSelect.value && degreeSelect.value) {
            fetchStudents();
        } else {
            studentList.innerHTML = '';
            studentDetails.innerHTML = '';
            currentStudents = [];
        }
    }

    function fetchStudents() {
        const yearSemester = yearSemesterSelect.value;
        const year = yearSemester.substring(0, 4);
        const semester = yearSemester.substring(5);
        const campus = campusSelect.value;
        const degree = degreeSelect.value;

        const params = new URLSearchParams({
            year: year,
            semester: semester,
            campus: campus,
            folder_prefix: 'Students-Enrollment-Details',
            degree_name: degree,
            sort_method: shuffleSelect.value
        });

        fetch(`/get-enrolled-students-timetable?${params}`)
            .then(response => response.json())
            .then(data => {
                currentStudents = data.students;
                displayStudents(currentStudents);
            })
            .catch(error => console.error('Error fetching students:', error));
    }

    function displayStudents(students) {
        const studentList = document.getElementById('student-list');
        studentList.innerHTML = '';
        students.forEach(student => {
            const li = document.createElement('li');
            li.textContent = `${student.StudentID} ${student.Student_Name}`;
            li.addEventListener('click', () => {
                showStudentDetails(student);
                fetchStudentTimetable(student.StudentID, li);
            });
            studentList.appendChild(li);
        });
    }

    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase();
        const filteredStudents = currentStudents.filter(student => {
            const idMatch = String(student.StudentID || '').toLowerCase().includes(searchTerm);
            const nameMatch = String(student.Student_Name || '').toLowerCase().includes(searchTerm);
            return idMatch || nameMatch;
        });
        displayStudents(filteredStudents);
    }

    function clearSearchAndReload() {
        searchInput.value = ''; // Clear the search input
        if (currentStudents.length > 0) {
            displayStudents(currentStudents); // Reload all students
        } else {
            checkFetchStudents(); // If no students are loaded, try to fetch them
        }
    }
    
    function showStudentDetails(student) {
        studentDetails.innerHTML = `
            <h3>${student.Student_Name}</h3>
            <p>${degreeSelect.value}</p>
            <p>Course Date: ${student['Course Start Date']} - ${student['Course End Date']}</p>
            <p>Enrolled Subjects: ${student.Enrolled_Subjects.join(', ')}</p>
        `;
        fetchStudentTimetable(student.StudentID, null);
    }

    function fetchYearSemester() {
        fetch('/api/get-year-semesters')
            .then(response => response.json())
            .then(data => {
                populateDropdown(yearSemesterSelect, data);
                yearSemesterSelect.disabled = false;
            })
            .catch(error => console.error('Error fetching year and semester data:', error));
    }

    function fetchDegrees() {
        fetch('/api/get-degrees')
            .then(response => response.json())
            .then(data => {
                populateDropdown(degreeSelect, data.map(d => d.name));
            })
            .catch(error => console.error('Error fetching degrees:', error));
    }

    function populateDropdown(dropdown, options) {
        dropdown.innerHTML = '<option value="" disabled selected>Select Year Semester</option>';
        options.forEach(option => {
            const optionElement = new Option(option, option);
            dropdown.appendChild(optionElement);
        });
    }



    function handleShuffleChange() {
        if (yearSemesterSelect.value && campusSelect.value && degreeSelect.value) {
            fetchStudents();
        }
    }






    function fetchDegrees() {
        fetch('/api/get-degrees')
            .then(response => response.json())
            .then(data => {
                populateDegreeDropdowns(data);
            })
            .catch(error => console.error('Error fetching degrees:', error));
    }
    
    function populateDegreeDropdowns(degrees) {
        const degreeSelect = document.getElementById('degree-select');
        const existingDegrees = document.getElementById('existingDegrees');
        
        // Clear existing options
        degreeSelect.innerHTML = '<option value="" disabled selected>Select Degree</option>';
        existingDegrees.innerHTML = '<option value="" disabled selected>Select Degree</option>';
        
        degrees.forEach(degree => {
            const option = new Option(degree.name, degree.name);
            degreeSelect.appendChild(option.cloneNode(true));
            existingDegrees.appendChild(option);
        });
    }
    
    function addDegreeOption() {
        const newDegreeName = document.getElementById('newDegreeName').value.trim();
        if (newDegreeName) {
            fetch('/api/add-degree', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: newDegreeName }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    fetchDegrees();  // Refresh the degree lists
                    document.getElementById('newDegreeName').value = '';  // Clear the input
                    alert('Degree added successfully');
                } else {
                    alert('Failed to add degree: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while adding the degree');
            });
        } else {
            alert('Please enter a degree name');
        }
    }
    
    function removeDegreeOption() {
        const degreeSelect = document.getElementById('existingDegrees');
        const selectedDegree = degreeSelect.value;
        if (selectedDegree) {
            fetch('/api/remove-degree', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: selectedDegree }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    fetchDegrees();  // Refresh the degree lists
                    alert('Degree removed successfully');
                } else {
                    alert('Failed to remove degree: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while removing the degree');
            });
        } else {
            alert('Please select a degree to remove');
        }
    }

    const modifyDegreeBtn = document.getElementById('modify-degree-btn');
    if (modifyDegreeBtn) {
        modifyDegreeBtn.addEventListener('click', showModifyDegreeModal);
    }

    function showModifyDegreeModal() {
        const modal = document.getElementById('modifyDegreeModal');
        modal.style.display = 'block';
    }

    const addDegreeBtn = document.getElementById('add-degree-btn');
    if (addDegreeBtn) {
        addDegreeBtn.addEventListener('click', addDegreeOption);
    }

    const removeDegreeBtn = document.getElementById('remove-degree-btn');
    if (removeDegreeBtn) {
        removeDegreeBtn.addEventListener('click', removeDegreeOption);
    }

    function closeModifyDegreeModal() {
        const modal = document.getElementById('modifyDegreeModal');
        modal.style.display = 'none';
    }

    const saveDegreeChangesBtn = document.getElementById('save-degree-changes-btn');
    if (saveDegreeChangesBtn) {
        saveDegreeChangesBtn.addEventListener('click', saveDegreeChanges);
    }

    function saveDegreeChanges() {
        closeModifyDegreeModal();
        alert('Changes saved successfully!');
    }

    // Attach event handler for closing the modal
    document.querySelector('.close').addEventListener('click', closeModifyDegreeModal);



    function fetchStudentTimetable(studentID, studentElement) {
        const year = yearSemesterSelect.value.substring(0, 4);
        const semester = yearSemesterSelect.value.substring(5);
        const campus = campusSelect.value;
        const degree = degreeSelect.value;
    
        const params = new URLSearchParams({
            year: year,
            semester: semester,
            campus: campus,
            folder_prefix: 'Timetable',
            degree_name: degree,
            student_id: studentID
        });
    
        fetch(`/get-student-timetable?${params}`)
        .then(response => response.json())
        .then(data => {
            if (data.timetable) {
                displayTimetable(data.timetable);
                const hasCollision = checkTimetableCollisions(data.timetable);
                if (studentElement) {
                    if (hasCollision) {
                        studentElement.classList.add('collision');
                    } else {
                        studentElement.classList.remove('collision');
                    }
                }
            } else {
                console.error('No timetable data found for the student');
                if (studentElement) {
                    studentElement.classList.remove('collision');
                }
            }
        })
        .catch(error => {
            console.error('Error fetching student timetable:', error);
            if (studentElement) {
                studentElement.classList.remove('collision');
            }
        });
    }
    
    function displayTimetable(timetableData) {
        const timetableBody = document.getElementById('timetable-body');
        timetableBody.innerHTML = ''; // Clear existing timetable
    
        const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
        const startTime = 7 * 60; // 7:00 AM in minutes
        const endTime = 23 * 60; // 11:00 PM in minutes
    
        // Create time slots for every 15 minutes
        for (let time = startTime; time < endTime; time += 15) {
            const row = document.createElement('tr');
            const timeCell = document.createElement('td');
            
            // Only show time for o'clock slots
            if (time % 60 === 0) {
                timeCell.textContent = formatTime(time);
                timeCell.className = 'time-cell';
            } else {
                timeCell.className = 'time-cell empty';
            }
            row.appendChild(timeCell);
    
            for (let day = 0; day < 7; day++) {
                const cell = document.createElement('td');
                const classesForTimeSlot = timetableData.filter(item => 
                    item.Day.toLowerCase() === days[day].toLowerCase() &&
                    timeOverlaps(time, item.From, item.To)
                );
        
                if (classesForTimeSlot.length > 0) {
                    classesForTimeSlot.forEach(classInfo => {
                        const classStartTime = convertTimeToMinutes(classInfo.From);
                        if (time === classStartTime) {
                            const classBlock = document.createElement('div');
                            classBlock.className = 'class-block';
                            classBlock.style.backgroundColor = getColorForSectionType(classInfo.SectionType);
                            classBlock.style.height = calculateBlockHeight(classInfo.From, classInfo.To);
                            
                            // Create spans for each line of text
                            const subjectCodeSpan = document.createElement('span');
                            subjectCodeSpan.textContent = classInfo.SubjectCode;
                            const titleSpan = document.createElement('span');
                            titleSpan.textContent = classInfo.Title;
                            
                            classBlock.appendChild(subjectCodeSpan);
                            classBlock.appendChild(titleSpan);

                            // Check for collisions
                            const collisions = classesForTimeSlot.filter(otherClass => 
                                otherClass !== classInfo && 
                                timeOverlaps(classStartTime, otherClass.From, otherClass.To)
                            );
                            
                            if (collisions.length > 0) {
                                classBlock.classList.add('collision');
                                // Create collision indicator
                                const collisionIndicator = document.createElement('div');
                                collisionIndicator.className = 'collision-indicator';
                                collisionIndicator.style.height = calculateCollisionHeight(classInfo, collisions);
                                classBlock.appendChild(collisionIndicator);
                            }
                            
                            cell.appendChild(classBlock);
                        }
                    });
                }
                row.appendChild(cell);
            }
            timetableBody.appendChild(row);
        }
    
        document.getElementById('timetable-container').style.display = 'block';
    }
    
    function calculateCollisionHeight(mainClass, collisions) {
        const mainStart = convertTimeToMinutes(mainClass.From);
        const mainEnd = convertTimeToMinutes(mainClass.To);
        let maxOverlap = 0;
    
        collisions.forEach(collision => {
            const collisionStart = convertTimeToMinutes(collision.From);
            const collisionEnd = convertTimeToMinutes(collision.To);
            const overlapStart = Math.max(mainStart, collisionStart);
            const overlapEnd = Math.min(mainEnd, collisionEnd);
            const overlap = overlapEnd - overlapStart;
            maxOverlap = Math.max(maxOverlap, overlap);
        });
    
        return `${maxOverlap * 1.5}px`; // Assuming each 15-min slot is 20px high
    }
    
    function calculateBlockHeight(startTime, endTime) {
        const start = convertTimeToMinutes(startTime);
        const end = convertTimeToMinutes(endTime);
        const duration = end - start;
        return `${duration * 1.5}px`; // Assuming each 15-min slot is 20px high
    }
    
    function timeOverlaps(slotTime, classStart, classEnd) {
        const slotStart = slotTime;
        const slotEnd = slotTime + 15;
        const classStartMinutes = convertTimeToMinutes(classStart);
        const classEndMinutes = convertTimeToMinutes(classEnd);
        return (slotStart < classEndMinutes && slotEnd > classStartMinutes);
    }
    
    function convertTimeToMinutes(timeString) {
        const [hours, minutes] = timeString.split(':').map(Number);
        return hours * 60 + minutes;
    }
    
    function formatTime(minutes) {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
    }
    
    function getColorForSectionType(sectionType) {
        switch (sectionType.toLowerCase()) {
            case 'lecture': return '#7AB0B5'; // Light blue
            case 'tutorial': return '#e8e1ca'; // Light yellow
            case 'lab': return '#d698a7'; // Light red
            default: return '#ffffff'; // White for unknown types
        }
    }

    function checkTimetableCollisions(timetableData) {
        for (let i = 0; i < timetableData.length; i++) {
            for (let j = i + 1; j < timetableData.length; j++) {
                if (timetableData[i].Day.toLowerCase() === timetableData[j].Day.toLowerCase()) {
                    const startTime1 = convertTimeToMinutes(timetableData[i].From);
                    const endTime1 = convertTimeToMinutes(timetableData[i].To);
                    const startTime2 = convertTimeToMinutes(timetableData[j].From);
                    const endTime2 = convertTimeToMinutes(timetableData[j].To);
    
                    if (
                        (startTime1 < endTime2 && endTime1 > startTime2) ||
                        (startTime2 < endTime1 && endTime2 > startTime1)
                    ) {
                        return true; // Collision found on the same day
                    }
                }
            }
        }
        return false; // No collisions
    }

});

