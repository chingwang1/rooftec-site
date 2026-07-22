/**
 * Close <details class="dropdown"> when clicking outside,
 * and only keep one open at a time.
 */
(function () {
  function closeAll(except) {
    document.querySelectorAll("details.dropdown[open]").forEach(function (d) {
      if (d !== except) d.removeAttribute("open");
    });
  }

  document.addEventListener(
    "click",
    function (e) {
      var open = document.querySelectorAll("details.dropdown[open]");
      if (!open.length) return;

      var inside = e.target.closest && e.target.closest("details.dropdown");
      if (!inside) {
        closeAll(null);
        return;
      }

      // Opening one closes the others
      closeAll(inside);
    },
    true
  );

  // When a details opens via toggle, close siblings
  document.addEventListener("toggle", function (e) {
    var t = e.target;
    if (!t || !t.matches || !t.matches("details.dropdown")) return;
    if (t.open) closeAll(t);
  }, true);
})();
