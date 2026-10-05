import os
import codecs

templates_dir = "D:/PDL/templates"

files = {}

files['base.html'] = """<!DOCTYPE html>
<html lang="en" class="dark scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}SOS Dispatch Command{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        glass: 'rgba(255, 255, 255, 0.03)',
                        glassHover: 'rgba(255, 255, 255, 0.08)',
                        glassBorder: 'rgba(255, 255, 255, 0.05)',
                        brandBlue: '#3b82f6',
                        brandPurple: '#8b5cf6'
                    },
                    animation: {
                        'float-slow': 'float 20s ease-in-out infinite',
                        'float-delayed': 'float 25s ease-in-out infinite 5s',
                        'pulse-glow': 'pulse-glow 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                    },
                    keyframes: {
                        float: {
                            '0%, 100%': { transform: 'translate(0, 0) scale(1)' },
                            '33%': { transform: 'translate(30px, -50px) scale(1.1)' },
                            '66%': { transform: 'translate(-20px, 20px) scale(0.9)' },
                        },
                        'pulse-glow': {
                            '0%, 100%': { opacity: '1', filter: 'drop-shadow(0 0 15px rgba(59,130,246,0.5))' },
                            '50%': { opacity: '.7', filter: 'drop-shadow(0 0 5px rgba(59,130,246,0.2))' },
                        }
                    }
                }
            }
        }
    </script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body { scroll-behavior: smooth; }
        .leaflet-container { background: #0b1120; font-family: inherit; }
        .leaflet-layer, .leaflet-control-zoom-in, .leaflet-control-zoom-out, .leaflet-control-attribution { 
            filter: invert(100%) hue-rotate(180deg) brightness(85%) contrast(120%); 
        }
        .glass-panel {
            background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.05);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        .btn-primary {
            position: relative; overflow: hidden; z-index: 1;
        }
        .btn-primary::before {
            content: ''; position: absolute; top: 0; left: -100%; width: 100%; h: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.7s ease; z-index: -1;
        }
        .btn-primary:hover::before { left: 100%; }
        
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #020617; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
    </style>
    {% block head %}{% endblock %}
</head>
<body class="bg-slate-950 text-slate-200 min-h-screen relative overflow-x-hidden font-sans selection:bg-brandBlue/30">
    
    <!-- Ambient Breathing Orbs -->
    <div class="fixed inset-0 z-[-1] pointer-events-none overflow-hidden opacity-70">
        <div class="absolute top-[-10%] left-[-10%] w-[600px] h-[600px] bg-brandBlue/20 rounded-full blur-[140px] animate-float-slow"></div>
        <div class="absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] bg-brandPurple/20 rounded-full blur-[140px] animate-float-delayed"></div>
    </div>

    <!-- Elegant Nav -->
    <nav class="glass-panel border-b-0 border-white/5 sticky top-0 z-50 transition-all duration-300" id="navbar">
        <div class="container mx-auto px-6 py-4 flex justify-between items-center">
            <a href="/" class="flex items-center gap-3 group nav-brand opacity-0">
                <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-brandBlue to-brandPurple flex items-center justify-center shadow-lg shadow-brandBlue/30 group-hover:scale-110 transition-transform duration-500">
                    <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                </div>
                <span class="text-xl font-bold tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-blue-100 to-slate-300">DISPATCH</span>
            </a>
            <div class="space-x-6 text-sm font-medium tracking-wide nav-links opacity-0">
                {% if current_user.is_authenticated %}
                    <a href="/logout" class="text-slate-400 hover:text-white transition-colors duration-300 hover:glow">Disconnect</a>
                {% else %}
                    <a href="/admin/login" class="text-slate-400 hover:text-white transition-colors duration-300 relative group">
                        Command
                        <span class="absolute -bottom-1 left-0 w-0 h-px bg-brandBlue transition-all duration-300 group-hover:w-full"></span>
                    </a>
                    <a href="/driver/login" class="text-slate-400 hover:text-white transition-colors duration-300 relative group">
                        Unit
                        <span class="absolute -bottom-1 left-0 w-0 h-px bg-brandPurple transition-all duration-300 group-hover:w-full"></span>
                    </a>
                {% endif %}
            </div>
        </div>
    </nav>

    <main class="container mx-auto px-4 md:px-8 py-8">
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <div class="mb-8 space-y-3 flash-messages">
                {% for message in messages %}
                    <div class="glass-panel border-red-500/30 text-red-200 px-6 py-4 rounded-xl flex items-center gap-3">
                        <svg class="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                        {{ message }}
                    </div>
                {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        
        <div id="page-content">
            {% block content %}{% endblock %}
        </div>
    </main>

    <script>
        // Global Entry Animations
        const tl = gsap.timeline();
        tl.to(".nav-brand", { opacity: 1, x: 0, duration: 0.8, ease: "power3.out", clearProps: "all" }, 0.1)
          .to(".nav-links", { opacity: 1, duration: 0.8, ease: "power3.out", clearProps: "all" }, 0.2);
          
        if(document.querySelector('.flash-messages')) {
            gsap.from(".flash-messages > div", { y: -20, opacity: 0, duration: 0.5, stagger: 0.1, ease: "back.out(1.7)"});
        }
    </script>
</body>
</html>"""

