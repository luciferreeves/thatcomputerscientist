/**
 * A self-contained library for managing pamphlets
 * Original source: https://shi.foo/static/js/libs/pamphlet.js
 * Credit must be given if this code is used in any way
 * @version 1.0.0
 * @module Pamphlet
 */
(function (window) {
    'use strict';

    /**
     * Manages pamphlets
     */
    class Pamphlet {
        /**
         * Creates a new Pamphlet instance
         * @param {Object} config - Configuration options
         * @param {string} [config.server='https://shi.foo/services/pamphlet'] - Server endpoint for pamphlet content
         * @param {number} [config.refreshInterval=3600000] - Refresh interval in milliseconds (0 to disable)
         */
        constructor(config = {}) {
            let refreshInterval = config.refreshInterval || 3600000;

            // Ensure refresh interval is either 0 (disabled) or valid
            if (refreshInterval > 0 && refreshInterval < 60000) {
                console.warn('Pamphlet: Refresh interval must be at least 1 minute (60000ms). Setting to 60000ms.');
                refreshInterval = 60000;
            } else if (refreshInterval < 0) {
                console.warn('Pamphlet: Refresh interval cannot be negative. Setting to 3600000ms.');
                refreshInterval = 3600000;
            } else if (isNaN(refreshInterval)) {
                console.warn('Pamphlet: Refresh interval must be a number. Setting to 3600000ms.');
                refreshInterval = 3600000;
            }

            // First spread the config object, then override with validated values
            this.config = {
                ...config,
                server: config.server || 'https://shi.foo/services/pamphlet',
                refreshInterval: refreshInterval
            };

            /** @type {Map<string, {element: HTMLElement, style: string}>} */
            this.slots = new Map();

            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.init());
            } else {
                this.init();
            }
        }

        /**
         * Initializes the Pamphlet instance by scanning for slots and setting up refresh interval
         * @private
         */
        init() {
            this.scanForSlots();

            if (this.config.refreshInterval > 0) {
                setInterval(() => this.refreshAll(), this.config.refreshInterval);
            }
        }

        /**
         * Scans the document for pamphlet elements and sets them up
         * @private
         */
        scanForSlots() {
            const elements = document.querySelectorAll('.pamphlet');
            elements.forEach(element => {
                const style = this.getStyle(element);
                if (style) {
                    this.setupSlot(element, style);
                }
            });
        }

        /**
         * Determines the style of a pamphlet element based on its classes
         * @private
         * @param {HTMLElement} element - Element to check
         * @returns {string|null} Style name or null if no valid style found
         */
        getStyle(element) {
            const classes = element.classList;
            if (classes.contains('pamphlet-banner')) return 'banner';
            if (classes.contains('pamphlet-big')) return 'big';
            if (classes.contains('pamphlet-button')) return 'button';
            return null;
        }

        /**
         * Sets up a new pamphlet slot
         * @private
         * @param {HTMLElement} element - Element to set up as a slot
         * @param {string} style - Style of the pamphlet
         */
        setupSlot(element, style) {
            const slotId = `slot-${Math.random().toString(36).substring(2, 9)}`;
            element.setAttribute('data-pamphlet-id', slotId);

            this.slots.set(slotId, {
                element,
                style
            });

            this.loadPamphlet(slotId);
        }

        /**
         * Loads pamphlet content for a specific slot
         * @private
         * @param {string} slotId - ID of the slot to load content for
         */
        loadPamphlet(slotId) {
            const slot = this.slots.get(slotId);
            if (!slot) return;

            try {
                const img = document.createElement('img');
                const seed = Math.random().toString(36).substring(7);
                img.src = `${this.config.server}?style=${slot.style}&seed=${seed}`;
                img.alt = 'Pamphlet';
                img.style.width = '100%';
                img.style.height = '100%';

                slot.element.innerHTML = '';
                slot.element.appendChild(img);

            } catch (error) {
                slot.element.innerHTML = '<!-- Failed to load pamphlet -->';
            }
        }

        /**
         * Refreshes all pamphlet slots
         * @public
         */
        refreshAll() {
            this.slots.forEach((slot, slotId) => {
                this.loadPamphlet(slotId);
            });
        }

        /**
         * Refreshes a specific pamphlet element
         * @public
         * @param {HTMLElement} element - Element to refresh
         */
        refresh(element) {
            const slotId = element.getAttribute('data-pamphlet-id');
            if (slotId) {
                this.loadPamphlet(slotId);
            }
        }
    }

    window.Pamphlet = Pamphlet;

})(window);