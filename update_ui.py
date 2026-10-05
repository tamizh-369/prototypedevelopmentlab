import os

templates_dir = "D:/PDL/templates"

files = {}

files['base.html'] = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}SOS Ambulance{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        glass: 'rgba(255, 255, 255, 0.05)',
                        glassBorder: 'rgba(255, 255, 255, 0.1)',
                    }
                }
            }
        }
    </script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        /* Custom map styling for dark mode */
        .leaflet-container { background: #0f172a; }
        .leaflet-layer,
        .leaflet-control-zoom-in,
        .leaflet-control-zoom-out,
        .leaflet-control-attribution { filter: invert(100%) hue-rotate(180deg) brightness(95%) contrast(90%); }
    </style>
    {% block head %}{% endblock %}
</head>
<body class="bg-slate-950 text-slate-200 min-h-screen relative overflow-x-hidden font-sans">
    
    <!-- Ambient glowing orbs background -->
    <div class="fixed inset-0 z-[-1] pointer-events-none overflow-hidden">
        <div class="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-blue-600/20 rounded-full blur-[120px]"></div>
        <div class="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-purple-600/20 rounded-full blur-[120px]"></div>
    </div>

    <nav class="bg-glass backdrop-blur-xl border-b border-glassBorder text-white p-4 sticky top-0 z-50 shadow-lg">
        <div class="container mx-auto flex justify-between items-center">
            <a href="/" class="text-xl font-bold tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">SOS DISPATCH</a>
            <div class="space-x-4 text-sm font-medium">
                {% if current_user.is_authenticated %}
                    <a href="/logout" class="hover:text-blue-400 transition">Logout</a>
                {% else %}
                    <a href="/admin/login" class="hover:text-blue-400 transition">Admin</a>
                    <a href="/driver/login" class="hover:text-blue-400 transition">Driver</a>
                {% endif %}
            </div>
        </div>
    </nav>

    <div class="container mx-auto p-4 md:p-8">
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <div class="mb-6 space-y-2">
                {% for message in messages %}
                    <div class="bg-red-500/20 border border-red-500/50 backdrop-blur-md text-red-200 p-4 rounded-xl shadow-lg">{{ message }}</div>
                {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </div>

    <script>
        gsap.from(".gsap-fade", {y: 30, opacity: 0, duration: 0.8, stagger: 0.1, ease: "power3.out"});
    </script>
</body>
</html>"""

files['index.html'] = """{% extends "base.html" %}
{% block content %}
<div class="max-w-3xl mx-auto mt-20 text-center gsap-fade">
    <div class="inline-block p-3 rounded-2xl bg-blue-500/10 border border-blue-500/20 backdrop-blur-md mb-6">
        <span class="text-blue-400 font-semibold tracking-widest text-sm uppercase">Live Dispatch System</span>
    </div>
    <h1 class="text-5xl md:text-7xl font-extrabold mb-6 tracking-tight">
        Rapid Emergency <br/>
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">Response</span>
    </h1>
    <p class="text-lg md:text-xl text-slate-400 mb-10 max-w-2xl mx-auto font-light">
        A glassmorphic, intelligent dispatch engine. Hit the button below to instantly trigger an SOS and watch the nearest ambulance route directly to you.
    </p>
    <a href="/report" class="inline-block bg-blue-600 hover:bg-blue-500 text-white px-8 py-4 rounded-xl text-lg font-bold shadow-lg shadow-blue-500/25 transition-all hover:scale-105 active:scale-95">
        Trigger Emergency SOS
    </a>
</div>
{% endblock %}"""

files['report.html'] = """{% extends "base.html" %}
{% block content %}
<div class="max-w-lg mx-auto mt-12 gsap-fade">
    <div class="bg-glass backdrop-blur-2xl border border-glassBorder p-8 rounded-3xl shadow-2xl relative overflow-hidden">
        <!-- Decoration inside card -->
        <div class="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-full blur-2xl transform translate-x-1/2 -translate-y-1/2"></div>
        
        <h2 class="text-3xl font-bold mb-8 text-white tracking-tight">Report Incident</h2>
        
        <form id="reportForm" class="space-y-6 relative z-10">
            <div>
                <label class="block text-slate-300 text-sm font-medium mb-2">Emergency Severity</label>
                <select id="severity" class="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition">
                    <option value="general">General Medical</option>
                    <option value="trauma">Trauma / Accident</option>
                    <option value="icu">Critical / ICU</option>
                </select>
            </div>
            
            <div>
                <label class="block text-slate-300 text-sm font-medium mb-2">Contact Number</label>
                <input type="text" id="contact" class="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-slate-200 focus:ring-2 focus:ring-blue-500 outline-none transition placeholder-slate-600" placeholder="e.g. 9876543210" required>
            </div>
            
            <div class="pt-2">
                <button type="button" id="getLocationBtn" class="w-full bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-200 px-4 py-3 rounded-xl transition flex items-center justify-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" /></svg>
                    Fetch My Coordinates
                </button>
                <p id="locationStatus" class="text-xs text-blue-400 mt-3 text-center h-4"></p>
            </div>
            
            <input type="hidden" id="lat">
            <input type="hidden" id="lng">
            
            <button type="submit" class="w-full bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white px-4 py-4 rounded-xl font-bold shadow-lg shadow-red-500/25 transition-all active:scale-95 text-lg uppercase tracking-wider">
                Dispatch Ambulance Now
            </button>
        </form>
    </div>
</div>

<script>
    document.getElementById('getLocationBtn').addEventListener('click', () => {
        const status = document.getElementById('locationStatus');
        status.textContent = "Acquiring GPS signal...";
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                document.getElementById('lat').value = pos.coords.latitude;
                document.getElementById('lng').value = pos.coords.longitude;
                status.textContent = "Coordinates locked successfully.";
            },
            (err) => {
                status.textContent = "Error: " + err.message;
            }
        );
    });

    document.getElementById('reportForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const lat = document.getElementById('lat').value;
        const lng = document.getElementById('lng').value;
        const severity = document.getElementById('severity').value;
        const contact = document.getElementById('contact').value;

        if (!lat || !lng) {
            alert("Please fetch coordinates first.");
            return;
        }

        const res = await fetch('/api/signal', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({lat, lng, severity, contact})
        });
        const data = await res.json();
        if (data.tracking_token) {
            window.location.href = `/track/${data.tracking_token}`;
        } else {
            alert("Error reporting incident: " + (data.error || "Unknown"));
        }
    });
