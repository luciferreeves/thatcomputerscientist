document.addEventListener('DOMContentLoaded', function () {
    const content = document.getElementById('weblog-body-content');
    const images = content.querySelectorAll('img');

    images.forEach((img, index) => {
        // Create a wrapper for the image
        const imgWrapper = document.createElement('div');
        imgWrapper.style.maxWidth = '100%';
        imgWrapper.className = 'image-wrapper';

        // Alternate between left and right alignment
        if (index % 2 === 0) {
            imgWrapper.style.float = 'left';
            imgWrapper.style.marginRight = '20px';
            imgWrapper.style.marginBottom = '15px';
        } else {
            imgWrapper.style.float = 'right';
            imgWrapper.style.marginLeft = '20px';
            imgWrapper.style.marginBottom = '15px';
        }

        // Replace the image with our wrapped version
        img.parentNode.insertBefore(imgWrapper, img);
        imgWrapper.appendChild(img);
    });

    window.MathJax = {
        tex: {
            inlineMath: [
                ['$', '$'],
                ['\\(', '\\)']
            ],
            displayMath: [
                ['$$', '$$'],
                ['\\[', '\\]']
            ],
            processEscapes: true,
            processEnvironments: true
        },
        options: {
            skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'],
            ignoreHtmlClass: 'tex2jax_ignore',
            processHtmlClass: 'tex2jax_process',
            enableMenu: false,
        }
    }
});

function showReplyForm(commentId) {
    document.getElementById(`reply-form-${commentId}`).style.display = 'block';
}

function hideReplyForm(commentId) {
    document.getElementById(`reply-form-${commentId}`).style.display = 'none';
}