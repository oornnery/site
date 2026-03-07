(function () {
    "use strict";

    function setCurrentYear() {
        var year = String(new Date().getFullYear());
        document.querySelectorAll("[data-current-year]").forEach(function (node) {
            node.textContent = year;
        });
    }

    function initNavbar() {
        document.querySelectorAll("[data-navbar]").forEach(function (navbar) {
            var toggle = navbar.querySelector("[data-nav-toggle]");
            var menu = navbar.querySelector("[data-nav-menu]");
            if (!toggle || !menu) {
                return;
            }
            var openIcon = navbar.querySelector("[data-nav-icon-open]");
            var closeIcon = navbar.querySelector("[data-nav-icon-close]");

            function setMenuState(isOpen) {
                var desktop = window.innerWidth >= 768;
                var expanded = !desktop && isOpen;
                navbar.classList.toggle("is-open", expanded);
                toggle.setAttribute("aria-expanded", String(expanded));
                if (desktop) {
                    menu.classList.remove("hidden");
                } else {
                    menu.classList.toggle("hidden", !expanded);
                }
                if (openIcon) {
                    openIcon.classList.toggle("hidden", expanded);
                }
                if (closeIcon) {
                    closeIcon.classList.toggle("hidden", !expanded);
                }
            }

            function close() {
                setMenuState(false);
            }

            setMenuState(false);

            toggle.addEventListener("click", function () {
                setMenuState(toggle.getAttribute("aria-expanded") !== "true");
            });

            navbar.querySelectorAll("[data-nav-link]").forEach(function (link) {
                link.addEventListener("click", close);
            });

            document.addEventListener("click", function (event) {
                if (event.target instanceof Node && !navbar.contains(event.target)) {
                    close();
                }
            });

            window.addEventListener("keydown", function (event) {
                if (event.key === "Escape") {
                    close();
                }
            });

            window.addEventListener("resize", close);
        });
    }

    function initScrollSnap() {
        var container = document.querySelector(".scroll-snap-container");
        if (!container) {
            return;
        }

        container.querySelectorAll(".scroll-indicator").forEach(function (indicator) {
            indicator.style.cursor = "pointer";
            indicator.addEventListener("click", function () {
                var sections = Array.from(container.querySelectorAll(".snap-section"));
                if (sections.length === 0) {
                    return;
                }
                var vh = container.clientHeight || window.innerHeight;
                var current = Math.round(container.scrollTop / vh);
                var next = Math.min(current + 1, sections.length - 1);
                sections[next].scrollIntoView({ behavior: "smooth", block: "start" });
            });
        });

        var mq = window.matchMedia("(max-width: 1024px)");
        function applySnap() {
            container.style.scrollSnapType = mq.matches ? "y proximity" : "y mandatory";
        }
        applySnap();
        mq.addEventListener("change", applySnap);
    }

    function initFeaturedCarousel() {
        document.querySelectorAll("[data-featured-carousel]").forEach(function (carousel) {
            var track = carousel.querySelector("[data-featured-track]");
            var slides = Array.from(carousel.querySelectorAll("[data-featured-slide]"));
            if (!track || slides.length === 0) {
                return;
            }

            var currentIndex = 0;
            var autoplayId = null;
            var autoplayMs = Number(carousel.getAttribute("data-featured-autoplay-ms")) || 3000;
            var currentLabel = carousel.querySelector("[data-featured-current]");
            var dots = Array.from(carousel.querySelectorAll("[data-featured-dot]"));
            var multiSlide = slides.length > 1;

            function goTo(index, animate) {
                if (animate === undefined) {
                    animate = true;
                }
                currentIndex = (index + slides.length) % slides.length;
                track.style.transitionDuration = animate ? "" : "0ms";
                track.style.transform = "translateX(-" + (currentIndex * 100) + "%)";

                slides.forEach(function (slide, i) {
                    slide.setAttribute("aria-hidden", i === currentIndex ? "false" : "true");
                });

                if (currentLabel) {
                    currentLabel.textContent = String(currentIndex + 1);
                }

                dots.forEach(function (dot, i) {
                    var active = i === currentIndex;
                    dot.classList.toggle("is-active", active);
                    dot.setAttribute("aria-current", active ? "true" : "false");
                });

                if (!animate) {
                    requestAnimationFrame(function () {
                        track.style.transitionDuration = "";
                    });
                }
            }

            function stopAutoplay() {
                if (autoplayId) {
                    clearInterval(autoplayId);
                    autoplayId = null;
                }
            }

            function startAutoplay() {
                stopAutoplay();
                if (!multiSlide) {
                    return;
                }
                autoplayId = setInterval(function () {
                    goTo(currentIndex + 1);
                }, autoplayMs);
            }

            goTo(0, false);

            if (!multiSlide) {
                return;
            }

            var prevBtn = carousel.querySelector("[data-featured-prev]");
            var nextBtn = carousel.querySelector("[data-featured-next]");

            if (prevBtn) {
                prevBtn.addEventListener("click", function () {
                    goTo(currentIndex - 1);
                    startAutoplay();
                });
            }
            if (nextBtn) {
                nextBtn.addEventListener("click", function () {
                    goTo(currentIndex + 1);
                    startAutoplay();
                });
            }

            dots.forEach(function (dot) {
                dot.addEventListener("click", function () {
                    var idx = Number(dot.getAttribute("data-featured-index"));
                    if (!Number.isNaN(idx)) {
                        goTo(idx);
                        startAutoplay();
                    }
                });
            });

            carousel.addEventListener("mouseenter", stopAutoplay);
            carousel.addEventListener("mouseleave", startAutoplay);
            carousel.addEventListener("focusin", stopAutoplay);
            carousel.addEventListener("focusout", function (event) {
                if (!event.relatedTarget || !carousel.contains(event.relatedTarget)) {
                    startAutoplay();
                }
            });

            document.addEventListener("visibilitychange", function () {
                if (document.hidden) {
                    stopAutoplay();
                } else {
                    startAutoplay();
                }
            });

            startAutoplay();
        });
    }

    function slugify(text) {
        return text
            .normalize("NFKD")
            .replace(/[^\w\s-]/g, "")
            .trim()
            .toLowerCase()
            .replace(/\s+/g, "-")
            .replace(/-+/g, "-")
            .replace(/^-|-$/g, "");
    }

    function initReadingProgress(content) {
        var root = document.querySelector("[data-reading-progress]");
        var bar = document.querySelector("[data-reading-progress-bar]");
        if (!root || !bar) {
            return;
        }

        function update() {
            var scrollTop = window.scrollY;
            var vh = window.innerHeight;
            var rect = content.getBoundingClientRect();
            var contentTop = rect.top + scrollTop;
            var contentHeight = content.offsetHeight;
            if (contentHeight <= 0) {
                bar.style.transform = "scaleX(0)";
                return;
            }
            var start = contentTop - (vh * 0.2);
            var end = contentTop + contentHeight - (vh * 0.7);
            var progress = Math.max(0, Math.min(1, (scrollTop - start) / Math.max(end - start, 1)));
            bar.style.transform = "scaleX(" + progress + ")";
            root.classList.toggle("is-active", progress > 0 && progress < 1);
        }

        window.addEventListener("scroll", update, { passive: true });
        window.addEventListener("resize", update);
        update();
    }

    function initToc(content) {
        var tocWrapper = document.querySelector("[data-post-toc-wrapper]");
        var tocContainer = document.querySelector("[data-post-toc]");
        if (!tocWrapper || !tocContainer) {
            return;
        }

        var headings = Array.from(content.querySelectorAll("h2, h3")).filter(function (h) {
            return h.textContent && h.textContent.trim().length > 0;
        });
        if (headings.length === 0) {
            return;
        }

        var usedIds = new Set(
            Array.from(content.querySelectorAll("[id]")).map(function (el) { return el.id; }).filter(Boolean)
        );

        var tocLinks = [];
        tocContainer.textContent = "";

        headings.forEach(function (heading, index) {
            var id = heading.id;
            if (!id) {
                var base = slugify(heading.textContent || "") || "section-" + (index + 1);
                var candidate = base;
                var suffix = 2;
                while (usedIds.has(candidate)) {
                    candidate = base + "-" + suffix;
                    suffix += 1;
                }
                id = candidate;
                heading.id = id;
                usedIds.add(id);
            }

            var link = document.createElement("a");
            link.href = "#" + id;
            link.textContent = heading.textContent.trim();
            link.className = "blog-post-toc-link";
            if (heading.tagName === "H3") {
                link.classList.add("is-subheading");
            }
            tocContainer.appendChild(link);
            tocLinks.push({ heading: heading, link: link });
        });

        if (tocLinks.length === 0) {
            return;
        }

        function setActive(id) {
            tocLinks.forEach(function (item) {
                item.link.classList.toggle("is-active", item.heading.id === id);
            });
        }

        function updateLayout() {
            if (tocLinks.length === 1) {
                var label = tocLinks[0].heading.textContent.trim();
                tocLinks[0].link.style.setProperty("--toc-offset", "50%");
                tocLinks[0].link.dataset.label = label;
                tocLinks[0].link.setAttribute("aria-label", label);
                return;
            }

            var offsets = tocLinks.map(function (item) { return item.heading.offsetTop; });
            var min = Math.min.apply(null, offsets);
            var max = Math.max.apply(null, offsets);
            var range = Math.max(max - min, 1);

            tocLinks.forEach(function (item, i) {
                var text = item.heading.textContent.trim();
                var mapped = 8 + (((offsets[i] - min) / range) * 84);
                item.link.style.setProperty("--toc-offset", mapped + "%");
                item.link.dataset.label = text;
                item.link.setAttribute("aria-label", text);
            });
        }

        var rafPending = false;

        function updateActiveHeading() {
            var pageH = document.documentElement.scrollHeight;
            if ((window.scrollY + window.innerHeight) >= (pageH - 2)) {
                setActive(tocLinks[tocLinks.length - 1].heading.id);
                return;
            }

            var baseOffset = Math.max(96, window.innerHeight * 0.12);
            var viewBottom = window.scrollY + window.innerHeight;
            var contentBottom = window.scrollY + content.getBoundingClientRect().bottom;
            var remaining = contentBottom - viewBottom;
            var boost = Math.max(0, (window.innerHeight * 0.45) - remaining);
            var line = window.scrollY + baseOffset + boost;
            var idx = 0;

            tocLinks.forEach(function (item, i) {
                if ((window.scrollY + item.heading.getBoundingClientRect().top) <= line) {
                    idx = i;
                }
            });

            setActive(tocLinks[idx].heading.id);
        }

        function onScroll() {
            if (rafPending) {
                return;
            }
            rafPending = true;
            requestAnimationFrame(function () {
                rafPending = false;
                updateActiveHeading();
            });
        }

        function onHashChange() {
            var hash = decodeURIComponent(window.location.hash.replace(/^#/, ""));
            if (!hash) {
                return;
            }
            var match = tocLinks.find(function (item) { return item.heading.id === hash; });
            if (match) {
                setActive(match.heading.id);
            }
        }

        tocLinks.forEach(function (item) {
            item.link.addEventListener("click", function () {
                setActive(item.heading.id);
            });
        });

        tocWrapper.classList.remove("hidden");
        window.addEventListener("scroll", onScroll, { passive: true });
        window.addEventListener("resize", function () {
            updateLayout();
            updateActiveHeading();
        });
        window.addEventListener("hashchange", onHashChange);
        updateLayout();

        if (window.location.hash) {
            onHashChange();
        } else {
            updateActiveHeading();
        }
    }

    function initPostEnhancements() {
        var content = document.querySelector("[data-post-content]");
        if (!content) {
            return;
        }
        initReadingProgress(content);
        initToc(content);
    }

    function init() {
        setCurrentYear();
        initNavbar();
        initScrollSnap();
        initFeaturedCarousel();
        initPostEnhancements();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
