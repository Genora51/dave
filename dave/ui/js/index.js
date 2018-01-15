const ENTER_KEYCODE = 13;

var socket = io();

function addMessage(text, isDave=false) {
    let messageClass = isDave ? "dave" : "user";
    let messageHtml = '<div class="message '
                    + messageClass
                    + '">' + text + '</div>';
    if (!isDave) $('.message.dave:last-of-type').addClass('last');
    $('.main').append(messageHtml);
}

$(function() {
    $('#user-input').focus();
    $('#user-input').on("keydown", function(e) {
        if (e.which == ENTER_KEYCODE) {
            let message = $(this).val();
            socket.emit("text request", message);
            addMessage(removeTags(message));
            $(this).val("");
        }
    });
    $('#speech-input').click(function(e) {
        if (!$(this).hasClass('disabled')) {
            $(this).addClass('disabled');
            socket.emit("speech request", null);
        }
    });
});

socket.on('plaintext reply', function(message) {
    addMessage(removeTags(message), isDave=true);
});

socket.on('speech reply', function(message) {
    addMessage(removeTags(message));
    $('#speech-input').removeClass('disabled');
    socket.emit('text request', message);
});