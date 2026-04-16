from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Tu interfaz Neón integrada (HTML/CSS)
INTERFAZ_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FocusMind App</title>
    <style>
        body { background-color: #0a0a0a; color: #00ffcc; font-family: sans-serif; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .container { border: 2px solid #00ffcc; padding: 20px; border-radius: 15px; box-shadow: 0 0 20px #00ffcc; width: 80%; max-width: 400px; }
        h1 { text-shadow: 0 0 10px #00ffcc; }
        input { background: transparent; border: 1px solid #00ffcc; color: #00ffcc; padding: 10px; margin: 10px 0; border-radius: 5px; width: 90%; outline: none; }
        button { background: #00ffcc; color: black; border: none; padding: 15px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; box-shadow: 0 0 15px #00ffcc; }
        button:active { transform: scale(0.98); }
    </style>
</head>
<body>
    <div class="container">
        <h1>FOCUSMIND</h1>
        <p>¿QUÉ HARÁS HOY?</p>
        <input type="text" id="tarea" placeholder="Ej. Estudiar Dinámica">
        <input type="number" id="mins" placeholder="Minutos (ej. 25)">
        <button onclick="sincronizar()">SINCRONIZAR</button>
    </div>

    <script>
        async function sincronizar() {
            const tarea = document.getElementById('tarea').value;
            const mins = document.getElementById('mins').value;
            
            const res = await fetch('/enviar_tarea', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ tarea: tarea, mins: parseInt(mins) })
            });
            
            if (res.ok) alert("¡Sincronizado con la PC!");
            else alert("Error al conectar");
        }
    </script>
</body>
</html>
"""

ultima_tarea = "Ninguna"
ultimos_minutos = 25
ultimo_id = 0

@app.route('/')
def home():
    # Esto ahora devuelve la interfaz neón en lugar de solo texto
    return render_template_string(INTERFAZ_HTML)

@app.route('/enviar_tarea', methods=['POST'])
def enviar():
    global ultima_tarea, ultimos_minutos, ultimo_id
    data = request.json
    if data:
        ultima_tarea = data.get('tarea', 'Sin nombre')
        ultimos_minutos = data.get('mins', 25)
        ultimo_id += 1
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/obtener_tarea', methods=['GET'])
def obtener():
    return jsonify({"tarea": ultima_tarea, "mins": ultimos_minutos, "id": ultimo_id})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
