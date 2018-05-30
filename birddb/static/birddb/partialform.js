function disableForm() {
    // hide the form
    this.style.display = "none";

    // add thank you message
    this.nextElementSibling.style.display = "";
}

function form_main() {
    var bird_error = document.getElementsByClassName("bird-error");
    for(var i = 0; i < bird_error.length; i++) {
        // add listener to form submit
        bird_error[i].addEventListener("submit", disableForm, false);
    }
}

form_main();