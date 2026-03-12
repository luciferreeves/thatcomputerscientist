(function() {
    var config = JSON.parse(document.getElementById('new-entry-config').textContent);

    var editor = new FancyMiku('#editor-container', {
        height: '600px',
        placeholder: config.placeholder
    });

    document.getElementById('entry-form').addEventListener('submit', function(e) {
        var content = editor.getContent();
        document.getElementById('entry-content').value = content;

        if (!content || content.trim() === '<p><br></p>' || content.trim() === '') {
            e.preventDefault();
            alert(config.alertEmpty);
            return false;
        }
    });
})();
