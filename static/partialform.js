function disableForm() {
    // hide the form
    this.style.display = "none";

    // add thank you message
    this.nextElementSibling.style.display = "";
}

function main() {
    var bird_error = document.getElementsByClassName("bird-error");
    var js_error = document.getElementsByClassName("bird-error-no-js");
    for(var i = 0; i < bird_error.length; i++) {
        // add listener to form submit
        bird_error[i].style.display = "";
        js_error[i].style.display = "none";

        bird_error[i].addEventListener("submit", disableForm, false);
    }
}

main();