from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Memoria temporal del servidor
datos_usuario = {
    "progreso": 0,
    "ultima_tarea": "Ninguna",
    "tiempo_meta": "25"
}

HTML_MOVIL = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>FocusMind Mobile</title>
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
            background: var(--bg); 
            color: var(--text-main); 
            margin: 0; 
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        h1 { font-size: 1.5rem; margin-bottom: 25px; color: var(--blue); letter-spacing: 1px; }

        .container { width: 100%; max-width: 400px; }

        .card { 
            background: var(--card); 
            border: 1px solid var(--border); 
            border-radius: 16px; 
            padding: 20px; 
            margin-bottom: 20px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }

        .progress-container {
            position: relative;
            width: 140px;
            height: 140px;
            margin: 0 auto 15px;
        }

        .circle-bg {
            fill: none;
            stroke: var(--border);
            stroke-width: 10;
        }

        .circle-progress {
            fill: none;
            stroke: var(--accent);
            stroke-width: 10;
            stroke-linecap: round;
            stroke-dasharray: 314; /* 2 * PI * 50 (radio) */
            stroke-dashoffset: calc(314 - (314 * {{ progreso }}) / 100);
            transition: stroke-dashoffset 1s ease-out;
            transform: rotate(-90deg);
            transform-origin: 50% 50%;
        }

        .percentage {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 1.8rem;
            font-weight: bold;
            color: white;
        }

        .label { color: var(--text-dim); font-size: 0.85rem; text-transform: uppercase; margin-bottom: 8px; display: block; }
        
        .status-text { font-size: 1rem; color: white; font-weight: 500; }

        input { 
            width: 100%; 
            padding: 14px; 
            border-radius: 10px; 
            border: 1px solid var(--border); 
            background: #010409; 
            color: white; 
            margin-bottom: 15px; 
            font-size: 1rem;
            box-sizing: border-box;
            outline: none;
        }

        input:focus { border-color: var(--blue); box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.3); }

        .flex-row { display: flex; gap: 10px; align-items: center; margin-bottom: 15px; }
        .flex-row input { margin-bottom: 0; }

        button { 
            width: 100%; 
            padding: 16px; 
            border-radius: 12px; 
            border: none; 
            background: var(--accent); 
            color: white; 
            font-weight: bold; 
            font-size: 1.1rem; 
            cursor: pointer; 
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        button:active { transform: scale(0.97); background: #2ea043; }
    </style>
    <script>
        // Recarga suave solo si no se está escribiendo
        setInterval(function(){
            if(document.activeElement.tagName !== 'INPUT') {
                fetch('/obtener_datos')
                .then(r => r.json())
                .then(data => {
                    if(data.progreso != {{ progreso }} || data.ultima_tarea != "{{ ultima_tarea }}") {
                        location.reload();
                    }
                });
            }
        }, 5000); 
    </script>
</head>
<body>
    <h1>FOCUSMIND HUB</h1>
    
    <div class="container">
        <div class="card">
            <span class="label">Sincronización Laptop</span>
            <div class="progress-container">
                <svg width="140" height="140">
                    <circle class="circle-bg" cx="70" cy="70" r="50"></circle>
                    <circle class="circle-progress" cx="70" cy="70" r="50"></circle>
                </svg>
                <div class="percentage">{{ progreso }}%</div>
            </div>
            <div class="status-text">💻 {{ ultima_tarea }}</div>
        </div>

        <div class="card">
            <span class="label">Nueva Actividad</span>
            <input type="text" id="tareaInput" placeholder="Escribe la tarea..." autocomplete="off">
            
            <div class="flex-row">
                <div style="flex: 2">
                    <span class="label">Minutos Meta</span>
                    <input type="number" id="metaInput" value="25" min="1">
                </div>
            </div>
            
            <button onclick="enviarALaptop()">
                <span>🚀</span> TRANSMITIR A PC
            </button>
        </div>
    </div>

    <script>
        function enviarALaptop() {
            const tarea = document.getElementById('tareaInput').value;
            const meta = document.getElementById('metaInput').value;
            
            if(!tarea) {
                alert("Por favor, ingresa una tarea.");
                return;
            }

            fetch('/actualizar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ 
                    'ultima_tarea': tarea, 
                    'tiempo_meta': meta,
                    'progreso': 0 
                })
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('tareaInput').value = "";
                // Pequeña vibración visual al botón para confirmar éxito
                const btn = document.querySelector('button');
                btn.style.background = '#58a6ff';
                btn.innerText = "✅ ENVIADO";
                setTimeout(() => {
                    location.reload();
                }, 800);
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_MOVIL, progreso=datos_usuario["progreso"], ultima_tarea=datos_usuario["ultima_tarea"])

@app.route('/actualizar', methods=['POST'])
def actualizar():
    global datos_usuario
    datos = request.json
    if 'ultima_tarea' in datos: datos_usuario["ultima_tarea"] = datos['ultima_tarea']
    if 'tiempo_meta' in datos: datos_usuario["tiempo_meta"] = datos['tiempo_meta']
    if 'progreso' in datos: datos_usuario["progreso"] = datos['progreso']
    return jsonify({"status": "ok"})

@app.route('/obtener_datos', methods=['GET'])
def obtener_datos():
    return jsonify(datos_usuario)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
