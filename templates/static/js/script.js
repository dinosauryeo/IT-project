function func() {
    //fetch the username and password from user
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
            console.log("login succesful");
            window.location.href = '/home'; // Redirect to home.html
        } 
        else {
            console.log("incorrect pasword");
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred');
    });
}
