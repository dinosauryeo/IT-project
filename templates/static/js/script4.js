
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
    const addYearSemesterBtn = document.getElementById('add-year-semester-btn');
    const addYearSemesterContainer = document.getElementById('add-year-semester-container');
    const saveYearSemesterBtn = document.getElementById('save-year-semester-btn');
    const yearSemesterSelect = document.getElementById('year-semester');
    const addSectionBtn = document.getElementById('add-section-btn');
    const yearSemesterSections = document.getElementById('year-semester-sections');
    const subjectInfoContainer = document.getElementById('subject-info');
    const subjectContainer = document.getElementById('subject-container'); // Container for subjects

    const sectionDropdown = document.createElement('select');
    sectionDropdown.id = 'section-dropdown';
    sectionDropdown.style.display = 'none'; // Initially hidden

    // Show the add-year-semester-container when "+" button is clicked
    addYearSemesterBtn.addEventListener('click', function () {
        addYearSemesterContainer.style.display = 'block';
        subjectInfoContainer.style.display = 'none'; // Hide existing subject info
        addYearSemesterSection(); // Add the first section
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
        const selectedValue = this.value;  // Should be in the format "2019_Semester1"

        fetch(`/getsubjects?year_semester=${selectedValue}`)
            .then(response => response.json())
            .then(data => {
                if (Array.isArray(data)) {
                    subjectContainer.innerHTML = '';  // Clear existing subjects

                    // Populate the container with clickable subjects
                    data.forEach(subject => {
                        const subjectItem = document.createElement('div');
                        subjectItem.classList.add('subject-item');
                        subjectItem.textContent = subject.subjectString;
                        subjectItem.dataset.subjectCode = subject.subjectCode;
                        subjectItem.dataset.coordinator = subject.coordinator; // Add these attributes
                        subjectItem.dataset.campus = subject.campus;         // Add these attributes
                        
                        // Log the data attributes to check their values
                        // console.log('Coordinator:', subjectItem.dataset.coordinator);
                        // console.log('Campus:', subjectItem.dataset.campus);
    
                        // Create and append the dropdown to each subject item
                        const sectionDropdown = document.createElement('select');
                        sectionDropdown.style.display = 'none';  // Hide initially
                        sectionDropdown.classList.add('section-dropdown'); // Add a class for easy styling and access
                        subjectItem.appendChild(sectionDropdown);
    
                        subjectContainer.appendChild(subjectItem);
                    });
                } else {
                    alert('Error fetching subjects: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error fetching subjects.');
            });
    });

    function loadSubjectDetails(subjectCode, yearSemester) {
        fetch(`/getsubjectdetails?subject_code=${subjectCode}&year_semester=${yearSemester}`)
            .then(response => response.json())
            .then(data => {
                if (data) {
                    // Update the subject information in the right bar
                    document.getElementById('subject-code').textContent = data.subjectCode || 'N/A';
                    document.getElementById('subject-title').textContent = data.subjectName || 'N/A';
                    document.getElementById('subject-coordinator').textContent = data.coordinator || 'N/A';
                    document.getElementById('campus').textContent = data.campus || 'N/A';

                    // Clear and populate lecture/tutorial list
                    const lectureTutorialList = document.getElementById('lecture-tutorial-list');
                    lectureTutorialList.innerHTML = '';
                    ['lecture', 'tutorial', 'lab'].forEach(type => {
                        if (data.sections[type] && data.sections[type].length > 0) {
                            data.sections[type].forEach(title => {
                                const listItem = document.createElement('li');
                                listItem.textContent = `${type.charAt(0).toUpperCase() + type.slice(1)}: ${title}`;
                                lectureTutorialList.appendChild(listItem);
                            });
                        }
                    });

                    // Remove any existing dropdowns
                    document.querySelectorAll('.section-dropdown').forEach(dropdown => dropdown.remove());

                    // Populate the section dropdown in the clicked subject item
                    const sectionDropdown = document.createElement('select');
                    sectionDropdown.classList.add('section-dropdown');
                    sectionDropdown.innerHTML = ''; // Clear existing options
                    ['lecture', 'tutorial', 'lab'].forEach(type => {
                        if (data.sections[type] && data.sections[type].length > 0) {
                            const optionGroup = document.createElement('optgroup');
                            optionGroup.label = type.charAt(0).toUpperCase() + type.slice(1);
                            data.sections[type].forEach(title => {
                                const option = document.createElement('option');
                                option.value = title;
                                option.textContent = title;
                                optionGroup.appendChild(option);
                            });
                            sectionDropdown.appendChild(optionGroup);
                        }
                    });

                    // Add the dropdown after the clicked subject item
                    const activeItem = document.querySelector('.subject-item.active');
                    if (activeItem) {
                        activeItem.insertAdjacentElement('afterend', sectionDropdown);
                    }

                    // Show the section dropdown
                    sectionDropdown.style.display = 'block';

                    // Show the subject-info section
                    document.getElementById('subject-info').style.display = 'block';

                } else {
                    alert('Error fetching subject details.');
                }
            })
            .catch(error => {
                console.error('Error fetching subject details:', error);
                alert('Error fetching subject details.');
            });
    }

    let currentSubjectInfo = {}; // This will store the current subject info

    // Add click event to load subject details
    subjectContainer.addEventListener('click', function (event) {
        if (event.target && event.target.classList.contains('subject-item')) {
            // Remove active class from all other subject items
            document.querySelectorAll('.subject-item').forEach(item => item.classList.remove('active'));

            event.target.classList.add('active');

            // Extract details from the clicked subject item
            const subjectCode = event.target.dataset.subjectCode;
            const subjectName = event.target.textContent.trim().substring(11); // Adjust if needed
            const coordinator = event.target.dataset.coordinator;
            const campus = event.target.dataset.campus;

            // Check the extracted values
            // console.log('Extracted Subject Code:', subjectCode);
            // console.log('Extracted Subject Name:', subjectName);
            // console.log('Extracted Coordinator:', coordinator);
            // console.log('Extracted Campus:', campus);

            // Split year and semester
            const year = document.getElementById('year-semester').value.substring(0, 4);
            const semester = document.getElementById('year-semester').value.substring(5);

            // Store extracted information
            currentSubjectInfo = {
                subjectCode: subjectCode,
                subjectName: subjectName,
                coordinator: coordinator,
                campus: campus,
                year: year,
                semester: semester
            };

            // console.log('Clicked subject details:', currentSubjectInfo);
            // console.log('Clicked subject code:', subjectCode);
            // console.log('semster:', semester);

            const selectedValue = document.getElementById('year-semester').value; // Get the selected year and semester
            if (subjectCode && selectedValue) {
                loadSubjectDetails(subjectCode, selectedValue);
            } else {
                alert('Subject code or year/semester is missing.');
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


});


