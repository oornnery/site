/**
 * Alpine data factory: navbar
 *
 * Handles mobile menu open/close state.
 * Used with @alpinejs/csp — all expressions are method calls or property reads.
 *
 * Template usage:
 *   <nav x-data="navbar()" @keydown.escape.window="close()">
 *     <button @click="toggle()" :aria-expanded="ariaExpanded">...</button>
 *     <div :class="{ 'hidden': !open, 'md:block': true }">...</div>
 *   </nav>
 */
export default () => ({
    open: false,

    toggle() {
        this.open = !this.open;
    },

    close() {
        this.open = false;
    },

    /** String form of open state for aria-expanded attribute. */
    get ariaExpanded() {
        return String(this.open);
    },
});
