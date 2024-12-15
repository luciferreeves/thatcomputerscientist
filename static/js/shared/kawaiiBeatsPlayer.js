/**
 * Original source: https://shi.foo/static/js/shared/kawaiiBeatsPlayer.js
 * Credit must be given if this code is used in any way
 * @fileoverview Audio player implementation with artwork management and persistent state
 * @version 1.0.0
 */
/** @type {string[]} Artwork collection for random assignment */
const artworkCollection = [
    "https://i.pinimg.com/enabled/564x/e2/5d/31/e25d3199f73c9453035727f8c7a70170.jpg",
    "https://i.pinimg.com/enabled/564x/5f/ed/28/5fed282cff8d22ac857e2a489031d05a.jpg",
    "https://i.pinimg.com/736x/05/a8/71/05a87162a78e2cad2ffe0a9eac6b4e2c.jpg",
    "https://i.pinimg.com/736x/c6/ac/13/c6ac139ed02c9accd34dbb16d7466025.jpg",
    "https://i.pinimg.com/736x/72/69/c3/7269c3d939764b024da9a6869dc59a0f.jpg",
    "https://i.pinimg.com/enabled/564x/cc/5c/6f/cc5c6f1c8e053d791ae2b4300ef5c9fe.jpg",
    "https://i.pinimg.com/enabled/564x/fa/0a/c2/fa0ac2b7145af1205c87350f7c735683.jpg",
    "https://i.pinimg.com/enabled/564x/94/84/57/9484579fcbf7e768d6206b07fa44c2b9.jpg",
    "https://i.pinimg.com/enabled/564x/fd/30/bf/fd30bf62f6409129ce6538f1b9ed7b8b.jpg",
    "https://i.pinimg.com/enabled/564x/44/b2/11/44b21104b4e41736c99ee183127aab3d.jpg",
    "https://i.pinimg.com/enabled/564x/f7/ce/56/f7ce5629aa91866020a559ef7e249f1c.jpg",
    "https://i.pinimg.com/enabled/564x/7b/ac/36/7bac368ff9b5f702d9b727491f8d4ef0.jpg",
    "https://i.pinimg.com/enabled/564x/39/1a/51/391a514a013f62ca9f25f47b4cbd7776.jpg",
    "https://i.pinimg.com/enabled/564x/03/d2/96/03d2967de5d249f88155cab461e69f3a.jpg",
];

/**
 * @typedef {Object} Song
 * @property {string} id - Unique identifier for the song
 * @property {string} title - Song title
 * @property {string} artist - Artist name
 * @property {string} album - Album name
 * @property {string} [artwork] - URL to artwork image
 */

/**
 * @typedef {Object} UIElements
 * @property {HTMLElement} playButton - Play/pause button
 * @property {HTMLElement} prevButton - Previous track button
 * @property {HTMLElement} nextButton - Next track button
 * @property {HTMLElement} timeElapsed - Time elapsed display
 * @property {HTMLElement} timeTotal - Total time display
 * @property {HTMLElement} songCover - Album artwork
 * @property {HTMLElement} songTitle - Song title display
 * @property {HTMLElement} songArtistAlbum - Artist and album display
 * @property {HTMLCanvasElement} visualizer - Audio visualizer canvas
 */

// Configuration
const STORE_LIMIT = artworkCollection.length;
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

/**
 * Manages artwork selection and rotation for songs
 */
class ArtworkManager {
    /**
     * @param {string[]} artworkCollection - Collection of artwork URLs
     */
    constructor(artworkCollection) {
        this.collection = artworkCollection;
        this.usedArtwork = new Set();
        this.availableArtwork = [...artworkCollection];
    }

    /**
     * @returns {string} Random unused artwork URL
     */
    getRandomArtwork() {
        if (this.availableArtwork.length === 0) {
            this.resetArtworkPool();
        }
        const randomIndex = Math.floor(Math.random() * this.availableArtwork.length);
        const artwork = this.availableArtwork[randomIndex];
        this.availableArtwork.splice(randomIndex, 1);
        this.usedArtwork.add(artwork);
        return artwork;
    }

    resetArtworkPool() {
        this.availableArtwork = [...this.collection];
        this.usedArtwork.clear();
    }

    /**
     * @param {string} artwork - Artwork URL to release back to pool
     */
    releaseArtwork(artwork) {
        if (this.usedArtwork.has(artwork)) {
            this.usedArtwork.delete(artwork);
            this.availableArtwork.push(artwork);
        }
    }
}

