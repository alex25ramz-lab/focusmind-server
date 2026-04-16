from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ultima_tarea = "Ninguna"
ultimos_minutos = 25
ultimo_id = 0

@app.route('/')
def home():
    # Mensaje de confirmación técnica
    return "Servidor FocusMind listo. Usa la interfaz para interactuar."

@app.route('/enviar_tarea', methods=['POST'])
def enviar():
    global ultima_tarea, ultimos_minutos, ultimo_id
    data = request.json
    if data:
        ultima_tarea = data.get('tarea', 'Sin nombre')
        ultimos_minutos = data.get('mins', 25)
        ultimo_id += 1
        return jsonify({"status": "ok", "id": ultimo_id}), 200
    return jsonify({"status": "error"}), 400

@app.route('/obtener_tarea', methods=['GET'])
def obtener():
    return jsonify({"tarea": ultima_tarea, "mins": ultimos_minutos, "id": ultimo_id})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
