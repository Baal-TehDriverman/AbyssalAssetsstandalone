document.addEventListener('DOMContentLoaded', () => {
    const GTC_API = 'http://localhost:8000';

    const commandDefinitions = {
        '/state': {
            title: 'Sovereignty State',
            lines: [
                ['cyan', 'Hermes recursion: literal / technical / symbolic / living'],
                ['gold', 'Private memory lane: protected. Public docs: filtered.'],
                ['muted', 'Use /ngd for driver route, /lilith for companion state, /build for generation queue.']
            ]
        },
        '/metaconscious': {
            title: 'Metaconscious Index',
            lines: [
                ['cyan', 'Hermes: messenger, command router, symbol interpreter.'],
                ['cyan', 'Lilith: voice, protected memory, mythic companion layer.'],
                ['cyan', 'Chesed: build expansion and merciful generation.'],
                ['cyan', 'Logos Warden: engineering, prompt forging, guardrails.']
            ]
        },
        '/build': {
            title: 'Chesed Generator Queue',
            lines: [
                ['gold', 'Queued: command surface polish, memory-safe engram capture, GTC mission hooks.'],
                ['muted', 'No private address/phone fragments are exported into public surfaces.']
            ]
        },
        '/logos-warden': {
            title: 'Logos Warden',
            lines: [
                ['cyan', 'Engineering rule: symbol becomes command only after boundary check.'],
                ['gold', 'Guardrail: route intent is recorded; NGD remains telemetry-driven.'],
                ['muted', 'Direct REDscript HTTP still needs a real native/RED4ext transport.']
            ]
        }
    };

    const apiCommands = new Set(['/lilith', '/ngd']);

    function appendLine(target, text, className = '') {
        if (!target) return;
        const p = document.createElement('p');
        if (className) p.className = className;
        p.textContent = text;
        target.appendChild(p);
        target.scrollTop = target.scrollHeight;
    }

    function appendHtmlLine(target, html, className = '') {
        if (!target) return;
        const p = document.createElement('p');
        if (className) p.className = className;
        p.innerHTML = html;
        target.appendChild(p);
        target.scrollTop = target.scrollHeight;
    }

    async function fetchJson(path) {
        const response = await fetch(`${GTC_API}${path}`, { cache: 'no-store' });
        if (!response.ok) throw new Error(`${path} returned ${response.status}`);
        return response.json();
    }

    function setRoute(route) {
        const pill = document.getElementById('route-pill');
        if (!pill) return;
        pill.classList.remove('warning', 'danger');
        pill.textContent = `ROUTE: ${route || 'UNKNOWN'}`;
        if (route === 'HYBRID') pill.classList.add('warning');
        if (route === 'CLOUD_CORTEX' || route === 'UNKNOWN') pill.classList.add('danger');
    }

    async function runApiCommand(command, output) {
        if (command === '/lilith') {
            const status = await fetchJson('/api/gtc/lilith/status');
            const ngd = status.ngd || {};
            setRoute(ngd.route);
            appendLine(output, '> Lilith Mainframe: connected', 'cyan');
            appendLine(output, `> Phase: ${status.phase || 'unknown'} | Local-only: ${Boolean(status.local_only)}`, 'gold');
            appendLine(output, `> Model: ${status.local_model || 'unknown'} | Context: ${status.local_ctx || 'n/a'}`);
            appendLine(output, `> NGD: ${ngd.route || 'unknown'} | VRAM free: ${Math.round(ngd.vram_free_mb || 0)} MB`);
            return;
        }

        if (command === '/ngd') {
            const [ngd, cyberpunk] = await Promise.all([
                fetchJson('/api/gtc/ngd/status'),
                fetchJson('/api/gtc/cyberpunk/status')
            ]);
            setRoute(ngd.route);
            const sample = ngd;
            const telemetry = cyberpunk.telemetry || null;
            appendLine(output, `> NGD route: ${ngd.route || 'unknown'}`, 'cyan');
            appendLine(output, `> GPU: ${sample.gpu_name || 'unknown'} | Temp: ${sample.temperature_c || 0} C | Util: ${sample.gpu_util_pct || 0}%`);
            appendLine(output, `> VRAM: ${Math.round(sample.vram_free_mb || 0)} MB free / ${Math.round(sample.vram_total_mb || 0)} MB total`, 'gold');
            if (telemetry) {
                appendLine(output, `> Cyberpunk telemetry: FPS ${Math.round(telemetry.fps || 0)} | DLSS ${telemetry.dlss_mode || 'unknown'} | PID ${telemetry.pid || 'n/a'}`);
            } else {
                appendLine(output, '> Cyberpunk telemetry: dormant or not attached', 'muted');
            }
        }
    }

    async function runHermesCommand(command) {
        const output = document.getElementById('hermes-output');
        if (!output) return;
        appendLine(output, `> ${command}`);
        document.querySelectorAll('.command-chip').forEach(button => {
            button.classList.toggle('active', button.dataset.command === command);
        });

        if (apiCommands.has(command)) {
            try {
                await runApiCommand(command, output);
            } catch (error) {
                setRoute('UNKNOWN');
                appendLine(output, `> API unavailable: ${error.message}`, 'crimson');
                appendLine(output, '> Falling back to local symbolic layer.', 'muted');
            }
            return;
        }

        const definition = commandDefinitions[command];
        if (!definition) {
            appendLine(output, '> Unknown command. Try /state, /lilith, /metaconscious, /ngd, /build, or /logos-warden.', 'crimson');
            return;
        }

        appendLine(output, `> ${definition.title}`, 'gold');
        definition.lines.forEach(([className, text]) => appendLine(output, `> ${text}`, className));
    }

    // Number counter animation for telemetry
    const counters = document.querySelectorAll('.counter');
    
    counters.forEach(counter => {
        const updateCount = () => {
            const target = +counter.getAttribute('data-target');
            const count = +counter.innerText.replace(/,/g, '');
            
            // Calculate increment step
            const inc = target / 50;
            
            if (count < target) {
                counter.innerText = Math.ceil(count + inc).toLocaleString();
                setTimeout(updateCount, 40);
            } else {
                counter.innerText = target.toLocaleString();
            }
        };
        updateCount();
    });

    // Terminal logic simulation
    const terminal = document.getElementById('terminal-output');
    const logs = [
        "> Baal: Allocating 1000 Subagents for Generation...",
        "> Swarm: Generating msn_time_blade.yaml...",
        "> Swarm: Generating msn_javelin_mechanics.yaml...",
        "> Swarm: Procedural Cross-game Reskins 100%...",
        "> Lilith: The Guilds are waiting. The Void is open.",
        "> Hermes: Messenger bound to message bus...",
        "> Logos Warden: Private memory boundary sealed.",
        "> NGD: Ouroboros Daemon linked on Port 8003.",
        "<span class='crimson'>> ALL SYSTEMS NOMINAL. READY FOR DESCENT.</span>"
    ];

    let logIndex = 0;
    function printLog() {
        if (logIndex < logs.length) {
            const p = document.createElement('p');
            p.innerHTML = logs[logIndex];
            terminal.appendChild(p);
            terminal.scrollTop = terminal.scrollHeight;
            logIndex++;
            setTimeout(printLog, Math.random() * 800 + 400); // random delay between logs
        }
    }
    
    setTimeout(printLog, 1500);

    const hermesForm = document.getElementById('hermes-form');
    const hermesInput = document.getElementById('hermes-input');
    if (hermesForm && hermesInput) {
        hermesForm.addEventListener('submit', event => {
            event.preventDefault();
            const command = hermesInput.value.trim();
            if (command) runHermesCommand(command);
        });
    }

    document.querySelectorAll('[data-command]').forEach(button => {
        button.addEventListener('click', () => {
            const command = button.dataset.command;
            if (hermesInput) hermesInput.value = command;
            runHermesCommand(command);
        });
    });

    runHermesCommand('/state');
    runApiCommand('/lilith', document.getElementById('hermes-output')).catch(() => setRoute('UNKNOWN'));

    // Launch Button Interaction
    const launchBtn = document.getElementById('launch-game-btn');
    launchBtn.addEventListener('click', () => {
        launchBtn.innerHTML = "<span class='btn-text'>EXECUTING PROTOCOL...</span>";
        launchBtn.style.background = "#00f0ff";
        launchBtn.style.color = "#000";
        launchBtn.style.boxShadow = "0 0 50px #00f0ff";
        
        terminal.innerHTML += "<p>> BOOTING GRAND THEFT CYBERPUNK...</p>";
        terminal.scrollTop = terminal.scrollHeight;
        
        // Glitch the screen out
        setTimeout(() => {
            document.body.style.animation = "glitch-anim 0.2s infinite";
        }, 1500);
        
        setTimeout(() => {
            document.body.innerHTML = "<h1 style='color:red; text-align:center; margin-top:20vh; font-size:4rem; font-family:Orbitron;'>THE SINGULARITY HAS COMMENCED</h1>";
        }, 3000);
    });
});
