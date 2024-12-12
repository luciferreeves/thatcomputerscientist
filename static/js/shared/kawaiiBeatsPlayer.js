// Collection of random anime artwork
const artworkCollection = [
    'https://i.pinimg.com/enabled/564x/e2/5d/31/e25d3199f73c9453035727f8c7a70170.jpg',
    'https://i.pinimg.com/enabled/564x/5f/ed/28/5fed282cff8d22ac857e2a489031d05a.jpg',
    'https://i.pinimg.com/736x/05/a8/71/05a87162a78e2cad2ffe0a9eac6b4e2c.jpg',
    'https://i.pinimg.com/736x/c6/ac/13/c6ac139ed02c9accd34dbb16d7466025.jpg',
    'https://i.pinimg.com/736x/72/69/c3/7269c3d939764b024da9a6869dc59a0f.jpg',
    'https://i.pinimg.com/enabled/564x/cc/5c/6f/cc5c6f1c8e053d791ae2b4300ef5c9fe.jpg',
    'https://i.pinimg.com/enabled/564x/fa/0a/c2/fa0ac2b7145af1205c87350f7c735683.jpg',
    'https://i.pinimg.com/enabled/564x/94/84/57/9484579fcbf7e768d6206b07fa44c2b9.jpg',
    'https://i.pinimg.com/enabled/564x/fd/30/bf/fd30bf62f6409129ce6538f1b9ed7b8b.jpg',
    'https://i.pinimg.com/enabled/564x/44/b2/11/44b21104b4e41736c99ee183127aab3d.jpg',
    'https://i.pinimg.com/enabled/564x/f7/ce/56/f7ce5629aa91866020a559ef7e249f1c.jpg',
    'https://i.pinimg.com/enabled/564x/7b/ac/36/7bac368ff9b5f702d9b727491f8d4ef0.jpg',
    'https://i.pinimg.com/enabled/564x/39/1a/51/391a514a013f62ca9f25f47b4cbd7776.jpg',
    'https://i.pinimg.com/enabled/564x/03/d2/96/03d2967de5d249f88155cab461e69f3a.jpg'
];

// Constants
const SEEKBAR_CONFIG = {
    HEIGHT: 4,
    THUMB_RADIUS: 6,
    HOVER_RADIUS: 8,
    COLORS: {
        BASE: 'rgba(255, 255, 255, 0.5)',
        PROGRESS: 'rgba(255, 255, 255, 1)',
        HOVER: 'rgba(255, 255, 255, 0.8)'
    }
};

const STORE_LIMIT = artworkCollection.length;
const MIN_SCREEN_WIDTH = 2800;

// Audio Context and Core Variables
let audioContext;
let sourceNode;
let analyzerNode;
let audioBuffer;
let startTime;
let pauseTime = 0;
let isPlaying = false;
let currentSong = null;
let isLoading = true;
let isDragging = false;

// DOM Elements
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

// Create and setup seekbar
const seekbarCanvas = document.createElement('canvas');
seekbarCanvas.id = 'custom-seekbar';
seekbarCanvas.width = 140;
seekbarCanvas.height = 20;
seekbarCanvas.style.cssText = 'position: absolute; left: 30px; top: 220px; cursor: pointer; z-index: 1;';
document.getElementById('song-time').parentNode.insertBefore(seekbarCanvas, document.getElementById('song-time'));

class ArtworkManager {
    constructor() {
        this.usedArtwork = new Set();
        this.availableArtwork = [...artworkCollection];
    }

    getRandomArtwork() {
        // If all artwork has been used, reset the pool
        if (this.availableArtwork.length === 0) {
            this.resetArtworkPool();
        }

        // Get random artwork from available pool
        const randomIndex = Math.floor(Math.random() * this.availableArtwork.length);
        const artwork = this.availableArtwork[randomIndex];

        // Remove from available pool and add to used set
        this.availableArtwork.splice(randomIndex, 1);
        this.usedArtwork.add(artwork);

        return artwork;
    }

    resetArtworkPool() {
        this.availableArtwork = [...artworkCollection];
        this.usedArtwork.clear();
    }

    releaseArtwork(artwork) {
        if (this.usedArtwork.has(artwork)) {
            this.usedArtwork.delete(artwork);
            this.availableArtwork.push(artwork);
        }
    }
}

