function loadHomePage() {
    window.location.href = '/home';
}

function loadStudentPage() {
    window.location.href = '/student';
}

function loadUploadPage() {
    window.location.href = '/upload';
}

function loadGeneratePage() {
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

// Hover event for Home link
document.getElementById('home-link').addEventListener('click', function() {
    showPage('home');
});

// Function to handle logout
function logout() {
    window.location.href = '/logout';
}

// Initialize counters for each section type
const sectionCounters = {
    lecture: 0,
    tutorial: 0,
    lab: 0
};

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

document.addEventListener('DOMContentLoaded', function () {
    // Navbar active state handling
    const navbarItems = document.querySelectorAll('.navbar li');
    navbarItems.forEach(function (item) {
        item.addEventListener('click', function () {
            navbarItems.forEach(function (el) {
                el.classList.remove('active');
            });
            this.classList.add('active');
        });
    });

    // Populate the year dropdown with years from 2000 to current year + 1
    const yearSelect = document.getElementById('edit-year');
    const currentYear = new Date().getFullYear();
    for (let year = 2000; year <= currentYear + 1; year++) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        yearSelect.appendChild(option);
    }

    // Add event listeners for each section type
    document.getElementById('add-Lecture').addEventListener('click', function () {
        addSectionToCategory('lecture');
    });

    document.getElementById('add-Tutorial').addEventListener('click', function () {
        addSectionToCategory('tutorial');
    });

    document.getElementById('add-Lab').addEventListener('click', function () {
        addSectionToCategory('lab');
    });


    // Fetch existing subject data
    const urlParams = new URLSearchParams(window.location.search);
    let year = urlParams.get('year');
    let semester = urlParams.get('semester');
    let subjectCode = urlParams.get('code');
    let campus = urlParams.get('campus');

    const subjectData = JSON.parse(sessionStorage.getItem('subjectData'));
    if (subjectData) {
        year = year || subjectData.year;
        semester = semester || subjectData.semester;
        subjectCode = subjectCode || subjectData.subjectCode;
        campus = campus || subjectData.campus;
    }

    console.log('Parameters:', { year, semester, subjectCode, campus });
    if (year && semester && subjectCode && campus) {
        fetch(`/get_subject_data?year=${year}&semester=${semester}&code=${subjectCode}&campus=${campus}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Fetched subject data:', data);
                populateForm(data);
            })
            .catch(error => {
                console.error('Error fetching subject data:', error);
                alert('Failed to load subject data. Please try again.');
            });
    } else {
        const missingParams = [];
        if (!year) missingParams.push('year');
        if (!semester) missingParams.push('semester');
        if (!subjectCode) missingParams.push('subject code');
        if (!campus) missingParams.push('campus');
        
        console.error('Missing required parameters:', missingParams.join(', '));
        alert(`Missing required information to load subject data: ${missingParams.join(', ')}`);
    }

function populateForm(data) {
    // Populate basic subject info
    document.getElementById('edit-year').value = data.year;
    document.getElementById('edit-semester').value = data.semester;
    document.getElementById('edit-campus').value = data.campus;
    document.getElementById('edit-coordinator').value = data.coordinator;
    document.getElementById('edit-subject-name').value = data.subjectName;
    document.getElementById('edit-subject-code').value = data.subjectCode;

    // Fetch locations for the campus
    fetchLocationsForCampus(data.campus).then(locations => {
        // Populate sections
        if (data.sections) {
            ['lecture', 'tutorial', 'lab'].forEach(sectionType => {
                const sectionContainer = document.getElementById(`edit-${sectionType}-sections`);
                sectionContainer.innerHTML = ''; // Clear existing sections
                sectionCounters[sectionType] = 0; // Reset counter

                if (data.sections[sectionType] && data.sections[sectionType].length > 0) {
                    data.sections[sectionType].forEach((section, sectionIndex) => {
                        const sectionDiv = addSectionToCategory(sectionType);
                        if (section.modules && section.modules.length > 0) {
                            section.modules.forEach((module, moduleIndex) => {
                                const moduleDiv = addModule(sectionDiv, sectionType);
                                populateModule(moduleDiv, module, sectionType, sectionIndex + 1, moduleIndex + 1, locations);
                            });
                        }
                    });
                } else {
                    // If no sections of this type, add an empty one
                    addSectionToCategory(sectionType);
                }
            });
        }
    }).catch(error => {
        console.error('Error fetching locations:', error);
        alert('Failed to load location data. Please try again.');
    });
}

function populateModule(moduleDiv, moduleData, sectionType, sectionNumber, moduleNumber, locations) {
    moduleDiv.querySelector('.module-title').textContent = `${sectionType.charAt(0).toUpperCase() + sectionType.slice(1)} ${sectionNumber}.${moduleNumber}`;
    moduleDiv.querySelector(`select[name="${sectionType}-day"]`).value = moduleData.day;
    moduleDiv.querySelector(`select[name="${sectionType}-from"]`).value = moduleData.from;
    moduleDiv.querySelector(`select[name="${sectionType}-to"]`).value = moduleData.to;
    moduleDiv.querySelector(`input[name="${sectionType}-limit"]`).value = moduleData.limit;
    moduleDiv.querySelector(`input[name="${sectionType}-name"]`).value = moduleData.name;
    moduleDiv.querySelector(`select[name="${sectionType}-mode"]`).value = moduleData.mode;

    // Populate location data
    populateLocationDropdowns(moduleDiv, moduleData.location, locations);
}

    



});

// Function to add sections to the respective bar
function addSectionToCategory(sectionType) {
    const categoryDiv = document.getElementById(`edit-${sectionType}-sections`);

    // Increment section count and create a unique section ID
    sectionCounters[sectionType]++;
    const sectionNumber = sectionCounters[sectionType];

    const sectionDiv = document.createElement('div');
    sectionDiv.className = 'section';
    sectionDiv.id = `${sectionType}-${sectionNumber}`;
    sectionDiv.innerHTML = `
        <div class="section-title">${sectionType.charAt(0).toUpperCase() + sectionType.slice(1)} ${sectionNumber}</div>
        <div class="section-actions">
            <button class="add-module-btn">+ Add Detail</button>
            <button class="delete-section-btn">Delete</button>
        </div>
    `;

    categoryDiv.appendChild(sectionDiv);

    // Handle delete section button
    sectionDiv.querySelector('.delete-section-btn').addEventListener('click', function() {
        const confirmDelete = confirm("Are you sure you want to delete this section?");
        if (confirmDelete) {
            categoryDiv.removeChild(sectionDiv);
            sectionCounters[sectionType]--;
            // Update section numbering
            updateSectionNumbers(sectionType);
        }
    });

    // Handle add module button
    sectionDiv.querySelector('.add-module-btn').addEventListener('click', function() {
        addModule(sectionDiv, sectionType);
    });

    return sectionDiv;
}

// Function to add a module within a section
function addModule(sectionDiv, sectionType) {
    // Get the current count of modules for this section
    const moduleCount = sectionDiv.querySelectorAll('.module').length + 1;
    const sectionNumber = sectionDiv.querySelector('.section-title').textContent.split(' ')[1]; // Extract section number

    const moduleDiv = document.createElement('div');
    moduleDiv.className = 'module';
    moduleDiv.innerHTML = `
        <div class="module-title">${sectionType.charAt(0).toUpperCase() + sectionType.slice(1)} ${sectionNumber}.${moduleCount}</div>
        <button class="delete-module-btn">Delete</button>
        <div class="select-row">
            <select id="${sectionType}-day-${sectionNumber}-${moduleCount}" name="${sectionType}-day">
                <option value="" disabled selected>Day</option>
                <option value="Monday">Monday</option>
                <option value="Tuesday">Tuesday</option>
                <option value="Wednesday">Wednesday</option>
                <option value="Thursday">Thursday</option>
                <option value="Friday">Friday</option>
                <option value="Saturday">Saturday</option>
                <option value="Sunday">Sunday</option>
            </select>
            <select id="${sectionType}-from-${sectionNumber}-${moduleCount}" name="${sectionType}-from" class="time-dropdown">
                <option value="" disabled selected>From</option>
            </select>
            <select id="${sectionType}-to-${sectionNumber}-${moduleCount}" name="${sectionType}-to" class="time-dropdown">
                <option value="" disabled selected>To</option>
            </select>
            <input type="number" id="${sectionType}-limit-${sectionNumber}-${moduleCount}" name="${sectionType}-limit" placeholder="Student Limit" min="1">
            <select id="${sectionType}-mode-${sectionNumber}-${moduleCount}" name="${sectionType}-mode">
                <option value="" disabled selected>Delivery Modes</option>
                <option value="online">Online</option>
                <option value="oncampus">On Campus</option>
            </select>
        </div>
        <div class="select-row">
            <input type="text" id="${sectionType}-name-${sectionNumber}-${moduleCount}" name="${sectionType}-name" placeholder="${sectionType === 'lecture' ? 'Lecturer' : 'Tutor'}">
            <select id="${sectionType}-building-${sectionNumber}-${moduleCount}" name="${sectionType}-building" class="location-dropdown">
                <option value="" disabled selected>Select Building</option>
            </select>
            <select id="${sectionType}-level-${sectionNumber}-${moduleCount}" name="${sectionType}-level" class="location-dropdown">
                <option value="" disabled selected>Select Level</option>
            </select>
            <select id="${sectionType}-classroom-${sectionNumber}-${moduleCount}" name="${sectionType}-classroom" class="location-dropdown">
                <option value="" disabled selected>Select Classroom</option>
            </select>
        </div>
    `;

    sectionDiv.appendChild(moduleDiv);
    populateTimeDropdowns(); // Populate time dropdowns after adding a new module
    
    // Populate location dropdowns for the new module
    const campus = document.getElementById('edit-campus').value || document.getElementById('campus').value;
    if (campus) {
        fetchLocationsForCampus(campus).then(locations => {
            populateLocationDropdowns(moduleDiv, null, locations);
        }).catch(error => {
            console.error('Error fetching locations:', error);
        });
    }

    // Handle delete module button
    moduleDiv.querySelector('.delete-module-btn').addEventListener('click', function() {
        const confirmDelete = confirm("Are you sure you want to delete this module?");
        if (confirmDelete) {
            sectionDiv.removeChild(moduleDiv);
            updateModuleNumbers(sectionDiv, sectionType);
        }
    });

    return moduleDiv;    
}

async function populateLocationDropdowns(moduleDiv, existingData = null, locations = null) {
    const campus = document.getElementById('edit-campus').value || document.getElementById('campus').value;
    if (!campus) {
        alert('Please select a campus first');
        return;
    }

    const buildingSelect = moduleDiv.querySelector('select[name$="-building"]');
    const levelSelect = moduleDiv.querySelector('select[name$="-level"]');
    const classroomSelect = moduleDiv.querySelector('select[name$="-classroom"]');

    try {
        if (!locations) {
            const response = await fetch(`/get_locations?campus=${campus}`);
            locations = await response.json();
        }

        // Function to populate a select element while preserving existing selection
        const populateSelect = (select, options, existingValue) => {
            const currentValue = select.value;
            select.innerHTML = '<option value="" disabled selected>Select</option>';
            options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option;
                optionElement.textContent = option;
                select.appendChild(optionElement);
            });
            select.value = existingValue || currentValue || '';
        };

        // Populate buildings
        const buildings = [...new Set(locations.map(loc => loc.building))];
        populateSelect(buildingSelect, buildings, existingData?.building);

        // Function to update levels
        const updateLevels = () => {
            const selectedBuilding = buildingSelect.value;
            const levels = [...new Set(locations
                .filter(loc => loc.building === selectedBuilding)
                .map(loc => loc.level))];
            populateSelect(levelSelect, levels, existingData?.level);
        };

        // Function to update classrooms
        const updateClassrooms = () => {
            const selectedBuilding = buildingSelect.value;
            const selectedLevel = levelSelect.value;
            const classrooms = locations
                .filter(loc => loc.building === selectedBuilding && loc.level === selectedLevel)
                .map(loc => loc.classroom);
            populateSelect(classroomSelect, classrooms, existingData?.classroom);
        };

        // Event listener for building selection
        buildingSelect.addEventListener('change', () => {
            updateLevels();
            updateClassrooms();
        });

        // Event listener for level selection
        levelSelect.addEventListener('change', updateClassrooms);

        // Initial population of levels and classrooms
        updateLevels();
        updateClassrooms();

    } catch (error) {
        console.error('Error populating location dropdowns:', error);
    }
}

// Function to update the numbering of sections
function updateSectionNumbers(sectionType) {
    const sections = document.querySelectorAll(`#edit-${sectionType}-sections .section`);
    sectionCounters[sectionType] = sections.length; // Update the counter based on the actual number of sections
    sections.forEach((sectionDiv, index) => {
        const sectionTitle = sectionDiv.querySelector('.section-title');
        sectionTitle.textContent = `${sectionType.charAt(0).toUpperCase() + sectionType.slice(1)} ${index + 1}`;
    });
}

// Function to update the numbering of modules in a section
function updateModuleNumbers(sectionDiv, sectionType) {
    const modules = sectionDiv.querySelectorAll('.module');
    modules.forEach((moduleDiv, index) => {
        const moduleCount = index + 1;
        const moduleTitle = moduleDiv.querySelector('.module-title');
        const sectionNumber = sectionDiv.querySelector('.section-title').textContent.split(' ')[1]; // Extract section number
        moduleTitle.textContent = `${sectionType.charAt(0).toUpperCase() + sectionType.slice(1)} ${sectionNumber}.${moduleCount}`;
    });
}

function fetchLocationsForCampus(campus) {
    return fetch(`/get_locations?campus=${campus}`)
        .then(response => response.json())
        .then(data => {
            console.log('Fetched locations:', data);
            return data;
        })
        .catch(error => {
            console.error('Error fetching locations:', error);
            return [];
        });
}

document.getElementById('edit-subject').addEventListener('click', function () {
    const form = document.getElementById('editSubjectForm');
    const year = form.querySelector('#edit-year').value;
    const semester = form.querySelector('#edit-semester').value;
    const campus = form.querySelector('#edit-campus').value;
    const coordinator = form.querySelector('#edit-coordinator').value;
    const subjectName = form.querySelector('#edit-subject-name').value;
    const subjectCode = form.querySelector('#edit-subject-code').value;

        // Gather section data
        const sections = ['lecture', 'tutorial', 'lab'].reduce((acc, type) => {
            const sectionDivs = document.querySelectorAll(`#edit-${type}-sections .section`);
            acc[type] = Array.from(sectionDivs).map(sectionDiv => {
                return {
                    title: sectionDiv.querySelector('.section-title').textContent,
                    modules: Array.from(sectionDiv.querySelectorAll('.module')).map(moduleDiv => ({
                        day: moduleDiv.querySelector(`select[name="${type}-day"]`).value,
                        from: moduleDiv.querySelector(`select[name="${type}-from"]`).value,
                        to: moduleDiv.querySelector(`select[name="${type}-to"]`).value,
                        limit: moduleDiv.querySelector(`input[name="${type}-limit"]`).value,
                        name: moduleDiv.querySelector(`input[name="${type}-name"]`).value,
                        mode: moduleDiv.querySelector(`select[name="${type}-mode"]`).value,
                        location: {
                            building: moduleDiv.querySelector(`select[name="${type}-building"]`).value,
                            level: moduleDiv.querySelector(`select[name="${type}-level"]`).value,
                            classroom: moduleDiv.querySelector(`select[name="${type}-classroom"]`).value
                        }
                    }))
                };
            });
            return acc;
        }, {});

        const subjectData = {
            year,
            semester,
            campus,
            coordinator,
            subjectName,
            subjectCode,
            sections
        };

        fetch('/editsubject', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(subjectData)
        }).then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Subject updated successfully!');
                // Optionally redirect or clear form
            } else {
                alert('Error updating subject: ' + data.message);
            }
        }).catch(error => {
            console.error('Error:', error);
            alert('Error updating subject.');
        });
});

