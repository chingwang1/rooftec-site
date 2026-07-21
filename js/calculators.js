/**
 * Roofing planning calculators — estimates only, not a substitute for site measure.
 */
(function () {
  "use strict";

  function $(id) {
    return document.getElementById(id);
  }

  function num(id) {
    var el = $(id);
    if (!el) return NaN;
    return parseFloat(String(el.value).replace(/,/g, ""));
  }

  function money(n) {
    return (
      "$" +
      Math.round(n).toLocaleString("en-AU", {
        maximumFractionDigits: 0,
      })
    );
  }

  function fmt(n, d) {
    if (!isFinite(n)) return "—";
    return n.toLocaleString("en-AU", {
      maximumFractionDigits: d == null ? 1 : d,
      minimumFractionDigits: d == null ? 0 : d,
    });
  }

  function setText(id, text) {
    var el = $(id);
    if (el) el.textContent = text;
  }

  function showResult(boxId) {
    var el = $(boxId);
    if (el) el.hidden = false;
  }

  /** Pitch factor: plan area × factor = roof surface area */
  function pitchFactor(degrees) {
    var rad = (degrees * Math.PI) / 180;
    return 1 / Math.cos(rad);
  }

  function degreesFromRiseRun(rise, run) {
    return (Math.atan(rise / run) * 180) / Math.PI;
  }

  // ── Roof area (plan + pitch) ─────────────────────────────────
  function calcRoofArea() {
    var length = num("ra-length");
    var width = num("ra-width");
    var pitch = num("ra-pitch");
    if (!(length > 0 && width > 0 && pitch >= 0 && pitch < 80)) {
      setText("ra-error", "Enter positive length & width, and pitch between 0–79°.");
      return;
    }
    setText("ra-error", "");
    var plan = length * width;
    var factor = pitchFactor(pitch);
    var surface = plan * factor;
    // simple hip/valley allowance if checked
    var complex = $("ra-complex") && $("ra-complex").checked;
    var waste = complex ? 1.12 : 1.05;
    var order = surface * waste;
    setText("ra-plan", fmt(plan, 1) + " m²");
    setText("ra-factor", fmt(factor, 3) + "×");
    setText("ra-surface", fmt(surface, 1) + " m²");
    setText("ra-order", fmt(order, 1) + " m²");
    showResult("ra-result");
  }

  // ── Sheet quantity ───────────────────────────────────────────
  function calcSheets() {
    var area = num("sh-area");
    var cover = num("sh-cover"); // effective cover width mm
    var length = num("sh-length"); // sheet length m
    var wastePct = num("sh-waste");
    if (!(area > 0 && cover > 0 && length > 0)) {
      setText("sh-error", "Enter roof area, cover width and sheet length.");
      return;
    }
    if (!(wastePct >= 0 && wastePct <= 40)) wastePct = 10;
    setText("sh-error", "");
    var coverM = cover / 1000;
    var sheetArea = coverM * length;
    var sheetsNet = area / sheetArea;
    var sheets = Math.ceil(sheetsNet * (1 + wastePct / 100));
    setText("sh-sheet-area", fmt(sheetArea, 2) + " m² each");
    setText("sh-net", fmt(sheetsNet, 1));
    setText("sh-total", String(sheets) + " sheets");
    showResult("sh-result");
  }

  // ── Gutter sizing (simplified AU residential) ────────────────
  // Q = A × I × C (rational method lite); compare to typical gutter capacities.
  function calcGutter() {
    var area = num("gu-area"); // catchment m²
    var intensity = num("gu-intensity"); // mm/h design rainfall
    var runLength = num("gu-run"); // gutter run m
    if (!(area > 0 && intensity > 0)) {
      setText("gu-error", "Enter catchment area and rainfall intensity.");
      return;
    }
    setText("gu-error", "");
    // runoff litres/sec ≈ A(m²) × I(mm/h) / 3600
    var qLs = (area * intensity) / 3600;
    var qLh = area * intensity; // L/h roughly for display

    // Rough capacity guides for common AU domestic gutters (indicative only)
    var options = [
      { name: "Quad / fascia gutter (standard domestic)", capacity: 1.5 },
      { name: "Large quad / high-front gutter", capacity: 2.5 },
      { name: "Box gutter (engineered — design required)", capacity: 5.0 },
    ];
    var pick = options[0];
    for (var i = 0; i < options.length; i++) {
      if (qLs <= options[i].capacity) {
        pick = options[i];
        break;
      }
      pick = options[i];
    }
    var downpipes = Math.max(1, Math.ceil(qLs / 1.2));
    var spacing =
      runLength > 0 ? fmt(runLength / downpipes, 1) + " m average spacing" : "—";

    setText("gu-flow", fmt(qLs, 2) + " L/s  (~" + fmt(qLh, 0) + " L/h)");
    setText("gu-suggest", pick.name);
    setText("gu-downpipes", String(downpipes) + " (indicative)");
    setText("gu-spacing", spacing);
    showResult("gu-result");
  }

  // ── Cost estimator (SEQ ballpark AUD) ────────────────────────
  function calcCost() {
    var area = num("co-area");
    var job = ($("co-job") && $("co-job").value) || "replace";
    var storeys = ($("co-storeys") && $("co-storeys").value) || "1";
    if (!(area > 0)) {
      setText("co-error", "Enter approximate roof area in m².");
      return;
    }
    setText("co-error", "");

    // Low/high $/m² ballparks — orientation only
    var rates = {
      repair: { low: 45, high: 120, label: "Targeted metal roof repairs" },
      resheet: { low: 95, high: 180, label: "Re-sheet / Colorbond re-roof" },
      replace: { low: 120, high: 260, label: "Full roof replacement package" },
      gutters: { low: 55, high: 140, label: "Gutter & downpipe upgrade (per m² roof)" },
      cladding: { low: 80, high: 200, label: "Wall cladding (per m² wall)" },
    };
    var r = rates[job] || rates.replace;
    var mult = storeys === "2" ? 1.15 : storeys === "complex" ? 1.3 : 1;
    var low = area * r.low * mult;
    var high = area * r.high * mult;
    setText("co-type", r.label);
    setText("co-range", money(low) + " – " + money(high) + " AUD");
    setText(
      "co-note",
      "Includes rough labour/materials band for SEQ. Access, pitch, colour, insulation, solar and structural work can move the quote outside this range."
    );
    showResult("co-result");
  }

  // ── Pitch converter ──────────────────────────────────────────
  function calcPitch() {
    var mode = ($("pi-mode") && $("pi-mode").value) || "deg";
    var deg, rise, run, pct;

    if (mode === "deg") {
      deg = num("pi-input");
      if (!(deg >= 0 && deg < 80)) {
        setText("pi-error", "Enter pitch in degrees (0–79).");
        return;
      }
      run = 12;
      rise = Math.tan((deg * Math.PI) / 180) * run;
      pct = Math.tan((deg * Math.PI) / 180) * 100;
    } else if (mode === "ratio") {
      rise = num("pi-rise");
      run = num("pi-run");
      if (!(rise >= 0 && run > 0)) {
        setText("pi-error", "Enter rise and run (e.g. 4 and 12).");
        return;
      }
      deg = degreesFromRiseRun(rise, run);
      pct = (rise / run) * 100;
    } else {
      pct = num("pi-input");
      if (!(pct >= 0 && pct < 600)) {
        setText("pi-error", "Enter pitch as a percentage.");
        return;
      }
      deg = (Math.atan(pct / 100) * 180) / Math.PI;
      run = 12;
      rise = (pct / 100) * run;
    }
    setText("pi-error", "");
    setText("pi-deg", fmt(deg, 1) + "°");
    setText("pi-ratio", fmt(rise, 2) + " : " + fmt(run, 0));
    setText("pi-pct", fmt(pct, 1) + "%");
    setText("pi-factor", fmt(pitchFactor(deg), 3) + "× plan area");
    showResult("pi-result");
  }

  function syncPitchMode() {
    var mode = ($("pi-mode") && $("pi-mode").value) || "deg";
    var single = $("pi-single-wrap");
    var ratio = $("pi-ratio-wrap");
    var label = $("pi-input-label");
    if (single) single.hidden = mode === "ratio";
    if (ratio) ratio.hidden = mode !== "ratio";
    if (label) {
      label.textContent =
        mode === "deg" ? "Pitch (degrees)" : mode === "pct" ? "Pitch (%)" : "Pitch";
    }
  }

  // ── Screws / fasteners ───────────────────────────────────────
  function calcScrews() {
    var area = num("sc-area");
    var spacing = num("sc-spacing"); // mm along sheet
    var ribs = num("sc-ribs"); // fixings across cover width
    var cover = num("sc-cover"); // mm cover width
    var wastePct = num("sc-waste");
    if (!(area > 0 && spacing > 0 && ribs > 0 && cover > 0)) {
      setText("sc-error", "Enter area, spacing, ribs per sheet width and cover width.");
      return;
    }
    if (!(wastePct >= 0 && wastePct <= 30)) wastePct = 10;
    setText("sc-error", "");
    // fixings per m² ≈ (1000/spacing) × (ribs / (cover/1000))
    var perM2 = (1000 / spacing) * (ribs / (cover / 1000));
    var total = Math.ceil(area * perM2 * (1 + wastePct / 100));
    var packs100 = Math.ceil(total / 100);
    setText("sc-density", fmt(perM2, 1) + " per m²");
    setText("sc-total", total.toLocaleString("en-AU") + " screws");
    setText("sc-packs", packs100 + " × 100-packs (approx)");
    showResult("sc-result");
  }

  // Wire up any calculators present on the page
  function bind(id, fn) {
    var btn = $(id);
    if (btn) btn.addEventListener("click", fn);
  }

  /** Prefill area fields from ?area=123 (e.g. map measure tool). */
  function applyQueryParams() {
    var params = new URLSearchParams(window.location.search);
    var area = parseFloat(params.get("area"));
    if (!(area > 0)) return;

    // Prefer dedicated area inputs on this page
    ["co-area", "sh-area", "sc-area", "gu-area"].forEach(function (id) {
      var el = $(id);
      if (el) {
        el.value = String(Math.round(area * 10) / 10);
        el.classList.add("calc-prefilled");
      }
    });

    // Auto-run matching calculator when we have an area field
    if ($("co-area") && $("co-calc")) calcCost();
    else if ($("sh-area") && $("sh-calc")) calcSheets();
    else if ($("sc-area") && $("sc-calc")) calcScrews();
    else if ($("gu-area") && $("gu-calc")) calcGutter();

    // Banner if present
    var note = $("calc-from-map");
    if (note) {
      note.hidden = false;
      note.textContent =
        "Area pre-filled from map measure (" +
        area.toLocaleString("en-AU", { maximumFractionDigits: 1 }) +
        " m²). Adjust if needed.";
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    bind("ra-calc", calcRoofArea);
    bind("sh-calc", calcSheets);
    bind("gu-calc", calcGutter);
    bind("co-calc", calcCost);
    bind("pi-calc", calcPitch);
    bind("sc-calc", calcScrews);

    var mode = $("pi-mode");
    if (mode) {
      mode.addEventListener("change", syncPitchMode);
      syncPitchMode();
    }

    // Enter key on inputs inside .calc-form
    document.querySelectorAll(".calc-form").forEach(function (form) {
      form.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          e.preventDefault();
          var btn = form.querySelector("button[type='button']");
          if (btn) btn.click();
        }
      });
    });

    applyQueryParams();
  });
})();