// Song Store Management
class SongStore {
    constructor() {
        this.songs = JSON.parse(localStorage.getItem('songStore')) || [];
        this.currentIndex = parseInt(localStorage.getItem('currentSongIndex')) || -1;
        this.artworkCache = JSON.parse(localStorage.getItem('artworkCache')) || {};
        this.artworkManager = new ArtworkManager();

        // Restore artwork state
        Object.values(this.artworkCache).forEach(artwork => {
            this.artworkManager.usedArtwork.add(artwork);
        });

        // Remove any artwork from availableArtwork that's already in use
        this.artworkManager.availableArtwork = this.artworkManager.availableArtwork
            .filter(artwork => !this.artworkManager.usedArtwork.has(artwork));
    }

    async addSong(song) {
        if (!song) return null;

        // Generate unique artwork for the song
        const artwork = this.artworkManager.getRandomArtwork();
        this.artworkCache[song.id] = artwork;

        // Always add the song, even if it's a duplicate
        this.songs.push({
            id: song.id,
            title: song.title,
            artist: song.artist,
            album: song.album
        });

        // Maintain the store limit
        if (this.songs.length > STORE_LIMIT) {
            const removedSong = this.songs.shift();
            // Release the artwork back to the pool
            const removedArtwork = this.artworkCache[removedSong.id];
            this.artworkManager.releaseArtwork(removedArtwork);
            delete this.artworkCache[removedSong.id];
            if (this.currentIndex > -1) this.currentIndex--;
        }

        this.currentIndex = this.songs.length - 1;
        this.save();

        return {
            ...this.songs[this.currentIndex],
            artwork: this.artworkCache[song.id]
        };
    }

    async getNext() {
        if (this.currentIndex < this.songs.length - 1) {
            this.currentIndex++;
            this.save();
            return {
                ...this.songs[this.currentIndex],
                artwork: this.artworkCache[this.songs[this.currentIndex].id]
            };
        }
        // Get new song if we're at the end
        const newSong = await this.fetchNewSong();
        return this.addSong(newSong);
    }

    async getPrevious() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.save();
            return {
                ...this.songs[this.currentIndex],
                artwork: this.artworkCache[this.songs[this.currentIndex].id]
            };
        }
        return null;
    }

    async fetchNewSong() {
        try {
            const response = await fetch('/stream/random-song');
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching new song:', error);
            return null;
        }
    }

    save() {
        localStorage.setItem('songStore', JSON.stringify(this.songs));
        localStorage.setItem('currentSongIndex', this.currentIndex.toString());
        localStorage.setItem('artworkCache', JSON.stringify(this.artworkCache));
    }

    getCurrentSong() {
        if (this.currentIndex >= 0) {
            const song = this.songs[this.currentIndex];
            return {
                ...song,
                artwork: this.artworkCache[song.id]
            };
        }
        return null;
    }

    getArtwork(songId) {
        return this.artworkCache[songId];
    }
}

const songStore = new SongStore();

// Audio Control Functions
async function initAudio() {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    analyzerNode = audioContext.createAnalyser();
    analyzerNode.fftSize = 256;
    analyzerNode.connect(audioContext.destination);
}

function formatTime(time) {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60).toString().padStart(2, '0');
    return `${minutes}:${seconds}`;
}

async function fetchAudio(url) {
    isLoading = true;
    updateControls();
    try {
        const response = await fetch(url);
        const arrayBuffer = await response.arrayBuffer();
        audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
        elements.timeTotal.textContent = formatTime(audioBuffer.duration);
        isLoading = false;
        updateControls();
    } catch (error) {
        console.error('Error loading audio:', error);
        isLoading = false;
        updateControls();
    }
}

function playAudio(offset = 0) {
    if (!audioBuffer) return;
    if (isPlaying) stopAudio();

    offset = Math.min(Math.max(0, offset), audioBuffer.duration);

    sourceNode = audioContext.createBufferSource();
    sourceNode.buffer = audioBuffer;
    sourceNode.connect(analyzerNode);

    sourceNode.onended = async () => {
        const currentTime = audioContext.currentTime - startTime;
        if (currentTime >= audioBuffer.duration - 0.1) {
            await loadNewSong(true, 'next');
        }
    };

    sourceNode.start(0, offset);
    startTime = audioContext.currentTime - offset;
    isPlaying = true;
    updateUI();
}

