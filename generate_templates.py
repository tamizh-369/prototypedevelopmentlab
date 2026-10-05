import os

templates_dir = "D:/PDL/templates"
os.makedirs(templates_dir, exist_ok=True)

files = {}

files['base.html'] = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}SOS Ambulance{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    {% block head %}{% endblock %}
</head>
<body class="bg-gray-100 min-h-screen text-gray-800 font-sans">
    <nav class="bg-red-600 text-white p-4 shadow-md flex justify-between items-center">
        <a href="/" class="text-xl font-bold">SOS Ambulance</a>
        <div>
            {% if current_user.is_authenticated %}
                <a href="/logout" class="hover:underline">Logout</a>
            {% else %}
                <a href="/admin/login" class="hover:underline mr-4">Admin</a>
                <a href="/driver/login" class="hover:underline">Driver</a>
            {% endif %}
        </div>
    </nav>
    <div class="container mx-auto p-4">
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <div class="mb-4">
                {% for message in messages %}
                    <div class="bg-yellow-200 text-yellow-800 p-3 rounded shadow-sm">{{ message }}</div>
                {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </div>
</body>
</html>"""

files['index.html'] = """{% extends "base.html" %}
{% block title %}SOS Ambulance - Home{% endblock %}
{% block content %}
<div class="max-w-2xl mx-auto mt-10 text-center">
    <h1 class="text-4xl font-bold mb-4 text-red-600">Emergency Dispatch System</h1>
    <p class="text-lg text-gray-600 mb-8">Fast, reliable ambulance dispatch system with live tracking.</p>
    <a href="/report" class="bg-red-600 text-white px-6 py-3 rounded-lg text-xl font-semibold shadow-lg hover:bg-red-700 transition">Report Emergency</a>
</div>
{% endblock %}"""

files['report.html'] = """{% extends "base.html" %}
{% block title %}Report Emergency{% endblock %}
{% block content %}
<div class="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md mt-10">
    <h2 class="text-2xl font-bold mb-6">Report an Emergency</h2>
    <form id="reportForm">
        <div class="mb-4">
            <label class="block text-gray-700 mb-2">Severity</label>
            <select id="severity" class="w-full border p-2 rounded">
                <option value="general">General</option>
                <option value="trauma">Trauma / Accident</option>
                <option value="icu">Critical / ICU</option>
            </select>
        </div>
        <div class="mb-4">
            <label class="block text-gray-700 mb-2">Contact Number</label>
            <input type="text" id="contact" class="w-full border p-2 rounded" placeholder="Your phone number" required>
        </div>
        <button type="button" id="getLocationBtn" class="bg-gray-200 text-gray-800 px-4 py-2 rounded mb-4 w-full">Use My Location</button>
        <p id="locationStatus" class="text-sm text-gray-500 mb-4"></p>
        
        <input type="hidden" id="lat">
        <input type="hidden" id="lng">
        
        <button type="submit" class="bg-red-600 text-white px-4 py-2 rounded w-full font-bold">Submit Emergency</button>
    </form>
</div>

<script>
    document.getElementById('getLocationBtn').addEventListener('click', () => {
        const status = document.getElementById('locationStatus');
        status.textContent = "Getting location...";
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                document.getElementById('lat').value = pos.coords.latitude;
                document.getElementById('lng').value = pos.coords.longitude;
                status.textContent = "Location acquired!";
            },
            (err) => {
                status.textContent = "Error getting location. " + err.message;
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
            alert("Please provide location first!");
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
            alert("Error reporting incident.");
        }
    });
</script>
{% endblock %}"""

files['track.html'] = """{% extends "base.html" %}
{% block title %}Track Ambulance{% endblock %}
{% block content %}
<div class="max-w-2xl mx-auto mt-10">
    <h2 class="text-2xl font-bold mb-4">Emergency Tracking</h2>
    <div class="bg-white p-4 rounded-lg shadow-md mb-6">
        <p class="text-lg">Status: <span id="status" class="font-bold text-red-600">{{ incident.status | title }}</span></p>
        <p id="ambulanceInfo" class="mt-2"></p>
    </div>
    
    <div id="map" class="h-96 w-full rounded-lg shadow-md z-0"></div>
</div>

<script>
    const token = '{{ incident.tracking_token }}';
    const incidentLat = {{ incident.lat }};
    const incidentLng = {{ incident.lng }};
    
    const map = L.map('map').setView([incidentLat, incidentLng], 14);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    
    L.marker([incidentLat, incidentLng]).addTo(map).bindPopup("Incident Location").openPopup();
    let ambMarker = null;

    async function pollStatus() {
        const res = await fetch(`/api/incident/${token}`);
        const data = await res.json();
        
        document.getElementById('status').textContent = data.status.toUpperCase();
        
        if (data.ambulance) {
            document.getElementById('ambulanceInfo').textContent = `Assigned Ambulance: ${data.ambulance.vehicle_number}`;
            if (data.ambulance.lat && data.ambulance.lng) {
                if (!ambMarker) {
                    ambMarker = L.marker([data.ambulance.lat, data.ambulance.lng], {
                        icon: L.icon({iconUrl: 'https://cdn-icons-png.flaticon.com/512/320/320150.png', iconSize: [32, 32]})
                    }).addTo(map);
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
<div class="max-w-sm mx-auto mt-20 bg-white p-6 rounded-lg shadow-md">
    <h2 class="text-2xl font-bold mb-4">Admin Login</h2>
    <form method="POST">
        <input type="text" name="username" placeholder="Username" class="w-full border p-2 rounded mb-4" required>
        <input type="password" name="password" placeholder="Password" class="w-full border p-2 rounded mb-4" required>
        <button type="submit" class="w-full bg-blue-600 text-white p-2 rounded">Login</button>
    </form>
</div>
{% endblock %}"""

files['driver_login.html'] = """{% extends "base.html" %}
{% block content %}
<div class="max-w-sm mx-auto mt-20 bg-white p-6 rounded-lg shadow-md">
    <h2 class="text-2xl font-bold mb-4">Driver Login</h2>
    <form method="POST">
        <input type="text" name="username" placeholder="Username" class="w-full border p-2 rounded mb-4" required>
        <input type="password" name="password" placeholder="Password" class="w-full border p-2 rounded mb-4" required>
        <button type="submit" class="w-full bg-green-600 text-white p-2 rounded">Login</button>
    </form>
</div>
{% endblock %}"""

files['admin_dashboard.html'] = """{% extends "base.html" %}
{% block content %}
<div class="flex flex-col md:flex-row gap-6 mt-6">
    <div class="w-full md:w-1/3 bg-white p-4 rounded-lg shadow-md h-[80vh] overflow-y-auto">
        <h2 class="text-xl font-bold mb-4">Recent Incidents</h2>
        {% for inc in incidents %}
        <div class="border-b pb-2 mb-2">
            <p class="font-bold">ID: {{ inc.id }} - <span class="text-blue-600">{{ inc.status }}</span></p>
            <p class="text-sm text-gray-600">Severity: {{ inc.severity }}</p>
            <a href="/track/{{ inc.tracking_token }}" target="_blank" class="text-sm text-indigo-500 hover:underline">Track Link</a>
        </div>
        {% endfor %}
    </div>
    <div class="w-full md:w-2/3">
        <div id="map" class="h-[80vh] w-full rounded-lg shadow-md z-0"></div>
    </div>
</div>

<script>
    // Just a placeholder map centered loosely on Chennai for our demo data
    const map = L.map('map').setView([13.0827, 80.2707], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    
    let markers = {};

    async function fetchAdminData() {
        const res = await fetch('/api/admin/data');
        const data = await res.json();
        
        // Clear old markers simply by re-rendering (in real app, diff them)
        Object.values(markers).forEach(m => map.removeLayer(m));
        markers = {};
        
        data.incidents.forEach(inc => {
            if(inc.status !== 'completed') {
                markers[`inc_${inc.id}`] = L.marker([inc.lat, inc.lng]).addTo(map).bindPopup(`Incident ${inc.id} - ${inc.status}`);
            }
        });
        
        data.ambulances.forEach(amb => {
            if(amb.lat && amb.lng) {
                markers[`amb_${amb.id}`] = L.marker([amb.lat, amb.lng], {
                    icon: L.icon({iconUrl: 'https://cdn-icons-png.flaticon.com/512/320/320150.png', iconSize: [24, 24]})
                }).addTo(map).bindPopup(`Amb ${amb.vehicle_number} - ${amb.status}`);
            }
        });
    }

    fetchAdminData();
    setInterval(fetchAdminData, 5000);
</script>
{% endblock %}"""

files['driver_dashboard.html'] = """{% extends "base.html" %}
{% block content %}
<div class="max-w-md mx-auto mt-10">
    <h2 class="text-2xl font-bold mb-4">Driver Dashboard</h2>
    
    <div class="bg-white p-6 rounded-lg shadow-md mb-6">
        <p class="mb-4"><strong>Current Status:</strong> <span id="ambStatus">{{ current_user.ambulance.status }}</span></p>
        
        {% if incident %}
            <div class="bg-red-100 p-4 rounded mb-4">
                <h3 class="font-bold text-red-700">Active Incident Assigned!</h3>
                <p>Severity: {{ incident.severity }}</p>
                <p>Contact: {{ incident.reporter_contact }}</p>
                <p class="mt-2 text-sm">Status: <span id="incStatus" class="font-bold">{{ incident.status }}</span></p>
            </div>
            
            <div class="flex flex-col gap-2">
                {% if incident.status == 'assigned' or incident.status == 'en_route' %}
                    <button onclick="updateStatus('en_route')" class="bg-yellow-500 text-white px-4 py-2 rounded">Mark En Route</button>
                    <button onclick="updateStatus('reached')" class="bg-blue-500 text-white px-4 py-2 rounded">Mark Reached Scene</button>
                {% elif incident.status == 'reached' or incident.status == 'hospital_redirect' %}
                    <button onclick="updateStatus('completed')" class="bg-green-600 text-white px-4 py-2 rounded">Mark Completed / Handed Over</button>
                {% endif %}
            </div>
        {% else %}
            <p class="text-green-600 font-bold">You are available. Waiting for dispatch...</p>
        {% endif %}
    </div>
    
    <div class="bg-white p-4 rounded-lg shadow-md">
        <h3 class="font-bold mb-2">Location Services</h3>
        <p id="locStatus" class="text-sm text-gray-500 mb-2">GPS disabled.</p>
        <button id="startGpsBtn" class="bg-gray-200 px-4 py-2 rounded text-sm w-full">Start Sending GPS</button>
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
        
        if (navigator.geolocation) {
            locStatus.textContent = "GPS Active... sending updates.";
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
    with open(os.path.join(templates_dir, filename), "w") as f:
        f.write(content)

print("Templates generated successfully.")
