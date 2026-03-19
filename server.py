from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# Diccionario para guardar los datos en la nube temporalmente
datos_usuario = {
    "tareas_completadas": 0,
    "progreso": 0,
    "ultima_tarea": "Ninguna",
    "mensaje_servidor": "Conectado a la nube"
}

# --- INTERFAZ PARA EL CELULAR (HTML/CSS) ---
HTML_MOVIL = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FocusMind Cloud</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #121212; color: white; text-align: center; margin: 0; padding: 20px; }
        .card { background: #1e1e26; border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        .progress-container { width: 200px; margin: 0 auto; }
        input { width: 80%; padding: 12px; border-radius: 8px; border: none; margin-bottom: 10px; font-size: 16px; }
        button { width: 85%; padding: 15px; border-radius: 8px; border: none; background: #28a745; color: white; font-weight: bold; font-size: 18px; cursor: pointer; }
        button:active { background: #218838; transform: scale(0.98); }
        h1 { color: #f0f0f0; font-size: 22px; text-transform: uppercase; letter-spacing: 2px; }
    </style>
</head>
<body>
    <h1>📊 Dashboard de Ingeniería</h1>
    
    <div class="card">
        <h3>Progreso de Hoy</h3>
        <div class="progress-container">
            <canvas id="graficaProgreso"></canvas>
        </div>
        <p id="textoProgreso">{{ progreso }}% Completado</p>
    </div>

    <div class="card">
        <input type="text" id="tareaInput" placeholder="Escribe nueva tarea...">
        <button onclick="mandarALaPC()">MANDAR A LA PC</button>
    </div>

    <script>
        // Configuración de la Gráfica de Dona
        const ctx = document.getElementById('graficaProgreso').getContext('2d');
        const grafica = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [{{ progreso }}, 100 - {{ progreso }}],
                    backgroundColor: ['#28a745', '#333'],
                    borderWidth: 0
                }]
            },
            options: { cutout: '80%', plugins: { legend: { display: false } } }
        });

        function mandarALaPC() {
            const tarea = document.getElementById('tareaInput').value;
            if (!tarea) return alert("Escribe algo, compa");

            fetch('/actualizar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ 'ultima_tarea': tarea })
            })
            .then(res => res.json())
            .then(data => {
                alert("¡Tarea enviada a la nube!");
                location.reload(); 
            });
        }
    </script>
</body>
</html>
"""

# --- RUTAS DEL SERVIDOR ---

@app.route('/movil')
def index():
    # Renderiza la interfaz del celular con los datos actuales
    return render_template_string(HTML_MOVIL, progreso=datos_usuario["progreso"])

@app.route('/actualizar', methods=['POST'])
def actualizar():
    global datos_usuario
    nuevo_dato = request.json
    if 'ultima_tarea' in nuevo_dato:
        datos_usuario["ultima_tarea"] = nuevo_dato['ultima_tarea']
    if 'progreso' in nuevo_dato:
        datos_usuario["progreso"] = nuevo_dato['progreso']
    return jsonify({"status": "ok", "datos": datos_usuario})

@app.route('/obtener_datos', methods=['GET'])
def obtener_datos():
    # Esta es la ruta que consultará tu laptop
    return jsonify(datos_usuario)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
