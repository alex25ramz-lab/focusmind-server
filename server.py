from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Almacén de datos
datos_tarea = {"tarea": "", "mins": "25"}

HTML_BASE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FocusMind OS Server</title>
    <style>
        body { background-color: #000; color: white; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background-color: #0a0a0a; border: 2px solid #00ffff; border-radius: 25px; padding: 40px; width: 85%; max-width: 400px; text-align: center; box-shadow: 0 0 20px rgba(0, 255, 255, 0.2); }
        h1 { color: #00ffff; letter-spacing: 5px; text-shadow: 0 0 10px #00ffff; }
        input { width: 100%; padding: 15px; margin-bottom: 20px; border-radius: 10px; border: none; font-size: 16px; }
        .btn-sincronizar { 
            width: 100%; padding: 18px; background-color: #00ffff; color: #000; border: 2px solid #fff; 
            border-radius: 12px; font-size: 18px; font-weight: bold; cursor: pointer;
            box-shadow: 0 0 15px #00ffff; transition: 0.3s;
        }
        .btn-sincronizar:active { transform: scale(0.95); box-shadow: 0 0 5px #00ffff; }
    </style>
</head>
<body>
    <div class="card">
        <h1>FOCUSMIND</h1>
        <form action="/enviar" method="POST">
            <input type="text" name="tarea" placeholder="ACTIVIDAD" required>
            <input type="number" name="mins" placeholder="MINUTOS" value="25">
            <button type="submit" class="btn-sincronizar">SINCRONIZAR</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_BASE)

@app.route('/enviar', methods=['POST'])
def enviar():
    global datos_tarea
    datos_tarea = {"tarea": request.form.get("tarea"), "mins": request.form.get("mins")}
    return render_template_string(HTML_BASE + "<script>alert('Enviado a FocusMind OS');</script>")

@app.route('/get_tarea', methods=['GET'])
def get_tarea():
    return jsonify(datos_tarea)

if __name__ == '__main__':
    app.run(debug=True)
