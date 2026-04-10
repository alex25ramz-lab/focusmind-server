from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Memoria temporal del servidor (Base de datos volátil)
datos_usuario = {
    "progreso": 0,
    "ultima_tarea": "Esperando conexión...",
    "tiempo_meta": "25"
}

HTML_MOVIL = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>FocusMind Mobile Hub</title>
    <style>
        :root {
            --bg: #0d1117;
            --card: #161b22;
            --border: #30363d;
            --accent: #238636;
            --text-main: #c9d1d9;
            --text-dim: #8b949e;
            --blue: #58a6ff;
        }

        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: var(--bg); 
            color: var(--text-main); 
            margin: 0; 
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        h1 { font-size: 1.4rem; margin-bottom: 25px; color: var(--blue); letter-spacing: 1.5px; text-transform: uppercase; }

        .container { width: 100%; max-width: 400px; }

        .card { 
            background: var(--card); 
            border: 1px solid var(--border); 
            border-radius: 18px; 
            padding: 22px; 
            margin-bottom: 20px; 
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        }

        .progress-container {
            position: relative;
            width: 150px;
            height: 150px;
            margin: 0 auto 15px;
        }

        svg { transform: rotate(-90deg); }

        .circle-bg {
            fill: none;
            stroke: var(--border);
            stroke-width: 12;
        }

        .circle-progress {
            fill: none;
            stroke: var(--accent);
            stroke-width: 12;
            stroke-linecap: round;
            stroke-dasharray: 377; /* 2 * PI * 60 */
            stroke-dashoffset: calc(377 - (377 * {{ progreso }}) / 100);
            transition: stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .percentage {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 2rem;
            font-weight: 800;
            color: white;
        }

        .label { color: var(--text-dim); font-size: 0.75rem; text-transform: uppercase; font-weight: bold; margin-bottom: 10px; display: block; letter-spacing: 0.5px; }
        
        .status-text { font-size: 1.1rem; color: white; font-weight: 500; text-align: center; }

        input { 
            width: 100%; 
            padding: 15px; 
            border-radius: 12px; 
            border: 1px solid var(--border); 
            background: #010409; 
            color: white; 
            margin-bottom: 18px; 
            font-size: 1rem;
            box-sizing: border-box;
            outline: none;
            transition: 0.2s;
        }

        input:focus { border-color: var(--blue); }

        .row { display: flex; gap: 12px; margin-bottom: 20px; }
        .row div { flex: 1; }

        button { 
            width: 100%; 
            padding: 18px; 
            border-radius: 14px; 
            border: none; 
            background: var(--accent); 
            color: white; 
            font-weight: bold; 
            font-size: 1.1rem; 
            cursor: pointer; 
            transition: 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        button:active { transform: scale(0.96); background: #2ea043; }
    </style>
    <script>
        // Verificación de estado en segundo plano para evitar refrescos manuales
        setInterval(function(){
            if(document.activeElement.tagName !== 'INPUT') {
                fetch('/obtener_datos')
                .then(r => r.json())
                .then(data => {
                    // Si el progreso cambió en la laptop, refrescamos para mostrarlo
                    if(data.progreso != {{ progreso }} || data.ultima_tarea != "{{ ultima_tarea }}") {
                        location.reload();
                    }
                });
            }
        }, 4000); 
    </script>
</head>
<body>
    <h1>FocusMind Control</h1>
    
    <div class="container">
        <div class="card">
            <span class="label">Laptop en tiempo real</span>
            <div class="progress-container">
                <svg width="150" height="150">
                    <circle class="circle-bg" cx="75" cy="75" r="60"></circle>
                    <circle class="circle-progress" cx="75" cy="75" r="60"></circle>
                </svg>
                <div class="percentage">{{ progreso }}%</div>
            </div>
            <div class="status-text">📍 {{ ultima_tarea }}</div>
        </div>

        <div class="card">
            <span class="label">Nueva Tarea</span>
            <input type="text" id="tareaInput" placeholder="¿En qué trabajaremos hoy?" autocomplete="off">
            
            <div class="row">
                <div>
                    <span class="label">Tiempo (Min)</span>
                    <input type="number" id="metaInput" value="25" min="1">
                </div>
            </div>
            
            <button onclick="enviarALaptop()">
                <span>⚡</span> TRANSMITIR A PC
            </button>
        </div>
    </div>

    <script>
        function enviarALaptop() {
            const tarea = document.getElementById('tareaInput').value;
            const meta = document.getElementById('metaInput').value;
            
            if(!tarea) {
                alert("Debes escribir una tarea antes de transmitir.");
                return;
            }

            fetch('/actualizar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ 
                    'ultima_tarea': tarea,
