/**
 * A class that implements marquee functionality for HTML elements
 * Original source: https://shi.foo/static/js/libs/marquee.js
 * Credit must be given if this code is used in any way
 */
class Marquee {
    /** @readonly */
    static DIRECTION = {
        LEFT: 'left',
        RIGHT: 'right',
        UP: 'up',
        DOWN: 'down'
    };

    /** @readonly */
    static BEHAVIOR = {
        SCROLL: 'scroll',
        SLIDE: 'slide',
        ALTERNATE: 'alternate'
    };

    /** @readonly */
    static DEFAULTS = {
        behavior: 'scroll',
        bgcolor: null,
        direction: 'left',
        height: null,
        width: null,
        hspace: 0,
        vspace: 0,
        loop: -1,
        scrollamount: 6,
        scrolldelay: 85,
        truespeed: false
    };

    /**
     * Creates a new Marquee instance
     * @param {HTMLElement} element - The element to transform into a marquee
     * @param {Object} [options] - Configuration options
     * @param {string} [options.behavior] - Scroll behavior (scroll, slide, alternate)
     * @param {string} [options.bgcolor] - Background color
     * @param {string} [options.direction] - Scroll direction (left, right, up, down)
     * @param {string|number} [options.height] - Container height
     * @param {string|number} [options.width] - Container width
     * @param {number} [options.hspace] - Horizontal margin
     * @param {number} [options.vspace] - Vertical margin
     * @param {number} [options.loop] - Number of loops (-1 for infinite)
     * @param {number} [options.scrollamount] - Pixels to move per step
     * @param {number} [options.scrolldelay] - Delay between steps in ms
     * @param {boolean} [options.truespeed] - Whether to respect exact scroll delay
     * @throws {Error} If invalid element is provided
     */
    constructor(element, options = {}) {
        if (!(element instanceof HTMLElement)) {
            throw new Error('Invalid element provided to Marquee');
        }

        this.element = element;

        const attributeOptions = {
            behavior: element.getAttribute('behavior'),
            bgcolor: element.getAttribute('bgcolor'),
            direction: element.getAttribute('direction'),
            height: element.getAttribute('height'),
            width: element.getAttribute('width'),
            hspace: element.getAttribute('hspace'),
            vspace: element.getAttribute('vspace'),
            loop: element.getAttribute('loop'),
            scrollamount: element.getAttribute('scrollamount'),
            scrolldelay: element.getAttribute('scrolldelay'),
            truespeed: element.hasAttribute('truespeed')
        };

        this.config = {
            ...Marquee.DEFAULTS,
            ...Object.fromEntries(Object.entries(attributeOptions).filter(([_, v]) => v != null)),
            ...this._normalizeOptions(options)
        };

        this._rafId = null;
        this._currentPos = 0;
        this._lastTime = Date.now();
        this._isPaused = false;
        this._loopCount = 0;
        this._originalContent = '';

        this._setupContainer();
        this._setupContent();
        this._setupDimensions();
        this._setupEventListeners();

        this._bindInlineHandlers();
        this.start();
    }

    /**
     * Normalizes numeric options by parsing them to integers
     * @private
     * @param {Object} options - Options to normalize
     * @returns {Object} Normalized options
     */
    _normalizeOptions(options) {
        return {
            ...options,
            scrollamount: parseInt(options.scrollamount) || Marquee.DEFAULTS.scrollamount,
            scrolldelay: parseInt(options.scrolldelay) || Marquee.DEFAULTS.scrolldelay,
            loop: parseInt(options.loop) || Marquee.DEFAULTS.loop,
            hspace: parseInt(options.hspace) || Marquee.DEFAULTS.hspace,
            vspace: parseInt(options.vspace) || Marquee.DEFAULTS.vspace
        };
    }

    /**
     * Sets up the container element
     * @private
     */
    _setupContainer() {
        this.container = document.createElement('div');
        this.container.style.overflow = 'hidden';
        this.container.style.position = 'relative';
        this.container.style.width = this.config.width || '100%';
        this.container.style.height = this.config.height || 'auto';

        if (this.config.bgcolor) {
            this.container.style.backgroundColor = this.config.bgcolor;
        }

        this.container.style.margin = `${this.config.vspace}px ${this.config.hspace}px`;
        this._originalContent = this.element.innerHTML;
        this.element.innerHTML = '';
        this.element.appendChild(this.container);

        const eventHandlers = this.element.attributes;
        for (let i = 0; i < eventHandlers.length; i++) {
            const attr = eventHandlers[i];
            if (attr.name.startsWith('on')) {
                this.container[attr.name] = this.element[attr.name];
            }
        }
    }

    /**
     * Sets up the content wrapper
     * @private
     */
    _setupContent() {
        this.contentWrapper = document.createElement('div');
        this.contentWrapper.style.position = 'absolute';
        this.contentWrapper.style.width = '100%';
        this.contentWrapper.innerHTML = this._originalContent.trim();

        if (this.config.direction === 'up' || this.config.direction === 'down') {
            this.contentWrapper.style.display = 'block';
        } else {
            this.contentWrapper.style.whiteSpace = 'nowrap';
        }

        if (this.config.behavior !== Marquee.BEHAVIOR.ALTERNATE) {
            const children = Array.from(this.contentWrapper.children);

            children.forEach(child => {
                const clone = child.cloneNode(true);
                this.contentWrapper.appendChild(clone);
            });
        }

        this.container.appendChild(this.contentWrapper);
    }

