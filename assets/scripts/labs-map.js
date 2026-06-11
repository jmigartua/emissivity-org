/* labs-map.js — renders the research-map markers from /assets/data/labs.json
   and fills homepage stat counters when present. Single source of truth:
   _data/institutions.yml via tools/generate_network.py. */
(function () {
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
        L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
          subdomains: "abcd"
        }).addTo(map);

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