</script>
{% endblock %}"""

files['track.html'] = """{% extends "base.html" %}
{% block content %}
<div class="max-w-4xl mx-auto mt-6 gsap-fade">
    <div class="flex flex-col md:flex-row gap-6 mb-6">
        <div class="w-full md:w-1/3 space-y-6">
            <div class="bg-glass backdrop-blur-xl border border-glassBorder p-6 rounded-3xl shadow-xl">
                <h3 class="text-slate-400 text-sm font-semibold uppercase tracking-wider mb-2">Live Status</h3>
                <div class="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400 mb-4" id="status">
                    {{ incident.status | title }}
                </div>
                
                <div class="space-y-4">
                    <div>
                        <p class="text-slate-500 text-xs uppercase tracking-wider">Assigned Unit</p>
                        <p id="ambulanceNumber" class="text-lg font-medium text-slate-200">Pending...</p>
                    </div>
                    <div>
                        <p class="text-slate-500 text-xs uppercase tracking-wider">Est. Arrival Time</p>
                        <p id="etaText" class="text-2xl font-bold text-green-400">Calculating...</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-glass backdrop-blur-xl border border-glassBorder p-6 rounded-3xl shadow-xl">
                <h3 class="text-slate-400 text-sm font-semibold uppercase tracking-wider mb-4">Incident Details</h3>
                <ul class="space-y-2 text-sm">
                    <li class="flex justify-between border-b border-slate-700/50 pb-2"><span class="text-slate-500">Severity</span> <span class="text-slate-200 capitalize">{{ incident.severity }}</span></li>
                    <li class="flex justify-between border-b border-slate-700/50 pb-2"><span class="text-slate-500">Contact</span> <span class="text-slate-200">{{ incident.reporter_contact }}</span></li>
                </ul>
            </div>
        </div>
        
        <div class="w-full md:w-2/3">
            <div class="bg-glass backdrop-blur-xl border border-glassBorder p-2 rounded-3xl shadow-xl h-[500px]">
                <div id="map" class="w-full h-full rounded-2xl z-0"></div>
            </div>
        </div>
    </div>