function stopAudio() {
    if (sourceNode) {
        sourceNode.stop();
        sourceNode = null;
        isPlaying = false;
        updateUI();
    }
}

function seekAudio(time) {
    if (!audioBuffer) return;
    const wasPlaying = isPlaying;
    stopAudio();
    pauseTime = time;
    if (wasPlaying) {
        playAudio(pauseTime);
    }
    drawSeekbar();
    savePlaybackState();
}

// UI Update Functions
function updateUI() {
    elements.playButton.innerHTML = isPlaying ? "&#10074;&#10074;" : "&#9658;";
    drawVisualizer();
    updateTimeDisplay();
    drawSeekbar();
}

function updateControls() {
    elements.playButton.disabled = isLoading;
    elements.prevButton.disabled = isLoading;
    elements.nextButton.disabled = isLoading;
    if (isLoading) stopAudio();
}

function updateSongInfo() {
    if (currentSong) {
        elements.songTitle.textContent = currentSong.title;
        elements.songArtistAlbum.textContent = `${currentSong.artist} - ${currentSong.album}`;
        // Always update artwork with the cached version or generate new
        elements.songCover.src = currentSong.artwork || songStore.getArtwork(currentSong.id);
    }
}

// Canvas Drawing Functions
function drawSeekbar() {
    if (!audioBuffer) return;

    const ctx = seekbarCanvas.getContext('2d');
    const { width, height } = seekbarCanvas;
    const centerY = height / 2;

    ctx.clearRect(0, 0, width, height);

    // Background bar
    ctx.fillStyle = SEEKBAR_CONFIG.COLORS.BASE;
    ctx.fillRect(0, centerY - SEEKBAR_CONFIG.HEIGHT / 2, width, SEEKBAR_CONFIG.HEIGHT);

    // Progress bar
    const currentTime = isPlaying ? audioContext.currentTime - startTime : pauseTime;
    const progress = (currentTime / audioBuffer.duration) * width;

    ctx.fillStyle = SEEKBAR_CONFIG.COLORS.PROGRESS;
    ctx.fillRect(0, centerY - SEEKBAR_CONFIG.HEIGHT / 2, progress, SEEKBAR_CONFIG.HEIGHT);

    // Thumb
    ctx.beginPath();
    ctx.arc(progress, centerY, SEEKBAR_CONFIG.THUMB_RADIUS, 0, Math.PI * 2);
    ctx.fill();
}

function drawVisualizer() {
    if (!isPlaying) return;

    const ctx = elements.visualizer.getContext('2d');
    const bufferLength = analyzerNode.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    function animate() {
        if (!isPlaying) return;
        requestAnimationFrame(animate);

        analyzerNode.getByteFrequencyData(dataArray);
        ctx.clearRect(0, 0, elements.visualizer.width, elements.visualizer.height);

        const barWidth = (elements.visualizer.width / bufferLength) * 2.5;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
            const barHeight = (dataArray[i] / 255) * elements.visualizer.height;
            ctx.fillStyle = `rgb(${dataArray[i]}, 50, 255)`;
            ctx.fillRect(x, elements.visualizer.height - barHeight, barWidth, barHeight);
            x += barWidth + 1;
        }
    }

    animate();
}

// State Management Functions
function savePlaybackState() {
    if (!currentSong) return;

    const currentTime = isPlaying ? audioContext.currentTime - startTime : pauseTime;
    const state = {
        songId: currentSong.id,
        timeStamp: Math.min(currentTime, audioBuffer?.duration || 0),
        isPlaying,
        artwork: elements.songCover.src,
        songTitle: currentSong.title,
        songArtist: currentSong.artist,
        songAlbum: currentSong.album
    };

    localStorage.setItem('playbackState', JSON.stringify(state));
}

