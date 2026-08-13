const SERVER = "http://localhost:8765";

const INPUT_LABELS = [
    "afst. doel",
    "richting",
    "muur L",
    "muur R",
    "koers",
    "ray 1",
    "ray 2",
    "ray 3",
    "ray 4",
    "ray 5"
];

const OUTPUT_LABELS = [
    "sturen",
    "snelheid"
];

const grid = document.getElementById("bot-grid");
const panel = document.getElementById("brain-panel");
const statsWrapper = document.getElementById("stats-svg-wrapper");
const status = document.getElementById("status");

let selectedId = null;
let knownBotCount = 0;

// Rolling history of a selected bot's inputs/hidden/outputs, used
// for the sparklines. Reset whenever the selection changes.
const HISTORY_LENGTH = 60;
let history = { inputs: [], hidden: [], outputs: [] };

function resetHistory() {
    history = { inputs: [], hidden: [], outputs: [] };
}

// ============================================================
// Polling loop
// ============================================================

async function refreshBotList() {

    try {

        const response = await fetch(`${SERVER}/bots`);
        const bots = await response.json();

        status.textContent = `Verbonden — ${bots.length} bots`;

        renderGrid(bots);

    } catch (error) {

        status.textContent = "Kan geen verbinding maken met localhost:8765 — draait main.py?";
    }
}

async function refreshSelectedBrain() {

    if (selectedId === null) {
        return;
    }

    try {

        const response = await fetch(`${SERVER}/bot/${selectedId}`);
        const bot = await response.json();

        if (bot.inputs && bot.inputs.length > 0) {
            pushHistory(bot);
        }

        renderBrain(bot);

    } catch (error) {
        // Silently skip a failed poll, next tick will retry.
    }
}

setInterval(refreshBotList, 300);
setInterval(refreshSelectedBrain, 150);
setInterval(refreshStats, 1000);

refreshBotList();
refreshStats();

// ============================================================
// Live simulation toggle + canvas rendering
// ============================================================
//
// Only fetches world/bot positions while the panel is visible, so
// it doesn't waste bandwidth or CPU when nobody's looking at it.

const toggleButton = document.getElementById("toggle-simulation");
const simulationPanel = document.getElementById("simulation-panel");
const canvas = document.getElementById("simulation-canvas");
const ctx = canvas.getContext("2d");

let simulationVisible = false;
let world = null;
let simulationInterval = null;

toggleButton.addEventListener("click", () => {

    simulationVisible = !simulationVisible;

    simulationPanel.classList.toggle("hidden", !simulationVisible);
    toggleButton.classList.toggle("active", simulationVisible);
    toggleButton.textContent = simulationVisible
        ? "Verberg live simulatie"
        : "Toon live simulatie";

    if (simulationVisible) {

        fetchWorld();
        simulationInterval = setInterval(drawFrame, 1000 / 30);

    } else {

        clearInterval(simulationInterval);
    }
});

async function fetchWorld() {

    try {

        const response = await fetch(`${SERVER}/world`);
        world = await response.json();

        canvas.width = world.width;
        canvas.height = world.height;

    } catch (error) {
        // Retried on next drawFrame indirectly via the periodic re-fetch below.
    }
}

// World only changes on course rotation, refetch occasionally
// while the panel is open rather than every frame.
setInterval(() => {
    if (simulationVisible) {
        fetchWorld();
    }
}, 5000);

async function drawFrame() {

    if (!world) {
        return;
    }

    try {

        const response = await fetch(`${SERVER}/bots`);
        const bots = await response.json();

        renderSimulationFrame(bots);

    } catch (error) {
        // Skip this frame, try again next tick.
    }
}

