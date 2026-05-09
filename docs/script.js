(function () {
  function revealOnScroll() {
    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var items = document.querySelectorAll(".reveal-item");

    if (reduceMotion || !("IntersectionObserver" in window)) {
      items.forEach(function (item) {
        item.classList.add("is-visible");
      });
      return;
    }

    document.documentElement.classList.add("reveal-ready");

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) {
          return;
        }

        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    }, {
      rootMargin: "0px 0px -8% 0px",
      threshold: 0.08
    });

    items.forEach(function (item) {
      observer.observe(item);
    });
  }

  function bindFaqDetails() {
    var details = document.querySelectorAll("#faq details");

    details.forEach(function (current) {
      current.addEventListener("toggle", function () {
        if (!current.open) {
          return;
        }

        details.forEach(function (other) {
          if (other !== current) {
            other.open = false;
          }
        });
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    revealOnScroll();
    bindFaqDetails();
  });
})();

// Version History
// ver1.0 - 2026-05-06 - Added reduced-motion-aware reveal animation and single-open FAQ details behavior.