// Song Loading and Navigation
async function loadNewSong(autoplay = false, direction = 'next') {
    try {
        const wasPlaying = isPlaying || autoplay;
        stopAudio();

        let nextSong;
        if (direction === 'next') {
            nextSong = await songStore.getNext();
        } else {
            nextSong = await songStore.getPrevious();
            if (!nextSong) return; // Don't proceed if no previous song
        }

        currentSong = nextSong;
        updateSongInfo(); // This will now use the cached artwork

        await fetchAudio(`/stream/song/${currentSong.id}`);
        pauseTime = 0; // Reset seek position for new song

        if (wasPlaying) {
            playAudio(0);
        }

        savePlaybackState();
    } catch (error) {
        console.error('Error loading song:', error);
    }
}

function getCurrentScale() {
    const screenWidth = window.innerWidth;
    return screenWidth <= MIN_SCREEN_WIDTH ? 1 : screenWidth / MIN_SCREEN_WIDTH;
}

// Event Listeners
function setupEventListeners() {
    seekbarCanvas.addEventListener('mousedown', (e) => {
        isDragging = true;
        const scale = getCurrentScale();
        const rect = seekbarCanvas.getBoundingClientRect();
        // Adjust position calculation for scale
        const position = Math.max(0, Math.min((e.clientX - rect.left) / scale, seekbarCanvas.width));
        handleSeek(position);
    });

    seekbarCanvas.addEventListener('mousemove', (e) => {
        if (isDragging) {
            const scale = getCurrentScale();
            const rect = seekbarCanvas.getBoundingClientRect();
            // Adjust position calculation for scale
            const position = Math.max(0, Math.min((e.clientX - rect.left) / scale, seekbarCanvas.width));
            handleSeek(position);
        }
    });

    seekbarCanvas.addEventListener('mouseup', () => isDragging = false);
    seekbarCanvas.addEventListener('mouseleave', () => isDragging = false);
    document.addEventListener('mouseup', () => isDragging = false);

    // Rest of the event listeners remain the same...
    elements.playButton.addEventListener('click', () => {
        if (isLoading) return;
        if (isPlaying) {
            stopAudio();
            pauseTime = audioContext.currentTime - startTime;
        } else {
            playAudio(pauseTime);
        }
        savePlaybackState();
    });

    elements.prevButton.addEventListener('click', () => loadNewSong(isPlaying, 'previous'));
    elements.nextButton.addEventListener('click', () => loadNewSong(isPlaying, 'next'));

    elements.songCover.addEventListener('error', () => {
        elements.songCover.src = songStore.getArtwork(currentSong.id);
        savePlaybackState();
    });

    document.addEventListener('visibilitychange', savePlaybackState);
    window.addEventListener('beforeunload', savePlaybackState);
}

function handleSeek(position) {
    if (!audioBuffer) return;
    const seekTime = (position / seekbarCanvas.width) * audioBuffer.duration;
    seekAudio(seekTime);
}

function updateTimeDisplay() {
    if (!audioBuffer) return;
    const currentTime = isPlaying ? audioContext.currentTime - startTime : pauseTime;
    elements.timeElapsed.textContent = formatTime(currentTime);
    elements.timeTotal.textContent = formatTime(audioBuffer.duration);
}

// Main update loop
function update() {
    if (audioBuffer && isPlaying) {
        const currentTime = audioContext.currentTime - startTime;
        if (currentTime >= audioBuffer.duration) {
            loadNewSong(true, 'next');
            return;
        }
    }

    updateTimeDisplay();
    drawSeekbar();
    requestAnimationFrame(update);
}

// Initialization
async function init() {
    await initAudio();
    setupEventListeners();

    try {
        const savedState = localStorage.getItem('playbackState');
        if (savedState) {
            const state = JSON.parse(savedState);
            currentSong = {
                id: state.songId,
                title: state.songTitle,
                artist: state.songArtist,
                album: state.songAlbum,
                artwork: state.artwork
            };

            updateSongInfo();
            await fetchAudio(`/stream/song/${state.songId}`);
            pauseTime = state.timeStamp || 0;

            if (state.isPlaying) {
                setTimeout(() => playAudio(pauseTime), 100);
            } else {
                drawSeekbar();
                updateTimeDisplay();
            }
        } else {
            await loadNewSong(false);
        }
    } catch (error) {
        console.error('Error restoring state:', error);
        await loadNewSong(false);
    }

    setInterval(savePlaybackState, 500);
    update();
}

init();