/**
 * Manages song queue and persistence
 */
class SongStore {
    /**
     * @param {number} limit - Maximum number of songs to store
     * @param {ArtworkManager} artworkManager - Artwork management instance
     */
    constructor(limit, artworkManager) {
        this.limit = limit;
        this.artworkManager = artworkManager;
        this.songs = JSON.parse(localStorage.getItem('songStore')) || [];
        this.currentIndex = parseInt(localStorage.getItem('currentSongIndex')) || -1;
        this.artworkCache = JSON.parse(localStorage.getItem('artworkCache')) || {};

        // Restore artwork state
        Object.values(this.artworkCache).forEach(artwork => {
            this.artworkManager.usedArtwork.add(artwork);
        });
        this.artworkManager.availableArtwork = this.artworkManager.availableArtwork
            .filter(artwork => !this.artworkManager.usedArtwork.has(artwork));
    }

    /**
     * @param {Song} song - Song to add to store
     * @returns {Promise<Song|null>} Added song with artwork
     */
    async addSong(song) {
        if (!song) return null;

        const artwork = this.artworkManager.getRandomArtwork();
        this.artworkCache[song.id] = artwork;

        this.songs.push({
            id: song.id,
            title: song.title,
            artist: song.artist,
            album: song.album
        });

        if (this.songs.length > this.limit) {
            const removedSong = this.songs.shift();
            const removedArtwork = this.artworkCache[removedSong.id];
            this.artworkManager.releaseArtwork(removedArtwork);
            delete this.artworkCache[removedSong.id];
            if (this.currentIndex > -1) this.currentIndex--;
        }

        this.currentIndex = this.songs.length - 1;
        this.save();

        return { ...song, artwork };
    }

    /**
     * @returns {Promise<Song|null>} Next song in queue or new song
     */
    async getNext() {
        if (this.currentIndex < this.songs.length - 1) {
            this.currentIndex++;
            this.save();
            return this._getSongWithArtwork(this.currentIndex);
        }
        const nextSongId = this.songs[this.currentIndex]?.id;
        const newSong = await this._fetchSong(nextSongId);
        return this.addSong(newSong);
    }

    /**
     * @returns {Promise<Song|null>} Previous song in queue
     */
    async getPrevious() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.save();
            return this._getSongWithArtwork(this.currentIndex);
        }
        return null;
    }

    /**
     * @private
     * @param {string} [nextSongId] - ID of current song for continuity
     * @returns {Promise<Song|null>} Fetched song data
     */
    async _fetchSong(nextSongId = null) {
        try {
            const url = nextSongId ?
                `/services/stream/random-song?next=${nextSongId}` :
                '/services/stream/random-song';
            const response = await fetch(url);
            return await response.json();
        } catch (error) {
            console.error('Error fetching song:', error);
            return null;
        }
    }

    /**
     * @private
     * @param {number} index - Index of song to retrieve
     * @returns {Song|null} Song with artwork
     */
    _getSongWithArtwork(index) {
        const song = this.songs[index];
        return song ? { ...song, artwork: this.artworkCache[song.id] } : null;
    }

    getCurrentSong() {
        return this.currentIndex >= 0 ? this._getSongWithArtwork(this.currentIndex) : null;
    }

    getArtwork(songId) {
        return this.artworkCache[songId];
    }

    save() {
        localStorage.setItem('songStore', JSON.stringify(this.songs));
        localStorage.setItem('currentSongIndex', this.currentIndex.toString());
        localStorage.setItem('artworkCache', JSON.stringify(this.artworkCache));
    }
}

/**
 * Manages audio playback and visualization
 */
class AudioPlayer {
    /**
     * @param {UIElements} elements - DOM elements
     * @param {SongStore} songStore - Song management instance
     */
    constructor(elements, songStore) {
        this.elements = elements;
        this.songStore = songStore;
        this.audioContext = null;
        this.sourceNode = null;
        this.analyzerNode = null;
        this.audioBuffer = null;
        this.startTime = 0;
        this.pauseTime = 0;
        this.isPlaying = false;
        this.isLoading = true;
        this.isDragging = false;
        this.currentSong = null;

        this.setupSeekbar();
        this.bindMethods();
    }

    /**
     * @private
     */
    setupSeekbar() {
        this.seekbarCanvas = document.createElement('canvas');
        this.seekbarCanvas.id = 'custom-seekbar';
        this.seekbarCanvas.width = 140;
        this.seekbarCanvas.height = 20;
        this.seekbarCanvas.style.cssText = 'position: absolute; left: 30px; top: 220px; cursor: pointer; z-index: 1;';
        document.getElementById('song-time').parentNode.insertBefore(
            this.seekbarCanvas,
            document.getElementById('song-time')
        );
    }