</div>

<script>
    const token = '{{ incident.tracking_token }}';
    const incidentLat = {{ incident.lat }};
    const incidentLng = {{ incident.lng }};
    
    const map = L.map('map').setView([incidentLat, incidentLng], 14);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);
    
    // Custom icons for dark theme
    const incIcon = L.icon({iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png', iconSize: [25, 41], iconAnchor: [12, 41]});
    const ambIcon = L.icon({iconUrl: 'https://cdn-icons-png.flaticon.com/512/320/320150.png', iconSize: [40, 40], className: 'invert-0'});

    L.marker([incidentLat, incidentLng], {icon: incIcon}).addTo(map).bindPopup("<b>Emergency Location</b>").openPopup();
    
    let ambMarker = null;
    let routeLayer = null;

    async function drawRoute(startLat, startLng, endLat, endLng) {
        try {
            const response = await fetch(`https://router.project-osrm.org/route/v1/driving/${startLng},${startLat};${endLng},${endLat}?overview=full&geometries=geojson`);
            const data = await response.json();
            
            if (data.routes && data.routes.length > 0) {
                const route = data.routes[0];
                const etaMinutes = Math.max(1, Math.round(route.duration / 60));
                
                document.getElementById('etaText').textContent = etaMinutes + " min";

                if (routeLayer) map.removeLayer(routeLayer);
                
                routeLayer = L.geoJSON(route.geometry, {
                    style: { color: '#60a5fa', weight: 6, opacity: 0.8, lineCap: 'round', dashArray: '1, 10' }
                }).addTo(map);
                
                map.fitBounds(routeLayer.getBounds(), { padding: [50, 50] });
            }
        } catch (e) {
            console.error("Routing error:", e);
        }
    }

    async function pollStatus() {
        const res = await fetch(`/api/incident/${token}`);
        const data = await res.json();
        
        document.getElementById('status').textContent = data.status.toUpperCase();
        
        if (data.ambulance && data.ambulance.id) {
            document.getElementById('ambulanceNumber').textContent = data.ambulance.vehicle_number;
            
            if (data.ambulance.lat && data.ambulance.lng) {
                if (!ambMarker) {
                    ambMarker = L.marker([data.ambulance.lat, data.ambulance.lng], {icon: ambIcon}).addTo(map);
                    drawRoute(data.ambulance.lat, data.ambulance.lng, incidentLat, incidentLng);
                } else {
                    ambMarker.setLatLng([data.ambulance.lat, data.ambulance.lng]);
                }
            }
        }
    }
    
    pollStatus();
    setInterval(pollStatus, 5000);
</script>
{% endblock %}"""

files['admin_login.html'] = """{% extends "base.html" %}
{% block content %}
<div class="max-w-sm mx-auto mt-24 gsap-fade">
    <div class="bg-glass backdrop-blur-2xl border border-glassBorder p-8 rounded-3xl shadow-2xl">
        <h2 class="text-2xl font-bold mb-6 text-center tracking-wide">Admin Portal</h2>
        <form method="POST" class="space-y-4">
            <input type="text" name="username" placeholder="Username" class="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-slate-200 outline-none focus:ring-2 focus:ring-purple-500" required>
            <input type="password" name="password" placeholder="Password" class="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-slate-200 outline-none focus:ring-2 focus:ring-purple-500" required>
            <button type="submit" class="w-full bg-purple-600 hover:bg-purple-500 text-white p-3 rounded-xl font-bold shadow-lg shadow-purple-500/25 transition">Access Command Center</button>
        </form>
    </div>
</div>
{% endblock %}"""

files['driver_login.html'] = """{% extends "base.html" %}
{% block content %}
<div class="max-w-sm mx-auto mt-24 gsap-fade">
    <div class="bg-glass backdrop-blur-2xl border border-glassBorder p-8 rounded-3xl shadow-2xl">
        <h2 class="text-2xl font-bold mb-6 text-center tracking-wide">Driver Terminal</h2>
        <form method="POST" class="space-y-4">
            <input type="text" name="username" placeholder="Driver ID" class="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-slate-200 outline-none focus:ring-2 focus:ring-green-500" required>
            <input type="password" name="password" placeholder="PIN code" class="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-slate-200 outline-none focus:ring-2 focus:ring-green-500" required>
            <button type="submit" class="w-full bg-green-600 hover:bg-green-500 text-white p-3 rounded-xl font-bold shadow-lg shadow-green-500/25 transition">Login to Unit</button>
        </form>
    </div>
</div>
{% endblock %}"""

files['admin_dashboard.html'] = """{% extends "base.html" %}
{% block content %}
<div class="h-[85vh] flex flex-col md:flex-row gap-6 gsap-fade">
    <div class="w-full md:w-1/3 bg-glass backdrop-blur-xl border border-glassBorder rounded-3xl shadow-xl flex flex-col overflow-hidden">
        <div class="p-6 border-b border-glassBorder bg-white/5">
            <h2 class="text-xl font-bold tracking-wide">Active Dispatches</h2>
        </div>
        <div class="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
            {% for inc in incidents %}
            <div class="bg-slate-900/40 border border-slate-700/50 p-4 rounded-2xl hover:bg-slate-800/60 transition">
                <div class="flex justify-between items-start mb-2">
                    <span class="text-xs text-slate-400">ID: #{{ inc.id }}</span>
                    <span class="px-2 py-1 bg-blue-500/20 text-blue-400 text-[10px] uppercase font-bold rounded">{{ inc.status }}</span>
                </div>
                <p class="text-sm text-slate-300 capitalize mb-3">Sev: {{ inc.severity }}</p>
                <a href="/track/{{ inc.tracking_token }}" target="_blank" class="inline-block text-xs text-blue-400 hover:text-blue-300 border border-blue-500/30 rounded-lg px-3 py-1 bg-blue-500/10 transition">View Tracker &rarr;</a>
            </div>
            {% else %}
            <p class="text-slate-500 text-center py-10">No active incidents.</p>
            {% endfor %}
        </div>
    </div>
    <div class="w-full md:w-2/3 bg-glass backdrop-blur-xl border border-glassBorder p-2 rounded-3xl shadow-xl">
        <div id="map" class="h-full w-full rounded-2xl z-0"></div>
    </div>
</div>

<style>
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
</style>

<script>
    const map = L.map('map').setView([13.0827, 80.2707], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);
    
    const incIcon = L.icon({iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png', iconSize: [25, 41], iconAnchor: [12, 41]});
    const ambIcon = L.icon({iconUrl: 'https://cdn-icons-png.flaticon.com/512/320/320150.png', iconSize: [30, 30], className: 'invert-0'});

    let markers = {};

    async function fetchAdminData() {
        const res = await fetch('/api/admin/data');
        const data = await res.json();
        
        Object.values(markers).forEach(m => map.removeLayer(m));
        markers = {};
        
        data.incidents.forEach(inc => {
            if(inc.status !== 'completed') {
                markers[`inc_${inc.id}`] = L.marker([inc.lat, inc.lng], {icon: incIcon})
                    .addTo(map).bindPopup(`<div class="text-slate-900"><b>Incident #${inc.id}</b><br/>Status: ${inc.status}</div>`);
            }
        });
        
        data.ambulances.forEach(amb => {
            if(amb.lat && amb.lng) {
                markers[`amb_${amb.id}`] = L.marker([amb.lat, amb.lng], {icon: ambIcon})
                    .addTo(map).bindPopup(`<div class="text-slate-900"><b>Unit ${amb.vehicle_number}</b><br/>Status: ${amb.status}</div>`);
            }
        });
    }

    fetchAdminData();
    setInterval(fetchAdminData, 4000);
</script>
{% endblock %}"""

files['driver_dashboard.html'] = """{% extends "base.html" %}
{% block content %}
<div class="max-w-md mx-auto mt-10 gsap-fade space-y-6">
    <div class="bg-glass backdrop-blur-2xl border border-glassBorder p-6 rounded-3xl shadow-xl">
        <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-bold">Unit Terminal</h2>
            <span class="px-3 py-1 rounded-full text-xs font-bold uppercase bg-slate-800 border border-slate-600" id="ambStatus">{{ current_user.ambulance.status }}</span>
        </div>
        
        {% if incident %}
            <div class="bg-red-500/10 border border-red-500/30 p-5 rounded-2xl mb-6 relative overflow-hidden">
                <div class="absolute top-0 right-0 w-2 h-full bg-red-500"></div>
                <h3 class="font-bold text-red-400 mb-2 uppercase tracking-wide text-sm flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span> Active Dispatch
                </h3>
                <p class="text-slate-200 capitalize">Severity: <span class="font-medium">{{ incident.severity }}</span></p>
                <p class="text-slate-200 mt-1">Contact: <span class="font-medium">{{ incident.reporter_contact }}</span></p>
                
                <div class="mt-4 pt-4 border-t border-red-500/20">
                    <span class="text-xs text-slate-400 uppercase tracking-wider block mb-2">Update Phase</span>
                    <div class="flex flex-col gap-3">
                        {% if incident.status == 'assigned' or incident.status == 'en_route' %}
                            <button onclick="updateStatus('en_route')" class="w-full bg-yellow-500/20 hover:bg-yellow-500/30 border border-yellow-500/50 text-yellow-400 px-4 py-3 rounded-xl transition">1. Mark En Route</button>
                            <button onclick="updateStatus('reached')" class="w-full bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/50 text-blue-400 px-4 py-3 rounded-xl transition">2. Arrived at Scene</button>
                        {% elif incident.status == 'reached' or incident.status == 'hospital_redirect' %}
                            <button onclick="updateStatus('completed')" class="w-full bg-green-500/20 hover:bg-green-500/30 border border-green-500/50 text-green-400 px-4 py-3 rounded-xl transition">3. Mission Complete</button>
                        {% endif %}
                    </div>
                </div>
            </div>
        {% else %}
            <div class="py-10 text-center border-2 border-dashed border-slate-700 rounded-2xl mb-6">
                <p class="text-slate-400">Unit available. Awaiting dispatch.</p>
            </div>
        {% endif %}
    </div>
    
    <div class="bg-glass backdrop-blur-2xl border border-glassBorder p-6 rounded-3xl shadow-xl">
        <h3 class="font-bold mb-1 text-slate-200">Telematics Link</h3>
        <p id="locStatus" class="text-xs text-slate-400 mb-4">GPS disabled.</p>
        <button id="startGpsBtn" class="w-full bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white px-4 py-3 rounded-xl transition shadow-lg flex items-center justify-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
            Activate Location Stream
        </button>
    </div>
</div>

<script>
    async function updateStatus(status) {
        await fetch('/api/driver/status', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({status})
        });
        window.location.reload();
    }

    document.getElementById('startGpsBtn').addEventListener('click', () => {
        const locStatus = document.getElementById('locStatus');
        const btn = document.getElementById('startGpsBtn');
        
        if (navigator.geolocation) {
            locStatus.innerHTML = "<span class='text-green-400 font-medium'>● Live</span> Streaming GPS coordinates...";
            btn.classList.add('bg-green-900/50', 'border-green-500/50');
            btn.textContent = "Stream Active";
            
            navigator.geolocation.watchPosition(async (pos) => {
                await fetch('/api/driver/location', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({lat: pos.coords.latitude, lng: pos.coords.longitude})
                });
            }, (err) => {
                locStatus.textContent = "GPS Error: " + err.message;
            }, { enableHighAccuracy: true });
        } else {
            locStatus.textContent = "Geolocation not supported.";
        }
    });
</script>
{% endblock %}"""

for filename, content in files.items():
    with open(os.path.join(templates_dir, filename), "w", encoding="utf-8") as f:
        f.write(content)

print("Glassmorphism UI update applied successfully.")
