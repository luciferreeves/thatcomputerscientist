(function () {
    "use strict";

    var GLYPHS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&<>/\\=+*[]".split("");

    function randomGlyph() {
        return GLYPHS[(Math.random() * GLYPHS.length) | 0];
    }

    function scramble(element, finalText, delay, duration) {
        var start = performance.now() + delay;
        element.textContent = "";

        function tick(now) {
            var progress = (now - start) / duration;
            if (progress < 0) {
                requestAnimationFrame(tick);
                return;
            }
            if (progress >= 1) {
                element.textContent = finalText;
                return;
            }
            var revealed = Math.floor(finalText.length * progress);
            var out = "";
            for (var i = 0; i < finalText.length; i++) {
                var char = finalText[i];
                if (char === " " || char === "." || char === "/") {
                    out += char;
                } else if (i < revealed) {
                    out += char;
                } else {
                    out += randomGlyph();
                }
            }
            element.textContent = out;
            requestAnimationFrame(tick);
        }

        requestAnimationFrame(tick);
    }

    function settle(element) {
        var final = element.getAttribute("data-final");
        element.textContent = final !== null ? final : element.textContent;
    }

    document.addEventListener("DOMContentLoaded", function () {
        var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        var deck = document.getElementById("letters-deck");
        var boot = document.getElementById("deck-boot");

        var targets = document.querySelectorAll("[data-decode]");
        var names = document.querySelectorAll(".channel-name");

        if (reduced) {
            targets.forEach(settle);
            if (boot) { boot.style.display = "none"; }
            if (deck) { deck.classList.add("is-ready"); }
            return;
        }

        targets.forEach(function (element) {
            var final = element.getAttribute("data-final");
            if (final === null) { final = element.textContent.trim(); }
            var delay = parseInt(element.getAttribute("data-decode-delay") || "300", 10);
            var duration = parseInt(element.getAttribute("data-decode-dur") || "850", 10);
            scramble(element, final, delay, duration);
        });

        names.forEach(function (element, index) {
            scramble(element, element.textContent.trim(), 2850 + index * 130, 650);
        });

        if (deck) {
            requestAnimationFrame(function () { deck.classList.add("is-ready"); });
        }
    });
})();
