(function() {
    var container = document.getElementById('letters-container');
    var username = container.dataset.username;
    var currentUser = container.dataset.currentUser;
    var olderUrl = container.dataset.olderUrl;
    var labelYou = container.dataset.labelYou;
    var labelLoading = container.dataset.labelLoading;
    var labelLoadOlder = container.dataset.labelLoadOlder;

    // --- WebSocket ---

    var wsProtocol = location.protocol === 'https:' ? 'wss://' : 'ws://';
    var wsUrl = wsProtocol + location.host + '/ws/letters/' + username + '/';
    var socket = null;

    function connectSocket() {
        socket = new WebSocket(wsUrl);
        socket.onopen = function() {};
        socket.onclose = function() {
            setTimeout(connectSocket, 3000);
        };
        socket.onmessage = function(e) {
            var data = JSON.parse(e.data);
            if (data.type === 'letter.new') {
                appendLetter(data);
            }
        };
    }
    connectSocket();

    function appendLetter(data) {
        var tbody = document.getElementById('letters-list').querySelector('tbody');

        var empty = tbody.querySelector('.empty-conversation');
        if (empty) empty.remove();

        var isSelf = data.sender === currentUser;
        var tr = document.createElement('tr');
        tr.className = 'letter-note ' + (isSelf ? 'from-self' : 'from-other');
        tr.dataset.letterId = data.letter_id;

        var time = new Date(data.created_at);
        var hours = String(time.getHours()).padStart(2, '0');
        var mins = String(time.getMinutes()).padStart(2, '0');

        var attachmentsHtml = '';
        if (data.attachments && data.attachments.length > 0) {
            attachmentsHtml = '<div class="letter-attachments">';
            for (var a = 0; a < data.attachments.length; a++) {
                var att = data.attachments[a];
                if (att.content_type && att.content_type.startsWith('image/')) {
                    attachmentsHtml += '<a href="' + att.url + '" target="_blank" class="letter-attachment letter-attachment-image"><img src="' + att.url + '" alt="' + att.original_name + '" /></a>';
                } else {
                    attachmentsHtml += '<a href="' + att.url + '" target="_blank" class="letter-attachment"><span class="letter-attachment-file">' + att.original_name + '</span></a>';
                }
            }
            attachmentsHtml += '</div>';
        }

        tr.innerHTML =
            '<td class="letter-gutter">' +
                '<div class="letter-stamp">' + hours + ':' + mins + '</div>' +
                '<div class="letter-sender">' + (isSelf ? labelYou : data.sender) + '</div>' +
            '</td>' +
            '<td class="letter-body">' + data.content + attachmentsHtml + '</td>';

        tbody.appendChild(tr);

        var atBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 100;
        if (atBottom || isSelf) {
            container.scrollTop = container.scrollHeight;
        }

        if (!isSelf && document.hasFocus()) {
            socket.send(JSON.stringify({ type: 'letter.read' }));
        }
    }

    // --- Editor ---

    var editorConfig = JSON.parse(document.getElementById('editor-config').textContent);

    var editor = new MarkMiku('#markmiku-editor', {
        placeholder: editorConfig.placeholder,
        emojis: editorConfig.emojis,
        attachmentUploadUrl: editorConfig.attachmentUploadUrl,
        attachmentRemoveUrl: editorConfig.attachmentRemoveUrl,
        csrfToken: editorConfig.csrfToken,
        maxAttachments: editorConfig.maxAttachments,
        maxAttachmentSize: editorConfig.maxAttachmentSize,
        onSend: function(html, attachmentIds) {
            socket.send(JSON.stringify({ type: 'letter.send', content: html, attachment_ids: attachmentIds }));
        }
    });

    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('markmiku-spoiler')) {
            e.target.classList.toggle('revealed');
        }
    });

    // --- Scroll & Load Older ---

    container.scrollTop = container.scrollHeight;

    var hasMore = container.dataset.hasMore === 'true';
    var loading = false;

    function loadOlderLetters() {
        if (loading || !hasMore) return;
        loading = true;

        var oldestId = container.dataset.oldestId;
        if (!oldestId) { loading = false; return; }

        var btn = document.getElementById('load-older-btn');
        if (btn) btn.textContent = labelLoading;

        var prevHeight = container.scrollHeight;

        fetch(olderUrl + '?before=' + oldestId)
            .then(function(r) { return r.text(); })
            .then(function(html) {
                var temp = document.createElement('table');
                temp.innerHTML = html;

                var wrapper = temp.querySelector('tbody[data-has-more]');
                if (!wrapper) { loading = false; return; }

                var rows = wrapper.querySelectorAll('tr.letter-note');
                if (rows.length > 0) {
                    var tbody = document.getElementById('letters-list').querySelector('tbody');
                    var firstChild = tbody.firstChild;
                    for (var i = 0; i < rows.length; i++) {
                        tbody.insertBefore(rows[i], firstChild);
                    }
                    container.dataset.oldestId = wrapper.dataset.oldestId;
                    container.scrollTop = container.scrollHeight - prevHeight;
                }

                hasMore = wrapper.dataset.hasMore === 'true';
                var loadOlderDiv = document.getElementById('load-older');
                if (!hasMore && loadOlderDiv) {
                    loadOlderDiv.remove();
                } else if (hasMore) {
                    var btn = document.getElementById('load-older-btn');
                    if (btn) btn.textContent = labelLoadOlder;
                }

                loading = false;
            })
            .catch(function() {
                loading = false;
                var btn = document.getElementById('load-older-btn');
                if (btn) btn.textContent = labelLoadOlder;
            });
    }

    container.addEventListener('scroll', function() {
        if (container.scrollTop < 100 && hasMore) {
            loadOlderLetters();
        }
    });

    var loadBtn = document.getElementById('load-older-btn');
    if (loadBtn) {
        loadBtn.addEventListener('click', loadOlderLetters);
    }

})();