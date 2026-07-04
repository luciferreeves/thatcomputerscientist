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
    THUMB_RADIUS: 5,
    HOVER_RADIUS: 7,
    COLORS: {
        BASE: '#333',
        PROGRESS: '#ff3333',
        GROOVE: '#111',
        THUMB: '#666',
        THUMB_INNER: '#999'
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
                `${serverURL}/api/kawaiibeats/random?next=${nextSongId}` :
                `${serverURL}/api/kawaiibeats/random`;
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
        this.gainNode = null;
        this.audio = new Audio();
        this.audio.crossOrigin = 'anonymous';
        this.audio.preload = 'auto';
        this.isPlaying = false;
        this.isLoading = true;
        this.isDragging = false;
        this.currentSong = null;
        this.volumeDial = document.querySelector('.volume-dial');
        this.dialIndicator = document.querySelector('.dial-indicator');
        this.volumeLevel = parseInt(localStorage.getItem('volumeLevel')) || 3;
        this.volume = this.volumeLevel / 6;

        this.setupSeekbar();
        this.bindMethods();
        this.setupVolumeControl();
    }

    /**
     * @private
     */
    setupSeekbar() {
        this.seekbarCanvas = document.createElement('canvas');
        this.seekbarCanvas.id = 'custom-seekbar';
        this.seekbarCanvas.width = 140;
        this.seekbarCanvas.height = 16;
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
            if (!this.audio.duration) return;
            const seekTime = (position / this.seekbarCanvas.width) * this.audio.duration;
            this.seek(seekTime);
        };

        this.handlePlayPause = () => {
            if (this.isLoading) return;
            if (this.isPlaying) {
                this.audio.pause();
                this.isPlaying = false;
                this.updateUI();
            } else {
                this.play(this.audio.currentTime);
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
            this.updateTimeDisplay();
            this.drawSeekbar();
            requestAnimationFrame(this.update);
        };
    }

    /**
     * @private
     */
    setupVolumeControl() {
        this.updateDialPosition();
        let lastLevel = this.volumeLevel;

        const handleVolumeChange = (e) => {
            const rect = this.volumeDial.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;

            // Calculate angle from center
            const deltaX = e.clientX - centerX;
            const deltaY = e.clientY - centerY;
            let angle = Math.atan2(deltaX, -deltaY) * (180 / Math.PI);

            // Normalize to -180 to 180
            while (angle < -180) angle += 360;
            while (angle > 180) angle -= 360;

            // Handle the dead zone at the bottom (between 135° and -135°)
            // If angle is in the bottom half (> 135 or < -135), clamp to nearest edge
            if (angle > 135 && angle <= 180) {
                angle = 135;
            } else if (angle < -135 && angle >= -180) {
                angle = -135;
            } else if (angle > 135 || angle < -135) {
                // In the dead zone - don't update
                return;
            }

            // Map angle to level (0-6)
            // -135° = level 0, 0° = level 3, 135° = level 6
            const normalizedAngle = angle + 135; // 0 to 270
            const newLevel = Math.round((normalizedAngle / 270) * 6);

            // Only update if level changed (one position at a time)
            if (newLevel !== lastLevel) {
                this.volumeLevel = newLevel;
                lastLevel = newLevel;
                this.volume = this.volumeLevel / 6;

                this.audio.volume = this.volume;
                if (this.gainNode) {
                    this.gainNode.gain.value = this.volume;
                }
                localStorage.setItem('volumeLevel', this.volumeLevel.toString());
                this.updateDialPosition();
            }
        };

        this.volumeDial.addEventListener('mousedown', (e) => {
            handleVolumeChange(e);
            const onMouseMove = (e) => handleVolumeChange(e);
            const onMouseUp = () => {
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
            };
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        });
    }

    /**
     * @private
     */
    updateDialPosition() {
        // Rotate dial indicator based on volume level (0-6)
        // Level 0 = -135°, Level 3 = 0°, Level 6 = 135°
        const angle = -135 + (this.volumeLevel / 6) * 270;
        this.dialIndicator.style.transform = `translateX(-50%) rotate(${angle}deg)`;
    }

    /**
     * Initializes audio context and event listeners
     */
    async init() {
        await this.initAudioContext();
        this.setupAudioEvents();
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
        this.gainNode = this.audioContext.createGain();
        this.gainNode.gain.value = this.volume;
        this.gainNode.connect(this.audioContext.destination);
        this.analyzerNode.connect(this.gainNode);

        this.sourceNode = this.audioContext.createMediaElementSource(this.audio);
        this.sourceNode.connect(this.analyzerNode);
        this.audio.volume = this.volume;
    }

    /**
     * @private
     */
    setupAudioEvents() {
        this.audio.addEventListener('canplay', () => {
            if (this.isLoading) {
                this.isLoading = false;
                this.updateControls();
            }
        });

        this.audio.addEventListener('ended', async () => {
            await this.loadNewSong(true, 'next');
        });

        this.audio.addEventListener('error', (e) => {
            console.error('Audio streaming error:', e);
            this.isLoading = false;
            this.updateControls();
        });
    }

    /**
     * @private
     * @param {string} url - Audio file URL
     */
    async loadAudio(url, startTime = 0) {
        this.isLoading = true;
        this.updateControls();

        return new Promise((resolve) => {
            const onCanPlay = () => {
                this.audio.removeEventListener('canplay', onCanPlay);
                this.audio.removeEventListener('error', onError);
                this.isLoading = false;
                this.updateControls();
                if (startTime > 0) {
                    this.audio.currentTime = startTime;
                }
                this.elements.timeTotal.textContent = this.formatTime(this.audio.duration || 0);
                resolve();
            };

            const onError = () => {
                this.audio.removeEventListener('canplay', onCanPlay);
                this.audio.removeEventListener('error', onError);
                console.error('Error loading audio');
                this.isLoading = false;
                this.updateControls();
                resolve();
            };

            this.audio.addEventListener('canplay', onCanPlay);
            this.audio.addEventListener('error', onError);
            this.audio.src = url;
            this.audio.load();
        });
    }

    /**
     * @private
     * @param {number} [offset=0] - Start offset in seconds
     */
    play(offset = 0) {
        if (!this.audio.src) return;

        if (this.audioContext.state === 'suspended') {
            this.audioContext.resume();
        }

        if (offset > 0 && isFinite(this.audio.duration)) {
            this.audio.currentTime = Math.min(Math.max(0, offset), this.audio.duration);
        }

        this.audio.play();
        this.isPlaying = true;
        this.updateUI();
    }

    /**
     * Stops audio playback
     * @private
     */
    stop() {
        this.audio.pause();
        this.isPlaying = false;
        this.updateUI();
    }

    /**
     * Seeks to specific time in audio
     * @private
     * @param {number} time - Time in seconds to seek to
     */
    seek(time) {
        if (!this.audio.duration) return;
        this.audio.currentTime = Math.min(Math.max(0, time), this.audio.duration);
        this.drawSeekbar();
        this.saveState();
    }

    /**
     * Updates all UI elements
     * @private
     */
    updateUI() {
        this.elements.playButton.innerHTML = this.isPlaying ? `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path fill-rule="evenodd" d="M6.75 5.25a.75.75 0 0 1 .75-.75H9a.75.75 0 0 1 .75.75v13.5a.75.75 0 0 1-.75.75H7.5a.75.75 0 0 1-.75-.75V5.25Zm7.5 0A.75.75 0 0 1 15 4.5h1.5a.75.75 0 0 1 .75.75v13.5a.75.75 0 0 1-.75.75H15a.75.75 0 0 1-.75-.75V5.25Z" clip-rule="evenodd" /></svg>` : `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path fill-rule="evenodd" d="M4.5 5.653c0-1.427 1.529-2.33 2.779-1.643l11.54 6.347c1.295.712 1.295 2.573 0 3.286L7.28 19.99c-1.25.687-2.779-.217-2.779-1.643V5.653Z" clip-rule="evenodd" /></svg>`;
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
        if (this.isLoading) {
            this.audio.pause();
            this.isPlaying = false;
            this.updateUI();
        }
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

            this.updateTextScroll();
        }
    }

    /**
     * @private
     */
    updateTextScroll() {
        this.updateElementScroll(this.elements.songTitle, 102);
        this.updateElementScroll(this.elements.songArtistAlbum, 104);
    }

    /**
     * @private
     */
    updateElementScroll(element, containerWidth) {
        element.style.animation = 'none';
        element.style.paddingLeft = '0';

        void element.offsetWidth;

        const textWidth = element.scrollWidth;

        if (textWidth > containerWidth) {
            element.classList.remove('no-scroll');

            const scrollDistance = -(textWidth - containerWidth);
            element.style.setProperty('--kb-scroll-distance', `${scrollDistance}px`);

            const duration = Math.max(24, (textWidth / 10));
            element.style.animation = `kb-text-scroll ${duration}s ease-in-out infinite`;
        } else {
            element.classList.add('no-scroll');
            element.style.animation = 'none';
        }
    }

    /**
     * Draws seekbar with current progress
     * @private
     */
    drawSeekbar() {
        if (!this.audio.duration) return;

        const ctx = this.seekbarCanvas.getContext('2d');
        const { width, height } = this.seekbarCanvas;
        const centerY = height / 2;

        ctx.clearRect(0, 0, width, height);

        ctx.fillStyle = SEEKBAR_CONFIG.COLORS.GROOVE;
        ctx.fillRect(0, centerY - 2, width, 4);
        ctx.strokeStyle = '#222';
        ctx.lineWidth = 1;
        ctx.strokeRect(0, centerY - 2, width, 4);

        const progress = (this.audio.currentTime / this.audio.duration) * width;

        ctx.fillStyle = SEEKBAR_CONFIG.COLORS.PROGRESS;
        ctx.fillRect(1, centerY - 1, progress - 1, 2);

        ctx.fillStyle = SEEKBAR_CONFIG.COLORS.THUMB;
        ctx.beginPath();
        ctx.arc(progress, centerY, SEEKBAR_CONFIG.THUMB_RADIUS, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = SEEKBAR_CONFIG.COLORS.THUMB_INNER;
        ctx.beginPath();
        ctx.arc(progress, centerY - 1, 2, 0, Math.PI * 2);
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
                const hue = (i / bufferLength) * 360;
                ctx.fillStyle = `hsl(${hue}, 100%, 50%)`;
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

        const state = {
            songId: this.currentSong.id,
            spotify_id: this.currentSong.spotify_id || this.currentSong.id,
            timeStamp: Math.min(this.audio.currentTime, this.audio.duration || 0),
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
        if (!this.audio.duration) return;
        const seekTime = (position / this.seekbarCanvas.width) * this.audio.duration;
        this.seek(seekTime);
    }

    /**
     * Handles play/pause button click
     * @private
     */
    handlePlayPause() {
        if (this.isLoading) return;
        if (this.isPlaying) {
            this.audio.pause();
            this.isPlaying = false;
        } else {
            this.audio.play();
            this.isPlaying = true;
        }
        this.updateUI();
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
        if (!this.audio.duration) return;
        this.elements.timeElapsed.textContent = this.formatTime(this.audio.currentTime);
        this.elements.timeTotal.textContent = this.formatTime(this.audio.duration);
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
                    spotify_id: state.songId,
                    title: state.songTitle,
                    artist: state.songArtist,
                    album: state.songAlbum,
                    album_art_url: state.album_art_url,
                    custom_album_art: state.custom_album_art,
                    streaming_url: state.streaming_url
                };

                this.updateSongInfo();
                await this.loadAudio(state.streaming_url, state.timeStamp || 0);

                if (state.isPlaying) {
                    setTimeout(() => this.play(state.timeStamp || 0), 100);
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
