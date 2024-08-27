function SendVeriCode() {
    var email = document.getElementById("email").value;
    //send the email address to python
    fetch('/send_email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({email:email})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log("verification send");
            alert("verification code sent!");
        } 
        else {
            console.log("verification fail to send");
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred');
    });
}

function relogin() {
    var email = document.getElementById("email").value;
    var vericode = document.getElementById("vericode").value;
    var resetpassword = document.getElementById("resetpassword").value;
    var confirmpassword = document.getElementById("comfpassword").value;

    fetch('/reset_password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({email:email, vericode:vericode, resetpassword:resetpassword, confirmpassword:confirmpassword})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log("suceess");
            alert(data.message);
            window.location.href = '/';
        } 
        else {
            console.log("reset failed");
            alert(data.message);
        }
    });
}