files['index.html'] = """{% extends "base.html" %}
{% block content %}
<div class="max-w-4xl mx-auto mt-16 md:mt-24 text-center">
    <div class="inline-block px-4 py-2 rounded-full glass-panel border border-brandBlue/30 mb-8 hero-badge opacity-0 translate-y-4">
        <span class="text-brandBlue font-semibold tracking-widest text-xs uppercase flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-brandBlue animate-pulse"></span>
            System Online
        </span>
    </div>
    
    <h1 class="text-5xl md:text-7xl font-extrabold mb-8 tracking-tight hero-title">
        <span class="block opacity-0 translate-y-8">Rapid Emergency</span>
        <span class="block text-transparent bg-clip-text bg-gradient-to-r from-brandBlue to-brandPurple opacity-0 translate-y-8">Response Network</span>
    </h1>
    
    <p class="text-lg md:text-xl text-slate-400 mb-12 max-w-2xl mx-auto font-light hero-text opacity-0 translate-y-4">
        Intelligent, real-time dispatch engine. Trigger an SOS below to instantly route the nearest available unit directly to your coordinates.
    </p>
    
    <div class="hero-btn opacity-0 translate-y-4 scale-95">
        <a href="/report" class="btn-primary inline-flex items-center gap-3 bg-gradient-to-r from-brandBlue to-brandPurple text-white px-10 py-5 rounded-2xl text-xl font-bold shadow-[0_0_40px_-10px_rgba(59,130,246,0.5)] transition-all hover:scale-105 hover:shadow-[0_0_60px_-15px_rgba(139,92,246,0.6)] active:scale-95">
            <svg class="w-6 h-6 animate-bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            Trigger Emergency SOS
        </a>
    </div>
</div>

<script>
    gsap.to(".hero-badge", { opacity: 1, y: 0, duration: 0.8, ease: "power3.out", delay: 0.2 });
    gsap.to(".hero-title span", { opacity: 1, y: 0, duration: 0.8, stagger: 0.15, ease: "power3.out", delay: 0.3 });
    gsap.to(".hero-text", { opacity: 1, y: 0, duration: 0.8, ease: "power3.out", delay: 0.6 });
    gsap.to(".hero-btn", { opacity: 1, y: 0, scale: 1, duration: 0.8, ease: "back.out(1.5)", delay: 0.8 });
</script>
{% endblock %}"""

