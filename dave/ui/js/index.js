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
            socket.emit("dave request", message);
            addMessage(removeTags(message));
            $(this).val("");
        }
    });
});

socket.on('plaintext reply', function(message) {
    addMessage(removeTags(message), isDave=true);
});
