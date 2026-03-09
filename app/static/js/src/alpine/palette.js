/**
 * Alpine data factory: palette
 *
 * Manages dark/light theme toggle and color palette selection.
 * Reads initial state from the <html> element (set by theme-bootstrap.js).
 *
 * Template usage:
 *   <div x-data="palette()" @keydown.escape.window="closeMenu()">
 *     <button @click="toggleMode()" :aria-label="modeLabel">...</button>
 *     <button @click="toggleMenu()" :aria-expanded="menuAriaExpanded">...</button>
 *     <div :class="{ 'hidden': !menuOpen }">
 *       <button @click="set('ocean')" :aria-selected="isActive('ocean')">...</button>
 *     </div>
 *   </div>
 */
export default () => ({
    mode: "dark",
    current: "default",
    menuOpen: false,

    init() {
        const root = document.documentElement;
        this.mode = root.dataset.theme || "dark";
        this.current = localStorage.getItem("palette") || "default";
    },

    toggleMode() {
        const next = this.mode === "dark" ? "light" : "dark";
        this.mode = next;
        const root = document.documentElement;
        root.dataset.theme = next;
        root.classList.toggle("dark", next === "dark");
        localStorage.setItem("theme", next);
    },

    toggleMenu() {
        this.menuOpen = !this.menuOpen;
    },

    closeMenu() {
        this.menuOpen = false;
    },

    set(id) {
        this.current = id || "default";
        this.menuOpen = false;
        const root = document.documentElement;
        if (id && id !== "default") {
            root.dataset.palette = id;
        } else {
            delete root.dataset.palette;
        }
        localStorage.setItem("palette", id || "default");
    },

    isActive(id) {
        return this.current === (id || "default");
    },

    get isDark() {
        return this.mode === "dark";
    },

    get isLight() {
        return this.mode === "light";
    },

    /** String form for aria-expanded on the palette menu trigger. */
    get menuAriaExpanded() {
        return String(this.menuOpen);
    },

    get modeLabel() {
        return this.mode === "dark" ? "Switch to light mode" : "Switch to dark mode";
    },
});
