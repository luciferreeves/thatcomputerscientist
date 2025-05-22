/**
 * Original source: https://shi.foo/static/js/shared/kawaiiBeatsPlayer.js
 * Credit must be given if this code is used in any way
 * @fileoverview Audio player implementation with artwork management and persistent state
 * @version 1.0.0
 */

/**
 * @typedef {Object} Song
 * @property {string} id - Unique identifier for the song (spotify_id)
 * @property {string} title - Song title
 * @property {string} artist - Artist name
 * @property {string} album - Album name
 * @property {string} [album_art_url] - URL to album artwork image
 * @property {string} [custom_album_art] - URL to custom album artwork image
 * @property {string} [streaming_url] - URL to the audio stream
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
const STORE_LIMIT = 20;
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
 * Manages song queue and persistence
 */
class SongStore {
    /**
     * @param {number} limit - Maximum number of songs to store
     */
    constructor(limit) {
        this.limit = limit;
        this.songs = JSON.parse(localStorage.getItem('songStore')) || [];
        this.currentIndex = parseInt(localStorage.getItem('currentSongIndex')) || -1;
    }

    /**
     * @param {Song} song - Song to add to store
     * @returns {Promise<Song|null>} Added song with artwork
     */
    async addSong(song) {
        if (!song) return null;

        this.songs.push({
            id: song.spotify_id,
            spotify_id: song.spotify_id,
            title: song.title,
            artist: song.artist,
            album: song.album,
            album_art_url: song.album_art_url,
            custom_album_art: song.custom_album_art,
            streaming_url: song.streaming_url
        });

        if (this.songs.length > this.limit) {
            this.songs.shift();
            if (this.currentIndex > -1) this.currentIndex--;
        }

        this.currentIndex = this.songs.length - 1;
        this.save();

        return song;
    }

    /**
     * @param {string} [serverURL=''] - Base URL for server requests
     * @returns {Promise<Song|null>} Next song in queue or new song
     */
    async getNext(serverURL = '') {
        if (this.currentIndex < this.songs.length - 1) {
            this.currentIndex++;
            this.save();
            return this.songs[this.currentIndex];
        }
        const nextSongId = this.songs[this.currentIndex]?.id;
        const newSong = await this._fetchSong(nextSongId, serverURL);
        return this.addSong(newSong);
    }

    /**
     * @returns {Promise<Song|null>} Previous song in queue
     */
    async getPrevious() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.save();
            return this.songs[this.currentIndex];
        }
        return null;
    }

    /**
     * @private
     * @param {string} [nextSongId] - ID of current song for continuity
     * @returns {Promise<Song|null>} Fetched song data
     */    /**
* @private
* @param {string} [nextSongId] - ID of current song for continuity
* @param {string} [serverURL=''] - Base URL for server requests
* @returns {Promise<Song|null>} Fetched song data
*/
    async _fetchSong(nextSongId = null, serverURL = '') {
        try {
            const endpoint = nextSongId ?
                `${serverURL}/services/kawaiibeats?next=${nextSongId}` :
                `${serverURL}/services/kawaiibeats`;
            const response = await fetch(endpoint);
            const song = await response.json();

            if (song && song.spotify_id && !song.id) {
                song.id = song.spotify_id;
            }

            return song;
        } catch (error) {
            console.error('Error fetching song:', error);
            return null;
        }
    }

    getCurrentSong() {
        return this.currentIndex >= 0 ? this.songs[this.currentIndex] : null;
    }

    getArtwork(songId) {
        const song = this.songs.find(s => s.id === songId);
        return song ? (song.custom_album_art || song.album_art_url) : null;
    }

    save() {
        localStorage.setItem('songStore', JSON.stringify(this.songs));
        localStorage.setItem('currentSongIndex', this.currentIndex.toString());
    }
}

/**
 * @typedef {Object} PlayerConfig
 * @property {number} [storeLimit=20] - Maximum number of songs to store
 * @property {string} [serverURL=''] - Base URL for server requests
 */

/**
 * Manages audio playback and visualization
 */
class AudioPlayer {
    /**
     * @param {UIElements} elements - DOM elements
     * @param {PlayerConfig} [config={}] - Configuration options
     */
    constructor(elements, config = {}) {
        this.elements = elements;
        this.config = {
            storeLimit: config.storeLimit || STORE_LIMIT,
            serverURL: config.serverURL || 'https://shi.foo'
        };
        this.songStore = new SongStore(this.config.storeLimit);
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
                this.currentSong.custom_album_art || this.currentSong.album_art_url || '';
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
            spotify_id: this.currentSong.spotify_id || this.currentSong.id,
            timeStamp: Math.min(currentTime, this.audioBuffer?.duration || 0),
            isPlaying: this.isPlaying,
            album_art_url: this.currentSong.album_art_url,
            custom_album_art: this.currentSong.custom_album_art,
            streaming_url: this.currentSong.streaming_url,
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
                await this.songStore.getNext(this.config.serverURL) :
                await this.songStore.getPrevious();

            if (!nextSong && direction === 'previous') return;

            this.currentSong = nextSong;
            this.updateSongInfo();

            await this.loadAudio(this.currentSong.streaming_url);
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
            if (this.currentSong.custom_album_art && this.elements.songCover.src !== this.currentSong.custom_album_art) {
                this.elements.songCover.src = this.currentSong.custom_album_art;
            } else if (this.currentSong.album_art_url && this.elements.songCover.src !== this.currentSong.album_art_url) {
                this.elements.songCover.src = this.currentSong.album_art_url;
            }
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
                    spotify_id: state.songId, // Use songId as spotify_id for consistency
                    title: state.songTitle,
                    artist: state.songArtist,
                    album: state.songAlbum,
                    album_art_url: state.album_art_url,
                    custom_album_art: state.custom_album_art,
                    streaming_url: state.streaming_url
                };

                this.updateSongInfo();
                await this.loadAudio(state.streaming_url);
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
