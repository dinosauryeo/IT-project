function func() {
    var email = document.getElementById("username").value;
    var pass = document.getElementById("password").value;
    if ((email == '123@gmail.com' || email == 'member1') && pass == '12345678') {
        window.location.assign("home.html") // Redirect to home.html
    } else {
        alert("wrong entry");
    }
}
