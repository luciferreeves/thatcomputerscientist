$(document).ready(function(){
    function createMessageElement(message, username, type) {
        var messageElement = document.createElement('div');
        var username = username || 'Anonymous';
        messageElement.classList.add('message');
        switch(type) {
            case 'connect':
                messageElement.innerHTML = '<span style="color: #a0e9ff;">' + "<b>" + username + "</b>: " + message + '</span>';
                break;
            case 'disconnect':
                messageElement.innerHTML = '<span style="color: #ff9494;">' + "<b>" + username + "</b>: " + message + '</span>';
                break;
            case 'bot':
                messageElement.innerHTML = '<span style="color: #fbbf49;">' + "<b>" + username + "</b>: " + message + '</span>';
                break;
            case 'default':
                messageElement.innerHTML ="<b>" + username + "</b>: " + message;
                break;
        }
        $('#messages').append(messageElement);
        $('#messages').animate({scrollTop: $('#messages').prop("scrollHeight")}, 100);
    }

    var protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    var URL = protocol + window.location.host + '/ws/chat/';

    var ws = new WebSocket(URL);
    ws.onopen = function(e) {
        createMessageElement('You are now connected to the Chat Server!', 'System', 'connect');
    }
    ws.onerror = function(e) {
        createMessageElement('Connection to the Chat Server failed!', 'System', 'disconnect');
    }
    ws.onclose = function(e) {
        createMessageElement('You have been disconnected from the Chat Server!', 'System', 'disconnect');
    }
    ws.onmessage = function(e) {
        var data = JSON.parse(e.data);
        if(data['username'] == 'Skippy') { // Bot
            createMessageElement(data['message'].trim(), data['username'], 'bot');
        } else if (data['username'] == 'System') { // System
            createMessageElement(data['message'].trim(), data['username'], 'connect');
        } else { // User
            createMessageElement(data['message'].trim(), data['username'], 'default');
        }
    }

    $('#chatbox-input').on('keyup', function(e) {
        if (e.keyCode == 13) {
            var message = $('#chatbox-input').val();
            ws.send(JSON.stringify({
                'message': message,
                'username': username
            }));
            $('#chatbox-input').val("");
        }
    });
});