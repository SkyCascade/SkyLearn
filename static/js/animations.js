/* =====================================================================
   SkyLearn — Motion & Depth Layer (behaviour)
   Purely additive & defensive: every selector is optional-chained so
   this script is safe to include on every page regardless of which
   elements exist there. Nothing here changes markup structure, only
   adds classes / small decorative nodes and listens for events.
   ===================================================================== */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------- Top progress bar ---------------- */
  var progress = document.createElement("div");
  progress.id = "sl-progress";
  document.documentElement.appendChild(progress);

  function startProgress() {
    progress.style.opacity = "1";
    progress.style.width = "70%";
  }
  function finishProgress() {
    progress.style.width = "100%";
    setTimeout(function () {
      progress.style.opacity = "0";
      setTimeout(function () { progress.style.width = "0%"; }, 300);
    }, 150);
  }

  startProgress();
  window.addEventListener("load", finishProgress);

  // Show progress again on internal navigation / form submits
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]");
    if (!a) return;
    var href = a.getAttribute("href") || "";
    if (href.startsWith("#") || a.target === "_blank" || e.metaKey || e.ctrlKey) return;
    if (a.origin && a.origin !== window.location.origin) return;
    startProgress();
  });
  document.addEventListener("submit", startProgress, true);

  /* ---------------- Page fade-in ---------------- */
  function markLoaded() { document.body.classList.add("sl-loaded"); }
  if (document.readyState === "complete" || document.readyState === "interactive") {
    requestAnimationFrame(markLoaded);
  } else {
    document.addEventListener("DOMContentLoaded", markLoaded);
  }
  window.addEventListener("pageshow", markLoaded); // bfcache safety

  /* ---------------- Ripple on buttons ---------------- */
  if (!reduceMotion) {
    document.addEventListener("click", function (e) {
      var btn = e.target.closest && e.target.closest(".btn");
      if (!btn) return;
      var rect = btn.getBoundingClientRect();
      var diameter = Math.max(rect.width, rect.height);
      var circle = document.createElement("span");
      circle.className = "sl-ripple";
      circle.style.width = circle.style.height = diameter + "px";
      circle.style.left = (e.clientX - rect.left - diameter / 2) + "px";
      circle.style.top = (e.clientY - rect.top - diameter / 2) + "px";
      btn.appendChild(circle);
      setTimeout(function () { circle.remove(); }, 650);
    });
  }

  /* ---------------- Scroll reveal + animated counters ---------------- */
  var revealTargets = document.querySelectorAll(
    ".card, .card-count, .bg-white.border, .title-1"
  );
  revealTargets.forEach(function (el) { el.classList.add("sl-reveal"); });

  function animateCount(el) {
    var raw = (el.textContent || "").trim().replace(/,/g, "");
    var target = parseFloat(raw);
    if (isNaN(target) || el.dataset.slCounted) return;
    el.dataset.slCounted = "1";
    if (reduceMotion) return;
    var start = null;
    var duration = 1100;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.floor(eased * target).toLocaleString();
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = target.toLocaleString();
    }
    requestAnimationFrame(step);
  }

  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("sl-visible");
        var counter = entry.target.querySelector(".card-count h2, h2");
        if (entry.target.classList.contains("card-count") && counter) {
          animateCount(counter);
        }
        io.unobserve(entry.target);
      });
    }, { threshold: 0.12 });
    revealTargets.forEach(function (el) { io.observe(el); });
  } else {
    revealTargets.forEach(function (el) { el.classList.add("sl-visible"); });
  }

  /* ---------------- 3D tilt on hover ---------------- */
  function initTilt(el, maxDeg) {
    if (el.dataset.slTilt || reduceMotion) return;
    el.dataset.slTilt = "1";
    var parent = el.parentElement;
    if (parent) parent.style.perspective = parent.style.perspective || "900px";
    el.style.transformStyle = "preserve-3d";
    el.addEventListener("mousemove", function (e) {
      var rect = el.getBoundingClientRect();
      var x = e.clientX - rect.left;
      var y = e.clientY - rect.top;
      var cx = rect.width / 2, cy = rect.height / 2;
      var rotY = ((x - cx) / cx) * maxDeg;
      var rotX = -((y - cy) / cy) * maxDeg;
      el.style.transform = "rotateX(" + rotX + "deg) rotateY(" + rotY + "deg) translateY(-4px)";
    });
    el.addEventListener("mouseleave", function () { el.style.transform = ""; });
  }
  document.querySelectorAll(".card-count, .bg-white.border").forEach(function (el) {
    initTilt(el, 7);
  });
  document.querySelectorAll(".card").forEach(function (el) {
    initTilt(el, 4);
  });

  /* ---------------- Sidebar stagger delay indices ---------------- */
  document.querySelectorAll("#side-nav ul > li").forEach(function (li, i) {
    li.style.setProperty("--sl-i", i);
  });

  /* ---------------- Navbar shadow on scroll ---------------- */
  var topNav = document.getElementById("top-navbar");
  if (topNav) {
    window.addEventListener("scroll", function () {
      topNav.classList.toggle("sl-scrolled", window.scrollY > 8);
    }, { passive: true });
  }

  /* ---------------- Decorative floating blobs behind auth cards ---------------- */
  function injectBlobs(container, palette) {
    if (!container || container.dataset.slBlobbed) return;
    container.dataset.slBlobbed = "1";
    container.classList.add("sl-auth-card-wrap");
    var sizes = [160, 120, 90];
    sizes.forEach(function (size, i) {
      var b = document.createElement("div");
      b.className = "sl-blob";
      b.style.width = size + "px";
      b.style.height = size + "px";
      b.style.background = palette[i % palette.length];
      b.style.top = (i === 1 ? 55 : 5 + i * 10) + "%";
      b.style.left = (i === 0 ? -10 : i === 1 ? 70 : 30) + "%";
      b.style.animationDelay = (i * 1.4) + "s";
      container.prepend(b);
    });
  }

  var authForm = document.getElementById("login-form");
  if (authForm) {
    var wrap = authForm.closest(".col-md-4") || authForm.closest(".card");
    injectBlobs(wrap, ["#f8d270", "#7c6fe0", "#5ec8d8"]);
  }

  /* ---------------- Scroll-to-top FAB ---------------- */
  var toTop = document.createElement("button");
  toTop.id = "sl-to-top";
  toTop.type = "button";
  toTop.setAttribute("aria-label", "Scroll to top");
  toTop.innerHTML = '<i class="fas fa-arrow-up"></i>';
  document.body.appendChild(toTop);
  toTop.addEventListener("click", function () {
    window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
  });
  window.addEventListener("scroll", function () {
    toTop.classList.toggle("sl-show", window.scrollY > 320);
  }, { passive: true });
})();
