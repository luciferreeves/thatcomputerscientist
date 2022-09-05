const refreshCaptchaButton = document.getElementById('refresh_captcha');

refreshCaptchaButton.addEventListener('click', function() {
    const refreshCaptchaURl = refreshCaptchaButton.getAttribute('data-refresh-captcha-url');

    const xhr = new XMLHttpRequest();
    xhr.open('GET', refreshCaptchaURl, true);
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.onload = function() {
        const data = JSON.parse(this.responseText);
        const captchaImage = document.getElementById('captcha_image');
        captchaImage.src = data['captcha'];
    }
    xhr.send();
});
