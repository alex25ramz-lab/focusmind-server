from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- INTERFAZ CON EL VERDE NEÓN QUE TE GUSTA ---
INTERFAZ_NEON = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FocusMind</title>
    <style>
        body { 
            background-color: #000; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            margin: 0; 
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }
        .card {
            background-color: #000;
            border: 2px solid #00ffaa; /* Verde Neón */
            border-radius: 25px;
            padding: 40px 20px;
            width: 320px;
            text-align: center;
            box-shadow: 0 0 20px rgba(0, 255, 170, 0.3);
        }
        h1 {
            color: #00ffaa;
            font-size: 32px;
            letter-spacing: 2px;
            margin-bottom: 30px;
            text-shadow: 0 0 10px #00ffaa, 0 0 20px #00ffaa;
            font-weight: bold;
        }
        input {
            width: 85%;
            background-color: #fff;
            border: none;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
            font-size: 16px;
            color: #333;
            outline: none;
            text-align: center;
        }
        input::placeholder {
            color: #888;
        }
        .btn-sincronizar {
            width: 95%;
            background-color: #00ffaa; /* Botón Verde Neón */
            color: #000;
            border: none;
            border-radius: 12px;
            padding: 15px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 0 25px #00ffaa;
            text-transform: uppercase;
            margin-top: 10px;
            transition: 0.3s;
        }
        .btn-sincronizar:active {
            transform: scale(0.95);
            box-shadow: 0 0 10px #00ffaa;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>FOCUSMIND</h1>
        
        <input type="text" id="tarea" placeholder="¿QUÉ TIENES PENSADO PARA HOY?">
        
        <input type="number" id="mins" placeholder="MINUTOS">
        
        <button class="btn-sincronizar" onclick="sincronizar()">SINCRONIZAR</button>
    </div>

    <script>
        async function sincronizar() {
            const tarea = document.getElementById('tarea').value;
            const mins = document.getElementById('mins').value;
            
            if(!tarea || !mins) {
                alert("Ingeniero, rellena ambos campos");
                return;
            }

            try {
                const res = await fetch('/enviar_tarea', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ tarea: tarea, mins: parseInt(mins) })
                });
                if(res.ok) {
                    alert("¡Sincronizado con éxito!");
                }
            } catch(e) {
                alert("Error de conexión con Render");
            }
        }
    </script>
</body>
</html>
"""

ultima_tarea = "Ninguna"
ultimos_minutos = 0
ultimo_id = 0

@app.route('/')
def home():
    return render_template_string(INTERFAZ_NEON)

@app.route('/enviar_tarea', methods=['POST'])
def enviar():
    global ultima_tarea, ultimos_minutos, ultimo_id
    data = request.json
    if data:
        ultima_tarea = data.get('tarea')
        ultimos_minutos = data.get('mins')
        ultimo_id += 1
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/obtener_tarea', methods=['GET'])
def obtener():
    return jsonify({"tarea": ultima_tarea, "mins": ultimos_minutos, "id": ultimo_id})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
