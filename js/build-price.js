/**
 * Build & price configurator + satellite map measure (single page).
 * Pricing is SEQ planning estimate only — not a fixed quote.
 */
(function () {
  "use strict";

  // ── Competitive SEQ rates (transparent breakdown) ─────────────
  // Competitor (QQR) reverse-engineered approx:
  //   ((base + 19 + 14 + 1.785 + profileExtra) * m2 + 1950) * 1.1
  //   base: Metal 108, Decramastic 122; Kliplok +10
  // We undercut slightly and expose the line items.
  var RATES = {
    basePerM2: {
      metal: 102, // vs ~108
      tile: 115, // vs ~122 (includes strip allowance)
      unknown: 108,
    },
    flashingsPerM2: 17, // valleys, ridges, barges package
    installPerM2: 13, // labour/install band
    wastePerM2: 1.6, // cuts / waste allowance
    profileExtra: {
      corrugated: 0,
      trimdek: 2,
      kliplok: 9, // vs +10
    },
    storeyMult: {
      single: 1,
      double: 1.12,
      complex: 1.22,
    },
    fixedSetup: 1750, // vs ~1950
    contingency: 1.08, // vs 1.10
    // Optional add-ons (toggles)
    guttersPerM2: 18,
    sarkingPerM2: 12,
    solarCoordFixed: 650,
  };

  var COLOURS = [
    { name: "Dover White", hex: "#f8fbf1" },
    { name: "Surfmist", hex: "#e4e2d5" },
    { name: "Southerly", hex: "#d2d1cb" },
    { name: "Shale Grey", hex: "#bcbfb9" },
    { name: "Bluegum", hex: "#969799" },
    { name: "Windspray", hex: "#888b8a" },
    { name: "Basalt", hex: "#6D6C6E" },
    { name: "Classic Cream", hex: "#e9dbb8" },
    { name: "Paperbark", hex: "#cabea4" },
    { name: "Evening Haze", hex: "#c4c2a9" },
    { name: "Dune", hex: "#B1ADA3" },
    { name: "Gully", hex: "#857E73" },
    { name: "Jasper", hex: "#6C6153" },
    { name: "Manor Red", hex: "#5E1D0E" },
    { name: "Wallaby", hex: "#7F7C78" },
    { name: "Woodland Grey", hex: "#4B4C46" },
    { name: "Pale Eucalypt", hex: "#7C846A" },
    { name: "Cottage Green", hex: "#304C3C" },
    { name: "Ironstone", hex: "#3E434C" },
    { name: "Deep Ocean", hex: "#364152" },
    { name: "Night Sky", hex: "#000000" },
    { name: "Monument", hex: "#323233" },
  ];

  var state = {
    areaM2: 160,
    planM2: 0,
    pitch: 22.5,
    useSurface: true,
    storey: "single",
    profile: "corrugated",
    colour: "Surfmist",
    currentRoof: "metal",
    gutters: true,
    sarking: true,
    solar: false,
    addressLabel: "",
  };

  var map = null;
  var drawnItems = null;
  var searchTimer = null;

  function $(id) {
    return document.getElementById(id);
  }

  function money(n) {
    return (
      "$" +
      Math.round(n).toLocaleString("en-AU", { maximumFractionDigits: 0 })
    );
  }

  function fmt(n, d) {
    if (!isFinite(n)) return "—";
    return n.toLocaleString("en-AU", {
      maximumFractionDigits: d == null ? 1 : d,
      minimumFractionDigits: 0,
    });
  }

  function pitchFactor(deg) {
    return 1 / Math.cos((deg * Math.PI) / 180);
  }

  function isLight(hex) {
    var h = hex.replace("#", "");
    if (h.length === 3)
      h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
    var r = parseInt(h.slice(0, 2), 16);
    var g = parseInt(h.slice(2, 4), 16);
    var b = parseInt(h.slice(4, 6), 16);
    return (r * 299 + g * 587 + b * 114) / 1000 > 160;
  }

  function computePrice() {
    var m2 = Math.max(0, state.areaM2 || 0);
    var base = RATES.basePerM2[state.currentRoof] || RATES.basePerM2.unknown;
    var profileEx = RATES.profileExtra[state.profile] || 0;
    var perM2 =
      base +
      RATES.flashingsPerM2 +
      RATES.installPerM2 +
      RATES.wastePerM2 +
      profileEx;
    if (state.gutters) perM2 += RATES.guttersPerM2;
    if (state.sarking) perM2 += RATES.sarkingPerM2;

    var storeyMult = RATES.storeyMult[state.storey] || 1;
    var sub =
      (perM2 * m2 + RATES.fixedSetup + (state.solar ? RATES.solarCoordFixed : 0)) *
      storeyMult;
    var total = sub * RATES.contingency;

    return {
      m2: m2,
      base: base,
      profileEx: profileEx,
      perM2: perM2,
      storeyMult: storeyMult,
      fixed: RATES.fixedSetup + (state.solar ? RATES.solarCoordFixed : 0),
      sub: sub,
      total: total,
      low: total * 0.92,
      high: total * 1.12,
    };
  }

  function profileLabel(p) {
    return { corrugated: "Corrugated", trimdek: "Trimdek", kliplok: "Kliplok" }[p] || p;
  }

  function storeyLabel(s) {
    return { single: "Single storey", double: "Double storey", complex: "Complex / steep" }[s] || s;
  }

  function currentLabel(c) {
    return {
      metal: "Existing metal",
      tile: "Tile / decramastic",
      unknown: "Not sure",
    }[c] || c;
  }

  function renderPrice() {
    var p = computePrice();
    setText("bp-total", money(p.total));
    setText("bp-range", money(p.low) + " – " + money(p.high));
    setText("bp-per-m2", money(p.perM2) + " / m² package");
    setText("bp-area-display", "Based on " + fmt(p.m2, 1) + " m²");

    // Breakdown
    var rows = [
      ["Roof area used", fmt(p.m2, 1) + " m²"],
      ["Base re-roof rate", money(p.base) + " / m² (" + currentLabel(state.currentRoof) + ")"],
      ["Flashings package", money(RATES.flashingsPerM2) + " / m²"],
      ["Install labour band", money(RATES.installPerM2) + " / m²"],
      ["Waste / cuts", money(RATES.wastePerM2) + " / m²"],
    ];
    if (p.profileEx)
      rows.push(["Profile premium (" + profileLabel(state.profile) + ")", "+" + money(p.profileEx) + " / m²"]);
    if (state.gutters) rows.push(["Gutters & downpipes", "+" + money(RATES.guttersPerM2) + " / m²"]);
    if (state.sarking) rows.push(["Sarking / insulation band", "+" + money(RATES.sarkingPerM2) + " / m²"]);
    if (state.solar) rows.push(["Solar coordination", money(RATES.solarCoordFixed) + " fixed"]);
    rows.push(["Site setup / access", money(RATES.fixedSetup)]);
    if (p.storeyMult > 1)
      rows.push(["Storey / complexity", "×" + p.storeyMult.toFixed(2)]);
    rows.push(["Planning contingency", "×" + RATES.contingency.toFixed(2)]);

    var tbody = $("bp-breakdown");
    if (tbody) {
      tbody.innerHTML = rows
        .map(function (r) {
          return (
            "<tr><td>" +
            r[0] +
            '</td><td class="bp-num">' +
            r[1] +
            "</td></tr>"
          );
        })
        .join("");
    }

    // Summary chips
    setText("sum-storey", storeyLabel(state.storey));
    setText("sum-profile", profileLabel(state.profile));
    setText("sum-colour", state.colour);
    setText("sum-current", currentLabel(state.currentRoof));
    setText("sum-area", fmt(p.m2, 1) + " m²");

    // Preview swatch
    var prev = $("bp-preview");
    if (prev) {
      var col = COLOURS.find(function (c) {
        return c.name === state.colour;
      });
      var hex = col ? col.hex : "#e4e2d5";
      prev.style.background = hex;
      prev.setAttribute("data-profile", state.profile);
      var label = $("bp-preview-label");
      if (label) {
        label.textContent = profileLabel(state.profile) + " · " + state.colour;
        label.style.color = isLight(hex) ? "#1a2b4a" : "#fff";
      }
    }

    // Sticky bar
    setText("bp-sticky-total", money(p.total));
    setText("bp-sticky-area", fmt(p.m2, 1) + " m²");
  }

  function setText(id, text) {
    var el = $(id);
    if (el) el.textContent = text;
  }

  function setAreaFromMap(planM2) {
    state.planM2 = planM2;
    var pitch = state.pitch;
    var surface = planM2 * pitchFactor(pitch);
    var use = state.useSurface && pitch > 0 ? surface : planM2;
    if (use > 0) {
      state.areaM2 = Math.round(use * 10) / 10;
      var input = $("bp-area");
      if (input) input.value = String(state.areaM2);
      setText(
        "mm-status",
        "Map measured " +
          fmt(planM2, 1) +
          " m² plan" +
          (state.useSurface ? " → " + fmt(surface, 1) + " m² surface (pitch " + pitch + "°)" : "") +
          ". Area field updated."
      );
      setText("mm-plan", fmt(planM2, 1) + " m²");
      setText("mm-surface", fmt(surface, 1) + " m²");
      var box = $("mm-result");
      if (box) box.hidden = false;
    }
    renderPrice();
  }

  // ── Map ──────────────────────────────────────────────────────
  function polygonAreaM2(latlngs) {
    if (!latlngs || latlngs.length < 3) return 0;
    if (typeof turf !== "undefined") {
      var coords = latlngs.map(function (ll) {
        return [ll.lng, ll.lat];
      });
      if (
        coords[0][0] !== coords[coords.length - 1][0] ||
        coords[0][1] !== coords[coords.length - 1][1]
      )
        coords.push(coords[0].slice());
      try {
        return Math.abs(turf.area(turf.polygon([coords])));
      } catch (e) {}
    }
    var R = 6378137;
    var pts = latlngs.slice();
    if (
      pts[0].lat !== pts[pts.length - 1].lat ||
      pts[0].lng !== pts[pts.length - 1].lng
    )
      pts.push(pts[0]);
    var total = 0;
    function rad(d) {
      return (d * Math.PI) / 180;
    }
    for (var i = 0; i < pts.length - 1; i++) {
      var p1 = pts[i],
        p2 = pts[i + 1];
      total +=
        rad(p2.lng - p1.lng) * (2 + Math.sin(rad(p1.lat)) + Math.sin(rad(p2.lat)));
    }
    return Math.abs((total * R * R) / 2);
  }

  function sumDrawnArea() {
    var total = 0;
    if (!drawnItems) return 0;
    drawnItems.eachLayer(function (layer) {
      if (layer instanceof L.Polygon || layer instanceof L.Rectangle) {
        var latlngs = layer.getLatLngs();
        var ring = Array.isArray(latlngs[0]) ? latlngs[0] : latlngs;
        total += polygonAreaM2(ring);
      }
    });
    return total;
  }

  function initMap() {
    var el = $("mm-map");
    if (!el || typeof L === "undefined") return;

    map = L.map("mm-map", {
      center: [-27.4698, 153.0251],
      zoom: 12,
      maxZoom: 20,
    });

    var sat = L.tileLayer(
      "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      {
        attribution: "Tiles © Esri — Maxar, Earthstar Geographics",
        maxZoom: 20,
        maxNativeZoom: 19,
      }
    );
    var labels = L.tileLayer(
      "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
      { maxZoom: 20, maxNativeZoom: 19, opacity: 0.85 }
    );
    sat.addTo(map);
    labels.addTo(map);

    drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    map.addControl(
      new L.Control.Draw({
        position: "topleft",
        draw: {
          polygon: {
            allowIntersection: false,
            shapeOptions: {
              color: "#c45c26",
              weight: 2,
              fillColor: "#c45c26",
              fillOpacity: 0.25,
            },
          },
          rectangle: {
            shapeOptions: {
              color: "#c45c26",
              weight: 2,
              fillColor: "#c45c26",
              fillOpacity: 0.25,
            },
          },
          polyline: false,
          circle: false,
          circlemarker: false,
          marker: false,
        },
        edit: { featureGroup: drawnItems, remove: true },
      })
    );

    function onDrawChange() {
      var plan = sumDrawnArea();
      if (plan > 0) setAreaFromMap(plan);
      else {
        var box = $("mm-result");
        if (box) box.hidden = true;
      }
    }

    map.on(L.Draw.Event.CREATED, function (e) {
      drawnItems.addLayer(e.layer);
      onDrawChange();
    });
    map.on(L.Draw.Event.EDITED, onDrawChange);
    map.on(L.Draw.Event.DELETED, onDrawChange);

    setTimeout(function () {
      map.invalidateSize();
    }, 250);
  }

  function searchAddress(query) {
    if (!query || query.length < 3) return;
    setText("mm-status", "Searching…");
    var url =
      "https://photon.komoot.io/api/?q=" +
      encodeURIComponent(query) +
      "&lat=-27.47&lon=153.03&limit=6&lang=en";
    fetch(url)
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        var box = $("mm-suggestions");
        if (!box) return;
        box.innerHTML = "";
        var feats = (data && data.features) || [];
        if (!feats.length) {
          setText("mm-status", "No matches — try street number + suburb.");
          box.hidden = true;
          return;
        }
        feats.forEach(function (f) {
          var p = f.properties || {};
          var c = f.geometry.coordinates;
          var label =
            [p.housenumber, p.street || p.name, p.city || p.district, p.state]
              .filter(Boolean)
              .join(" ") || p.name;
          var btn = document.createElement("button");
          btn.type = "button";
          btn.className = "mm-suggest-item";
          btn.textContent = label;
          btn.addEventListener("click", function () {
            state.addressLabel = label;
            map.setView([c[1], c[0]], 19);
            var input = $("mm-search");
            if (input) input.value = label;
            box.hidden = true;
            setText(
              "mm-status",
              "Zoomed to property — draw the roof outline with the polygon tool."
            );
            var g = $("mm-google-link");
            if (g) {
              g.href =
                "https://www.google.com/maps/search/?api=1&query=" +
                encodeURIComponent(c[1] + "," + c[0]);
            }
          });
          box.appendChild(btn);
        });
        box.hidden = false;
        setText("mm-status", "Pick an address, then draw the roof.");
      })
      .catch(function () {
        setText("mm-status", "Search unavailable — pan the map manually.");
      });
  }

  // ── UI wiring ────────────────────────────────────────────────
  function selectToggle(groupSelector, valueAttr, stateKey) {
    document.querySelectorAll(groupSelector).forEach(function (btn) {
      btn.addEventListener("click", function () {
        document.querySelectorAll(groupSelector).forEach(function (b) {
          b.classList.remove("is-active");
        });
        btn.classList.add("is-active");
        state[stateKey] = btn.getAttribute(valueAttr);
        renderPrice();
      });
    });
  }

  function renderColours() {
    var grid = $("bp-colours");
    if (!grid) return;
    grid.innerHTML = "";
    COLOURS.forEach(function (c) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className =
        "bp-swatch" + (c.name === state.colour ? " is-active" : "");
      btn.style.background = c.hex;
      btn.title = c.name;
      btn.setAttribute("aria-label", c.name);
      btn.addEventListener("click", function () {
        state.colour = c.name;
        renderColours();
        renderPrice();
      });
      grid.appendChild(btn);
    });
  }

  function wireForm() {
    var area = $("bp-area");
    if (area) {
      area.value = String(state.areaM2);
      area.addEventListener("input", function () {
        var v = parseFloat(area.value);
        if (v > 0) state.areaM2 = v;
        renderPrice();
      });
    }

    var pitch = $("mm-pitch");
    if (pitch) {
      pitch.value = String(state.pitch);
      pitch.addEventListener("input", function () {
        state.pitch = parseFloat(pitch.value) || 0;
        if (state.planM2 > 0) setAreaFromMap(state.planM2);
        else renderPrice();
      });
    }

    var useSurface = $("mm-use-surface");
    if (useSurface) {
      useSurface.checked = state.useSurface;
      useSurface.addEventListener("change", function () {
        state.useSurface = useSurface.checked;
        if (state.planM2 > 0) setAreaFromMap(state.planM2);
      });
    }

    selectToggle("[data-storey]", "data-storey", "storey");
    selectToggle("[data-profile]", "data-profile", "profile");
    selectToggle("[data-current]", "data-current", "currentRoof");

    ["bp-gutters", "bp-sarking", "bp-solar"].forEach(function (id) {
      var el = $(id);
      if (!el) return;
      var key = id.replace("bp-", "");
      if (key === "gutters") el.checked = state.gutters;
      if (key === "sarking") el.checked = state.sarking;
      if (key === "solar") el.checked = state.solar;
      el.addEventListener("change", function () {
        if (key === "gutters") state.gutters = el.checked;
        if (key === "sarking") state.sarking = el.checked;
        if (key === "solar") state.solar = el.checked;
        renderPrice();
      });
    });

    var search = $("mm-search");
    var sbtn = $("mm-search-btn");
    if (search) {
      search.addEventListener("input", function () {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(function () {
          searchAddress(search.value.trim());
        }, 400);
      });
      search.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          e.preventDefault();
          searchAddress(search.value.trim());
        }
      });
    }
    if (sbtn)
      sbtn.addEventListener("click", function () {
        searchAddress((search && search.value.trim()) || "");
      });

    var clearBtn = $("mm-clear");
    if (clearBtn) {
      clearBtn.addEventListener("click", function () {
        if (drawnItems) drawnItems.clearLayers();
        state.planM2 = 0;
        var box = $("mm-result");
        if (box) box.hidden = true;
        setText("mm-status", "Drawings cleared.");
      });
    }

    document.addEventListener("click", function (e) {
      var wrap = $("mm-search-wrap");
      var box = $("mm-suggestions");
      if (wrap && box && !wrap.contains(e.target)) box.hidden = true;
    });

    // Enquiry form: attach estimate summary to message on submit
    var enq = $("bp-enquiry-msg");
    if (enq) {
      var form = enq.closest("form");
      if (form) {
        form.addEventListener(
          "submit",
          function () {
            var p = computePrice();
            var notes = enq.value.trim();
            if (notes.indexOf("Build & price enquiry") === 0) return;
            enq.value =
              "Build & price enquiry\n" +
              "Area: " +
              fmt(p.m2, 1) +
              " m²\n" +
              "Profile: " +
              profileLabel(state.profile) +
              "\n" +
              "Colour: " +
              state.colour +
              "\n" +
              "Current roof: " +
              currentLabel(state.currentRoof) +
              "\n" +
              "Storey: " +
              storeyLabel(state.storey) +
              "\n" +
              "Est. price: " +
              money(p.total) +
              " (range " +
              money(p.low) +
              " – " +
              money(p.high) +
              ")\n" +
              (state.addressLabel ? "Address: " + state.addressLabel + "\n" : "") +
              (notes ? "\nCustomer notes:\n" + notes : "");
          },
          true
        );
      }
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    // URL ?area=
    var params = new URLSearchParams(window.location.search);
    var area = parseFloat(params.get("area"));
    if (area > 0) state.areaM2 = area;

    initMap();
    renderColours();
    wireForm();
    renderPrice();

    // Mark default toggles active
    document
      .querySelectorAll('[data-storey="' + state.storey + '"]')
      .forEach(function (b) {
        b.classList.add("is-active");
      });
    document
      .querySelectorAll('[data-profile="' + state.profile + '"]')
      .forEach(function (b) {
        b.classList.add("is-active");
      });
    document
      .querySelectorAll('[data-current="' + state.currentRoof + '"]')
      .forEach(function (b) {
        b.classList.add("is-active");
      });
  });
})();