files['report.html'] = """{% extends "base.html" %}
{% block content %}
<div class="max-w-lg mx-auto mt-8 md:mt-12">
    <div class="glass-panel p-8 md:p-10 rounded-3xl relative overflow-hidden report-card opacity-0 scale-95">
        
        <!-- Animated Background Gradient inside card -->
        <div class="absolute -top-24 -right-24 w-48 h-48 bg-brandBlue/20 rounded-full blur-3xl animate-pulse"></div>
        <div class="absolute -bottom-24 -left-24 w-48 h-48 bg-red-500/10 rounded-full blur-3xl animate-pulse" style="animation-delay: 1s;"></div>
        
        <div class="relative z-10">
            <div class="flex items-center gap-4 mb-8 form-elem opacity-0 translate-y-4">
                <div class="w-12 h-12 rounded-2xl bg-red-500/20 flex items-center justify-center border border-red-500/30">
                    <svg class="w-6 h-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                </div>
                <div>
                    <h2 class="text-2xl font-bold text-white tracking-tight">Signal Incident</h2>
                    <p class="text-sm text-slate-400">Dispatch system ready.</p>
                </div>
            </div>
            
            <form id="reportForm" class="space-y-6">
                <div class="form-elem opacity-0 translate-y-4">
                    <label class="block text-slate-300 text-sm font-medium mb-2 tracking-wide">Emergency Severity</label>
                    <div class="relative">
                        <select id="severity" class="w-full bg-slate-900/60 border border-slate-700/50 rounded-xl p-3.5 text-slate-200 focus:ring-2 focus:ring-brandBlue focus:border-brandBlue outline-none transition-all appearance-none">
                            <option value="general">General Medical</option>
                            <option value="trauma">Trauma / Accident</option>
                            <option value="icu">Critical / ICU</option>
                        </select>
                        <div class="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">
                            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                        </div>
                    </div>
                </div>
                
                <div class="form-elem opacity-0 translate-y-4">
                    <label class="block text-slate-300 text-sm font-medium mb-2 tracking-wide">Contact Number</label>
                    <input type="text" id="contact" class="w-full bg-slate-900/60 border border-slate-700/50 rounded-xl p-3.5 text-slate-200 focus:ring-2 focus:ring-brandBlue outline-none transition-all placeholder-slate-600 focus:bg-slate-900/80" placeholder="e.g. 9876543210" required>
                </div>
                
                <div class="form-elem opacity-0 translate-y-4">
                    <label class="block text-slate-300 text-sm font-medium mb-2 tracking-wide flex justify-between">
                        Location Coordinates
                        <span id="locationStatus" class="text-xs text-brandBlue font-medium"></span>
                    </label>
                    <div class="flex flex-col sm:flex-row gap-3 mb-3">
                        <input type="text" id="lat" class="w-full bg-slate-900/60 border border-slate-700/50 rounded-xl p-3 text-slate-200 focus:ring-2 focus:ring-brandBlue outline-none transition-all placeholder-slate-600 text-sm" placeholder="Latitude">
                        <input type="text" id="lng" class="w-full bg-slate-900/60 border border-slate-700/50 rounded-xl p-3 text-slate-200 focus:ring-2 focus:ring-brandBlue outline-none transition-all placeholder-slate-600 text-sm" placeholder="Longitude">
                    </div>
                    <button type="button" id="getLocationBtn" class="w-full bg-slate-800/80 hover:bg-slate-700 border border-slate-600/50 text-slate-200 px-4 py-3 rounded-xl transition-all flex items-center justify-center gap-2 text-sm group">
                        <svg class="w-4 h-4 text-brandBlue group-hover:animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                        Target GPS Coordinates
                    </button>
                </div>
                
                <div class="form-elem opacity-0 translate-y-4 pt-4">
                    <button type="submit" class="btn-primary w-full bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white px-4 py-4 rounded-xl font-bold shadow-[0_0_20px_-5px_rgba(225,29,72,0.5)] transition-all active:scale-[0.98] text-lg uppercase tracking-wider flex items-center justify-center gap-2">
                        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                        Deploy Ambulance
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>

<script>
    // Entry Animations
    gsap.to(".report-card", { opacity: 1, scale: 1, duration: 0.6, ease: "power3.out" });
    gsap.to(".form-elem", { opacity: 1, y: 0, duration: 0.6, stagger: 0.1, ease: "power3.out", delay: 0.2 });

    // Location Logic
    const locBtn = document.getElementById('getLocationBtn');
    locBtn.addEventListener('click', () => {
        const status = document.getElementById('locationStatus');
        status.textContent = "Acquiring signal...";
        status.classList.add("animate-pulse");
        
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                document.getElementById('lat').value = pos.coords.latitude;
                document.getElementById('lng').value = pos.coords.longitude;
                status.classList.remove("animate-pulse");
                status.textContent = "Signal locked.";
                status.className = "text-xs text-green-400 font-medium";
                
                // Flash green effect on inputs
                gsap.to(["#lat", "#lng"], { borderColor: "#4ade80", duration: 0.3, yoyo: true, repeat: 1 });
            },
            (err) => {
                status.classList.remove("animate-pulse");
                status.textContent = "Error: " + err.message;
                status.className = "text-xs text-red-400 font-medium";
            }
        );
    });

    document.getElementById('reportForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const lat = document.getElementById('lat').value;
        const lng = document.getElementById('lng').value;
        
        if (!lat || !lng) {
            gsap.to(["#lat", "#lng"], { x: [-5, 5, -5, 5, 0], duration: 0.4, borderColor: "#ef4444" });
            return;
        }

        // Add a nice loading state to button
        const btn = e.target.querySelector('button[type="submit"]');
        const origContent = btn.innerHTML;
        btn.innerHTML = `<svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Initializing Protocol...`;
        
        try {
            const res = await fetch('/api/signal', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({lat, lng, severity: document.getElementById('severity').value, contact: document.getElementById('contact').value})
            });
            const data = await res.json();
            
            if (data.tracking_token) {
                // Exit animation before redirect
                gsap.to(".report-card", { scale: 0.95, opacity: 0, duration: 0.4, ease: "power2.in", onComplete: () => {
                    window.location.href = `/track/${data.tracking_token}`;
                }});
            } else {
                btn.innerHTML = origContent;
                alert("Error: " + (data.error || "Unknown"));
            }
        } catch(err) {
            btn.innerHTML = origContent;
        }
    });
</script>
{% endblock %}"""

