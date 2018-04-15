const ENTER_KEYCODE = 13;

var socket = io();

function removeTags(unsafe) {
    /* Sanitise plain text as HTML */
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

function addMessage(text, isDave=false) {
    /* Add a message to the bottom of the page, then scroll */
    let messageClass = isDave ? "dave" : "user";
    // Create HTML from message and class
    let messageHtml = '<div class="message '
                    + messageClass
                    + '">' + text + '</div>';
    // Add 'last' class to ensure correct border-radius applied
    if (!isDave) $('.message.dave:last-of-type').addClass('last');
    // Animate scroll
    let $main = $('.main');
    let $message = $(messageHtml);
    $main.append($message)
    let height = $main[0].scrollHeight;
    $main.stop().animate({
        scrollTop: height
    }, 300);
    // Return last message for calling function
    return $message;
}

$(function() {
    $('#user-input').focus();
    $('#user-input').on("keydown", function(e) {
        // On enter text, check for ENTER key
        if (e.which == ENTER_KEYCODE) {
            let message = $(this).val();
            if (message !== "") {
                // If message, emit to server and add to page
                socket.emit("text request", message);
                addMessage(removeTags(message));
                // Clear textbox
                $(this).val("");
            }
        }
    });
    $('#speech-input').click(function(e) {
        // Attempt speech-recognition, if currently allowed
        if (!$(this).hasClass('disabled')) {
            // Disable further attempts until server reply
            $(this).addClass('disabled');
            // Request server
            socket.emit("speech request", null);
        }
    });
    $('.toolbar').click(function(e) {
        // Send request
        socket.emit("reload modules", null);
    });
    $(document).on('click', 'a', function(e){
        e.preventDefault();
        socket.emit("open link", $(this).attr("href"));
    });
});

socket.on('plaintext reply', function(message) {
    // If message, add to page
    if (message !== null) {
        addMessage(removeTags(message), isDave=true);
    }
});

socket.on('coloured reply', function(data){
    /* Coloured box for response */
    var message;
    // Check for sanitised type
    if (data["form"] == 'msg') {
        message = removeTags(data["message"]);
    } else {
        message = data["message"];
    }
    // Add and colour message
    box = addMessage(message, isDave=true);
    box.css('background-color', data["colour"]);
});

socket.on('html reply', function(message) {
    // Add reply as raw html, if possible
    if (message !== null) {
        addMessage(message, isDave=true);
    }
});

socket.on('speech reply', function(data) {
    /* Response from 'speech request' emission */
    // Re-enable speech input
    $('#speech-input').removeClass('disabled');
    let message = data[0];
    let error = data[1];
    // If no error, add request as user and emit to server
    if (!error) {
        addMessage(removeTags(message));
        socket.emit('text request', message);
    } else {
        // Otherwise, add error message as Dave
        addMessage(removeTags(message), isDave=true);
    }
});
