document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('campusSelect').addEventListener('change', onCampusSelect);
    loadLocations();
});

async function onCampusSelect() {
    const campusValue = document.getElementById('campusSelect').value;
    if (campusValue) {
        document.getElementById('buildingSection').style.display = 'block';
        document.getElementById('classroomSection').style.display = 'none';
        await loadBuildings(campusValue);
    } else {
        document.getElementById('buildingSection').style.display = 'none';
        document.getElementById('classroomSection').style.display = 'none';
    }
}

async function loadBuildings(campus) {
    try {
        const response = await fetch(`/get_buildings/${campus}`);
        const buildings = await response.json();
        const buildingSelect = document.getElementById('buildingSelect');
        buildingSelect.innerHTML = '<option value="" disabled selected>Select Building</option>';
        buildings.forEach(building => {
            const option = document.createElement('option');
            option.value = building;
            option.textContent = building;
            buildingSelect.appendChild(option);
        });
        buildingSelect.addEventListener('change', onBuildingSelect);
    } catch (error) {
        console.error('Error loading buildings:', error);
    }
}

function onBuildingSelect() {
    const buildingValue = document.getElementById('buildingSelect').value;
    if (buildingValue) {
        document.getElementById('classroomSection').style.display = 'block';
    } else {
        document.getElementById('classroomSection').style.display = 'none';
    }
}

function addBuildingInput() {
    const buildingInputs = document.getElementById('buildingInputs');
    const newInput = document.createElement('div');
    newInput.className = 'input-group';
    newInput.innerHTML = `
        <input type="text" class="building-input" placeholder="Enter building name">
        <button class="remove-btn" onclick="removeInput(this)">-</button>
    `;
    buildingInputs.appendChild(newInput);
}

function addClassroomInput() {
    const classroomInputs = document.getElementById('classroomInputs');
    const newInput = document.createElement('div');
    newInput.className = 'input-group';
    newInput.innerHTML = `
        <input type="text" class="classroom-input" placeholder="Enter classroom number">
        <button class="remove-btn" onclick="removeInput(this)">-</button>
    `;
    classroomInputs.appendChild(newInput);
}

function removeInput(button) {
    button.parentElement.remove();
}

async function addBuildings() {
    const campus = document.getElementById('campusSelect').value;
    const buildingInputs = document.querySelectorAll('.building-input');
    const buildings = Array.from(buildingInputs).map(input => input.value.trim()).filter(Boolean);

    try {
        const response = await fetch('/add_buildings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ campus, buildings }),
        });
        if (response.ok) {
            alert('Buildings added successfully');
            document.getElementById('buildingInputs').innerHTML = `
                <div class="input-group">
                    <input type="text" class="building-input" placeholder="Enter building name">
                    <button class="remove-btn" onclick="removeInput(this)">-</button>
                </div>
            `;
            await loadBuildings(campus);
            document.getElementById('classroomSection').style.display = 'block';
        } else {
            console.error('Failed to add buildings');
        }
    } catch (error) {
        console.error('Error adding buildings:', error);
    }
}

function addLevelInput() {
    const levelInputs = document.getElementById('levelInputs');
    const newLevel = document.createElement('div');
    newLevel.className = 'level-group';
    newLevel.innerHTML = `
        <div class="level-input-container">
            <input type="text" class="level-input" placeholder="Enter level">
            <button class="remove-btn" onclick="removeLevelInput(this)">- Level</button>
            <button onclick="addClassroomInput(this)">+ Classroom</button>
        </div>
        <div class="classroom-inputs"></div>
    `;
    levelInputs.appendChild(newLevel);
}

function removeLevelInput(button) {
    button.closest('.level-group').remove();
}

function addClassroomInput(button) {
    const levelGroup = button.closest('.level-group');
    const classroomInputs = levelGroup.querySelector('.classroom-inputs');
    const newInput = document.createElement('div');
    newInput.className = 'input-group';
    newInput.innerHTML = `
        <input type="text" class="classroom-input" placeholder="Enter classroom number">
        <button class="remove-btn" onclick="removeClassroomInput(this)">- Classroom</button>
    `;
    classroomInputs.appendChild(newInput);
}

