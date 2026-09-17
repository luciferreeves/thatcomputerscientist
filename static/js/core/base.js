new Pamphlet({
    server: '/services/pamphlet',
    refreshInterval: 120000 // 2 minutes
});

// KawaiiBeats Player
const elements = {
    playButton: document.getElementById('song-play'),
    prevButton: document.getElementById('song-prev'),
    nextButton: document.getElementById('song-next'),
    timeElapsed: document.getElementById('song-time-elapsed'),
    timeTotal: document.getElementById('song-time-total'),
    songCover: document.getElementById('song-cover'),
    songTitle: document.getElementById('song-title'),
    songArtistAlbum: document.getElementById('song-artist-album'),
    visualizer: document.getElementById('song-visualizer')
};

const player = new AudioPlayer(elements, {
    storeLimit: STORE_LIMIT,
    serverURL: window.location.origin,
});
player.init();

function presentAlert(message, duration = 6000) {
    const alertEl = document.getElementById('global-alert');
    const textEl = alertEl.querySelector('.hologram-text');

    if (alertEl.classList.contains('show') || alertEl.classList.contains('hide')) {
        alertEl.classList.remove('show', 'hide');
        clearTimeout(alertEl.hideTimeout);
        clearTimeout(alertEl.removeTimeout);
    }

    textEl.textContent = message.toUpperCase();

    void alertEl.offsetWidth;

    requestAnimationFrame(() => {
        alertEl.classList.add('show');
    });

    const animationTimeIn = 1300;
    const visibleDuration = duration;
    const animationTimeOut = 1300;

    alertEl.hideTimeout = setTimeout(() => {
        alertEl.classList.add('hide');
        alertEl.classList.remove('show');

        alertEl.removeTimeout = setTimeout(() => {
            alertEl.classList.remove('hide');
        }, animationTimeOut + 200);
    }, animationTimeIn + visibleDuration);
}