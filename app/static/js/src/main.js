/**
 * main.js — bundle entry point
 *
 * Registers Alpine data factories and Stimulus controllers, then starts both
 * frameworks. Also runs lightweight bootstrap utilities (current year, scroll
 * snap) that do not warrant a full framework component.
 *
 * Build output: app/static/js/main.js (esbuild IIFE bundle)
 * Loaded as:    <script defer src="/static/js/main.js"></script>
 */

import Alpine from "@alpinejs/csp";
import { Application } from "@hotwired/stimulus";

import navbar from "./alpine/navbar.js";
import palette from "./alpine/palette.js";
import carousel from "./alpine/carousel.js";

import TocController from "./controllers/toc-controller.js";
import ReadingProgressController from "./controllers/reading-progress-controller.js";

/* ── Alpine ── */

Alpine.data("navbar", navbar);
Alpine.data("palette", palette);
Alpine.data("carousel", carousel);

window.Alpine = Alpine;
Alpine.start();

/* ── Stimulus ── */

const stimulusApp = Application.start();
stimulusApp.register("toc", TocController);
stimulusApp.register("reading-progress", ReadingProgressController);

/* ── Bootstrap utilities ── */

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

const onReady = (fn) => {
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", fn);
    } else {
        fn();
    }
};

/** Update [data-current-year] elements with the current year. */
const initCurrentYear = () => {
    const year = String(new Date().getFullYear());
    for (const node of $$("[data-current-year]")) {
        node.textContent = year;
    }
};

/**
 * Scroll snap responsiveness: switch between proximity (mobile) and mandatory
 * (desktop) so users aren't trapped mid-section on small screens.
 */
const initScrollSnap = () => {
    const container = $(".scroll-snap-container");
    if (!container) return;

    for (const indicator of $$(".scroll-indicator", container)) {
        indicator.addEventListener("click", () => {
            const sections = $$(".snap-section", container);
            if (!sections.length) return;
            const vh = container.clientHeight || innerHeight;
            const current = Math.round(container.scrollTop / vh);
            const next = Math.min(current + 1, sections.length - 1);
            sections[next].scrollIntoView({ behavior: "smooth", block: "start" });
        });
    }

    const mq = matchMedia("(max-width: 1024px)");
    const apply = () => {
        container.style.scrollSnapType = mq.matches ? "y proximity" : "y mandatory";
    };
    apply();
    mq.addEventListener("change", apply);
};

onReady(() => {
    initCurrentYear();
    initScrollSnap();
});
