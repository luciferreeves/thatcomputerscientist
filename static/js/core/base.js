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