from Flask import Flask, render_template_string, request, jsonify

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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FocusMind Control</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0d1117; color: white; text-align: center; padding: 20px; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 15px; padding: 25px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .circle { width: 120px; height: 120px; border-radius: 50%; border: 8px solid #30363d; border-top: 8px solid #238636; margin: 20px auto; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: bold; }
        input { width: 85%; padding: 15px; border-radius: 8px; border: 1px solid #30363d; background: #0d1117; color: white; margin-bottom: 15px; font-size: 1rem; }
        .input-meta { width: 40%; border-color: #58a6ff; text-align: center; }
        button { width: 90%; padding: 18px; border-radius: 8px; border: none; background: #238636; color: white; font-weight: bold; font-size: 1.1rem; cursor: pointer; transition: 0.3s; }
        button:active { transform: scale(0.95); background: #2ea043; }
        .status { color: #8b949e; font-size: 0.9rem; margin-top: 10px; }
    </style>
    <script>
        setInterval(function(){
            if(document.activeElement.tagName !== 'INPUT') { location.reload(); }
        }, 5000); 
    </script>
</head>
<body>
    <h1>🚀 FocusMind Control</h1>
    
    <div class="card">
        <h3>Progreso en Laptop</h3>
        <div class="circle">{{ progreso }}%</div>
        <p class="status">Última acción: <b>{{ ultima_tarea }}</b></p>
    </div>

    <div class="card">
        <p>Nueva Tarea:</p>
        <input type="text" id="tareaInput" placeholder="¿Qué vamos a hacer?">
        <p>Tiempo Meta (Minutos):</p>
        <input type="number" id="metaInput" class="input-meta" value="25">
        <br><br>
        <button onclick="enviarALaptop()">ENVIAR A LA PC</button>
    </div>

    <script>
        function enviarALaptop() {
            const tarea = document.getElementById('tareaInput').value;
            const meta = document.getElementById('metaInput').value;
            if(!tarea) return alert("Escribe la tarea, compa");

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
                alert("Sincronizado con la PC");
                document.getElementById('tareaInput').value = "";
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
