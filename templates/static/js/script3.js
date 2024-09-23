
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
    const currentYear = new Date().getFullYear();
    for (let year = 2000; year <= currentYear + 1; year++) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        yearSelect.appendChild(option);
    }

    // Populate time dropdowns after DOM is loaded
    populateTimeDropdowns();


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
    // Function to handle form submission
    document.getElementById('create-subject').addEventListener('click', function () {
        const form = document.getElementById('createSubjectForm');
        const year = form.querySelector('#year').value;
        const semester = form.querySelector('#semester').value;
        const campus = form.querySelector('#campus').value;
        const coordinator = form.querySelector('#coordinator').value;
        const subjectName = form.querySelector('#subject-name').value;
        const subjectCode = form.querySelector('#subject-code').value;
    
        // Gather section data
        const sections = ['lecture', 'tutorial', 'lab'].reduce((acc, type) => {
            const sectionDivs = document.querySelectorAll(`#${type}-sections .section`);
            acc[type] = Array.from(sectionDivs).map(sectionDiv => {
                return {
                    title: sectionDiv.querySelector('.section-title').textContent,
                    modules: Array.from(sectionDiv.querySelectorAll('.module')).map(moduleDiv => ({
                        day: moduleDiv.querySelector(`select[name="${type}-day"]`).value,
                        from: moduleDiv.querySelector(`select[name="${type}-from"]`).value,
                        to: moduleDiv.querySelector(`select[name="${type}-to"]`).value,
                        limit: moduleDiv.querySelector(`input[name="${type}-limit"]`).value, // Get the student limit
                        name: moduleDiv.querySelector(`input[name="${type}-name"]`).value,
                        location: moduleDiv.querySelector(`input[name="${type}-location"]`).value,
                        mode: moduleDiv.querySelector(`select[name="${type}-mode"]`).value,
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

// Show the Create Subject page when "Add Subject" is clicked
document.querySelector('button[onclick="addSubject()"]').addEventListener('click', function () {
    showPage('create-subject');
});


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
            <input type="text" id="${sectionType}-location-${sectionNumber}-${moduleCount}" name="${sectionType}-location" placeholder="Location">
        </div>
    `;

    sectionDiv.appendChild(moduleDiv);
    populateTimeDropdowns(); // Populate time dropdowns after adding a new module

    // Handle delete module button
    moduleDiv.querySelector('.delete-module-btn').addEventListener('click', function() {
        const confirmDelete = confirm("Are you sure you want to delete this module?");
        if (confirmDelete) {
            sectionDiv.removeChild(moduleDiv);
            updateModuleNumbers(sectionDiv, sectionType);
        }
    });
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


