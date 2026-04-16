from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- INTERFAZ NEÓN PERSONALIZADA ---
INTERFAZ_NEON = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FocusMind</title>
    <style>
        body { background-color: #000; color: #00ffcc; font-family: 'Segoe UI', sans-serif; text-align: center; margin: 0; padding: 20px; }
        .box { border: 2px solid #00ffcc; border-radius: 15px; padding: 20px; box-shadow: 0 0 20px #00ffcc; max-width: 320px; margin: auto; margin-top: 50px; background: rgba(0, 255, 204, 0.05); }
        h1 { font-size: 28px; text-shadow: 0 0 15px #00ffcc; margin-bottom: 5px; }
        p { font-weight: bold; letter-spacing: 1px; }
        input { background: transparent; border: 1px solid #00ffcc; color: #fff; width: 85%; padding: 12px; margin: 15px 0; border-radius: 8px; text-align: center; outline: none; font-size: 16px; }
        input::placeholder { color: rgba(0, 255, 204, 0.4); }
        button { background: #00ffcc; color: #000; border: none; padding: 18px; border-radius: 8px; font-weight: bold; cursor: pointer; box-shadow: 0 0 15px #00ffcc; width: 95%; font-size: 16px; text-transform: uppercase; }
        button:active { transform: scale(0.96); box-shadow: 0 0 5px #00ffcc; }
    </style>
</head>
<body>
    <div class="box">
        <h1>FOCUSMIND</h1>
        <p style="margin-top: 20px;">¿QUÉ TIENES PENSADO PARA HOY?</p>
        <input type="text" id="tarea" placeholder="Escribe tu objetivo aquí...">
        
        <p>TIEMPO ESTIMADO (MIN)</p>
        <input type="number" id="mins" value="25">
        
        <br><br>
        <button onclick="sincronizar()">⚡ SINCRONIZAR CON PC ⚡</button>
    </div>

    <script>
        async function sincronizar() {
            const tarea = document.getElementById('tarea').value;
            const mins = document.getElementById('mins').value;
            if(!tarea) return alert("¡Ingeniero, escribe una tarea primero!");

            try {
                const res = await fetch('/enviar_tarea', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ tarea: tarea, mins: parseInt(mins) })
                });
                if(res.ok) alert("¡Enviado a la laptop con éxito!");
                else alert("Error al conectar con el servidor");
            } catch(e) { alert("El servidor no responde"); }
        }
    </script>
</body>
</html>
"""

# Variables de control para la PC
ultima_tarea = "Ninguna"
ultimos_minutos = 25
ultimo_id = 0

@app.route('/')
def home():
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