    /**
     * @private
     */
    bindMethods() {
        this.handleSeek = (position) => {
            if (!this.audioBuffer) return;
            const seekTime = (position / this.seekbarCanvas.width) * this.audioBuffer.duration;
            this.seek(seekTime);
        };

        this.handlePlayPause = () => {
            if (this.isLoading) return;
            if (this.isPlaying) {
                this.stop();
                this.pauseTime = this.audioContext.currentTime - this.startTime;
            } else {
                this.play(this.pauseTime);
            }
            this.saveState();
        };

        this.handlePrevious = () => this.loadNewSong(this.isPlaying, 'previous');
        this.handleNext = () => this.loadNewSong(this.isPlaying, 'next');

        this.handleVisibilityChange = () => {
            if (document.hidden) {
                this.saveState();
            }
        };

        this.handleBeforeUnload = () => {
            this.saveState();
        };

        this.update = () => {
            if (this.audioBuffer && this.isPlaying) {
                const currentTime = this.audioContext.currentTime - this.startTime;
                if (currentTime >= this.audioBuffer.duration) {
                    this.loadNewSong(true, 'next');
                    return;
                }
            }
            this.updateTimeDisplay();
            this.drawSeekbar();
            requestAnimationFrame(this.update);
        };
    }

    /**
     * Initializes audio context and event listeners
     */
    async init() {
        await this.initAudioContext();
        this.setupEventListeners();
        await this.restoreState();
        setInterval(() => this.saveState(), 500);
        requestAnimationFrame(this.update);
    }

    /**
     * @private
     */
    async initAudioContext() {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        this.analyzerNode = this.audioContext.createAnalyser();
        this.analyzerNode.fftSize = 256;
        this.analyzerNode.connect(this.audioContext.destination);
    }

    /**
     * @private
     * @param {string} url - Audio file URL
     */
    async loadAudio(url) {
        this.isLoading = true;
        this.updateControls();
        try {
            const response = await fetch(url);
            const arrayBuffer = await response.arrayBuffer();
            this.audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
            this.elements.timeTotal.textContent = this.formatTime(this.audioBuffer.duration);
        } catch (error) {
            console.error('Error loading audio:', error);
        } finally {
            this.isLoading = false;
            this.updateControls();
        }
    }

    /**
     * @private
     * @param {number} [offset=0] - Start offset in seconds
     */
    play(offset = 0) {
        if (!this.audioBuffer) return;
        if (this.isPlaying) this.stop();

        offset = Math.min(Math.max(0, offset), this.audioBuffer.duration);

        this.sourceNode = this.audioContext.createBufferSource();
        this.sourceNode.buffer = this.audioBuffer;
        this.sourceNode.connect(this.analyzerNode);

        this.sourceNode.onended = async () => {
            const currentTime = this.audioContext.currentTime - this.startTime;
            if (currentTime >= this.audioBuffer.duration - 0.1) {
                await this.loadNewSong(true, 'next');
            }
        };

        this.sourceNode.start(0, offset);
        this.startTime = this.audioContext.currentTime - offset;
        this.isPlaying = true;
        this.updateUI();
    }

    /**
     * Stops audio playback
     * @private
     */
    stop() {
        if (this.sourceNode) {
            this.sourceNode.stop();
            this.sourceNode = null;
            this.isPlaying = false;
            this.updateUI();
        }
    }

    /**
     * Seeks to specific time in audio
     * @private
     * @param {number} time - Time in seconds to seek to
     */
    seek(time) {
        if (!this.audioBuffer) return;
        const wasPlaying = this.isPlaying;
        this.stop();
        this.pauseTime = time;
        if (wasPlaying) {
            this.play(this.pauseTime);
        }
        this.drawSeekbar();
        this.saveState();
    }

    /**
     * Updates all UI elements
     * @private
     */
    updateUI() {
        this.elements.playButton.innerHTML = this.isPlaying ? "&#10074;&#10074;" : "&#9658;";
        this.drawVisualizer();
        this.updateTimeDisplay();
        this.drawSeekbar();
    }

    /**
     * Updates control button states
     * @private
     */
    updateControls() {
        this.elements.playButton.disabled = this.isLoading;
        this.elements.prevButton.disabled = this.isLoading;
        this.elements.nextButton.disabled = this.isLoading;
        if (this.isLoading) this.stop();
    }

