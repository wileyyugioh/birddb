function disableForm(event) {
    event.preventDefault();

    // hide the form
    this.style.display = "none";

    // add thank you message
    this.nextElementSibling.style.display = "";

    // whisk our data away
    var data = new FormData(event.target);
    var req = new XMLHttpRequest();
    req.open("POST", event.target.action)
    req.send(data);

    return false;
}

function form_main() {
    var bird_error = document.getElementsByClassName("bird-error");
    for(var i = 0; i < bird_error.length; i++) {
        // add listener to form submit
        bird_error[i].addEventListener("submit", disableForm, false);
    }
}

form_main();