function renderSimulationFrame(bots) {

    ctx.fillStyle = "#0f1118";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Obstacles
    ctx.fillStyle = "#c8465a";
    world.obstacles.forEach(o => {
        ctx.fillRect(o.x, o.y, o.width, o.height);
    });

    // Goal
    if (world.goal) {
        ctx.strokeStyle = "#50ff8c";
        ctx.lineWidth = 5;
        ctx.beginPath();
        ctx.arc(world.goal.x, world.goal.y, world.goal.radius, 0, Math.PI * 2);
        ctx.stroke();
    }

    // Bots
    bots.forEach(bot => {

        if (!bot.alive && !bot.reached_goal) {
            ctx.globalAlpha = 0.25;
        } else {
            ctx.globalAlpha = 1;
        }

        ctx.fillStyle = bot.is_best ? "#ffd250" : "#50b4ff";

        ctx.beginPath();
        ctx.arc(bot.x, bot.y, world.bot_radius, 0, Math.PI * 2);
        ctx.fill();

        // Direction indicator
        ctx.strokeStyle = "#dce6ff";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(bot.x, bot.y);
        ctx.lineTo(
            bot.x + Math.cos(bot.angle) * 12,
            bot.y + Math.sin(bot.angle) * 12
        );
        ctx.stroke();

        if (bot.id === selectedId) {

            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(bot.x, bot.y, world.bot_radius + 4, 0, Math.PI * 2);
            ctx.stroke();
        }
    });

    ctx.globalAlpha = 1;
}

// ============================================================
// Bot grid
// ============================================================

function renderGrid(bots) {

    // Only rebuild the DOM structure if the bot count changed,
    // otherwise just update classes to avoid flicker.
    if (bots.length !== knownBotCount) {

        grid.innerHTML = "";

        bots.forEach(bot => {

            const button = document.createElement("button");

            button.className = "bot-button";
            button.textContent = bot.id;
            button.dataset.id = bot.id;

            button.addEventListener("click", () => {
                selectedId = bot.id;
                resetHistory();
                refreshSelectedBrain();
                updateSelectionStyles();
            });

            grid.appendChild(button);
        });

        knownBotCount = bots.length;
    }

    bots.forEach(bot => {

        const button = grid.querySelector(`[data-id="${bot.id}"]`);

        if (!button) {
            return;
        }

        button.classList.toggle("alive", bot.alive);
        button.classList.toggle("dead", !bot.alive);
        button.classList.toggle("reached-goal", bot.reached_goal);
        button.title = `fitness: ${bot.fitness}`;
    });

    updateSelectionStyles();
}

function updateSelectionStyles() {

    grid.querySelectorAll(".bot-button").forEach(button => {

        button.classList.toggle(
            "selected",
            Number(button.dataset.id) === selectedId
        );
    });
}

// ============================================================
// Brain diagram
// ============================================================

function renderBrain(bot) {

    const inputs = bot.inputs;
    const hidden = bot.hidden;
    const outputs = bot.outputs;

    const wih = bot.weights_input_hidden;   // [inputs][hidden]
    const who = bot.weights_hidden_output;  // [hidden][outputs]

    const width = 780;
    const height = Math.max(360, hidden.length * 28);

    const inputX = 90;
    const hiddenX = width / 2;
    const outputX = width - 90;

    const inputYs = layoutColumn(inputs.length, height);
    const hiddenYs = layoutColumn(hidden.length, height);
    const outputYs = layoutColumn(outputs.length, height);

    let svg = `<svg viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">`;

    // ------------------------------------------------------
    // Connections: input -> hidden
    // ------------------------------------------------------

    for (let i = 0; i < inputs.length; i++) {
        for (let h = 0; h < hidden.length; h++) {

            const weight = wih[i][h];

            svg += connectionLine(
                inputX, inputYs[i],
                hiddenX, hiddenYs[h],
                weight
            );
        }
    }

    // ------------------------------------------------------
    // Connections: hidden -> output
    // ------------------------------------------------------

    for (let h = 0; h < hidden.length; h++) {
        for (let o = 0; o < outputs.length; o++) {

            const weight = who[h][o];

            svg += connectionLine(
                hiddenX, hiddenYs[h],
                outputX, outputYs[o],
                weight
            );
        }
    }

    // ------------------------------------------------------
    // Nodes
    // ------------------------------------------------------

    inputs.forEach((value, i) => {
        svg += node(inputX, inputYs[i], value, INPUT_LABELS[i] ?? `in ${i}`, "start");
    });

    hidden.forEach((value, h) => {
        svg += node(hiddenX, hiddenYs[h], value, "", "middle");
    });

    outputs.forEach((value, o) => {
        svg += node(outputX, outputYs[o], value, OUTPUT_LABELS[o] ?? `out ${o}`, "end");
    });

    svg += "</svg>";

    const statusLabel = !bot.alive
        ? (bot.reached_goal ? "bereikte doel" : "dood")
        : "levend";

    panel.innerHTML = `
        <div id="brain-header">
            <strong>Bot #${bot.id}</strong>
            <span>${statusLabel}</span>
            <span>fitness: ${bot.fitness}</span>
        </div>
        <div id="plain-explanation">${explainBot(bot)}</div>
        <div id="brain-svg-wrapper">${svg}</div>
        <div class="legend">
            <div><span class="swatch" style="background:var(--positive)"></span>positief gewicht</div>
            <div><span class="swatch" style="background:var(--negative)"></span>negatief gewicht</div>
            <div>Node-kleur = activatie (donker → fel = -1 → +1)</div>
        </div>
        <div id="sparklines">
            <h3>Inputs over tijd</h3>
            ${renderSparklineGroup(history.inputs, INPUT_LABELS)}
            <h3 style="margin-top:14px">Outputs over tijd</h3>
            ${renderSparklineGroup(history.outputs, OUTPUT_LABELS)}
        </div>
    `;
}

