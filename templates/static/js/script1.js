function SendVeriCode() {
    var email = document.getElementById("email").value;
    //send the email address to python
    fetch('/send_vericode', {
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

    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W])[A-Za-z\d\W]{8,}$/;

    if (resetpassword !== confirmPassword) {
        alert("Passwords do not match!");
        return;
    }
    if (!regex.test(resetpassword)){
        alert("This password doesn't meet the required requirement");
        return;
    }

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
