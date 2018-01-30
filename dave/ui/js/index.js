const ENTER_KEYCODE = 13;

var socket = io();

function addMessage(text, isDave=false) {
    let messageClass = isDave ? "dave" : "user";
    let messageHtml = '<div class="message '
                    + messageClass
                    + '">' + text + '</div>';
    if (!isDave) $('.message.dave:last-of-type').addClass('last');
    let $main = $('.main');
    $main.append(messageHtml)
    let height = $main[0].scrollHeight;
    $main.stop().animate({
        scrollTop: height
    }, 300);
    return $('.message.dave:last-of-type');
}

$(function() {
    $('#user-input').focus();
    $('#user-input').on("keydown", function(e) {
        if (e.which == ENTER_KEYCODE) {
            let message = $(this).val();
            if (message !== "") {
                socket.emit("text request", message);
                addMessage(removeTags(message));
                $(this).val("");
            }
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
    if (message !== null) {
        addMessage(removeTags(message), isDave=true);
    }
});

socket.on('coloured reply', function(data){
    var message;
    if (data["form"] == 'msg') {
        message = removeTags(data["message"]);
    } else {
        message = data["message"];
    }
    box = addMessage(message, isDave=true);
    box.css('background-color', data["colour"]);
});

socket.on('html reply', function(message) {
    if (message !== null) {
        addMessage(message, isDave=true);
    }
});

socket.on('speech reply', function(data) {
    $('#speech-input').removeClass('disabled');
    let message = data[0];
    let error = data[1];
    if (!error) {
        addMessage(removeTags(message));
        socket.emit('text request', message);
    } else {
        addMessage(removeTags(message), isDave=true);
    }
});