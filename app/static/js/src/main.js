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
 * Canvas cursor: spring-physics ribbon trails that follow the cursor inside
 * the scroll-snap container. Uses the site's accent color. Disabled when
 * prefers-reduced-motion is set or on touch-only devices.
 */
const initCanvasCursor = () => {
    const container = $(".scroll-snap-container");
    if (!container) return;
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    if (!matchMedia("(pointer: fine)").matches) return;

    const canvas = document.createElement("canvas");
    canvas.className = "canvas-cursor";
    container.appendChild(canvas);
    const ctx = canvas.getContext("2d");

    const cfg = {
        trails: 15,
        size: 40,
        friction: 0.45,
        dampening: 0.25,
        tension: 0.98,
        spring: 0.4,
    };

    const pos = { x: -1000, y: -1000 };
    let lines = [];
    let running = false;

    function Node() {
        this.x = 0;
        this.y = 0;
        this.vx = 0;
        this.vy = 0;
    }

    function Trail(i) {
        this.spring = cfg.spring + (i / cfg.trails) * 0.025;
        this.friction = cfg.friction + Math.random() * 0.01 - 0.005;
        this.nodes = [];
        for (let j = 0; j < cfg.size; j++) {
            const n = new Node();
            n.x = pos.x;
            n.y = pos.y;
            this.nodes.push(n);
        }
    }

    Trail.prototype.update = function () {
        let sp = this.spring;
        const first = this.nodes[0];
        first.vx += (pos.x - first.x) * sp;
        first.vy += (pos.y - first.y) * sp;
        for (let i = 0; i < this.nodes.length; i++) {
            const node = this.nodes[i];
            if (i > 0) {
                const prev = this.nodes[i - 1];
                node.vx += (prev.x - node.x) * sp;
                node.vy += (prev.y - node.y) * sp;
                node.vx += prev.vx * cfg.dampening;
                node.vy += prev.vy * cfg.dampening;
            }
            node.vx *= this.friction;
            node.vy *= this.friction;
            node.x += node.vx;
            node.y += node.vy;
            sp *= cfg.tension;
        }
    };

    Trail.prototype.draw = function () {
        let x = this.nodes[0].x;
        let y = this.nodes[0].y;
        ctx.beginPath();
        ctx.moveTo(x, y);
        for (let i = 1, len = this.nodes.length - 2; i < len; i++) {
            const cur = this.nodes[i];
            const nxt = this.nodes[i + 1];
            x = 0.5 * (cur.x + nxt.x);
            y = 0.5 * (cur.y + nxt.y);
            ctx.quadraticCurveTo(cur.x, cur.y, x, y);
        }
        const a = this.nodes[this.nodes.length - 2];
        const b = this.nodes[this.nodes.length - 1];
        ctx.quadraticCurveTo(a.x, a.y, b.x, b.y);
        ctx.stroke();
        ctx.closePath();
    };

    let accentRgb = "124,124,255";
    const readAccent = () => {
        const v = getComputedStyle(document.documentElement)
            .getPropertyValue("--accent-rgb")
            .trim();
        if (v) accentRgb = v;
    };
    readAccent();

    const observer = new MutationObserver(readAccent);
    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ["data-theme", "data-palette"],
    });

    const resize = () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    };

    const initLines = () => {
        lines = [];
        for (let i = 0; i < cfg.trails; i++) {
            lines.push(new Trail(i));
        }
    };

    const render = () => {
        if (!running) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.strokeStyle = "rgba(" + accentRgb + ", 0.25)";
        ctx.lineWidth = 1;
        for (let i = 0; i < lines.length; i++) {
            lines[i].update();
            lines[i].draw();
        }
        requestAnimationFrame(render);
    };

    const start = () => {
        if (!running) {
            running = true;
            render();
        }
    };
    const stop = () => {
        running = false;
    };

    let idleTimer = 0;
    let resizeRaf = 0;
    let started = false;

    const onMove = (e) => {
        pos.x = e.clientX;
        pos.y = e.clientY;
        if (!started) {
            started = true;
            initLines();
        }
        start();
        clearTimeout(idleTimer);
        idleTimer = setTimeout(stop, 3000);
    };

    const debouncedResize = () => {
        if (resizeRaf) return;
        resizeRaf = requestAnimationFrame(() => {
            resize();
            resizeRaf = 0;
        });
    };

    document.addEventListener("visibilitychange", () => {
        if (document.hidden) stop();
    });

    resize();
    window.addEventListener("resize", debouncedResize);
    document.addEventListener("mousemove", onMove);
};

onReady(() => {
    initCurrentYear();
    initScrollSnap();
    initCanvasCursor();
});
