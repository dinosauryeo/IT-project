
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




// Function to handle logout
function logout() {
    window.location.href = '/logout';
}





document.addEventListener('DOMContentLoaded', function () {
    const addYearSemesterBtn = document.getElementById('add-year-semester-btn');
    const addYearSemesterContainer = document.getElementById('add-year-semester-container');
    const saveYearSemesterBtn = document.getElementById('save-year-semester-btn');
    const yearSemesterSelect = document.getElementById('year-semester');
    const addSectionBtn = document.getElementById('add-section-btn');
    const yearSemesterSections = document.getElementById('year-semester-sections');
    const campusSelect = document.getElementById('campus-select');
    const subjectInfoContainer = document.getElementById('subject-info');
    const subjectContainer = document.getElementById('subject-container'); // Container for subjects
    const sectionDropdown = document.createElement('select');

    const inheritBtn = document.getElementById('inherit-btn');
    const inheritDialog = document.getElementById('inherit-dialog');
    const confirmInheritBtn = document.getElementById('confirm-inherit-btn');
    const cancelInheritBtn = document.getElementById('cancel-inherit-btn');
    const fromYearSelect = document.getElementById('from-year');
    const fromSemesterSelect = document.getElementById('from-semester');
    const toYearSelect = document.getElementById('to-year');
    const toSemesterSelect = document.getElementById('to-semester');

    const closeInheritBtn = document.getElementById('close-inherit-btn');
    const closeYearSemesterBtn = document.getElementById('close-year-semester-btn');
    
    // Function to fetch year and semester from the database
    function fetchYearSemester() {
        fetch('/api/get-year-semesters')
            .then(response => response.json())
            .then(data => {
                populateYearSemesterDropdown(data);
            })
            .catch(error => console.error('Error fetching year and semester data:', error));
    }

    // Populate the year-semester dropdown with data from the server
    function populateYearSemesterDropdown(data) {
        // Clear existing options first
        yearSemesterSelect.innerHTML = '<option value="" disabled selected>Year Semester</option>';
        data.forEach(yearSemester => {
            const option = new Option(yearSemester, yearSemester);
            yearSemesterSelect.appendChild(option);
        });
        yearSemesterSelect.disabled = false; // Enable the dropdown
    }

    // Call fetchYearSemester on page load to populate dropdown
    fetchYearSemester();

    closeInheritBtn.addEventListener('click', hideInheritDialog);
    function hideInheritDialog() {
        inheritDialog.style.display = 'none';
    }

    closeYearSemesterBtn.addEventListener('click', hideYearSemesterSelect);
    function hideYearSemesterSelect() {
        addYearSemesterContainer.style.display = 'none';
    }

    sectionDropdown.id = 'section-dropdown';
    sectionDropdown.style.display = 'none'; // Initially hidden

    // Show the add-year-semester-container when "+" button is clicked
    addYearSemesterBtn.addEventListener('click', function () {
        addYearSemesterContainer.style.display = 'block';
        inheritDialog.style.display = 'none';
        subjectInfoContainer.style.display = 'none'; // Hide existing subject info
        //addYearSemesterSection(); // Add the first section
    });
    
    // Initially disable campus select
    campusSelect.disabled = true;

    // Enable campus select when year-semester is selected
    yearSemesterSelect.addEventListener('change', function() {
        const selectedValue = this.value;
        if (selectedValue) {
            campusSelect.disabled = false;
            campusSelect.value = ''; // Reset campus selection
            subjectContainer.innerHTML = ''; // Clear subject list
            subjectInfoContainer.style.display = 'none'; // Hide subject info
        } else {
            campusSelect.disabled = true;
        }
    });
    
    // Event listener for campus change
    campusSelect.addEventListener('change', function() {
        const selectedYearSemester = yearSemesterSelect.value;
        const selectedCampus = this.value;
        console.log('Campus changed:', selectedCampus, 'Year-semester:', selectedYearSemester);
    
        if (selectedYearSemester && selectedCampus) {
            console.log('Fetching subjects for', selectedYearSemester, selectedCampus);
            fetchSubjects(selectedYearSemester, selectedCampus);
        } else {
            console.log('Clearing subjects, not all parameters selected');
            subjectContainer.innerHTML = '';
        }
    });

    // Function to create and add a year-semester section
    function addYearSemesterSection() {
        const section = document.createElement('div');
        section.classList.add('year-semester-section');
        
        const yearSelect = document.createElement('select');
        yearSelect.classList.add('year-select');
        const currentYear = new Date().getFullYear();
        for (let i = currentYear - 5; i <= currentYear + 1; i++) {
            const option = document.createElement('option');
            option.value = i;
            option.textContent = i;
            yearSelect.appendChild(option);
        }
        section.appendChild(yearSelect);

        const semesterSelect = document.createElement('select');
        semesterSelect.classList.add('semester-select');
        semesterSelect.innerHTML = `
            <option value="" disabled selected>Semester</option>
            <option value="Semester1">Semester 1</option>
            <option value="Winter">Winter</option>
            <option value="Semester2">Semester 2</option>
            <option value="Summer">Summer</option>
        `;
        section.appendChild(semesterSelect);

        const removeBtn = document.createElement('button');
        removeBtn.textContent = '-';
        removeBtn.addEventListener('click', function () {
            section.remove();
        });
        section.appendChild(removeBtn);

        yearSemesterSections.appendChild(section);
    }

    // Add a new year-semester section when "+" button is clicked
    addSectionBtn.addEventListener('click', function () {
        addYearSemesterSection();
    });

    // Handle Save All Button Click
    saveYearSemesterBtn.addEventListener('click', function () {
        const sections = yearSemesterSections.querySelectorAll('.year-semester-section');

        sections.forEach(section => {
            const yearSelect = section.querySelector('.year-select');
            const semesterSelect = section.querySelector('.semester-select');
            const selectedYear = yearSelect.value;
            const selectedSemester = semesterSelect.value;
            const yearSemesterValue = `${selectedYear}_${selectedSemester}`;

            if (selectedYear && selectedSemester) {
                // Check if this combination already exists in the main dropdown
                const exists = Array.from(yearSemesterSelect.options).some(option => option.value === yearSemesterValue);
                
                if (!exists) {
                    // Create and add the new option to the main dropdown
                    const option = document.createElement('option');
                    option.value = yearSemesterValue;
                    option.textContent = yearSemesterValue;
                    yearSemesterSelect.appendChild(option);
                    yearSemesterSelect.disabled = false; // Enable the dropdown
                }
            }
        });

        // Hide the add-year-semester-container after saving and show subject info again
        addYearSemesterContainer.style.display = 'none';
        subjectInfoContainer.style.display = 'block';
        // Clear all sections after saving
        yearSemesterSections.innerHTML = '';
        document.getElementById('subject-info').style.display = 'none';
    });


    // Add event listener to the year-semester dropdown to fetch subjects
    document.getElementById('year-semester').addEventListener('change', function() {
        const selectedValue = this.value;
        const selectedCampus = campusSelect.value;
        console.log('Year-semester changed:', selectedValue, 'Campus:', selectedCampus);
    
        if (selectedValue && selectedCampus) {
            console.log('Fetching subjects for', selectedValue, selectedCampus);
            fetchSubjects(selectedValue, selectedCampus);
        } else {
            console.log('Clearing subjects, not all parameters selected');
            subjectContainer.innerHTML = '';
            if (!selectedCampus) {
                campusSelect.disabled = false;
            }
        }
    });

    function fetchSubjects(yearSemester, campus) {
        console.log('fetchSubjects called with:', yearSemester, campus);
        const url = `/getsubjects?year_semester=${yearSemester}&campus=${campus}`;
        console.log('Fetching from URL:', url);
    
        fetch(url)
            .then(response => {
                console.log('Response status:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('Received data:', data);
                if (Array.isArray(data)) {
                    console.log('Data is an array, populating subject list');
                    populateSubjectList(data);
                } else {
                    console.error('Error fetching subjects:', data.message);
                    alert('Error fetching subjects: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                alert('Error fetching subjects: ' + error.message);
            });
    }
    
    function populateSubjectList(subjects) {
        console.log('Populating subject list with', subjects.length, 'subjects');
        subjectContainer.innerHTML = '';
    
        subjects.forEach(subject => {
            console.log('Adding subject:', subject.subjectString);
            const subjectItem = document.createElement('div');
            subjectItem.classList.add('subject-item');
            subjectItem.textContent = subject.subjectString;
            subjectItem.dataset.subjectCode = subject.subjectCode;
            subjectItem.dataset.coordinator = subject.coordinator;
            subjectItem.dataset.campus = subject.campus;
    
            subjectContainer.appendChild(subjectItem);
        });
    }

    function loadSubjectDetails(subjectCode, yearSemester, campus) {
        // Split year and semester
        const year = yearSemester.substring(0, 4);
        const semester = yearSemester.substring(5);
    
        fetch(`/getsubjectdetails?subject_code=${subjectCode}&year=${year}&semester=${semester}&campus=${campus}`)
            .then(response => response.json())
            .then(data => {
                if (data) {
                    console.log('Received subject details:', data);
    
                    // Update currentSubjectInfo
                    currentSubjectInfo = {
                        subjectCode: data.subjectCode,
                        subjectName: data.subjectName,
                        coordinator: data.coordinator,
                        campus: data.campus,
                        year: year,
                        semester: semester
                    };
                    
                    // Update the subject information in the right bar
                    document.getElementById('subject-code').textContent = data.subjectCode || 'N/A';
                    document.getElementById('subject-title').textContent = data.subjectName || 'N/A';
                    document.getElementById('subject-coordinator').textContent = data.coordinator || 'N/A';
                    document.getElementById('campus').textContent = data.campus || 'N/A';
    
                    // Clear and populate lecture/tutorial/lab list
                    const sectionsList = document.getElementById('lecture-tutorial-list');
                    sectionsList.innerHTML = '';
    
                    ['lecture', 'tutorial', 'lab'].forEach(type => {
                        if (data.sections && data.sections[type] && data.sections[type].length > 0) {
                            const typeHeader = document.createElement('h3');
                            typeHeader.textContent = type.charAt(0).toUpperCase() + type.slice(1) + 's';
                            sectionsList.appendChild(typeHeader);
    
                            data.sections[type].forEach(section => {
                                const sectionItem = document.createElement('li');
                                sectionItem.innerHTML = `<strong>${section.title}</strong>`;
                                
                                // Create a nested list for modules
                                const modulesList = document.createElement('ul');
                                renderModules(section.modules, modulesList);
                                sectionItem.appendChild(modulesList);
    
                                sectionsList.appendChild(sectionItem);
                            });
                        }
                    });
    
                    subjectInfoContainer.style.display = 'block';
                    fetchEnrolledStudents(subjectCode, yearSemester, campus);

                } else {
                    console.error('No data received for subject details');
                    alert('Error fetching subject details.');
                }
            })
            .catch(error => {
                console.error('Error fetching subject details:', error);
                alert('Error fetching subject details.');
            });
    }

    function fetchEnrolledStudents(subjectCode, yearSemester, campus) {
        const year = yearSemester.substring(0, 4);
        const semester = yearSemester.substring(5);
        const folderPrefix = `Students-Enrollment-Details`;
        const url = `/get-enrolled-students?subject_code=${subjectCode}&year=${year}&semester=${semester}&campus=${campus}&folder_prefix=${folderPrefix}`;
    
        console.log(`Fetching enrolled students with URL: ${url}`);
    
        fetch(url)
            .then(response => {
                console.log(`Response status: ${response.status}`);
                if (!response.ok) {
                    return response.text().then(text => {
                        throw new Error(`HTTP error! status: ${response.status}, body: ${text}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log(`Received data:`, data);
                const enrolledStudentsList = document.getElementById('enrolled-students');
                enrolledStudentsList.innerHTML = ''; // Clear existing list
    
                // Display the count
                const countElement = document.createElement('p');
                countElement.textContent = `Total enrolled students: ${data.count}`;
                enrolledStudentsList.appendChild(countElement);
    
                if (data.students && data.students.length > 0) {
                    data.students.forEach(student => {
                        const listItem = document.createElement('li');
                        listItem.textContent = `${student.StudentID} - ${student.Student_Name}`;
                        enrolledStudentsList.appendChild(listItem);
                    });
    
                    document.getElementById('subject-info').style.display = 'block';
                    console.log(`Displayed ${data.count} enrolled students`);
                } else {
                    console.log('No enrolled students found');
                    enrolledStudentsList.innerHTML += '<li>No enrolled students found</li>';
                }
            })
            .catch(error => {
                console.error('Error fetching enrolled students:', error);
                document.getElementById('enrolled-students').innerHTML = `<li>Error fetching enrolled students: ${error.message}</li>`;
            });
    }

    function renderModules(modules, parentElement) {
        modules.forEach(module => {
            const moduleItem = document.createElement('li');
            moduleItem.innerHTML = `
                Day: ${module.day}<br>
                From: ${module.from}<br>
                To: ${module.to}<br>
                Lecturer/Tutor name: ${module.name}<br>
                Student limit: ${module.limit}<br>
                Delivery mode: ${module.mode}<br>
                Location: ${module.location.building}, ${module.location.level}, ${module.location.classroom}
            `;
    
            // If this module has sub-modules, render them recursively
            if (module.modules && module.modules.length > 0) {
                const subModulesList = document.createElement('ul');
                renderModules(module.modules, subModulesList);
                moduleItem.appendChild(subModulesList);
            }
    
            parentElement.appendChild(moduleItem);
        });
    }

    let currentSubjectInfo = {}; // This will store the current subject info

    // Add click event to load subject details
    subjectContainer.addEventListener('click', function (event) {
        if (event.target && event.target.classList.contains('subject-item')) {
            // Remove active class from all other subject items
            document.querySelectorAll('.subject-item').forEach(item => item.classList.remove('active'));
            event.target.classList.add('active');
    
            const subjectCode = event.target.dataset.subjectCode;
            const yearSemester = yearSemesterSelect.value;
            const campus = campusSelect.value;
    
            if (subjectCode && yearSemester && campus) {
                loadSubjectDetails(subjectCode, yearSemester, campus);
            } else {
                alert('Subject code, year/semester, or campus is missing.');
            }
        }
    });

    document.querySelector('#edit-subject-btn').addEventListener('click', function() {
        if (currentSubjectInfo.subjectCode && currentSubjectInfo.subjectName) {
            // Store the subject data in sessionStorage
            sessionStorage.setItem('subjectData', JSON.stringify(currentSubjectInfo));
            // Redirect with the subject code and name
            window.location.href = `/editsubject?code=${encodeURIComponent(currentSubjectInfo.subjectCode)}&name=${encodeURIComponent(currentSubjectInfo.subjectName)}`;
        } else {
            alert('No subject selected. Please select a subject to edit.');
        }
    });

    // Function to populate year and semester dropdowns
    function populateYearSemesterDropdowns() {
        const currentYear = new Date().getFullYear();
        const semesters = ['Semester1', 'Winter', 'Semester2', 'Summer'];

        for (let i = currentYear - 5; i <= currentYear + 1; i++) {
            fromYearSelect.add(new Option(i, i));
            toYearSelect.add(new Option(i, i));
        }

        semesters.forEach(semester => {
            fromSemesterSelect.add(new Option(semester, semester));
            toSemesterSelect.add(new Option(semester, semester));
        });
    }
    
    populateYearSemesterDropdowns();

    // Show inherit dialog and clear subject selections
    inheritBtn.addEventListener('click', function() {
    // Show the inherit dialog
    inheritDialog.style.display = 'block';  
    
    // Hide the add-year-semester container if it's visible
    addYearSemesterContainer.style.display = 'none';
    
    // Clear the selected year-semester and campus
    yearSemesterSelect.value = ''; // Clear year-semester selection
    campusSelect.value = ''; // Clear campus selection
    campusSelect.disabled = true; // Disable campus select again
    
    // Clear the subject list and hide the subject info container
    subjectContainer.innerHTML = ''; // Clear the subjects
    subjectInfoContainer.style.display = 'none'; // Hide subject info container
});


    // Handle inherit confirmation
    confirmInheritBtn.addEventListener('click', function() {
        const fromYear = fromYearSelect.value;
        const fromSemester = fromSemesterSelect.value;
        const toYear = toYearSelect.value;
        const toSemester = toSemesterSelect.value;

        // Send request to server to perform the inheritance
        fetch('/inherit_subjects', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                fromYear: fromYear,
                fromSemester: fromSemester,
                toYear: toYear,
                toSemester: toSemester
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Subjects inherited successfully!');
                // Refresh the subject list or update the UI as needed
            } else {
                alert('Failed to inherit subjects: ' + data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An error occurred while inheriting subjects.');
        });

        inheritDialog.style.display = 'none';
    });



});


