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

