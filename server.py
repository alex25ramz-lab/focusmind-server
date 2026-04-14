from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Memoria temporal del servidor
datos_compartidos = {
    "tarea": "Esperando misión...",
    "tiempo": "25"
}

# Interfaz para tu celular
html_template = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FocusMind Control</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #05070a; color: white; text-align: center; padding-top: 50px; }
        .card { background: rgba(255,255,255,0.05); border: 1px solid #00d2ff; padding: 30px; border-radius: 20px; display: inline-block; width: 80%; max-width: 350px; }
        input { width: 90%; padding: 12px; margin: 10px 0; border-radius: 8px; border: none; font-size: 16px; }
        button { width: 95%; padding: 15px; border-radius: 8px; border: none; background: #00d2ff; color: #05070a; font-weight: bold; font-size: 18px; cursor: pointer; }
        h1 { letter-spacing: 2px; color: #00d2ff; }
    </style>
</head>
<body>
    <div class="card">
        <h1>FOCUSMIND</h1>
        <form action="/actualizar" method="post">
            <input type="text" name="t" placeholder="¿Qué tarea harás?" required>
            <input type="number" name="m" placeholder="Minutos (ej: 25)" value="25">
            <button type="submit">SINCRONIZAR</button>
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
    datos_compartidos["tarea"] = request.form.get("t")
    datos_compartidos["tiempo"] = request.form.get("m")
    return '<script>alert("Sincronizado con la Laptop"); window.location.href="/";</script>'

@app.route('/get_data')
def get_data():
    return jsonify(datos_compartidos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
