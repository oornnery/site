"use strict";

(() => {
    const ENDPOINT = "/api/v1/analytics/track";
    const MAX_BATCH = 20;
    const FLUSH_MS = 5000;

    let queue = [];

    const enqueue = (name, fields = {}) => {
        queue.push({
            event_name: name,
            page_path: fields.pagePath ?? location.pathname,
            element_id: fields.elementId ?? "",
            element_text: (fields.elementText ?? "").slice(0, 512),
            target_url: fields.targetUrl ?? "",
            metadata: fields.metadata ?? {},
            occurred_at: new Date().toISOString(),
        });
        if (queue.length >= MAX_BATCH) flush();
    };

    const flush = () => {
        if (!queue.length) return;
        const payload = JSON.stringify({ events: queue.splice(0, MAX_BATCH) });
        if (navigator.sendBeacon) {
            navigator.sendBeacon(ENDPOINT, new Blob([payload], { type: "application/json" }));
        } else {
            fetch(ENDPOINT, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: payload,
                keepalive: true,
                credentials: "same-origin",
            }).catch(() => {});
        }
    };

    const trackClicks = () => {
        document.addEventListener("click", (e) => {
            const el = e.target.closest("[data-analytics-event]");
            if (!el) return;
            enqueue(el.dataset.analyticsEvent || "click", {
                pagePath: el.dataset.analyticsPath,
                elementId: el.dataset.analyticsId || el.id,
                elementText: el.dataset.analyticsLabel || el.textContent?.trim(),
                targetUrl: el.dataset.analyticsTarget || el.getAttribute("href"),
            });
        });
    };

    const trackSectionScroll = () => {
        const sections = document.querySelectorAll("[data-analytics-section]");
        if (!sections.length) return;

        const observer = new IntersectionObserver((entries) => {
            for (const entry of entries) {
                if (!entry.isIntersecting) continue;
                observer.unobserve(entry.target);
                enqueue("section_scroll", {
                    elementId: entry.target.dataset.analyticsSection || entry.target.id || "section",
                });
            }
        }, { threshold: 0.6 });

        sections.forEach((s) => observer.observe(s));
    };

    const init = () => {
        const meta = document.querySelector('meta[name="analytics-enabled"]');
        if (meta?.content === "false") return;

        enqueue("page_view", { metadata: { referrer: document.referrer } });
        trackClicks();
        trackSectionScroll();

        setInterval(flush, FLUSH_MS);
        document.addEventListener("visibilitychange", () => {
            if (document.visibilityState === "hidden") flush();
        });
        addEventListener("beforeunload", flush);
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