files['track.html'] = """{% extends "base.html" %}
{% block content %}
<div class="max-w-5xl mx-auto">
    <div class="flex flex-col lg:flex-row gap-6">
        
        <!-- Left Panel: Status Data -->
        <div class="w-full lg:w-1/3 space-y-6">
            <!-- Main Status Card -->
            <div class="glass-panel p-6 rounded-3xl relative overflow-hidden track-elem opacity-0 translate-x-[-20px]">
                <div class="absolute top-0 right-0 w-32 h-32 bg-brandBlue/10 rounded-full blur-2xl -mr-10 -mt-10"></div>
                
                <h3 class="text-slate-500 text-xs font-bold uppercase tracking-widest mb-2 flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-brandBlue animate-pulse"></span>
                    Live Status
                </h3>
                <div class="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-300 mb-6" id="status">
                    {{ incident.status | title }}
                </div>
                
                <div class="space-y-6">
                    <div class="bg-slate-900/40 p-4 rounded-2xl border border-white/5">
                        <p class="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-1">Assigned Unit</p>
                        <p id="ambulanceNumber" class="text-xl font-bold text-slate-200">Pending...</p>
                        <p id="driverName" class="text-sm text-brandBlue mt-1 font-medium"></p>
                    </div>
                    
                    <div class="bg-slate-900/40 p-4 rounded-2xl border border-white/5 border-l-2 border-l-green-500">
                        <p class="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-1">Est. Arrival Time</p>
                        <p id="etaText" class="text-3xl font-black text-green-400 font-mono tracking-tighter">-- min</p>
                    </div>
                </div>
            </div>
            
            <!-- Details Card -->
            <div class="glass-panel p-6 rounded-3xl track-elem opacity-0 translate-x-[-20px]">
                <h3 class="text-slate-500 text-xs font-bold uppercase tracking-widest mb-4">Incident Details</h3>
                <ul class="space-y-3 text-sm">
                    <li class="flex justify-between items-center pb-3 border-b border-slate-800">
                        <span class="text-slate-400">Severity</span> 
                        <span class="text-slate-200 font-medium capitalize px-2 py-1 bg-white/5 rounded-md">{{ incident.severity }}</span>
                    </li>
                    <li class="flex justify-between items-center pb-1">
                        <span class="text-slate-400">Contact</span> 
                        <span class="text-slate-200 font-medium font-mono">{{ incident.reporter_contact }}</span>
                    </li>
                </ul>
            </div>
        </div>
        
        <!-- Right Panel: Map -->
        <div class="w-full lg:w-2/3">
            <div class="glass-panel p-2 rounded-3xl h-[600px] relative track-elem opacity-0 translate-y-10 group">
                <!-- Outer subtle glow -->
                <div class="absolute inset-0 bg-gradient-to-b from-brandBlue/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none rounded-3xl"></div>
                <div id="map" class="w-full h-full rounded-[1.25rem] z-0"></div>
            </div>
        </div>
        
    </div>
</div>

<script>
    gsap.to(".track-elem", { opacity: 1, x: 0, y: 0, duration: 0.7, stagger: 0.15, ease: "power3.out" });

    const token = '{{ incident.tracking_token }}';
    const incidentLat = {{ incident.lat }};
    const incidentLng = {{ incident.lng }};
    
    const map = L.map('map', { zoomControl: false }).setView([incidentLat, incidentLng], 14);
    L.control.zoom({ position: 'bottomright' }).addTo(map);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);
    
    const incIcon = L.icon({iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png', iconSize: [25, 41], iconAnchor: [12, 41]});
    const ambIcon = L.icon({iconUrl: 'https://cdn-icons-png.flaticon.com/512/320/320150.png', iconSize: [40, 40], className: 'drop-shadow-lg'});

    L.marker([incidentLat, incidentLng], {icon: incIcon}).addTo(map).bindPopup("<div class='font-bold text-slate-800'>Target Location</div>");
    
    let ambMarker = null;
    let routeLayer = null;

    // Counter animation for ETA
    function animateValue(id, start, end, duration) {
        const obj = document.getElementById(id);
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start) + start) + " <span class='text-sm text-green-500/70 uppercase tracking-widest'>min</span>";
            if (progress < 1) window.requestAnimationFrame(step);
        };
        window.requestAnimationFrame(step);
    }

    async function drawRoute(startLat, startLng, endLat, endLng) {
        try {
            const response = await fetch(`https://router.project-osrm.org/route/v1/driving/${startLng},${startLat};${endLng},${endLat}?overview=full&geometries=geojson`);
            const data = await response.json();
            
            if (data.routes && data.routes.length > 0) {
                const route = data.routes[0];
                const etaMinutes = Math.max(1, Math.round(route.duration / 60));
                
                const etaEl = document.getElementById('etaText');
                const currentText = etaEl.innerText;
                if(currentText === "-- min" || currentText === "Calculating...") {
                    animateValue("etaText", 0, etaMinutes, 1000);
                } else {
                    etaEl.innerHTML = etaMinutes + " <span class='text-sm text-green-500/70 uppercase tracking-widest'>min</span>";
                }

                if (routeLayer) map.removeLayer(routeLayer);
                
                routeLayer = L.geoJSON(route.geometry, {
                    style: { color: '#3b82f6', weight: 6, opacity: 0.9, lineCap: 'round', lineJoin: 'round', dashArray: '1, 10' }
                }).addTo(map);
                
                map.fitBounds(routeLayer.getBounds(), { padding: [50, 50], animate: true, duration: 1 });
            }
        } catch (e) {}
    }

    async function pollStatus() {
        const res = await fetch(`/api/incident/${token}`);
        const data = await res.json();
        
        const statusEl = document.getElementById('status');
        if(statusEl.innerText.toLowerCase() !== data.status.toLowerCase()) {
            statusEl.innerText = data.status.toUpperCase();
            gsap.from(statusEl, { scale: 1.1, opacity: 0.5, duration: 0.5 });
        }
        
        if (data.ambulance && data.ambulance.id) {
            document.getElementById('ambulanceNumber').textContent = data.ambulance.vehicle_number;
            if (data.ambulance.driver_name) {
                document.getElementById('driverName').innerHTML = `Pilot: <span class="text-white">${data.ambulance.driver_name}</span>`;
            }
            
            if (data.ambulance.lat && data.ambulance.lng) {
                if (!ambMarker) {
                    ambMarker = L.marker([data.ambulance.lat, data.ambulance.lng], {icon: ambIcon}).addTo(map);
                    drawRoute(data.ambulance.lat, data.ambulance.lng, incidentLat, incidentLng);
                } else {
                    const oldLatLng = ambMarker.getLatLng();
                    if(oldLatLng.lat !== data.ambulance.lat || oldLatLng.lng !== data.ambulance.lng) {
                        ambMarker.setLatLng([data.ambulance.lat, data.ambulance.lng]);
                        // Only redraw route occasionally in real life, but we'll do it to keep ETA fresh
                        drawRoute(data.ambulance.lat, data.ambulance.lng, incidentLat, incidentLng);
                    }
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
<div class="max-w-sm mx-auto mt-24">
    <div class="glass-panel p-10 rounded-3xl relative overflow-hidden login-card opacity-0 scale-95">
        <div class="absolute top-0 right-0 w-32 h-32 bg-brandPurple/20 rounded-full blur-2xl -mr-10 -mt-10"></div>
        
        <h2 class="text-2xl font-bold mb-8 text-center tracking-wide text-white">Central Command</h2>
        
        <form method="POST" class="space-y-5 relative z-10">
            <div>
                <input type="text" id="username" name="username" placeholder="Admin ID" class="w-full bg-slate-900/60 border border-slate-700/50 rounded-xl p-3.5 text-slate-200 outline-none focus:ring-2 focus:ring-brandPurple focus:bg-slate-900/80 transition-all placeholder-slate-500" required>
            </div>
            <div>
                <input type="password" id="password" name="password" placeholder="Passcode" class="w-full bg-slate-900/60 border border-slate-700/50 rounded-xl p-3.5 text-slate-200 outline-none focus:ring-2 focus:ring-brandPurple focus:bg-slate-900/80 transition-all placeholder-slate-500" required>
            </div>
            <button type="submit" class="btn-primary w-full bg-brandPurple hover:bg-purple-500 text-white p-4 rounded-xl font-bold shadow-[0_0_20px_-5px_rgba(139,92,246,0.6)] transition-all active:scale-[0.98]">Authorize Access</button>
        </form>
        
        <div class="mt-8 text-center border-t border-slate-700/50 pt-5 relative z-10">
            <button type="button" onclick="autoFill()" class="text-xs font-medium text-slate-500 hover:text-brandPurple transition-colors flex items-center justify-center gap-2 mx-auto">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                Autofill Demo Credentials
            </button>
        </div>
    </div>
</div>
<script>
    gsap.to(".login-card", { opacity: 1, scale: 1, duration: 0.6, ease: "back.out(1.2)" });
    function autoFill() {
        document.getElementById('username').value='admin';
        document.getElementById('password').value='admin';
        gsap.to(["#username", "#password"], { backgroundColor: "rgba(139, 92, 246, 0.1)", duration: 0.3, yoyo: true, repeat: 1 });
    }
</script>
{% endblock %}"""

