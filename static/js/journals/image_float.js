document.querySelectorAll('.entry-container .weblog-content').forEach(function(content) {
    content.querySelectorAll('img').forEach(function(img, i) {
        img.classList.add(i % 2 === 0 ? 'float-left' : 'float-right');
    });
});