function removeClassroomInput(button) {
    button.closest('.input-group').remove();
}

async function addClassrooms() {
    const campus = document.getElementById('campusSelect').value;
    const building = document.getElementById('buildingSelect').value;
    const levelGroups = document.querySelectorAll('.level-group');
    
    const classroomData = Array.from(levelGroups).map(levelGroup => {
        const level = levelGroup.querySelector('.level-input').value.trim();
        const classroomInputs = levelGroup.querySelectorAll('.classroom-input');
        const classrooms = Array.from(classroomInputs)
            .map(input => input.value.trim())
            .filter(Boolean);
        return { level, classrooms };
    }).filter(data => data.level && data.classrooms.length > 0);

    try {
        const response = await fetch('/add_classrooms', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ campus, building, classroomData }),
        });
        if (response.ok) {
            alert('Classrooms added successfully');
            document.getElementById('levelInputs').innerHTML = `
                <div class="level-group">
                    <div class="level-input-container">
                        <input type="text" class="level-input" placeholder="Enter level">
                        <button class="remove-btn" onclick="removeLevelInput(this)">- Level</button>
                        <button onclick="addClassroomInput(this)">+ Classroom</button>
                    </div>
                    <div class="classroom-inputs"></div>
                </div>
            `;
            loadLocations();
        } else {
            console.error('Failed to add classrooms');
        }
    } catch (error) {
        console.error('Error adding classrooms:', error);
    }
}


async function loadLocations() {
    try {
        const response = await fetch('/get_locations');
        const locations = await response.json();
        displayLocations(locations);
    } catch (error) {
        console.error('Error loading locations:', error);
    }
}

function displayLocations(locations) {
    const locationList = document.getElementById('locationList');
    locationList.innerHTML = '';
    locations.forEach(location => {
        const locationElement = document.createElement('div');
        locationElement.className = 'location-item';
        locationElement.innerHTML = `
            <p>${location.campus} - ${location.building}, Level ${location.level}, Room ${location.classroom}</p>
            <button onclick="deleteLocation('${location._id}')">Delete</button>
        `;
        locationList.appendChild(locationElement);
    });
}

async function deleteLocation(locationId) {
    if (confirm('Are you sure you want to delete this location?')) {
        try {
            const response = await fetch(`/delete_location/${locationId}`, {
                method: 'DELETE',
            });
            if (response.ok) {
                loadLocations();
            } else {
                console.error('Failed to delete location');
            }
        } catch (error) {
            console.error('Error deleting location:', error);
        }
    }
}



async function deleteAllBuildingsInCampus() {
    const campus = document.getElementById('campusSelect').value;
    if (!campus) {
        alert('Please select a campus first');
        return;
    }

    if (confirm(`Are you sure you want to delete all buildings and classrooms in ${campus} campus?`)) {
        try {
            const response = await fetch(`/delete_all_buildings_in_campus/${campus}`, {
                method: 'DELETE',
            });
            if (response.ok) {
                alert(`All buildings and classrooms in ${campus} have been deleted`);
                loadBuildings(campus);
                loadLocations();
            } else {
                console.error('Failed to delete all buildings');
            }
        } catch (error) {
            console.error('Error deleting all buildings:', error);
        }
    }
}

async function deleteAllClassroomsInBuilding() {
    const campus = document.getElementById('campusSelect').value;
    const building = document.getElementById('buildingSelect').value;
    if (!campus || !building) {
        alert('Please select a campus and a building first');
        return;
    }

    if (confirm(`Are you sure you want to delete all classrooms in ${building}, ${campus}?`)) {
        try {
            const response = await fetch(`/delete_all_classrooms_in_building/${campus}/${building}`, {
                method: 'DELETE',
            });
            if (response.ok) {
                alert(`All classrooms in ${building}, ${campus} have been deleted`);
                loadLocations();
            } else {
                console.error('Failed to delete all classrooms');
            }
        } catch (error) {
            console.error('Error deleting all classrooms:', error);
        }
    }
}



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