function explainBot(bot) {

    if (bot.inputs.length < 10 || bot.outputs.length < 2) {
        return `<p class="placeholder" style="font-size:13px">Wachten op data…</p>`;
    }

    const [distanceInput, , , , , ray1, ray2, ray3, ray4, ray5] = bot.inputs;
    const [turn, speedRaw] = bot.outputs;

    const speed = (speedRaw + 1) / 2;
    const minRay = Math.min(ray1, ray2, ray3, ray4, ray5);

    const lines = [];

    // Status
    if (bot.reached_goal) {
        lines.push("🏁 Deze bot heeft het doel bereikt!");
    } else if (!bot.alive) {
        lines.push(
            bot.hit_obstacle
                ? "💥 Deze bot is tegen een muur gebotst en is uitgeschakeld."
                : "⏹️ Deze bot is gestopt zonder het doel te bereiken."
        );
    } else {
        lines.push("🟢 Deze bot is nog actief op weg naar het doel.");
    }

    // Distance to goal (rough, qualitative)
    if (bot.alive || bot.reached_goal) {

        if (distanceInput < 0.15) {
            lines.push("📍 Hij is heel dichtbij het doel.");
        } else if (distanceInput < 0.4) {
            lines.push("📍 Hij zit op redelijke afstand van het doel.");
        } else {
            lines.push("📍 Hij is nog ver van het doel verwijderd.");
        }
    }

    // Steering behaviour
    if (bot.alive) {

        if (turn > 0.2) {
            lines.push("🔄 Hij stuurt op dit moment naar rechts.");
        } else if (turn < -0.2) {
            lines.push("🔄 Hij stuurt op dit moment naar links.");
        } else {
            lines.push("➡️ Hij houdt op dit moment koers, rijdt rechtdoor.");
        }

        if (speed > 0.66) {
            lines.push("⚡ Hij geeft flink gas.");
        } else if (speed > 0.33) {
            lines.push("🚶 Hij rijdt gematigd.");
        } else {
            lines.push("🐢 Hij rijdt heel voorzichtig, bijna stilstaand.");
        }

        // Obstacle awareness
        if (minRay < 0.15) {
            lines.push("⚠️ Er zit ergens vlakbij een muur — hij moet nu ontwijken.");
        } else if (minRay < 0.45) {
            lines.push("👀 Hij houdt een muur in de gaten die niet ver weg is.");
        } else {
            lines.push("✅ Geen muren in de buurt, vrij zicht naar voren.");
        }
    }

    return `<ul class="plain-explanation-list">${lines.map(line => `<li>${line}</li>`).join("")}</ul>`;
}

function pushHistory(bot) {

    history.inputs.push(bot.inputs);
    history.hidden.push(bot.hidden);
    history.outputs.push(bot.outputs);

    if (history.inputs.length > HISTORY_LENGTH) {
        history.inputs.shift();
        history.hidden.shift();
        history.outputs.shift();
    }
}

function renderSparklineGroup(samples, labels) {

    if (samples.length === 0) {
        return `<p class="placeholder" style="font-size:12px">Wachten op data…</p>`;
    }

    const seriesCount = samples[0].length;
    let rows = "";

    for (let i = 0; i < seriesCount; i++) {

        const series = samples.map(sample => sample[i]);
        const latest = series[series.length - 1];

        rows += `
            <div class="sparkline-row">
                <span class="label">${labels[i] ?? i}</span>
                ${sparklineSvg(series)}
                <span class="value">${latest.toFixed(2)}</span>
            </div>
        `;
    }

    return rows;
}

