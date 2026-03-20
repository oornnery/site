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
import htmx from "htmx.org";

import { initFrontendTelemetry } from "./telemetry.js";
import navbar from "./alpine/navbar.js";
import palette from "./alpine/palette.js";
import carousel from "./alpine/carousel.js";
import contactForm from "./alpine/contact-form.js";

import TocController from "./controllers/toc-controller.js";
import ReadingProgressController from "./controllers/reading-progress-controller.js";

initFrontendTelemetry();

/* ── Alpine ── */

Alpine.data("navbar", navbar);
Alpine.data("palette", palette);
Alpine.data("carousel", carousel);
Alpine.data("contactForm", contactForm);

window.Alpine = Alpine;
Alpine.start();

/* ── htmx ── */

window.htmx = htmx;

// Swap fragment even on 4xx/5xx so inline validation errors are displayed.
htmx.config.responseHandling = [
    { code: "204", swap: false },
    { code: ".*", swap: true },
];

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
        if (!indicator.hasAttribute("aria-label")) {
            indicator.setAttribute("aria-label", "Scroll to next section");
        }
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

/**
 * Spotlight effect: radial accent glow follows the cursor inside snap-sections.
 * Uses CSS custom properties (--spotlight-x/y/opacity) updated via mousemove.
 * Disabled when prefers-reduced-motion is set.
 */
const initSpotlight = () => {
    const container = $(".scroll-snap-container");
    if (!container) return;
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const sections = $$(".snap-section", container);
    if (!sections.length) return;

    let active = null;
    let rafId = 0;
    let mx = 0;
    let my = 0;

    const paint = () => {
        rafId = 0;
        if (!active) return;
        active.style.setProperty("--spotlight-x", mx + "px");
        active.style.setProperty("--spotlight-y", my + "px");
    };

    container.addEventListener("mousemove", (e) => {
        const section = e.target.closest(".snap-section");
        if (section !== active) {
            if (active) active.style.setProperty("--spotlight-opacity", "0");
            active = section;
            if (active) active.style.setProperty("--spotlight-opacity", "1");
        }
        if (!active) return;

        const rect = active.getBoundingClientRect();
        mx = e.clientX - rect.left;
        my = e.clientY - rect.top;

        if (!rafId) rafId = requestAnimationFrame(paint);
    });

    container.addEventListener("mouseleave", () => {
        if (active) active.style.setProperty("--spotlight-opacity", "0");
        active = null;
    });
};

onReady(() => {
    initCurrentYear();
    initScrollSnap();
    initSpotlight();
});