    /**
     * Sets up initial dimensions and positions
     * @private
     */
    _setupDimensions() {
        requestAnimationFrame(() => {
            switch (this.config.direction) {
                case Marquee.DIRECTION.LEFT:
                    this._currentPos = this.container.offsetWidth;
                    break;
                case Marquee.DIRECTION.RIGHT:
                    this._currentPos = -this.contentWrapper.offsetWidth;
                    break;
                case Marquee.DIRECTION.UP:
                    this._currentPos = this.container.offsetHeight;
                    break;
                case Marquee.DIRECTION.DOWN:
                    this._currentPos = -this.contentWrapper.offsetHeight;
                    break;
            }
            this._applyPosition();
        });
    }

    /**
     * Sets up event listeners for hover and visibility
     * @private
     */
    _setupEventListeners() {
        if (!this.config.truespeed) {
            this.container.addEventListener('mouseenter', () => this.pause());
            this.container.addEventListener('mouseleave', () => this.start());
        }

        this._visibilityHandler = () => {
            if (document.hidden) {
                this.pause();
            } else if (!this._isPaused) {
                this.start();
            }
        };
        document.addEventListener('visibilitychange', this._visibilityHandler);
    }

    /**
     * Sets up inline event handlers
     * @private
     */
    _bindInlineHandlers() {
        if (this.element.hasAttribute('onmouseover')) {
            const originalStop = this.element.getAttribute('onmouseover');
            this.element.removeAttribute('onmouseover');
            this.element.addEventListener('mouseover', () => this.pause());
        }

        if (this.element.hasAttribute('onmouseout')) {
            const originalStart = this.element.getAttribute('onmouseout');
            this.element.removeAttribute('onmouseout');
            this.element.addEventListener('mouseout', () => this.start());
        }
    }

    /**
     * Applies the current position to the content wrapper
     * @private
     */
    _applyPosition() {
        const isVertical = this.config.direction === 'up' || this.config.direction === 'down';
        const transform = isVertical ?
            `translateY(${this._currentPos}px)` :
            `translateX(${this._currentPos}px)`;
        this.contentWrapper.style.transform = transform;
    }

    /**
     * Animation frame handler
     * @private
     */
    _animate() {
        const currentTime = Date.now();
        const deltaTime = currentTime - this._lastTime;

        if (deltaTime >= this.config.scrolldelay) {
            this._lastTime = currentTime;
            const pixelsToMove = this.config.scrollamount;

            switch (this.config.direction) {
                case Marquee.DIRECTION.LEFT:
                    this._currentPos -= pixelsToMove;
                    if (this._currentPos <= -this.contentWrapper.offsetWidth / 2) {
                        this._currentPos = this.container.offsetWidth;
                        this._handleLoop();
                    }
                    break;

                case Marquee.DIRECTION.RIGHT:
                    this._currentPos += pixelsToMove;
                    if (this._currentPos >= this.container.offsetWidth) {
                        this._currentPos = -this.contentWrapper.offsetWidth / 2;
                        this._handleLoop();
                    }
                    break;

                case Marquee.DIRECTION.UP:
                    this._currentPos -= pixelsToMove;
                    if (this._currentPos <= -this.contentWrapper.offsetHeight / 2) {
                        this._currentPos = this.container.offsetHeight;
                        this._handleLoop();
                    }
                    break;

                case Marquee.DIRECTION.DOWN:
                    this._currentPos += pixelsToMove;
                    if (this._currentPos >= this.container.offsetHeight) {
                        this._currentPos = -this.contentWrapper.offsetHeight / 2;
                        this._handleLoop();
                    }
                    break;
            }

            this._applyPosition();
        }

        if (!this._isPaused) {
            this._rafId = requestAnimationFrame(() => this._animate());
        }
    }

    /**
     * Handles loop counting and stopping
     * @private
     */
    _handleLoop() {
        if (this.config.loop !== -1) {
            this._loopCount++;
            if (this._loopCount >= this.config.loop) {
                this.stop();
            }
        }
    }

    /**
     * Starts or resumes the marquee animation
     * @public
     */
    start() {
        this._isPaused = false;
        this._lastTime = Date.now();
        if (!this._rafId) {
            this._animate();
        }
    }

    /**
     * Pauses the marquee animation
     * @public
     */
    pause() {
        this._isPaused = true;
        if (this._rafId) {
            cancelAnimationFrame(this._rafId);
            this._rafId = null;
        }
    }

    /**
     * Stops the marquee animation and resets position
     * @public
     */
    stop() {
        this.pause();
        this._currentPos = 0;
        this._loopCount = 0;
        this._applyPosition();
    }

    /**
     * Cleans up the marquee and restores original content
     * @public
     */
    destroy() {
        this.stop();
        this.container.remove();
        this.element.innerHTML = this._originalContent;
        document.removeEventListener('visibilitychange', this._visibilityHandler);
    }
}