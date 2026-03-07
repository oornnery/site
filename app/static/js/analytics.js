(function () {
    "use strict";

    var ENDPOINT = "/api/v1/analytics/track";
    var MAX_BATCH = 20;
    var FLUSH_MS = 5000;

    var queue = [];
    var enabled = true;

    function enqueue(eventName, fields) {
        queue.push({
            event_name: eventName,
            page_path: fields.pagePath || window.location.pathname,
            element_id: fields.elementId || "",
            element_text: (fields.elementText || "").slice(0, 512),
            target_url: fields.targetUrl || "",
            metadata: fields.metadata || {},
            occurred_at: new Date().toISOString(),
        });
        if (queue.length >= MAX_BATCH) {
            flush();
        }
    }

    function flush() {
        if (queue.length === 0) {
            return;
        }
        var payload = JSON.stringify({ events: queue.splice(0, MAX_BATCH) });
        if (navigator.sendBeacon) {
            navigator.sendBeacon(ENDPOINT, new Blob([payload], { type: "application/json" }));
        } else {
            fetch(ENDPOINT, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: payload,
                keepalive: true,
                credentials: "same-origin",
            }).catch(function () {});
        }
    }

    function trackClicks() {
        document.addEventListener("click", function (event) {
            var el = event.target.closest("[data-analytics-event]");
            if (!el) {
                return;
            }
            var href = el.getAttribute("href") || "";
            enqueue(el.dataset.analyticsEvent || "click", {
                pagePath: el.dataset.analyticsPath || window.location.pathname,
                elementId: el.dataset.analyticsId || el.id || "",
                elementText: el.dataset.analyticsLabel || (el.textContent || "").trim(),
                targetUrl: el.dataset.analyticsTarget || href,
            });
        });
    }

    function trackSectionScroll() {
        var sections = document.querySelectorAll("[data-analytics-section]");
        if (sections.length === 0) {
            return;
        }
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) {
                    return;
                }
                observer.unobserve(entry.target);
                enqueue("section_scroll", {
                    elementId: entry.target.dataset.analyticsSection || entry.target.id || "section",
                });
            });
        }, { threshold: 0.6 });

        sections.forEach(function (section) {
            observer.observe(section);
        });
    }

    function init() {
        var meta = document.querySelector('meta[name="analytics-enabled"]');
        if (meta && meta.content === "false") {
            enabled = false;
            return;
        }

        enqueue("page_view", { metadata: { referrer: document.referrer || "" } });
        trackClicks();
        trackSectionScroll();

        window.setInterval(flush, FLUSH_MS);
        window.addEventListener("visibilitychange", function () {
            if (document.visibilityState === "hidden") {
                flush();
            }
        });
        window.addEventListener("beforeunload", flush);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
