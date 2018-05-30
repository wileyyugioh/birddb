function disableForm() {
    // hide the form
    this.style.display = "none";

    // add thank you message
    this.nextElementSibling.style.display = "";
}

function form_main() {
    var bird_error = document.getElementsByClassName("bird-error");
    var bird_report = document.getElementsByClassName("bird-error-report");

    for(var i = 0; i < bird_error.length; i++) {
        // add listener to form submit
        bird_error[i].addEventListener("submit", disableForm, true);

        // add error form to report button
        bird_report[i].error_form = bird_error[i];

        // add listener to report button clicked
        bird_report[i].addEventListener("click", function() {
            this.error_form.style.display = "";
            this.style.display = "none";

        }, false);
    }
}

form_main();