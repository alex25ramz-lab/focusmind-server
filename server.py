from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Base de datos temporal en memoria
datos_usuario = {
    "progreso": 0,
    "ultima_tarea": "Ninguna"
}

# --- INTERFAZ PARA EL CELULAR (HTML/CSS) ---
# Esta es la vista que verás al entrar a tu link de Render
HTML_MOVIL = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FocusMind Dashboard</title>
    <style>
        body { font-family: sans-serif; background-color: #0d1117; color: white; text-align: center; padding: 20px; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
        input { width: 90%; padding: 12px; margin: 10px 0; border-radius: 6px; border: 1px solid #30363d; background: #0d1117; color: white; }
        button { width: 95%; padding: 15px; background-color: #238636; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
        h1 { font-size: 1.5rem; margin-bottom: 20px; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
    </style>
</head>
<body>
    <h1>📊 DASHBOARD DE INGENIERÍA</h1>
    
    <div class="card">
        <h3>Progreso de Hoy</h3>
        <div style="font-size: 2rem; color: #58a6ff;">{{ progreso }}%</div>
    </div>

    <div class="card">
        <input type="text" id="tarea" placeholder="¿En qué vas a trabajar?">
        <button onclick="enviar()">MANDAR A LA PC</button>
    </div>

    <script>
        function enviar() {
            const tareaInput = document.getElementById('tarea');
            if(!tareaInput.value) return alert("Escribe una tarea, compa");

            fetch('/actualizar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({'ultima_tarea': tareaInput.value})
            })
            .then(res => res.json())
            .then(data => {
                alert("¡Tarea enviada a la nube!");
                tareaInput.value = "";
            });
        }
    </script>
</body>
</html>
"""

# --- RUTAS DE COMUNICACIÓN ---

@app.route('/')
def home():
    # Renderiza la interfaz del celular con el progreso actual
    return render_template_string(HTML_MOVIL, progreso=datos_usuario["progreso"])

@app.route('/actualizar', methods=['POST'])
def actualizar():
    global datos_usuario
    datos_recibidos = request.json
    
    # Actualiza los datos con lo que mande el Celular o la Laptop
    if 'ultima_tarea' in datos_recibidos:
        datos_usuario["ultima_tarea"] = datos_recibidos['ultima_tarea']
    if 'progreso' in datos_recibidos:
        datos_usuario["progreso"] = datos_recibidos['progreso']
        
    return jsonify({"status": "recibido", "datos_actuales": datos_usuario})

@app.route('/obtener_datos', methods=['GET'])
def obtener_datos():
    # Esta es la ruta que tu Laptop consulta cada 5 segundos
    return jsonify(datos_usuario)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
