// Theme bootstrap — loaded synchronously in <head> before CSS to prevent FOUC.
// Must remain self-contained: no imports, no external dependencies.
(function () {
    var d = document.documentElement;
    var t = localStorage.getItem("theme");
    var p = localStorage.getItem("palette");
    if (!t) {
        t = matchMedia("(prefers-color-scheme:light)").matches ? "light" : "dark";
    }
    d.dataset.theme = t;
    d.classList.toggle("dark", t === "dark");
    if (p && p !== "default") {
        d.dataset.palette = p;
    }
})();