function sparklineSvg(series) {

    const width = 200;
    const height = 24;
    const min = -1;
    const max = 1;

    const points = series.map((value, i) => {

        const x = (i / Math.max(1, series.length - 1)) * width;
        const clamped = Math.max(min, Math.min(max, value));
        const y = height - ((clamped - min) / (max - min)) * height;

        return `${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(" ");

    return `
        <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
            <line x1="0" y1="${height / 2}" x2="${width}" y2="${height / 2}" stroke="var(--border)" stroke-width="1" />
            <polyline points="${points}" fill="none" stroke="var(--bot-color)" stroke-width="1.5" />
        </svg>
    `;
}

// ============================================================
// Population stats (fitness over generations)
// ============================================================

async function refreshStats() {

    try {

        const response = await fetch(`${SERVER}/stats`);
        const stats = await response.json();

        renderStats(stats);

    } catch (error) {
        // Server not up yet, next tick will retry.
    }
}

function renderStats(stats) {

    const history = stats.history ?? [];

    if (history.length === 0) {
        statsWrapper.innerHTML = `<p class="placeholder" style="font-size:12px">Nog geen generaties voltooid.</p>`;
        return;
    }

    const width = 260;
    const height = 160;
    const margin = 20;

    const bestValues = history.map(h => h.best);
    const avgValues = history.map(h => h.average);
    const maxValue = Math.max(...bestValues, 1);

    const toPoints = values => values.map((value, i) => {

        const x = margin + (i / Math.max(1, values.length - 1)) * (width - margin * 2);
        const y = height - margin - (value / maxValue) * (height - margin * 2);

        return `${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(" ");

    const svg = `
        <svg viewBox="0 0 ${width} ${height}">
            <line x1="${margin}" y1="${height - margin}" x2="${width - margin}" y2="${height - margin}" stroke="var(--border)" stroke-width="1" />
            <polyline points="${toPoints(avgValues)}" fill="none" stroke="var(--text-dim)" stroke-width="1.5" />
            <polyline points="${toPoints(bestValues)}" fill="none" stroke="var(--best-color)" stroke-width="2" />
        </svg>
    `;

    statsWrapper.innerHTML = svg + `
        <div class="stats-caption">
            <div><span class="swatch" style="background:var(--best-color);display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;"></span>beste fitness</div>
            <div style="margin-top:4px"><span class="swatch" style="background:var(--text-dim);display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;"></span>gemiddelde fitness</div>
            <div style="margin-top:8px">Generatie ${stats.generation}</div>
        </div>
    `;
}

function layoutColumn(count, height) {

    const margin = 30;
    const usable = height - margin * 2;

    if (count <= 1) {
        return [height / 2];
    }

    const step = usable / (count - 1);

    return Array.from({ length: count }, (_, i) => margin + step * i);
}

function connectionLine(x1, y1, x2, y2, weight) {

    const magnitude = Math.min(Math.abs(weight), 2) / 2;
    const color = weight >= 0 ? "var(--positive)" : "var(--negative)";
    const opacity = 0.08 + magnitude * 0.5;
    const strokeWidth = 0.5 + magnitude * 2;

    return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${strokeWidth}" opacity="${opacity.toFixed(2)}" />`;
}

function node(x, y, value, label, anchor) {

    const radius = 9;
    const fill = activationColor(value);

    const labelX = anchor === "start" ? x - 16 : anchor === "end" ? x + 16 : x;
    const labelY = y + 4;

    const labelSvg = label
        ? `<text x="${labelX}" y="${labelY}" text-anchor="${anchor}" class="node-label">${label}</text>`
        : "";

    return `
        <circle cx="${x}" cy="${y}" r="${radius}" fill="${fill}" stroke="#0f1118" stroke-width="1.5" />
        ${labelSvg}
    `;
}

function activationColor(value) {

    // value roughly in [-1, 1] (tanh output) or unbounded for raw
    // sensor inputs, clamp for safety.
    const clamped = Math.max(-1, Math.min(1, value));

    if (clamped >= 0) {

        const intensity = Math.round(clamped * 255);
        return `rgb(${80 + intensity * 0.3}, ${100 + intensity * 0.4}, 255)`;

    } else {

        const intensity = Math.round(-clamped * 255);
        return `rgb(255, ${100 - intensity * 0.3}, ${100 - intensity * 0.3})`;
    }
}