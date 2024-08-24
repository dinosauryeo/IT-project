function func() {
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username: username, password: password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.href = "home.html"; // Redirect to home.html
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred');
    });
}
