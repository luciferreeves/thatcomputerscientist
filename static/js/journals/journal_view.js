(function() {
    var host = document.getElementById('journal-entries-host');
    var template = document.getElementById('journal-entries-template');
    var shadow = host.attachShadow({ mode: 'open' });

    var styleUrls = JSON.parse(document.getElementById('journal-view-config').textContent);
    styleUrls.forEach(function(href) {
        var link = document.createElement('link');
        link.rel = 'stylesheet';
        link.type = 'text/css';
        link.href = href;
        shadow.appendChild(link);
    });

    shadow.appendChild(template.content.cloneNode(true));

    shadow.querySelectorAll('.entry-container .weblog-content').forEach(function(content) {
        content.querySelectorAll('img').forEach(function(img, i) {
            img.classList.add(i % 2 === 0 ? 'float-left' : 'float-right');
        });
    });
})();
