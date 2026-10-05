import os

templates_dir = "D:/PDL/templates"

modifications = {
    "index.html": """
<div class="mt-12 text-center hero-btn opacity-0 translate-y-4">
    <a href="/report?demo=1" class="inline-flex items-center gap-2 text-slate-400 hover:text-brandBlue transition-colors text-sm font-bold tracking-widest uppercase border border-slate-700 hover:border-brandBlue/50 bg-slate-900/50 px-6 py-3 rounded-xl shadow-lg">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        Run Automated Demo
    </a>
</div>
""",

    "report.html": """
<script>
    const isDemo = new URLSearchParams(window.location.search).get('demo') === '1';
    if (isDemo) {
        const overlay = document.createElement('div');
        overlay.className = 'fixed inset-0 z-[999] bg-transparent cursor-wait';
        document.body.appendChild(overlay);

        const delay = ms => new Promise(r => setTimeout(r, ms));
        async function typeStr(id, str) {
            const el = document.getElementById(id);
            el.value = '';
            for(let char of str) { el.value += char; await delay(80); }
        }

        (async () => {
            await delay(1500);
            await typeStr('contact', '9876543210');
            await delay(500);
            await typeStr('addressSearch', 'Marina Beach, Chennai');
            await delay(500);
            document.getElementById('searchBtn').click();
            await delay(2500);
            
            const form = document.getElementById('reportForm');
            const origFetch = window.fetch;
            window.fetch = async (...args) => {
                const res = await origFetch(...args);
                const clone = res.clone();
                const data = await clone.json();
                if(data.tracking_token) {
                    gsap.to(".report-card", { scale: 0.95, opacity: 0, duration: 0.4, onComplete: () => {
                        window.location.href = `/track/${data.tracking_token}?demo=2`;
                    }});
                }
                return res;
            };
            document.querySelector('#reportForm button[type="submit"]').click();
        })();
    }
</script>
""",

    "track.html": """
<script>
    if (new URLSearchParams(window.location.search).get('demo') === '2') {
        const overlay = document.createElement('div');
        overlay.className = 'fixed inset-0 z-[999] bg-transparent cursor-wait';
        document.body.appendChild(overlay);
        
        setTimeout(() => {
            window.location.href = '/admin/login?demo=3';
        }, 5000);
    }
</script>
""",

    "admin_login.html": """
<script>
    if (new URLSearchParams(window.location.search).get('demo') === '3') {
        const overlay = document.createElement('div');
        overlay.className = 'fixed inset-0 z-[999] bg-transparent cursor-wait';
        document.body.appendChild(overlay);
        
        document.querySelector('form').action = '?demo=4';
        const delay = ms => new Promise(r => setTimeout(r, ms));
        async function typeStr(id, str) {
            const el = document.getElementById(id);
            el.value = '';
            for(let char of str) { el.value += char; await delay(80); }
        }
        (async () => {
            await delay(1000);
            await typeStr('username', 'admin');
            await delay(200);
            await typeStr('password', 'admin');
            await delay(500);
            document.querySelector('form button').click();
        })();
    }
</script>
""",

    "admin_dashboard.html": """
<script>
    if (new URLSearchParams(window.location.search).get('demo') === '4') {
        const overlay = document.createElement('div');
        overlay.className = 'fixed inset-0 z-[999] bg-transparent cursor-wait';
        document.body.appendChild(overlay);
        
        setTimeout(async () => {
            document.getElementById('simSpeedSlider').value = 80;
            await updateSimSpeed(80);
            
            setTimeout(() => {
                const ambKeys = Object.keys(markers).filter(k => k.startsWith('amb_'));
                for(let k of ambKeys) {
                    markers[k].fire('click');
                    break; // Just click the first one
                }
                
                setTimeout(() => {
                    window.location.href = '/driver/login?demo=5';
                }, 6000);
            }, 1000);
        }, 1500);
    }
</script>
""",

    "driver_login.html": """
<script>
    if (new URLSearchParams(window.location.search).get('demo') === '5') {
        const overlay = document.createElement('div');
        overlay.className = 'fixed inset-0 z-[999] bg-transparent cursor-wait';
        document.body.appendChild(overlay);
        
        document.querySelector('form').action = '?demo=6_start';
        const delay = ms => new Promise(r => setTimeout(r, ms));
        async function typeStr(id, str) {
            const el = document.getElementById(id);
            el.value = '';
            for(let char of str) { el.value += char; await delay(80); }
        }
        (async () => {
            await delay(1000);
            await typeStr('username', 'driver1');
            await delay(200);
            await typeStr('password', 'driver');
            await delay(500);
            document.querySelector('form button').click();
        })();
    }
</script>
""",

    "driver_dashboard.html": """
<script>
    // Monkey patch updateStatus to keep query params
    const origUpdateStatus = updateStatus;
    updateStatus = async function(status) {
        await fetch('/api/driver/status', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({status})
        });
        const urlParams = new URLSearchParams(window.location.search);
        let currentDemo = urlParams.get('demo');
        let nextDemo = currentDemo;
        if(currentDemo === '6_start') nextDemo = '6_enroute';
        else if(currentDemo === '6_enroute') nextDemo = '6_arrived';
        else if(currentDemo === '6_arrived') nextDemo = '6_complete';
        
        if (currentDemo) {
            window.location.href = window.location.pathname + '?demo=' + nextDemo;
        } else {
            window.location.reload();
        }
    };

    const demoState = new URLSearchParams(window.location.search).get('demo');
    if (demoState && demoState.startsWith('6')) {
        const overlay = document.createElement('div');
        overlay.className = 'fixed inset-0 z-[999] bg-transparent cursor-wait';
        document.body.appendChild(overlay);
        
        setTimeout(() => {
            if (demoState === '6_start') {
                document.getElementById('startGpsBtn').click();
                setTimeout(() => {
                    const btn = document.querySelector('button[onclick="updateStatus(\\'en_route\\')"]');
                    if (btn) btn.click();
                }, 2000);
            } 
            else if (demoState === '6_enroute') {
                setTimeout(() => {
                    const btn = document.querySelector('button[onclick="updateStatus(\\'reached\\')"]');
                    if (btn) btn.click();
                }, 3000);
            }
            else if (demoState === '6_arrived') {
                setTimeout(() => {
                    const btn = document.querySelector('button[onclick="updateStatus(\\'completed\\')"]');
                    if (btn) btn.click();
                }, 2000);
            }
            else if (demoState === '6_complete') {
                setTimeout(() => {
                    window.location.href = '/'; // Back to home!
                }, 2000);
            }
        }, 1000);
    }
</script>
"""
}

for filename, patch_code in modifications.items():
    filepath = os.path.join(templates_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple injection before {% endblock %}
    if patch_code not in content:
        content = content.replace("{% endblock %}", patch_code + "\n{% endblock %}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
print("Injected Auto-Pilot logic successfully.")
