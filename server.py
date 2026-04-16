from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- ESTA ES LA INTERFAZ QUE VERÁS EN EL CELULAR ---
INTERFAZ_NEON = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FocusMind</title>
    <style>
        body { background-color: #000; color: #00ffcc; font-family: 'Segoe UI', sans-serif; text-align: center; margin: 0; padding: 20px; }
        .box { border: 2px solid #00ffcc; border-radius: 15px; padding: 20px; box-shadow: 0 0 15px #00ffcc; max-width: 300px; margin: auto; margin-top: 50px; }
        h1 { font-size: 24px; text-shadow: 0 0 10px #00ffcc; }
        input { background: transparent; border: 1px solid #00ffcc; color: #fff; width: 80%; padding: 10px; margin: 10px 0; border-radius: 5px; text-align: center; outline: none; }
        button { background: #00ffcc; color: #000; border: none; padding: 15px 30px; border-radius: 5px; font-weight: bold; cursor: pointer; box-shadow: 0 0 10px #00ffcc; width: 90%; }
        button:active { transform: scale(0.95); box-shadow: 0 0 5px #00ffcc; }
    </style>
</head>
<body>
    <div class="box">
        <h1>FOCUSMIND</h1>
        <p>¿QUÉ HARÁS HOY?</p>
        <input type="text" id="tarea" placeholder="Ej. Tarea de Dinámica">
        <p>TIEMPO (MIN)</p>
        <input type="number" id="mins" value="25">
        <br><br>
        <button onclick="sincronizar()">SINCRONIZAR</button>
    </div>

    <script>
        async function sincronizar() {
            const tarea = document.getElementById('tarea').value;
            const mins = document.getElementById('mins').value;
            if(!tarea) return alert("Escribe una tarea");

            try {
                const res = await fetch('/enviar_tarea', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ tarea: tarea, mins: parseInt(mins) })
                });
                if(res.ok) alert("¡Sincronizado con éxito!");
                else alert("Error al sincronizar");
            } catch(e) { alert("No se pudo conectar al servidor"); }
        }
    </script>
</body>
</html>
"""

# Variables para la PC
ultima_tarea = "Ninguna"
ultimos_minutos = 25
ultimo_id = 0

@app.route('/')
def home():
    # Esto hace que se vea la interfaz neón al abrir el link
    return render_template_string(INTERFAZ_NEON)

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
