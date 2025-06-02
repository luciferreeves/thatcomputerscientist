document.addEventListener('DOMContentLoaded', function () {
    initializeImageLayout();
    setupLightbox();
    configureMathJax();
});

function initializeImageLayout() {
    const content = document.getElementById('weblog-body-content');
    if (!content) return;

    const images = content.querySelectorAll('img');

    const filteredImages = Array.from(images).filter(img => !img.classList.contains('block'));

    if (filteredImages.length > 0) {
        filteredImages.forEach((img, index) => {
            img.setAttribute('data-lightbox', 'content-images');
            img.setAttribute('data-title', img.alt || 'Image ' + (index + 1));

            const imgLink = document.createElement('a');
            imgLink.href = img.src;
            imgLink.className = 'lightbox-image';

            const imgWrapper = document.createElement('div');
            imgWrapper.style.maxWidth = '100%';
            imgWrapper.className = 'image-wrapper';

            if (index % 2 === 0) {
                imgWrapper.style.float = 'left';
                imgWrapper.style.marginRight = '11px';
                imgWrapper.style.marginBottom = '11px';
            } else {
                imgWrapper.style.float = 'right';
                imgWrapper.style.marginLeft = '11px';
                imgWrapper.style.marginBottom = '11px';
            }

            img.parentNode.insertBefore(imgWrapper, img);
            imgWrapper.appendChild(imgLink);
            imgLink.appendChild(img);
        });
    }

    const blockImages = Array.from(images).filter(img => img.classList.contains('block'));

    blockImages.forEach((img) => {
        img.setAttribute('data-lightbox', 'content-images');
        img.setAttribute('data-title', img.alt || 'Image');

        const imgLink = document.createElement('a');
        imgLink.href = img.src;
        imgLink.className = 'lightbox-image';

        img.parentNode.insertBefore(imgLink, img);
        imgLink.appendChild(img);
    });
}

function setupLightbox() {
    const lightbox = document.createElement('div');
    lightbox.id = 'lightbox';
    lightbox.className = 'lightbox';
    lightbox.innerHTML = `
        <div class="lightbox-overlay"></div>
        <div class="lightbox-container">
            <div class="lightbox-content">
                <img src="" alt="Lightbox Image" class="lightbox-image">
                <div class="lightbox-caption"></div>
            </div>
            <button class="lightbox-close">&times;</button>
            <button class="lightbox-prev">&#10094;</button>
            <button class="lightbox-next">&#10095;</button>
        </div>
    `;
    document.body.appendChild(lightbox);

    const style = document.createElement('style');
    style.textContent = `
        .lightbox { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 9999; }
        .lightbox.active { display: flex; justify-content: center; align-items: center; }
        .lightbox-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); }
        .lightbox-container { position: relative; max-width: 80%; max-height: 80%; z-index: 10000; }
        .lightbox-content { position: relative; }
        .lightbox-content img { display: block; max-width: 100%; max-height: 80vh; margin: 0 auto; border: 3px solid white; }
        .lightbox-caption { color: white; text-align: center; padding: 10px; background: rgba(0,0,0,0.7); }
        .lightbox-close { position: absolute; top: -50px; right: -50px; color: white; background: transparent; border: none; font-size: 24px; cursor: pointer; }
        .lightbox-prev, .lightbox-next { position: absolute; top: 50%; transform: translateY(-50%); color: white; background: rgba(0,0,0,0.5); border: none; font-size: 18px; padding: 15px; cursor: pointer; }
        .lightbox-prev { left: -50px; }
        .lightbox-next { right: -50px; }
    `;
    document.head.appendChild(style);

    let images = [];
    let currentIndex = 0;

    document.querySelectorAll('a.lightbox-image').forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();

            images = Array.from(document.querySelectorAll('a.lightbox-image'));
            currentIndex = images.indexOf(this);

            openLightbox(this.href, this.querySelector('img').getAttribute('alt'));
        });
    });

    document.querySelector('.lightbox-close').addEventListener('click', closeLightbox);
    document.querySelector('.lightbox-overlay').addEventListener('click', closeLightbox);

    document.querySelector('.lightbox-prev').addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            const prevLink = images[currentIndex];
            openLightbox(prevLink.href, prevLink.querySelector('img').getAttribute('alt'));
        }
    });

    document.querySelector('.lightbox-next').addEventListener('click', () => {
        if (currentIndex < images.length - 1) {
            currentIndex++;
            const nextLink = images[currentIndex];
            openLightbox(nextLink.href, nextLink.querySelector('img').getAttribute('alt'));
        }
    });

    document.addEventListener('keydown', (e) => {
        if (!document.querySelector('.lightbox.active')) return;

        switch (e.key) {
            case 'Escape': closeLightbox(); break;
            case 'ArrowLeft': document.querySelector('.lightbox-prev').click(); break;
            case 'ArrowRight': document.querySelector('.lightbox-next').click(); break;
        }
    });

    function openLightbox(src, caption) {
        const lightboxImg = document.querySelector('.lightbox img');
        const lightboxCaption = document.querySelector('.lightbox-caption');

        lightboxImg.src = src;
        lightboxCaption.textContent = caption || '';
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent scrolling
    }

    function closeLightbox() {
        lightbox.classList.remove('active');
        document.body.style.overflow = ''; // Re-enable scrolling
    }
}

function showReplyForm(commentId) {
    const replyForm = document.getElementById(`reply-form-${commentId}`);
    if (replyForm) replyForm.style.display = 'block';
}

function hideReplyForm(commentId) {
    const replyForm = document.getElementById(`reply-form-${commentId}`);
    if (replyForm) replyForm.style.display = 'none';
}