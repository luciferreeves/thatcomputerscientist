(function () {
    // Core configuration constants
    const SITE_BASE_WIDTH = 1000;
    const MIN_SCALE_WIDTH = 1600;  // Threshold for starting scale adjustments
    const HI_RES_WIDTH = 1920;     // Threshold for forcing maximum resolution
    const MAX_DENSITY = 3;         // Maximum supported image density

    // Calculate appropriate image density based on screen size and device
    function getTargetDensity() {
        const screenWidth = window.innerWidth;
        const devicePixelRatio = window.devicePixelRatio || 1;

        if (screenWidth < MIN_SCALE_WIDTH) return 1;
        if (screenWidth >= HI_RES_WIDTH) return MAX_DENSITY;

        const scaleRatio = screenWidth / MIN_SCALE_WIDTH;
        const effectiveScale = scaleRatio * devicePixelRatio;

        return effectiveScale > 2 ? 2 : 1;
    }

    // Update single image to appropriate resolution
    function forceHighResImage(img) {
        const srcset = img.getAttribute('srcset');
        if (!srcset) return;

        const sources = srcset.split(',').map(src => {
            const [url, size] = src.trim().split(' ');
            return {
                url: url,
                density: parseFloat(size.replace('x', '')) || 1
            };
        }).sort((a, b) => b.density - a.density);

        const targetDensity = getTargetDensity();
        const targetSource = sources.reduce((prev, curr) => {
            if (curr.density <= targetDensity && curr.density > prev.density) {
                return curr;
            }
            return prev;
        }, { density: 0 });

        if (img.src !== targetSource.url) {
            const newImg = document.createElement('img');
            Array.from(img.attributes).forEach(attr => {
                if (attr.name !== 'src' && attr.name !== 'srcset') {
                    newImg.setAttribute(attr.name, attr.value);
                }
            });
            newImg.src = targetSource.url;
            img.parentNode.replaceChild(newImg, img);
        }
    }

    // Update all images on the page
    function updateAllImages() {
        document.querySelectorAll('img[srcset]').forEach(forceHighResImage);
    }

    // Calculate and apply scaling based on screen width
    function calculateScale() {
        const screenWidth = window.innerWidth;
        const wrapper = document.getElementById('body-wrapper');
        if (!wrapper) return;

        if (screenWidth <= MIN_SCALE_WIDTH) {
            wrapper.style.transform = 'scale(1)';
            wrapper.style.transformOrigin = 'left top';
            wrapper.style.left = '50%';
            wrapper.style.marginLeft = `-${SITE_BASE_WIDTH / 2}px`;
            return;
        }

        const scaleRatio = screenWidth / MIN_SCALE_WIDTH;
        const scaledWidth = SITE_BASE_WIDTH * scaleRatio;
        const leftPosition = (screenWidth - scaledWidth) / 2;

        wrapper.style.transform = `scale(${scaleRatio})`;
        wrapper.style.transformOrigin = 'left top';
        wrapper.style.left = `${leftPosition}px`;
        wrapper.style.position = 'absolute';
        wrapper.style.marginLeft = '0';
    }

    // Initialize wrapper positioning and initial calculations
    function init() {
        const wrapper = document.getElementById('body-wrapper');
        if (wrapper) {
            wrapper.style.position = 'absolute';
            wrapper.style.width = `${SITE_BASE_WIDTH}px`;
            wrapper.style.top = '0';
        }

        calculateScale();
        updateAllImages();
    }

    // Handle dynamically added images
    const observer = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1) {
                    if (node.tagName === 'IMG' && node.hasAttribute('srcset')) {
                        forceHighResImage(node);
                    }
                    node.querySelectorAll('img[srcset]').forEach(forceHighResImage);
                }
            });
        });
    });

    // Debounced resize handler
    let resizeTimeout;
    function handleResize() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            calculateScale();
            updateAllImages();
        }, 100);
    }

    // Event listeners and initialization
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            init();
            observer.observe(document.body, { childList: true, subtree: true });
        });
    } else {
        init();
        observer.observe(document.body, { childList: true, subtree: true });
    }

    window.addEventListener('load', init);
    window.addEventListener('resize', handleResize);
    window.addEventListener('orientationchange', handleResize);
})();