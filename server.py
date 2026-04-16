from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- INTERFAZ AVANZADA CON AUTO-LIMPIEZA ---
INTERFAZ_AVANZADA = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FocusMind OS</title>
    <style>
        :root { --neon-green: #00ffaa; --dark-bg: #050505; }
        
        body { 
            background-color: var(--dark-bg); 
            display: flex; justify-content: center; align-items: center; 
            height: 100vh; margin: 0; font-family: 'Segoe UI', sans-serif;
            overflow: hidden;
        }

        .card {
            background-color: rgba(0, 0, 0, 0.9);
            border: 2px solid var(--neon-green);
            border-radius: 30px;
            padding: 50px 25px;
            width: 320px;
            text-align: center;
            position: relative;
            box-shadow: 0 0 20px rgba(0, 255, 170, 0.2);
            animation: pulse 4s infinite;
        }

        /* Línea de escaneo láser */
        .card::after {
            content: "";
            position: absolute;
            top: -100%; left: 0; width: 100%; height: 100%;
            background: linear-gradient(to bottom, transparent, rgba(0, 255, 170, 0.1), transparent);
            animation: scan 3s infinite linear;
            pointer-events: none;
        }

        @keyframes scan {
            0% { top: -100%; }
            100% { top: 100%; }
        }

        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 15px rgba(0, 255, 170, 0.2); }
            50% { box-shadow: 0 0 30px rgba(0, 255, 170, 0.5); border-color: #00ffcc; }
        }

        h1 {
            color: var(--neon-green);
            font-size: 35px;
            letter-spacing: 4px;
            margin-bottom: 30px;
            text-shadow: 0 0 15px var(--neon-green);
            font-weight: 900;
        }

        input {
            width: 85%;
            background: rgba(255, 255, 255, 0.9);
            border: 2px solid transparent;
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 20px;
            font-size: 16px;
            font-weight: bold;
            color: #111;
            outline: none;
            transition: 0.3s;
            text-align: center;
        }

        .btn-sincronizar {
            width: 95%;
            background-color: var(--neon-green);
            color: #000;
            border: none;
            border-radius: 15px;
            padding: 18px;
            font-size: 20px;
            font-weight: 900;
            cursor: pointer;
            box-shadow: 0 0 20px var(--neon-green);
            transition: 0.4s;
            margin-top: 10px;
        }

        .btn-sincronizar:active { transform: scale(0.9); }

        .status-dot {
            width: 10px; height: 10px; background: var(--neon-green);
            border-radius: 50%; display: inline-block; margin-right: 10px;
            box-shadow: 0 0 8px var(--neon-green);
        }
    </style>
</head>
<body>
    <div class="card">
        <div style="color: var(--neon-green); font-size: 10px; margin-bottom: 10px;">
            <span class="status-dot"></span> SYSTEM ONLINE
        </div>
        <h1>FOCUSMIND</h1>
        
        <input type="text" id="tarea" placeholder="¿QUÉ TIENES PENSADO?">
        <input type="number" id="mins" placeholder="MINUTOS">
        
        <button class="btn-sincronizar" onclick="sincronizar()">SINCRONIZAR</button>
        
        <p style="color: #444; font-size: 9px; margin-top: 20px;">V.2.1 - MECATRÓNICA CORP</p>
    </div>

    <script>
        async function sincronizar() {
            const btn = document.querySelector('.btn-sincronizar');
            const inputTarea = document.getElementById('tarea');
            const inputMins = document.getElementById('mins');
            
            if(!inputTarea.value || !inputMins.value) {
                alert("ERROR: FALTAN DATOS");
                return;
            }

            btn.innerHTML = "ENVIANDO...";

            try {
                const res = await fetch('/enviar_tarea', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ 
                        tarea: inputTarea.value, 
                        mins: parseInt(inputMins.value) 
                    })
                });
                
                if(res.ok) {
                    btn.innerHTML = "¡ENVIADO!";
                    
                    // --- AQUÍ ESTÁ EL TRUCO DE LA LIMPIEZA ---
                    setTimeout(() => { 
                        inputTarea.value = ""; // Borra la tarea
                        inputMins.value = "";  // Borra los minutos
                        btn.innerHTML = "SINCRONIZAR"; 
                    }, 1500); 
                }
            } catch(e) {
                alert("FALLA DE ENLACE");
                btn.innerHTML = "REINTENTAR";
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
    return render_template_string(INTERFAZ_AVANZADA)

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
