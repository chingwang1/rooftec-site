/**
 * Satellite roof measure: search address → draw polygon → plan m² → cost estimator.
 * Uses Leaflet + Esri World Imagery (no Google billing key required).
 */
(function () {
  "use strict";

  var map = null;
  var drawnItems = null;
  var drawControl = null;
  var searchTimer = null;
  var lastPlanM2 = 0;
  var lastSurfaceM2 = 0;
  var lastLabel = "";

  function $(id) {
    return document.getElementById(id);
  }

  function fmt(n, d) {
    if (!isFinite(n)) return "—";
    return n.toLocaleString("en-AU", {
      maximumFractionDigits: d == null ? 1 : d,
      minimumFractionDigits: 0,
    });
  }

  function pitchFactor(degrees) {
    var rad = (degrees * Math.PI) / 180;
    return 1 / Math.cos(rad);
  }

  /** Geodesic polygon area in m² from Leaflet latLngs (closed or open). */
  function polygonAreaM2(latlngs) {
    if (!latlngs || latlngs.length < 3) return 0;

    // Prefer Turf if loaded
    if (typeof turf !== "undefined") {
      var coords = latlngs.map(function (ll) {
        return [ll.lng, ll.lat];
      });
      // close ring
      if (
        coords[0][0] !== coords[coords.length - 1][0] ||
        coords[0][1] !== coords[coords.length - 1][1]
      ) {
        coords.push(coords[0].slice());
      }
      try {
        return Math.abs(turf.area(turf.polygon([coords])));
      } catch (e) {
        /* fall through */
      }
    }

    // Spherical excess (Earth radius 6378137 m)
    var R = 6378137;
    var pts = latlngs.slice();
    if (
      pts[0].lat !== pts[pts.length - 1].lat ||
      pts[0].lng !== pts[pts.length - 1].lng
    ) {
      pts.push(pts[0]);
    }
    var total = 0;
    for (var i = 0; i < pts.length - 1; i++) {
      var p1 = pts[i];
      var p2 = pts[i + 1];
      total +=
        toRad(p2.lng - p1.lng) *
        (2 + Math.sin(toRad(p1.lat)) + Math.sin(toRad(p2.lat)));
    }
    return Math.abs((total * R * R) / 2);
  }

  function toRad(d) {
    return (d * Math.PI) / 180;
  }

  function sumDrawnArea() {
    var total = 0;
    if (!drawnItems) return 0;
    drawnItems.eachLayer(function (layer) {
      if (layer instanceof L.Polygon || layer instanceof L.Rectangle) {
        var latlngs = layer.getLatLngs();
        // Leaflet may nest rings
        var ring = Array.isArray(latlngs[0]) ? latlngs[0] : latlngs;
        total += polygonAreaM2(ring);
      }
    });
    return total;
  }

  function updateResults() {
    var plan = sumDrawnArea();
    lastPlanM2 = plan;
    var pitchEl = $("mm-pitch");
    var pitch = pitchEl ? parseFloat(pitchEl.value) : 0;
    if (!(pitch >= 0 && pitch < 80)) pitch = 0;
    var surface = plan * pitchFactor(pitch);
    lastSurfaceM2 = surface;

    var useSurface = $("mm-use-surface") && $("mm-use-surface").checked;
    var forQuote = useSurface && pitch > 0 ? surface : plan;

    setVisible("mm-result", plan > 0);
    if (plan <= 0) {
      setText("mm-status", "Draw a polygon around the roof outline on the satellite map.");
      return;
    }

    setText("mm-plan", fmt(plan, 1) + " m²");
    setText("mm-factor", pitch > 0 ? fmt(pitchFactor(pitch), 3) + "×" : "1.000× (flat / plan)");
    setText("mm-surface", fmt(surface, 1) + " m²");
    setText("mm-for-quote", fmt(forQuote, 1) + " m²");
    setText(
      "mm-status",
      lastLabel
        ? "Measured near: " + lastLabel
        : "Polygon measured — adjust points if needed, then send to the cost estimator."
    );

    // Update action links
    var q = encodeURIComponent(String(Math.round(forQuote * 10) / 10));
    var cost = $("mm-to-cost");
    var sheets = $("mm-to-sheets");
    var screws = $("mm-to-screws");
    if (cost) cost.href = "roof-cost-estimator.html?area=" + q;
    if (sheets) sheets.href = "roof-sheet-calculator.html?area=" + q;
    if (screws) screws.href = "screw-fastener-calculator.html?area=" + q;
  }

  function setText(id, text) {
    var el = $(id);
    if (el) el.textContent = text;
  }

  function setVisible(id, on) {
    var el = $(id);
    if (el) el.hidden = !on;
  }

  function clearSearchResults() {
    var box = $("mm-suggestions");
    if (box) {
      box.innerHTML = "";
      box.hidden = true;
    }
  }

  function showSuggestions(items) {
    var box = $("mm-suggestions");
    if (!box) return;
    box.innerHTML = "";
    if (!items.length) {
      box.hidden = true;
      return;
    }
    items.forEach(function (item) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "mm-suggest-item";
      btn.textContent = item.label;
      btn.addEventListener("click", function () {
        goTo(item.lat, item.lon, item.label);
        clearSearchResults();
        var input = $("mm-search");
        if (input) input.value = item.label;
      });
      box.appendChild(btn);
    });
    box.hidden = false;
  }

  function goTo(lat, lon, label) {
    lastLabel = label || "";
    if (!map) return;
    map.setView([lat, lon], 19);
    setText("mm-status", "Zoomed to property — draw the roof outline (polygon tool on the left).");
    // Open Google Maps in parallel for reference (optional link update)
    var g = $("mm-google-link");
    if (g) {
      g.href =
        "https://www.google.com/maps/search/?api=1&query=" +
        encodeURIComponent(lat + "," + lon);
      g.hidden = false;
    }
  }

  function searchAddress(query) {
    if (!query || query.length < 3) {
      clearSearchResults();
      return;
    }
    setText("mm-status", "Searching…");
    // Photon (Komoot) — free geocoder, bias to SEQ
    var url =
      "https://photon.komoot.io/api/?q=" +
      encodeURIComponent(query) +
      "&lat=-27.47&lon=153.03&limit=6&lang=en";

    fetch(url, { headers: { Accept: "application/json" } })
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        var feats = (data && data.features) || [];
        var items = feats.map(function (f) {
          var p = f.properties || {};
          var c = f.geometry && f.geometry.coordinates;
          var parts = [p.name, p.street, p.housenumber, p.city || p.county, p.state, p.country]
            .filter(Boolean);
          // Better label
          var label =
            p.name ||
            [p.housenumber, p.street, p.city || p.district, p.state]
              .filter(Boolean)
              .join(" ") ||
            parts.join(", ");
          if (p.city && label.indexOf(p.city) === -1) label += ", " + p.city;
          if (p.state && label.indexOf(p.state) === -1) label += ", " + p.state;
          return {
            lat: c[1],
            lon: c[0],
            label: label,
          };
        });
        // Prefer AU results
        items.sort(function (a, b) {
          var aAu = /Australia|Queensland|QLD|Brisbane|Coast/i.test(a.label) ? 0 : 1;
          var bAu = /Australia|Queensland|QLD|Brisbane|Coast/i.test(b.label) ? 0 : 1;
          return aAu - bAu;
        });
        if (!items.length) {
          setText("mm-status", "No matches — try suburb + street number (e.g. 12 Example St Brisbane).");
          clearSearchResults();
          return;
        }
        showSuggestions(items);
        setText("mm-status", "Pick an address from the list, then draw the roof.");
      })
      .catch(function () {
        setText(
          "mm-status",
          "Address search unavailable. Pan the map to your suburb, or open Google Maps for reference."
        );
        clearSearchResults();
      });
  }

  function initMap() {
    var el = $("mm-map");
    if (!el || typeof L === "undefined") return;

    map = L.map("mm-map", {
      center: [-27.4698, 153.0251],
      zoom: 12,
      maxZoom: 20,
    });

    // Satellite basemap (Esri World Imagery — free tile service)
    var sat = L.tileLayer(
      "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      {
        attribution:
          "Tiles &copy; Esri — Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community",
        maxZoom: 20,
        maxNativeZoom: 19,
      }
    );
    var labels = L.tileLayer(
      "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
      {
        attribution: "Labels &copy; Esri",
        maxZoom: 20,
        maxNativeZoom: 19,
        opacity: 0.85,
      }
    );
    sat.addTo(map);
    labels.addTo(map);

    L.control
      .layers(
        {
          Satellite: L.layerGroup([sat, labels]),
          Streets: L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "&copy; OpenStreetMap",
            maxZoom: 19,
          }),
        },
        null,
        { position: "topright" }
      )
      .addTo(map);

    drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    drawControl = new L.Control.Draw({
      position: "topleft",
      draw: {
        polygon: {
          allowIntersection: false,
          showArea: false,
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
      edit: {
        featureGroup: drawnItems,
        remove: true,
      },
    });
    map.addControl(drawControl);

    map.on(L.Draw.Event.CREATED, function (e) {
      drawnItems.addLayer(e.layer);
      updateResults();
    });
    map.on(L.Draw.Event.EDITED, updateResults);
    map.on(L.Draw.Event.DELETED, updateResults);

    // Fit SEQ-ish default already set
    setTimeout(function () {
      map.invalidateSize();
    }, 200);
  }

  function wireUi() {
    var search = $("mm-search");
    var btn = $("mm-search-btn");
    if (search) {
      search.addEventListener("input", function () {
        clearTimeout(searchTimer);
        var q = search.value.trim();
        searchTimer = setTimeout(function () {
          searchAddress(q);
        }, 400);
      });
      search.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          e.preventDefault();
          clearTimeout(searchTimer);
          searchAddress(search.value.trim());
        }
      });
    }
    if (btn) {
      btn.addEventListener("click", function () {
        searchAddress((search && search.value.trim()) || "");
      });
    }

    var pitch = $("mm-pitch");
    var useSurface = $("mm-use-surface");
    if (pitch) pitch.addEventListener("input", updateResults);
    if (useSurface) useSurface.addEventListener("change", updateResults);

    var clearBtn = $("mm-clear");
    if (clearBtn) {
      clearBtn.addEventListener("click", function () {
        if (drawnItems) drawnItems.clearLayers();
        updateResults();
        setText("mm-status", "Drawings cleared. Draw a new roof outline when ready.");
      });
    }

    // Click outside suggestions
    document.addEventListener("click", function (e) {
      var wrap = $("mm-search-wrap");
      if (wrap && !wrap.contains(e.target)) clearSearchResults();
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initMap();
    wireUi();
    updateResults();
  });
})();
