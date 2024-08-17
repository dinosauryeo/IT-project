function showPage(pageId) {
    // Hide all pages
    var pages = document.querySelectorAll('.page');
    pages.forEach(function(page) {
        page.style.display = 'none';
    });

    // Show the selected page
    var selectedPage = document.getElementById(pageId);
    selectedPage.style.display = 'block';
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
});

document.getElementById('uploadForm').addEventListener('submit', function (e) {
    e.preventDefault();
    let fileInput = document.getElementById('fileInput');
    let file = fileInput.files[0];

    if (file) {
        let formData = new FormData();
        formData.append('file', file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('uploadStatus').innerText = 'File uploaded successfully!';
            console.log('File Data:', data);  // Display the JSON data
        })
        .catch(error => {
            document.getElementById('uploadStatus').innerText = 'File upload failed.';
            console.error('Error:', error);
        });
    }
});
