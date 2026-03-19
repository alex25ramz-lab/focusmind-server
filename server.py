from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

datos_usuario = {
    "progreso": 0,
    "ultima_tarea": "Ninguna",
    "tiempo_meta": "10" # Valor por defecto
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
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 15px; padding: 25px; margin-bottom: 20px; }
        .circle { width: 100px; height: 100px; border-radius: 50%; border: 8px solid #30363d; border-top: 8px solid #238636; margin: 15px auto; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: bold; }
        input { width: 85%; padding: 12px; border-radius: 8px; border: 1px solid #30363d; background: #0d1117; color: white; margin-bottom: 10px; }
        .input-meta { width: 40%; border-color: #58a6ff; }
        button { width: 90%; padding: 15px; border-radius: 8px; border: none; background: #238636; color: white; font-weight: bold; cursor: pointer; }
        .status { color: #8b949e; font-size: 0.8rem; }
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
        <h3>Estado Actual</h3>
        <div class="circle">{{ progreso }}%</div>
        <p class="status">Última: <b>{{ ultima_tarea }}</b></p>
    </div>

    <div class="card">
        <p>Nueva Tarea:</p>
        <input type="text" id="tareaInput" placeholder="Nombre de la tarea...">
        <p>Tiempo Meta (Minutos):</p>
        <input type="number" id="metaInput" class="input-meta" value="25">
        <br><br>
        <button onclick="enviarALaptop()">MANDAR A LA PC</button>
    </div>

    <script>
        function enviarALaptop() {
            const tarea = document.getElementById('tareaInput').value;
            const meta = document.getElementById('metaInput').value;
            if(!tarea) return alert("Escribe la tarea");

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
                alert("Sincronizado con éxito");
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
