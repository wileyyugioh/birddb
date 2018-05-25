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
    this.controller.className = "bird-call audio-button audio-play";
}

function main() {
    var players = document.getElementsByClassName("audio-player");

    // assumes 1 audio control for every audio player
    for(var i = 0; i < players.length; i++) {
        // create the new button
        var audio_button = document.createElement("a");
        audio_button.className = "bird-call audio-button audio-play";

        var audio_player = players[i];

        // add it to the html
        audio_player.parentNode.insertBefore(audio_button, audio_player.parentNode.firstChild);

        // remove default behavior
        audio_player.controls = false;

        // add player to controls and vice versa
        audio_button.player = audio_player;
        audio_player.controller = audio_button;

        // add listeners
        audio_button.addEventListener("click", doToggle, false);
        audio_player.addEventListener("ended", doEnd, false);
    }
}

main();