    /**
     * Updates song information display
     * @private
     */
    updateSongInfo() {
        if (this.currentSong) {
            this.elements.songTitle.textContent = this.currentSong.title;
            this.elements.songArtistAlbum.textContent =
                `${this.currentSong.artist} - ${this.currentSong.album}`;
            this.elements.songCover.src =
                this.currentSong.artwork || this.songStore.getArtwork(this.currentSong.id);
        }
    }

    /**
     * Draws seekbar with current progress
     * @private
     */
    drawSeekbar() {
        if (!this.audioBuffer) return;

        const ctx = this.seekbarCanvas.getContext('2d');
        const { width, height } = this.seekbarCanvas;
        const centerY = height / 2;

        ctx.clearRect(0, 0, width, height);

        // Background bar
        ctx.fillStyle = SEEKBAR_CONFIG.COLORS.BASE;
        ctx.fillRect(0, centerY - SEEKBAR_CONFIG.HEIGHT / 2, width, SEEKBAR_CONFIG.HEIGHT);

        // Progress bar
        const currentTime = this.isPlaying ?
            this.audioContext.currentTime - this.startTime : this.pauseTime;
        const progress = (currentTime / this.audioBuffer.duration) * width;

        ctx.fillStyle = SEEKBAR_CONFIG.COLORS.PROGRESS;
        ctx.fillRect(0, centerY - SEEKBAR_CONFIG.HEIGHT / 2, progress, SEEKBAR_CONFIG.HEIGHT);

        // Thumb
        ctx.beginPath();
        ctx.arc(progress, centerY, SEEKBAR_CONFIG.THUMB_RADIUS, 0, Math.PI * 2);
        ctx.fill();
    }

    /**
     * Draws audio visualization
     * @private
     */
    drawVisualizer() {
        if (!this.isPlaying) return;

        const ctx = this.elements.visualizer.getContext('2d');
        const bufferLength = this.analyzerNode.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const animate = () => {
            if (!this.isPlaying) return;
            requestAnimationFrame(animate);

            this.analyzerNode.getByteFrequencyData(dataArray);
            ctx.clearRect(0, 0, this.elements.visualizer.width, this.elements.visualizer.height);

            const barWidth = (this.elements.visualizer.width / bufferLength) * 2.5;
            let x = 0;

            for (let i = 0; i < bufferLength; i++) {
                const barHeight = (dataArray[i] / 255) * this.elements.visualizer.height;
                ctx.fillStyle = `rgb(${dataArray[i]}, 50, 255)`;
                ctx.fillRect(x, this.elements.visualizer.height - barHeight, barWidth, barHeight);
                x += barWidth + 1;
            }
        };

        animate();
    }

    /**
     * Saves current playback state
     * @private
     */
    saveState() {
        if (!this.currentSong) return;

        const currentTime = this.isPlaying ?
            this.audioContext.currentTime - this.startTime : this.pauseTime;
        const state = {
            songId: this.currentSong.id,
            timeStamp: Math.min(currentTime, this.audioBuffer?.duration || 0),
            isPlaying: this.isPlaying,
            artwork: this.elements.songCover.src,
            songTitle: this.currentSong.title,
            songArtist: this.currentSong.artist,
            songAlbum: this.currentSong.album
        };

        localStorage.setItem('playbackState', JSON.stringify(state));
    }

    /**
     * Loads and plays a new song
     * @private
     * @param {boolean} autoplay - Whether to start playing immediately
     * @param {'next'|'previous'} direction - Direction to load song from
     */
    async loadNewSong(autoplay = false, direction = 'next') {
        try {
            const wasPlaying = this.isPlaying || autoplay;
            this.stop();

            const nextSong = direction === 'next' ?
                await this.songStore.getNext() :
                await this.songStore.getPrevious();

            if (!nextSong && direction === 'previous') return;

            this.currentSong = nextSong;
            this.updateSongInfo();

            await this.loadAudio(`/services/stream/song/${this.currentSong.id}`);
            this.pauseTime = 0;

            if (wasPlaying) {
                this.play(0);
            }

            this.saveState();
        } catch (error) {
            console.error('Error loading song:', error);
        }
    }

