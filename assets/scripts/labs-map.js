/* labs-map.js — renders the research-map markers from /assets/data/labs.json
   and fills homepage stat counters when present. Single source of truth:
   _data/institutions.yml via tools/generate_network.py.

   Basemap: OpenFreeMap "Positron" vector style (free, no API key, OSM data),
   drawn with MapLibre GL through the maplibre-gl-leaflet bridge, loaded on
   demand. If WebGL or the CDN is unavailable, it falls back to muted
   OpenStreetMap raster tiles. (CARTO basemaps now require an API key.) */
(function () {
  var MAPLIBRE_JS = "https://cdnjs.cloudflare.com/ajax/libs/maplibre-gl/5.6.0/maplibre-gl.js";
  var MAPLIBRE_CSS = "https://cdnjs.cloudflare.com/ajax/libs/maplibre-gl/5.6.0/maplibre-gl.css";
  var BRIDGE_JS = "https://cdn.jsdelivr.net/npm/@maplibre/maplibre-gl-leaflet@0.1.4/leaflet-maplibre-gl.min.js";
  var STYLE_URL = "https://tiles.openfreemap.org/styles/positron";
  var OFM_ATTR = '<a href="https://openfreemap.org" target="_blank" rel="noopener">OpenFreeMap</a> ' +
    '&copy; <a href="https://www.openmaptiles.org/" target="_blank" rel="noopener">OpenMapTiles</a> ' +
    'Data from <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>';

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement("script");
      s.src = src; s.async = true; s.onload = resolve; s.onerror = reject;
      document.head.appendChild(s);
    });
  }
  function loadCss(href) {
    var l = document.createElement("link");
    l.rel = "stylesheet"; l.href = href;
    document.head.appendChild(l);
  }
  function webglOk() {
    try {
      var c = document.createElement("canvas");
      return !!(window.WebGLRenderingContext && (c.getContext("webgl2") || c.getContext("webgl")));
    } catch (e) { return false; }
  }
  function rasterFallback(map) {
    map.getContainer().classList.add("labmap--raster");
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
  }
  /* Bring Positron onto the site palette (theme.css tokens): white land,
     soft blue-grey water, no ocean names — the markers carry the story. */
  function tuneStyle(gl) {
    function paint(id, prop, val) { try { if (gl.getLayer(id)) gl.setPaintProperty(id, prop, val); } catch (e) {} }
    function hide(id) { try { if (gl.getLayer(id)) gl.setLayoutProperty(id, "visibility", "none"); } catch (e) {} }
    paint("background", "background-color", "#ffffff");
    paint("water", "fill-color", "#dfe6ee");
    paint("waterway", "line-color", "#dfe6ee");
    hide("water_name_point_label");
    hide("water_name_line_label");
    gl.getStyle().layers.forEach(function (l) {
      if (l.type === "symbol" && /place|country|continent/.test(l.id)) paint(l.id, "text-color", "#74808c");
    });
  }

  function addBasemap(map) {
    if (!webglOk()) { rasterFallback(map); return; }
    loadCss(MAPLIBRE_CSS);
    var p = window.maplibregl ? Promise.resolve() : loadScript(MAPLIBRE_JS);
    p.then(function () { return L.maplibreGL ? null : loadScript(BRIDGE_JS); })
      .then(function () {
        var layer = L.maplibreGL({ style: STYLE_URL, attribution: OFM_ATTR, interactive: false }).addTo(map);
        var gl = layer.getMaplibreMap && layer.getMaplibreMap();
        if (gl) gl.on("load", function () { tuneStyle(gl); });
      })
      .catch(function (e) { console.warn("labs-map: vector basemap unavailable", e); rasterFallback(map); });
  }

  var dataUrl = "/assets/data/labs.json";
  try {
    if (document.currentScript && document.currentScript.src) {
      dataUrl = new URL("../data/labs.json", document.currentScript.src).href;
    }
  } catch (e) { /* keep absolute fallback */ }
  function init() {
    fetch(dataUrl)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var s = data.stats;
        var el;
        if ((el = document.getElementById("stat-inst"))) el.textContent = s.institutions;
        if ((el = document.getElementById("stat-countries"))) el.textContent = s.countries;
        if ((el = document.getElementById("stat-core"))) el.textContent = s.core;
        if ((el = document.getElementById("stat-eco"))) el.textContent = s.ecosystems;
        if ((el = document.getElementById("country-line"))) {
          el.innerHTML = s.countries_list.join(" · ") +
            ' &nbsp;—&nbsp; <a href="/network/index.html">browse by country, tier, or ecosystem →</a>';
        }

        var mapEl = document.getElementById("labmap");
        if (!mapEl || typeof L === "undefined") return;

        var map = L.map(mapEl, {
          center: [30, 5],
          zoom: 2,
          minZoom: 2,
          maxZoom: 8,
          scrollWheelZoom: false,
          worldCopyJump: true
        });
        addBasemap(map);

        data.labs.forEach(function (lab) {
          var style = lab.tier === "engineered"
            ? { radius: 5, color: "#9a6f0b", weight: 2, fillColor: "#ffffff", fillOpacity: 1 }
            : { radius: 5, color: "#1b3a6b", weight: 1.5, fillColor: "#1b3a6b", fillOpacity: 0.85 };
          L.circleMarker([lab.lat, lab.lon], style)
            .bindTooltip("<strong>" + lab.short + "</strong><br/>" + lab.city + ", " + lab.country)
            .on("click", function () { window.location.href = lab.url; })
            .addTo(map);
        });
      })
      .catch(function (e) { console.warn("labs-map:", e); });
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
