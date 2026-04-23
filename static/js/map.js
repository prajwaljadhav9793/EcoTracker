let map = L.map('map').setView([20, 77], 5);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '© OpenStreetMap'
}).addTo(map);

let polyline = L.polyline([], { color: 'green' }).addTo(map);

let path = [];
let totalDistance = 0;
let watchId = null;


navigator.geolocation.getCurrentPosition(
  function(position) {
    let lat = position.coords.latitude;
    let lon = position.coords.longitude;

    map.setView([lat, lon], 17);

    L.marker([lat, lon]).addTo(map)
      .bindPopup("You are here 📍")
      .openPopup();
  },
  function(error) {
    alert("Location access denied or unavailable");
  },
  {
    enableHighAccuracy: true,
    timeout: 10000,
    maximumAge: 0
  }
);


function getDistance(lat1, lon1, lat2, lon2) {
  let R = 6371; // Earth radius in km

  let dLat = (lat2 - lat1) * Math.PI / 180;
  let dLon = (lon2 - lon1) * Math.PI / 180;

  let a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) *
    Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) *
    Math.sin(dLon / 2);

  let c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c; // distance in KM
}



function startTracking() {
   
    if (watchId !== null) {
    alert("Tracking already running ⚠️");
    return;
  }

  watchId = navigator.geolocation.watchPosition(
    function(position) {

      let lat = position.coords.latitude;
      let lon = position.coords.longitude;

      if (path.length > 0) {
        let prev = path[path.length - 1];

        let distance = getDistance(prev[0], prev[1], lat, lon);
        totalDistance += distance;
      }

      path.push([lat, lon]);

      polyline.addLatLng([lat, lon]);

      map.setView([lat, lon]);

      let carbon = totalDistance * 0.21;

      document.getElementById("info").innerHTML =
        "Distance: " + totalDistance.toFixed(2) + " km <br>" +
        "Carbon: " + carbon.toFixed(2) + " kg CO₂";

    },
    function(error) {
      alert("Error getting location");
    },
    {
      enableHighAccuracy: true,
      maximumAge: 0,
      timeout: 10000
    }
  );
}


function stopTracking() {

  if (watchId !== null) {
    navigator.geolocation.clearWatch(watchId);
    watchId = null;
  }

  let distance = totalDistance.toFixed(2);

  // redirect to calculator (NOT result)
  window.location.href = "/calculator?distance=" + distance;
}