files['driver_login.html'] = """{% extends "base.html" %}
{% block content %}
<div class="max-w-sm mx-auto mt-24">
    <div class="glass-panel p-10 rounded-3xl relative overflow-hidden login-card opacity-0 scale-95">
        <div class="absolute top-0 right-0 w-32 h-32 bg-emerald-500/20 rounded-full blur-2xl -mr-10 -mt-10"></div>
        
        <h2 class="text-2xl font-bold mb-8 text-center tracking-wide text-white">Pilot Terminal</h2>
        
        <form method="POST" class="space-y-5 relative z-10">
            <div>
                <input type="text" id="username" name="username" placeholder="Pilot ID" class="w-full bg-slate-900/60 border border-slate-700/50 rounded-xl p-3.5 text-slate-200 outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-slate-900/80 transition-all placeholder-slate-500" required>
            </div>
            <div>
                <input type="password" id="password" name="password" placeholder="Passcode" class="w-full bg-slate-900/60 border border-slate-700/50 rounded-xl p-3.5 text-slate-200 outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-slate-900/80 transition-all placeholder-slate-500" required>
            </div>
            <button type="submit" class="btn-primary w-full bg-emerald-600 hover:bg-emerald-500 text-white p-4 rounded-xl font-bold shadow-[0_0_20px_-5px_rgba(16,185,129,0.6)] transition-all active:scale-[0.98]">Connect Unit</button>
        </form>
        
        <div class="mt-8 text-center border-t border-slate-700/50 pt-5 relative z-10">
            <button type="button" onclick="autoFill()" class="text-xs font-medium text-slate-500 hover:text-emerald-400 transition-colors flex items-center justify-center gap-2 mx-auto">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                Autofill Demo Credentials
            </button>
        </div>
    </div>
</div>
<script>
    gsap.to(".login-card", { opacity: 1, scale: 1, duration: 0.6, ease: "back.out(1.2)" });
    function autoFill() {
        document.getElementById('username').value='driver1';
        document.getElementById('password').value='driver';
        gsap.to(["#username", "#password"], { backgroundColor: "rgba(16, 185, 129, 0.1)", duration: 0.3, yoyo: true, repeat: 1 });
    }
</script>
{% endblock %}"""

# Adding admin and driver dashboard with updated styling in next block if needed, but they are already heavily glassmorphic. 
# Let's apply minor updates to dashboards for consistency.

for filename, content in files.items():
    with codecs.open(os.path.join(templates_dir, filename), "w", encoding="utf-8") as f:
        f.write(content)

print("Enhanced UI update applied successfully.")
