(function (window) {
    'use strict';

    class Pamphlet {
        constructor(config = {}) {
            this.config = {
                server: config.server || '/services/pamphlet',
                refreshInterval: config.refreshInterval || 3600000,
                ...config
            };

            this.slots = new Map();

            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.init());
            } else {
                this.init();
            }
        }

        init() {
            this.scanForSlots();

            if (this.config.refreshInterval > 0) {
                setInterval(() => this.refreshAll(), this.config.refreshInterval);
            }
        }

        scanForSlots() {
            const elements = document.querySelectorAll('.pamphlet');
            elements.forEach(element => {
                const style = this.getStyle(element);
                if (style) {
                    this.setupSlot(element, style);
                }
            });
        }

        getStyle(element) {
            const classes = element.classList;
            if (classes.contains('pamphlet-banner')) return 'banner';
            if (classes.contains('pamphlet-big')) return 'big';
            if (classes.contains('pamphlet-button')) return 'button';
            return null;
        }

        setupSlot(element, style) {
            const slotId = `slot-${Math.random().toString(36).substring(2, 9)}`;
            element.setAttribute('data-pamphlet-id', slotId);

            this.slots.set(slotId, {
                element,
                style
            });

            this.loadPamphlet(slotId);
        }

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

        refreshAll() {
            this.slots.forEach((slot, slotId) => {
                this.loadPamphlet(slotId);
            });
        }

        refresh(element) {
            const slotId = element.getAttribute('data-pamphlet-id');
            if (slotId) {
                this.loadPamphlet(slotId);
            }
        }
    }

    window.Pamphlet = Pamphlet;

})(window);
