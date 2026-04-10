from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Memoria temporal (Lo que se muestra en el celular)
datos_usuario = {
    "progreso": 0,
    "ultima_tarea": "Sistema Iniciado",
    "tiempo_meta": "25"
}

# La "piel" de tu página web (HTML/CSS)
HTML_MOVIL = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>FocusMind Hub</title>
    <style>
        :root {
            --bg: #0d1117;
            --card: #161b22;
            --border: #30363d;
            --accent: #238636;
            --blue: #58a6ff;
        }
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: var(--bg); 
            color: white; 
            margin: 0; 
            padding: 20px;
            display: flex; flex-direction: column; align-items: center;
        }
        .card { 
            background: var(--card); 
            border: 1px solid var(--border); 
            border-radius: 20px; 
            padding: 25px; 
            width: 100%; max-width: 350px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            margin-bottom: 20px;
            text-align: center;
        }
        h1 { color: var(--blue); font-size: 1.2rem; letter-spacing: 2px; }
        .circle {
            width: 120px; height: 120px;
            border-radius: 50%;
            border: 10px solid var(--border);
            border-top: 10px solid var(--accent);
            margin: 20px auto;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.5rem; font-weight: bold;
            transition: 0.5s;
        }
        input {
            width: 100%; padding: 15px; margin: 10px 0;
            background: #010409; border: 1px solid var(--border);
            color: white; border-radius: 10px; box-sizing: border-box;
        }
        button {
            width: 100%; padding: 15px;
            background: var(--accent); color: white;
            border: none; border-radius: 10px;
            font-weight: bold; font-size: 1rem; cursor: pointer;
        }
        button:active { transform: scale(0.98); }
        .status { color: #8b949e; font-size: 0.9rem; margin-top: 10px; }
    </style>
    <script>
        // Actualiza el progreso sin recargar toda la página
        setInterval(function(){
            if(document.activeElement.tagName !== 'INPUT') {
                fetch('/obtener_datos').then(r => r.json()).then(data => {
                    if(data.progreso != {{ progreso }}) { location.reload(); }
                });
            }
        }, 5000);
    </script>
</head>
<body>
    <h1>FOCUSMIND REMOTE</h1>
    
    <div class="card">
        <div class="status">Progreso en Laptop:</div>
        <div class="circle">{{ progreso }}%</div>
        <div style="font-weight: bold;">{{ ultima_tarea }}</div>
    </div>

    <div class="card">
        <input type="text" id="t" placeholder="¿Qué tarea enviaremos?">
        <input type="number" id="m" value="25">
        <button onclick="enviar()">TRANSMITIR A PC</button>
    </div>

    <script>
        function enviar() {
            const t = document.getElementById('t').value;
            const m = document.getElementById('m').value;
            if(!t) return alert("Escribe algo");
            
            fetch('/actualizar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({'ultima_tarea': t, 'tiempo_meta': m, 'progreso': 0})
            }).then(() => {
                alert("Tarea enviada con éxito");
                location.reload();
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
