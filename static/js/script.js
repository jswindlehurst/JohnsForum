

function comparePassword() {
    let password = document.getElementById("password");
    let password2 = document.getElementById("password2");
    let resultDisplay = document.getElementById("result");

    if (password != password2) {
        resultDisplay.textContent = "The Passwords do not Match, try again"
    } else {
        resultDisplay.textContent = "The Passwords Match."
    }

}