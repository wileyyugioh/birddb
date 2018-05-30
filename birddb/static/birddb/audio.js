function toggleAudio(audio_handle, audio_button) {
    if(audio_handle.paused) {
        audio_handle.play();
        audio_button.className = "bird-call audio-button audio-stop";
    } else {
        audio_handle.pause();
        audio_handle.currentTime = 0;
        audio_button.className = "bird-call audio-button audio-play";
    }
}

function doToggle() {
    toggleAudio(this.player, this);
}

function doEnd() {
    this.custom_controller.className = "bird-call audio-button audio-play";
}

function audio_main() {
    var players = document.getElementsByClassName("audio-player");
    var buttons = document.getElementsByClassName("audio-button")

    // assumes 1 audio control for every audio player
    for(var i = 0; i < players.length; i++) {
        var audio_player = players[i];
        var audio_button = buttons[i];

        // enable the button
        audio_button.style.display = "";

        // add player to controls and vice versa
        audio_button.player = audio_player;
        audio_player.custom_controller = audio_button;

        // add listeners
        audio_button.addEventListener("click", doToggle, false);
        audio_player.addEventListener("ended", doEnd, false);
    }
}

audio_main();