    /**
     * Sets up all event listeners
     * @private
     */
    setupEventListeners() {
        this.seekbarCanvas.addEventListener('mousedown', (e) => {
            this.isDragging = true;
            const rect = this.seekbarCanvas.getBoundingClientRect();
            const position = Math.max(0, Math.min((e.clientX - rect.left), this.seekbarCanvas.width));
            this.handleSeek(position);
        });

        this.seekbarCanvas.addEventListener('mousemove', (e) => {
            if (this.isDragging) {
                const rect = this.seekbarCanvas.getBoundingClientRect();
                const position = Math.max(0, Math.min((e.clientX - rect.left), this.seekbarCanvas.width));
                this.handleSeek(position);
            }
        });

        this.seekbarCanvas.addEventListener('mouseup', () => this.isDragging = false);
        this.seekbarCanvas.addEventListener('mouseleave', () => this.isDragging = false);
        document.addEventListener('mouseup', () => this.isDragging = false);

        this.elements.playButton.addEventListener('click', this.handlePlayPause);
        this.elements.prevButton.addEventListener('click', () => this.loadNewSong(this.isPlaying, 'previous'));
        this.elements.nextButton.addEventListener('click', () => this.loadNewSong(this.isPlaying, 'next'));

        this.elements.songCover.addEventListener('error', () => {
            this.elements.songCover.src = this.songStore.getArtwork(this.currentSong.id);
            this.saveState();
        });

        document.addEventListener('visibilitychange', this.handleVisibilityChange);
        window.addEventListener('beforeunload', this.handleBeforeUnload);
    }

    /**
     * Handles seek bar interaction
     * @private
     * @param {number} position - Position in pixels on seekbar
     */
    handleSeek(position) {
        if (!this.audioBuffer) return;
        const seekTime = (position / this.seekbarCanvas.width) * this.audioBuffer.duration;
        this.seek(seekTime);
    }

    /**
     * Handles play/pause button click
     * @private
     */
    handlePlayPause() {
        if (this.isLoading) return;
        if (this.isPlaying) {
            this.stop();
            this.pauseTime = this.audioContext.currentTime - this.startTime;
        } else {
            this.play(this.pauseTime);
        }
        this.saveState();
    }

    /**
     * Handles visibility change
     * @private
     */
    handleVisibilityChange() {
        if (document.hidden) {
            this.saveState();
        }
    }

    /**
     * Handles page unload
     * @private
     */
    handleBeforeUnload() {
        this.saveState();
    }

    /**
     * Updates time display
     * @private
     */
    updateTimeDisplay() {
        if (!this.audioBuffer) return;
        const currentTime = this.isPlaying ?
            this.audioContext.currentTime - this.startTime : this.pauseTime;
        this.elements.timeElapsed.textContent = this.formatTime(currentTime);
        this.elements.timeTotal.textContent = this.formatTime(this.audioBuffer.duration);
    }

    /**
     * Formats time in seconds to MM:SS format
     * @private
     * @param {number} time - Time in seconds
     * @returns {string} Formatted time string
     */
    formatTime(time) {
        const minutes = Math.floor(time / 60);
        const seconds = Math.floor(time % 60).toString().padStart(2, '0');
        return `${minutes}:${seconds}`;
    }

    /**
     * Main update loop
     * @private
     */
    update() {
        if (this.audioBuffer && this.isPlaying) {
            const currentTime = this.audioContext.currentTime - this.startTime;
            if (currentTime >= this.audioBuffer.duration) {
                this.loadNewSong(true, 'next');
                return;
            }
        }

        this.updateTimeDisplay();
        this.drawSeekbar();
        requestAnimationFrame(this.update);
    }

    /**
     * Restores previous playback state
     * @private
     */
    async restoreState() {
        try {
            const savedState = localStorage.getItem('playbackState');
            if (savedState) {
                const state = JSON.parse(savedState);
                this.currentSong = {
                    id: state.songId,
                    title: state.songTitle,
                    artist: state.songArtist,
                    album: state.songAlbum,
                    artwork: state.artwork
                };

                this.updateSongInfo();
                await this.loadAudio(`/services/stream/song/${state.songId}`);
                this.pauseTime = state.timeStamp || 0;

                if (state.isPlaying) {
                    setTimeout(() => this.play(this.pauseTime), 100);
                } else {
                    this.drawSeekbar();
                    this.updateTimeDisplay();
                }
            } else {
                await this.loadNewSong(false);
            }
        } catch (error) {
            console.error('Error restoring state:', error);
            await this.loadNewSong(false);
        }
    }
}

// Initialize player
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

const artworkManager = new ArtworkManager(artworkCollection);
const songStore = new SongStore(STORE_LIMIT, artworkManager);
const player = new AudioPlayer(elements, songStore);
player.init();
