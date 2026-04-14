from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Diccionario donde se guarda la información temporalmente
datos_compartidos = {
    "tarea": "Esperando misión...",
    "tiempo": "25"
}

# Diseño futurista para el celular
html_template = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>FocusMind Command</title>
    <style>
        :root { --bg: #05070a; --accent: #00d2ff; --glass: rgba(255, 255, 255, 0.05); }
        body { font-family: 'Segoe UI', sans-serif; background: radial-gradient(circle at top, #1a2a44 0%, #05070a 100%); color: white; margin: 0; display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .card { background: var(--glass); backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.1); border-radius: 25px; padding: 30px; width: 85%; max-width: 350px; text-align: center; box-shadow: 0 20px 40px rgba(0,0,0,0.4); }
        h1 { font-size: 1.4rem; letter-spacing: 3px; background: linear-gradient(to right, #00d2ff, #3a7bd5); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 25px; }
        .group { margin-bottom: 15px; text-align: left; }
        label { font-size: 0.7rem; color: var(--accent); font-weight: bold; margin-left: 5px; text-transform: uppercase; }
        input { width: 100%; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 15px; color: white; margin-top: 5px; box-sizing: border-box; outline: none; font-size: 1rem; }
        button { width: 100%; background: linear-gradient(45deg, #3a7bd5, #00d2ff); border: none; padding: 18px; border-radius: 12px; color: white; font-weight: bold; font-size: 1rem; cursor: pointer; margin-top: 15px; transition: 0.3s; }
        button:active { transform: scale(0.98); }
    </style>
</head>
<body>
    <div class="card">
        <h1>FOCUSMIND</h1>
        <form action="/actualizar" method="post">
            <div class="group">
                <label>Misión</label>
                <input type="text" name="tarea_input" placeholder="¿Qué harás?" required>
            </div>
            <div class="group">
                <label>Tiempo (min)</label>
                <input type="number" name="tiempo_input" value="25">
            </div>
            <button type="submit">DESPLEGAR</button>
        </form>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/actualizar', methods=['POST'])
def actualizar():
    # Sincronizamos los nombres que vienen del formulario con los del diccionario
    datos_compartidos["tarea"] = request.form.get("tarea_input")
    datos_compartidos["tiempo"] = request.form.get("tiempo_input")
    return '<script>alert("Enviado con éxito"); window.location.href="/";</script>'

@app.route('/get_data')
def get_data():
    return jsonify(datos_compartidos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
