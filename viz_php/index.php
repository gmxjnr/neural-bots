<?php
// This page is intentionally static PHP: it just serves the HTML
// shell. All live data comes from the Python server (viz_server.py)
// over HTTP, fetched directly by app.js.
?>
<!DOCTYPE html>
<html lang="nl">

<head>
    <meta charset="UTF-8">
    <title>Neural Bots — Brain Viewer</title>
    <link rel="stylesheet" href="style.css">
</head>

<body>

    <header>
        <div>
            <h1>Brain Viewer</h1>
            <p id="status">Verbinden met <code>localhost:8765</code>…</p>
        </div>
        <button id="toggle-simulation" class="toggle-button">Toon live simulatie</button>
    </header>

    <section id="simulation-panel" class="hidden" aria-label="Live simulatie">
        <canvas id="simulation-canvas" width="1200" height="700"></canvas>
    </section>

    <main>
        <section id="bot-grid" aria-label="Botlijst"></section>

        <section id="brain-panel">
            <p class="placeholder">Klik op een bot om zijn brein te zien.</p>
        </section>

        <section id="stats-panel">
            <h2>Populatie</h2>
            <div id="stats-svg-wrapper"></div>
        </section>
    </main>

    <script src="app.js"></script>
</body>

</html>