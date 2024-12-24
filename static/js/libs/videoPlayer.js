class VideoPlayer {
    static defaultConfig = {
        selectors: {
            container: '.win98-player',
            video: '#video-player',
            controls: {
                play: '#playBtn',
                pause: '#pauseBtn',
                stop: '#stopBtn',
                seekBack: '#seekBackBtn',
                seekForward: '#seekForwardBtn',
                fullscreen: '#fullscreenBtn',
                mute: '#muteBtn',
                cc: '#ccBtn',
                quality: '.quality-btn',
                subDub: '.sub-dub-control .sub-dub-btn'
            },
            displays: {
                timeCurrent: '.time-current',
                timeTotal: '.time-total'
            },
            sliders: {
                seek: {
                    slider: '.seek-slider',
                    fill: '.seek-fill',
                    buffer: '.seek-buffer',
                    thumb: '.seek-thumb'
                },
                volume: {
                    slider: '.volume-slider',
                    fill: '.volume-track .volume-fill',
                    thumb: '.volume-thumb'
                }
            },
            menus: {
                quality: '.quality-menu',
                subDub: '.sub-dub-menu',
                caption: '.caption-menu'
            },
            subtitles: {
                container: '#custom-subtitles'
            }
        },
        hls: {
            debug: false,
            capLevelToPlayerSize: true,
            defaultAudioCodec: 'mp4a.40.2'
        },
        subtitles: {
            default: {
                fontSize: 24,
                strokeWidth: 4,
                padding: 4
            },
            fullscreen: {
                fontSize: 48,
                strokeWidth: 8,
                padding: 8
            }
        },
        keyboard: {
            enabled: true,
            shortcuts: {
                space: 'togglePlayPause',
                arrowleft: 'seekBackward',
                arrowright: 'seekForward',
                f: 'toggleFullscreen',
                m: 'toggleMute',
                arrowup: ['changeVolume', 0.1],
                arrowdown: ['changeVolume', -0.1],
                '+': ['changeSubtitleSize', 1],
                '=': ['changeSubtitleSize', 1],
                '-': ['changeSubtitleSize', -1],
                '0': 'resetSubtitleSize'
            }
        },
        source: {
            url: '',
            type: 'hls',  // 'hls' or 'video'
            tracks: []    // Array of subtitle tracks
        }
    };

    static STORAGE_KEYS = {
        VOLUME: 'videoplayer_volume',
        QUALITY: 'videoplayer_quality'
    };

    constructor(config = {}) {
        this.config = this.mergeConfig(VideoPlayer.defaultConfig, config);
        this.initializeElements();
        this.setupSource();
        this.setupEventListeners();
        this.setupSubtitles();
        this.setupFullscreenHandling();
        this.setupVideoInteractions();
        this.setupBufferingIndicator();
        this.loadVolume();

        if (this.config.keyboard.enabled) {
            this.setupKeyboardControls();
        }

        this.initializeSubtitleSize();
    }

    mergeConfig(defaultConfig, userConfig) {
        const merged = { ...defaultConfig };

        const merge = (target, source) => {
            Object.keys(source).forEach(key => {
                if (source[key] instanceof Object && !Array.isArray(source[key])) {
                    if (!target[key]) target[key] = {};
                    merge(target[key], source[key]);
                } else {
                    target[key] = source[key];
                }
            });
        };

        merge(merged, userConfig);
        return merged;
    }

    initializeElements() {
        const s = this.config.selectors;
        this.elements = {
            container: document.querySelector(s.container),
            video: document.querySelector(s.video),
            controls: {},
            displays: {},
            sliders: {
                seek: {},
                volume: {}
            },
            menus: {},
            subtitles: {}
        };

        // Initialize controls
        Object.entries(s.controls).forEach(([key, selector]) => {
            this.elements.controls[key] = document.querySelector(selector);
        });

        // Initialize displays
        Object.entries(s.displays).forEach(([key, selector]) => {
            this.elements.displays[key] = document.querySelector(selector);
        });

        // Initialize sliders
        Object.entries(s.sliders).forEach(([type, selectors]) => {
            Object.entries(selectors).forEach(([key, selector]) => {
                this.elements.sliders[type][key] = document.querySelector(selector);
            });
        });

        // Initialize menus
        Object.entries(s.menus).forEach(([key, selector]) => {
            this.elements.menus[key] = document.querySelector(selector);
        });

        // Initialize subtitles container
        this.elements.subtitles.container = document.querySelector(s.subtitles.container);
    }

    initializeSubtitleSize() {
        const isFullscreen = !!document.fullscreenElement;
        const config = isFullscreen ? this.config.subtitles.fullscreen : this.config.subtitles.default;

        this.subtitleStyles = {
            fontSize: `${config.fontSize}px`,
            strokeWidth: `${config.strokeWidth}px`,
            padding: `${config.padding}px`
        };

        const span = this.elements.subtitles.container.querySelector('span');
        if (span) {
            span.style.fontSize = this.subtitleStyles.fontSize;
            span.style.webkitTextStroke = `${this.subtitleStyles.strokeWidth} black`;
            span.style.padding = this.subtitleStyles.padding;
        }
    }

    setupSource() {
        const { url, type } = this.config.source;
        if (!url) return;

        if (type === 'hls') {
            if (!Hls.isSupported()) return;

            this.hls = new Hls(this.config.hls);
            this.hls.attachMedia(this.elements.video);
            this.hls.loadSource(url);

            this.hls.on(Hls.Events.MANIFEST_PARSED, (event, data) => {
                this.setupQualityMenu(data.levels);
            });
        } else {
            this.elements.video.src = url;
        }
    }

    setupEventListeners() {
        // Video controls
        this.elements.controls.play.addEventListener('click', () => this.elements.video.play());
        this.elements.controls.pause.addEventListener('click', () => this.elements.video.pause());
        this.elements.controls.stop.addEventListener('click', () => {
            this.elements.video.pause();
            this.elements.video.currentTime = 0;
        });
        this.elements.controls.seekBack.addEventListener('click', () => this.seekBackward());
        this.elements.controls.seekForward.addEventListener('click', () => this.seekForward());
        this.elements.controls.fullscreen.addEventListener('click', () => this.toggleFullscreen());
        this.elements.controls.mute.addEventListener('click', () => this.toggleMute());

        // Video events
        this.elements.video.addEventListener('timeupdate', () => this.updateTimeDisplay());
        this.elements.video.addEventListener('loadedmetadata', () => {
            this.elements.displays.timeTotal.textContent = this.formatTime(this.elements.video.duration);
        });
        this.elements.video.addEventListener('progress', () => this.updateBuffer());

        // Setup slider events
        this.setupSliderEvents();

        // Setup menu events
        this.setupMenuEvents();
    }

    setupSliderEvents() {
        // Seek slider
        this.elements.sliders.seek.slider.addEventListener('input', (e) => {
            const value = e.target.value;
            this.elements.video.currentTime = (value / 100) * this.elements.video.duration;
            this.updateSeekDisplay(value);
        });

        // Volume slider
        this.elements.sliders.volume.slider.addEventListener('input', (e) => {
            const value = e.target.value;
            this.updateVolume(value / 100);
        });
    }

    setupMenuEvents() {
        const closeMenus = (except) => {
            Object.entries(this.elements.menus).forEach(([key, menu]) => {
                try {
                    if (key !== except) menu.classList.remove('show');
                } catch (e) { }
            });
        };

        // Quality menu
        this.elements.controls.quality?.addEventListener('click', () => {
            this.elements.menus.quality.classList.toggle('show');
            closeMenus('quality');
        });

        // Sub/Dub menu
        this.elements.controls.subDub?.addEventListener('click', () => {
            this.elements.menus.subDub.classList.toggle('show');
            closeMenus('subDub');
        });

        // Caption menu
        this.elements.controls.cc?.addEventListener('click', () => {
            this.elements.menus.caption.classList.toggle('show');
            closeMenus('caption');
        });

        // Close menus when clicking outside
        document.addEventListener('click', (e) => {
            try {
                if (!e.target.closest('.quality-control')) this.elements.menus.quality.classList.remove('show');
            } catch (e) { }

            try {
                if (!e.target.closest('.sub-dub-control')) this.elements.menus.subDub.classList.remove('show');
            } catch (e) { }

            try {
                if (!e.target.closest('#ccBtn')) this.elements.menus.caption.classList.remove('show');
            } catch (e) { }
        });
    }

    saveVolume(volume) {
        try {
            localStorage.setItem(VideoPlayer.STORAGE_KEYS.VOLUME, volume);
        } catch (e) { }
    }

    loadVolume() {
        try {
            const savedVolume = localStorage.getItem(VideoPlayer.STORAGE_KEYS.VOLUME);
            if (savedVolume !== null) {
                this.updateVolume(parseFloat(savedVolume));
            }
        } catch (e) { }
    }

    saveQuality(quality) {
        try {
            localStorage.setItem(VideoPlayer.STORAGE_KEYS.QUALITY, quality);
        } catch (e) { }
    }

    loadQuality() {
        try {
            const savedQuality = localStorage.getItem(VideoPlayer.STORAGE_KEYS.QUALITY);
            if (savedQuality !== null && this.hls) {
                this.hls.currentLevel = parseInt(savedQuality);
                // Update quality button text
                const qualityButton = this.elements.controls.quality;
                const qualityText = savedQuality === '-1' ? 'Auto' :
                    `${this.hls.levels[savedQuality].height}p`;
                qualityButton.innerHTML = this.getQualityButtonHTML(qualityText);
            }
        } catch (e) { }
    }

    getQualityButtonHTML(text) {
        return `<svg class="win98-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
        </svg>                          
        <svg class="win98-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 15 12 18.75 15.75 15m-7.5-6L12 5.25 15.75 9" />
        </svg>${text}`;
    }

    setupBufferingIndicator() {
        const playerContainer = this.elements.video.closest('.win98-player-content');
        let loadingTimeout;

        const isBuffering = () => {
            const video = this.elements.video;

            // If seeking or initial load
            if (video.seeking || video.readyState < 3) return true;

            // If playing but not enough data
            if (!video.paused && video.currentTime > 0) {
                // Check if we have data for the current position
                for (let i = 0; i < video.buffered.length; i++) {
                    if (video.currentTime >= video.buffered.start(i) &&
                        video.currentTime <= video.buffered.end(i)) {
                        // Check if we have enough buffer ahead
                        const aheadBuffer = video.buffered.end(i) - video.currentTime;
                        if (aheadBuffer < 0.5) return true; // Less than 0.5 seconds ahead
                        return false;
                    }
                }
                return true; // Current time not in any buffer range
            }
            return false;
        };

        const showLoading = () => {
            if (loadingTimeout) clearTimeout(loadingTimeout);
            loadingTimeout = setTimeout(() => {
                if (isBuffering()) {
                    playerContainer.classList.add('video-loading');
                }
            }, 100);
        };

        const hideLoading = () => {
            if (loadingTimeout) clearTimeout(loadingTimeout);
            loadingTimeout = setTimeout(() => {
                if (!isBuffering()) {
                    playerContainer.classList.remove('video-loading');
                }
            }, 100);
        };

        // Video events
        this.elements.video.addEventListener('waiting', showLoading);
        this.elements.video.addEventListener('canplay', hideLoading);
        this.elements.video.addEventListener('playing', hideLoading);
        this.elements.video.addEventListener('progress', showLoading); // Check on data load
        this.elements.video.addEventListener('timeupdate', () => {
            if (isBuffering()) showLoading();
            else hideLoading();
        });
        this.elements.video.addEventListener('seeked', hideLoading);
        this.elements.video.addEventListener('stalled', showLoading);

        // HLS specific events
        if (this.hls) {
            this.hls.on(Hls.Events.FRAG_LOADING, showLoading);
            this.hls.on(Hls.Events.FRAG_BUFFERED, hideLoading);
            this.hls.on(Hls.Events.ERROR, showLoading);
        }

        // Initial loading state
        if (!this.elements.video.readyState || this.elements.video.readyState < 3) {
            playerContainer.classList.add('video-loading');
        }
    }

    setupQualityMenu(levels) {
        this.elements.menus.quality.innerHTML = `
            <button data-quality="-1">Auto</button>
            ${levels.map((level, index) => `
                <button data-quality="${index}">${level.height}p</button>
            `).join('')}
        `;

        this.elements.menus.quality.addEventListener('click', (e) => {
            if (e.target.tagName === 'BUTTON') {
                const quality = parseInt(e.target.dataset.quality);
                this.hls.currentLevel = quality;
                this.elements.controls.quality.innerHTML = this.getQualityButtonHTML(e.target.textContent);
                this.elements.menus.quality.classList.remove('show');
                this.saveQuality(quality); // Save quality setting
            }
        });

        // Load saved quality after menu setup
        this.loadQuality();
    }

    setupSubtitles() {
        const { tracks } = this.config.source;
        if (!tracks || !tracks.length) return;

        // Clear existing tracks
        while (this.elements.video.textTracks.length > 0) {
            this.elements.video.removeChild(this.elements.video.textTracks[0]);
        }

        // Add new tracks and store them
        this.subtitleTracks = tracks.map((trackInfo, index) => {
            const track = document.createElement('track');
            track.kind = trackInfo.kind;
            track.label = trackInfo.label;
            track.srclang = trackInfo.srclang || 'en';
            track.src = trackInfo.file;
            if (trackInfo.default) {
                track.default = true;
            }
            this.elements.video.appendChild(track);
            return track;
        });

        // Setup custom subtitle display and initialize default track
        setTimeout(() => {
            const tracks = this.elements.video.textTracks;
            // First hide all tracks
            for (let track of tracks) {
                track.mode = 'hidden';
            }

            // Find and initialize default track
            const defaultTrackIndex = tracks.length ? this.config.source.tracks.findIndex(track => track.default) : -1;
            this.currentTrackIndex = defaultTrackIndex;

            if (defaultTrackIndex !== -1) {
                // Set up the track immediately
                this.setupTrackCueListener(defaultTrackIndex);

                // Update the CC button text
                const defaultTrack = this.config.source.tracks[defaultTrackIndex];
                this.elements.controls.cc.innerHTML = `
                    <svg class="win98-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 15 12 18.75 15.75 15m-7.5-6L12 5.25 15.75 9" />
                    </svg>${defaultTrack.label}
                `;
            }
        }, 100);

        this.setupCaptionMenu();
    }

    setupTrackCueListener(trackIndex) {
        // Remove existing cue listeners
        if (this.currentTrack) {
            this.currentTrack.removeEventListener('cuechange', this.cueChangeHandler);
        }

        // If track index is -1 (off) or invalid, just clear subtitles
        if (trackIndex === -1 || !this.elements.video.textTracks[trackIndex]) {
            this.elements.subtitles.container.innerHTML = '';
            return;
        }

        // Set up new track
        this.currentTrack = this.elements.video.textTracks[trackIndex];
        this.currentTrack.mode = 'showing';

        // Create cue change handler
        this.cueChangeHandler = (e) => {
            this.elements.subtitles.container.innerHTML = '';
            if (this.currentTrack.activeCues?.length > 0) {
                const cue = this.currentTrack.activeCues[0];
                const span = document.createElement('span');
                span.innerHTML = cue.text;

                Object.assign(span.style, {
                    fontSize: this.subtitleStyles.fontSize,
                    webkitTextStroke: `${this.subtitleStyles.strokeWidth} black`,
                    padding: this.subtitleStyles.padding
                });

                this.elements.subtitles.container.appendChild(span);
            }
        };

        // Add the listener
        this.currentTrack.addEventListener('cuechange', this.cueChangeHandler);
    }

    setupCaptionMenu() {
        const { tracks } = this.config.source;
        if (!tracks || !tracks.length) return;

        this.elements.menus.caption.innerHTML = `
            <button data-track="off">Off</button>
            ${tracks.map((track, index) => `
                <button data-track="${index}">${track.label}</button>
            `).join('')}
        `;

        this.elements.menus.caption.addEventListener('click', (e) => {
            if (e.target.tagName === 'BUTTON') {
                const selectedTrackIndex = e.target.dataset.track;
                const trackIndex = selectedTrackIndex === 'off' ? -1 : parseInt(selectedTrackIndex);

                // Update display state
                this.elements.subtitles.container.style.display = trackIndex >= 0 ? 'block' : 'none';

                // Hide all tracks first
                Array.from(this.elements.video.textTracks).forEach(track => {
                    track.mode = 'hidden';
                });

                // Setup the new track listener
                this.setupTrackCueListener(trackIndex);

                // Update button text
                this.elements.controls.cc.innerHTML = `
                    <svg class="win98-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 15 12 18.75 15.75 15m-7.5-6L12 5.25 15.75 9" />
                    </svg>${e.target.textContent}
                `;

                this.elements.menus.caption.classList.remove('show');
            }
        });

        // Activate default track if specified
        const defaultTrackIndex = tracks.findIndex(track => track.default);
        if (defaultTrackIndex !== -1) {
            const defaultButton = this.elements.menus.caption.querySelector(`[data-track="${defaultTrackIndex}"]`);
            if (defaultButton) {
                defaultButton.click();
            }
        }
    }

    setupFullscreenHandling() {
        let timeout;

        const showControls = () => {
            if (document.fullscreenElement === this.elements.container) {
                this.elements.container.classList.add('controls-visible');
                this.elements.container.style.cursor = 'default';
                if (timeout) clearTimeout(timeout);
                timeout = setTimeout(() => {
                    if (!this.isHoveringControls) {
                        this.elements.container.classList.remove('controls-visible');
                        this.elements.container.style.cursor = 'none';
                    }
                }, 3000);
            }
        };

        document.addEventListener('fullscreenchange', () => {
            if (document.fullscreenElement === this.elements.container) {
                this.elements.container.addEventListener('mousemove', showControls);
                showControls();
                this.updateSubtitleSizeForFullscreen(true);
            } else {
                this.elements.container.removeEventListener('mousemove', showControls);
                this.elements.container.classList.remove('controls-visible');
                this.elements.container.style.cursor = 'default';
                document.body.style.cursor = 'default';
                this.updateSubtitleSizeForFullscreen(false);
            }
        });

        this.isHoveringControls = false;
        const controlsArea = this.elements.container.querySelector('.win98-controls');

        controlsArea.addEventListener('mouseenter', () => {
            this.isHoveringControls = true;
            if (document.fullscreenElement === this.elements.container) {
                this.elements.container.classList.add('controls-visible');
            }
        });

        controlsArea.addEventListener('mouseleave', () => {
            this.isHoveringControls = false;
            if (document.fullscreenElement === this.elements.container) {
                timeout = setTimeout(() => {
                    if (!this.isHoveringControls) {
                        this.elements.container.classList.remove('controls-visible');
                    }
                }, 3000);
            }
        });
    }

    setupVideoInteractions() {
        this.elements.video.addEventListener('click', (e) => {
            if (this.isDragging) return;
            this.togglePlayPause();
        });

        let clickTimeout;
        this.elements.video.addEventListener('click', (e) => {
            if (clickTimeout) {
                clearTimeout(clickTimeout);
                clickTimeout = null;
                this.toggleFullscreen();
            } else {
                clickTimeout = setTimeout(() => {
                    clickTimeout = null;
                }, 300);
            }
        });

        this.isDragging = false;
        this.elements.sliders.seek.slider.addEventListener('mousedown', () => this.isDragging = true);
        document.addEventListener('mouseup', () => this.isDragging = false);
    }

    setupKeyboardControls() {
        document.addEventListener('keydown', (e) => {
            if (!this.elements.video || e.target.matches('input, textarea')) return;
            if (e.ctrlKey || e.altKey || e.metaKey) return;
            if (e.target !== document.body) return;

            const shortcut = this.config.keyboard.shortcuts[e.key.toLowerCase()];
            if (shortcut) {
                e.preventDefault();
                if (Array.isArray(shortcut)) {
                    this[shortcut[0]](...shortcut.slice(1));
                } else {
                    this[shortcut]();
                }
            }
        });
    }

    // Utility methods
    formatTime(seconds) {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = Math.floor(seconds % 60);
        return h > 0
            ? `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
            : `${m}:${s.toString().padStart(2, '0')}`;
    }

    updateTimeDisplay() {
        const progress = (this.elements.video.currentTime / this.elements.video.duration) * 100;
        // If there is a single digit in minutes, add a leading zero
        const currentTime = this.formatTime(this.elements.video.currentTime);
        const singleDigitMinutes = currentTime.length === 4 && currentTime[1] === ':';
        this.elements.displays.timeCurrent.textContent = singleDigitMinutes ? `0${currentTime}` : currentTime;
        this.updateSeekDisplay(progress);
    }

    updateSeekDisplay(progress) {
        this.elements.sliders.seek.fill.style.width = `${progress}%`;
        this.elements.sliders.seek.slider.value = progress;
        this.elements.sliders.seek.thumb.style.left = `${progress}%`;
    }

    updateBuffer() {
        if (this.elements.video.buffered.length > 0) {
            const bufferedEnd = this.elements.video.buffered.end(this.elements.video.buffered.length - 1);
            const bufferedProgress = (bufferedEnd / this.elements.video.duration) * 100;
            this.elements.sliders.seek.buffer.style.width = `${bufferedProgress}%`;
        }
    }

    updateVolume(volume) {
        this.elements.video.volume = volume;
        this.updateVolumeSliders(volume);
        this.updateMuteButton(volume > 0);
        if (this.elements.video.muted && volume > 0) this.elements.video.muted = false;
        this.saveVolume(volume); // Save volume setting
    }

    updateVolumeSliders(volume) {
        const percentage = volume * 100;
        this.elements.sliders.volume.fill.style.width = `${percentage}%`;
        this.elements.sliders.volume.slider.value = percentage;
        this.elements.sliders.volume.thumb.style.left = `${percentage}%`;
    }

    updateMuteButton(isAudio) {
        this.elements.controls.mute.querySelector('.win98-icon').innerHTML = isAudio ?
            '<path stroke-linecap="round" stroke-linejoin="round" d="M19.114 5.636a9 9 0 0 1 0 12.728M16.463 8.288a5.25 5.25 0 0 1 0 7.424M6.75 8.25l4.72-4.72a.75.75 0 0 1 1.28.53v15.88a.75.75 0 0 1-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.009 9.009 0 0 1 2.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75Z" />' :
            '<path stroke-linecap="round" stroke-linejoin="round" d="M17.25 9.75 19.5 12m0 0 2.25 2.25M19.5 12l2.25-2.25M19.5 12l-2.25 2.25m-10.5-6 4.72-4.72a.75.75 0 0 1 1.28.53v15.88a.75.75 0 0 1-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.009 9.009 0 0 1 2.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75Z" />';
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            this.elements.container.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }

    togglePlayPause() {
        if (this.elements.video.paused) {
            this.elements.video.play();
        } else {
            this.elements.video.pause();
        }
    }

    toggleMute() {
        this.elements.video.muted = !this.elements.video.muted;
        if (!this.elements.video.muted && this.elements.video.volume === 0) this.updateVolume(1);
        this.updateVolumeSliders(this.elements.video.muted ? 0 : this.elements.video.volume);
        this.updateMuteButton(!this.elements.video.muted);
    }

    seekBackward() {
        this.elements.video.currentTime = Math.max(0, this.elements.video.currentTime - 10);
    }

    seekForward() {
        this.elements.video.currentTime = Math.min(this.elements.video.duration, this.elements.video.currentTime + 10);
    }

    changeVolume(delta) {
        const newVolume = Math.max(0, Math.min(1, this.elements.video.volume + delta));
        this.updateVolume(newVolume);
    }

    resetSubtitleSize() {
        const isFullscreen = !!document.fullscreenElement;
        const config = isFullscreen ? this.config.subtitles.fullscreen : this.config.subtitles.default;

        this.subtitleStyles = {
            fontSize: `${config.fontSize}px`,
            strokeWidth: `${config.strokeWidth}px`,
            padding: `${config.padding}px`
        };

        const span = this.elements.subtitles.container.querySelector('span');
        if (span) {
            span.style.fontSize = this.subtitleStyles.fontSize;
            span.style.webkitTextStroke = `${this.subtitleStyles.strokeWidth} black`;
            span.style.padding = this.subtitleStyles.padding;
        }
    }

    changeSubtitleSize(delta) {
        const isFullscreen = !!document.fullscreenElement;
        const config = isFullscreen ? this.config.subtitles.fullscreen : this.config.subtitles.default;
        const currentSize = parseInt(this.subtitleStyles.fontSize);
        const minSize = config.fontSize * 0.5;
        const maxSize = config.fontSize * 1.5;

        const newSize = Math.min(Math.max(currentSize + (delta * 2), minSize), maxSize);
        if (newSize === currentSize) return;

        const strokeSize = newSize / 6;
        const paddingSize = strokeSize / 2;

        this.subtitleStyles = {
            fontSize: `${newSize}px`,
            strokeWidth: `${strokeSize}px`,
            padding: `${paddingSize}px`
        };

        const span = this.elements.subtitles.container.querySelector('span');
        if (span) {
            span.style.fontSize = this.subtitleStyles.fontSize;
            span.style.webkitTextStroke = `${this.subtitleStyles.strokeWidth} black`;
            span.style.padding = this.subtitleStyles.padding;
        }
    }

    updateSubtitleSizeForFullscreen(isFullscreen) {
        const config = isFullscreen ? this.config.subtitles.fullscreen : this.config.subtitles.default;

        this.subtitleStyles = {
            fontSize: `${config.fontSize}px`,
            strokeWidth: `${config.strokeWidth}px`,
            padding: `${config.padding}px`
        };

        const span = this.elements.subtitles.container.querySelector('span');
        if (span) {
            span.style.fontSize = this.subtitleStyles.fontSize;
            span.style.webkitTextStroke = `${this.subtitleStyles.strokeWidth} black`;
            span.style.padding = this.subtitleStyles.padding;
        }
    }
}