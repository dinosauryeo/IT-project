
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
    const yearSelect = document.getElementById('year');
    if (yearSelect) {
        const currentYear = new Date().getFullYear();
        for (let year = 2000; year <= currentYear + 1; year++) {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            yearSelect.appendChild(option);
        }
    } else {
        console.error('Year select element not found');
    }

    // Populate time dropdowns after DOM is loaded
    populateTimeDropdowns();

    // Add event listeners for each section type
    const addLectureBtn = document.getElementById('add-Lecture');
    const addTutorialBtn = document.getElementById('add-Tutorial');
    const addLabBtn = document.getElementById('add-Lab');

    if (addLectureBtn) {
        addLectureBtn.addEventListener('click', function () {
            addSectionToCategory('lecture');
        });
    }

    if (addTutorialBtn) {
        addTutorialBtn.addEventListener('click', function () {
            addSectionToCategory('tutorial');
        });
    }

    if (addLabBtn) {
        addLabBtn.addEventListener('click', function () {
            addSectionToCategory('lab');
        });
    }

    // Function to handle form submission
    const createSubjectBtn = document.getElementById('create-subject');
    if (createSubjectBtn) {
        createSubjectBtn.addEventListener('click', function () {
            const form = document.getElementById('createSubjectForm');
            if (!form) {
                console.error('Create subject form not found');
                return;
            }

            const year = form.querySelector('#year')?.value;
            const semester = form.querySelector('#semester')?.value;
            const campus = form.querySelector('#campus')?.value;
            const coordinator = form.querySelector('#coordinator')?.value;
            const subjectName = form.querySelector('#subject-name')?.value;
            const subjectCode = form.querySelector('#subject-code')?.value;

            // Gather section data
            const sections = ['lecture', 'tutorial', 'lab'].reduce((acc, type) => {
                const sectionDivs = document.querySelectorAll(`#${type}-sections .section`);
                acc[type] = Array.from(sectionDivs).map(sectionDiv => {
                    return {
                        title: sectionDiv.querySelector('.section-title')?.textContent,
                        modules: Array.from(sectionDiv.querySelectorAll('.module')).map(moduleDiv => ({
                            day: moduleDiv.querySelector(`select[name="${type}-day"]`)?.value,
                            from: moduleDiv.querySelector(`select[name="${type}-from"]`)?.value,
                            to: moduleDiv.querySelector(`select[name="${type}-to"]`)?.value,
                            limit: moduleDiv.querySelector(`input[name="${type}-limit"]`)?.value,
                            name: moduleDiv.querySelector(`input[name="${type}-name"]`)?.value,
                            mode: moduleDiv.querySelector(`select[name="${type}-mode"]`)?.value,
                            location: {
                                building: moduleDiv.querySelector(`select[name="${type}-building"]`)?.value,
                                level: moduleDiv.querySelector(`select[name="${type}-level"]`)?.value,
                                classroom: moduleDiv.querySelector(`select[name="${type}-classroom"]`)?.value
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

            fetch('/createsubject', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(subjectData)
            }).then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Subject created successfully!');
                    // Optionally redirect or clear form
                } else {
                    alert('Error creating subject: ' + data.message);
                }
            }).catch(error => {
                console.error('Error:', error);
                alert('Error creating subject.');
            });
        });
    } else {
        console.error('Create subject button not found');
    }


});
// Function to add sections to the respective bar
function addSectionToCategory(sectionType) {
    const categoryDiv = document.getElementById(`${sectionType}-sections`);

    sectionCounters[sectionType]++;
    const sectionDiv = document.createElement('div');
    sectionDiv.className = 'section';
    sectionDiv.innerHTML = `
        <div class="section-title">${sectionType.charAt(0).toUpperCase() + sectionType.slice(1)} ${sectionCounters[sectionType]}</div>
        <div class="section-actions">
            <button class="add-module-btn">+ Add Detail</button>
            <button class="delete-section-btn">Delete</button>
        </div>
    `;

    categoryDiv.appendChild(sectionDiv);
    populateTimeDropdowns(); // Populate time dropdowns after adding a new section

    // Handle delete section button
    sectionDiv.querySelector('.delete-section-btn').addEventListener('click', function() {
        const confirmDelete = confirm("Are you sure you want to delete this section?");
        if (confirmDelete) {
            categoryDiv.removeChild(sectionDiv);
            sectionCounters[sectionType]--;
        }
    });

    // Handle add module button
    sectionDiv.querySelector('.add-module-btn').addEventListener('click', function() {
        addModule(sectionDiv, sectionType);
    });
}



// Function to add sections to the respective bar
function addSectionToCategory(sectionType) {
    const categoryDiv = document.getElementById(`${sectionType}-sections`);

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
    populateTimeDropdowns(); // Populate time dropdowns after adding a new section

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
}

function addModule(sectionDiv, sectionType) {
    const moduleCount = sectionDiv.querySelectorAll('.module').length + 1;
    const sectionNumber = sectionDiv.querySelector('.section-title').textContent.split(' ')[1];

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
    populateTimeDropdowns();
    populateLocationDropdowns(moduleDiv);

    moduleDiv.querySelector('.delete-module-btn').addEventListener('click', function() {
        if (confirm("Are you sure you want to delete this module?")) {
            sectionDiv.removeChild(moduleDiv);
            updateModuleNumbers(sectionDiv, sectionType);
        }
    });
}

async function populateLocationDropdowns(moduleDiv) {
    const campus = document.getElementById('campus').value;
    if (!campus) {
        alert('Please select a campus first');
        return;
    }

    try {
        const response = await fetch(`/get_campus_locations/${campus}`);
        const locations = await response.json();

        const buildingSelect = moduleDiv.querySelector('select[name$="-building"]');
        const levelSelect = moduleDiv.querySelector('select[name$="-level"]');
        const classroomSelect = moduleDiv.querySelector('select[name$="-classroom"]');

        // Populate buildings
        const buildings = [...new Set(locations.map(loc => loc.building))];
        buildings.forEach(building => {
            const option = document.createElement('option');
            option.value = building;
            option.textContent = building;
            buildingSelect.appendChild(option);
        });

        // Event listener for building selection
        buildingSelect.addEventListener('change', () => {
            const selectedBuilding = buildingSelect.value;
            
            // Filter levels for the selected building
            const levels = [...new Set(locations
                .filter(loc => loc.building === selectedBuilding)
                .map(loc => loc.level))];
            
            // Populate levels
            levelSelect.innerHTML = '<option value="" disabled selected>Select Level</option>';
            levels.forEach(level => {
                const option = document.createElement('option');
                option.value = level;
                option.textContent = level;
                levelSelect.appendChild(option);
            });
        });

        // Event listener for level selection
        levelSelect.addEventListener('change', () => {
            const selectedBuilding = buildingSelect.value;
            const selectedLevel = levelSelect.value;
            
            // Filter classrooms for the selected building and level
            const classrooms = locations
                .filter(loc => loc.building === selectedBuilding && loc.level === selectedLevel)
                .map(loc => loc.classroom);
            
            // Populate classrooms
            classroomSelect.innerHTML = '<option value="" disabled selected>Select Classroom</option>';
            classrooms.forEach(classroom => {
                const option = document.createElement('option');
                option.value = classroom;
                option.textContent = classroom;
                classroomSelect.appendChild(option);
            });
        });

    } catch (error) {
        console.error('Error fetching locations:', error);
    }
}

// Function to update the numbering of sections
function updateSectionNumbers(sectionType) {
    const sections = document.querySelectorAll(`#${sectionType}-sections .section`);
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

