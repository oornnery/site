/**
 * Alpine data factory: carousel
 *
 * CSP-safe featured-posts carousel using scrollTo() — no inline styles.
 * The viewport uses overflow-x: auto with scrollbar hidden via CSS.
 *
 * Template usage:
 *   <div x-data="carousel(3000)" @mouseenter="stopAutoplay()" @mouseleave="startAutoplay()">
 *     <div data-carousel-viewport>
 *       <div data-carousel-track>
 *         <div data-slide>...</div>
 *       </div>
 *     </div>
 *     <button @click="prev()">←</button>
 *     <button @click="next()">→</button>
 *     <button @click="goTo(0)" :class="{ 'is-active': current === 0 }">•</button>
 *     <span x-text="current + 1"></span>/<span x-text="total"></span>
 *   </div>
 */
export default (autoplayMs = 3000) => ({
    current: 0,
    total: 0,
    autoplayId: null,

    init() {
        this._slides = [...this.$el.querySelectorAll("[data-slide]")];
        this._viewport = this.$el.querySelector("[data-carousel-viewport]");
        this._prevButton = this.$el.querySelector("[data-carousel-prev]");
        this._nextButton = this.$el.querySelector("[data-carousel-next]");
        this._dotButtons = [...this.$el.querySelectorAll("[data-carousel-dot]")];
        this.total = this._slides.length;

        this._onPrevClick = () => this.prev();
        this._onNextClick = () => this.next();
        this._onDotClick = (event) => {
            const index = Number(event.currentTarget.dataset.carouselDot);
            if (!Number.isNaN(index)) {
                this.goTo(index);
                this.startAutoplay();
            }
        };

        this._prevButton?.addEventListener("click", this._onPrevClick);
        this._nextButton?.addEventListener("click", this._onNextClick);
        this._dotButtons.forEach((button) => {
            button.addEventListener("click", this._onDotClick);
        });

        this._syncState();
        if (this.total > 1) {
            this.startAutoplay();
        }
        // pause when tab becomes hidden
        this._onVisibility = () => {
            document.hidden ? this.stopAutoplay() : this.startAutoplay();
        };
        document.addEventListener("visibilitychange", this._onVisibility);
    },

    destroy() {
        this.stopAutoplay();
        document.removeEventListener("visibilitychange", this._onVisibility);
        this._prevButton?.removeEventListener("click", this._onPrevClick);
        this._nextButton?.removeEventListener("click", this._onNextClick);
        this._dotButtons?.forEach((button) => {
            button.removeEventListener("click", this._onDotClick);
        });
    },

    goTo(index) {
        if (!this.total) {
            return;
        }
        this.current = ((index % this.total) + this.total) % this.total;
        if (this._viewport) {
            this._viewport.scrollTo({
                left: this.current * this._viewport.offsetWidth,
                behavior: "smooth",
            });
        }
        this._syncState();
    },

    prev() {
        this.goTo(this.current - 1);
        this.startAutoplay();
    },

    next() {
        this.goTo(this.current + 1);
        this.startAutoplay();
    },

    startAutoplay() {
        this.stopAutoplay();
        if (this.total > 1) {
            this.autoplayId = setInterval(
                () => this.goTo(this.current + 1),
                autoplayMs,
            );
        }
    },

    stopAutoplay() {
        if (this.autoplayId) {
            clearInterval(this.autoplayId);
            this.autoplayId = null;
        }
    },

    isActive(index) {
        return this.current === index;
    },

    get hasPrevNext() {
        return this.total > 1;
    },

    _syncState() {
        this._slides.forEach((slide, i) => {
            slide.setAttribute("aria-hidden", String(i !== this.current));
        });

        this._dotButtons.forEach((button, i) => {
            const isActive = i === this.current;
            button.classList.toggle("is-active", isActive);
            button.setAttribute("aria-current", isActive ? "true" : "false");
        });
    },
});
