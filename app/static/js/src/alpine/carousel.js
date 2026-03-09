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
        this.total = this.$el.querySelectorAll("[data-slide]").length;
        this._syncAriaHidden();
        if (this.total > 1) {
            this.startAutoplay();
        }
        // pause when tab becomes hidden
        document.addEventListener("visibilitychange", () => {
            document.hidden ? this.stopAutoplay() : this.startAutoplay();
        });
    },

    goTo(index) {
        this.current = ((index % this.total) + this.total) % this.total;
        const viewport = this.$el.querySelector("[data-carousel-viewport]");
        if (viewport) {
            viewport.scrollTo({
                left: this.current * viewport.offsetWidth,
                behavior: "smooth",
            });
        }
        this._syncAriaHidden();
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

    /** Sync aria-hidden on slides via DOM (not template-level, avoids Jinja/Alpine index mismatch). */
    _syncAriaHidden() {
        this.$el.querySelectorAll("[data-slide]").forEach((slide, i) => {
            slide.setAttribute("aria-hidden", String(i !== this.current));
        });
    },
});
