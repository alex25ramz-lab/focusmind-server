from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Variables globales simples para evitar errores de base de datos
ultima_tarea = "Ninguna"
ultimos_minutos = 25
ultimo_id = 0

@app.route('/')
def home():
    # Esta es la ruta que verás en el celular para confirmar que sirve
    return f"SISTEMA FOCUSMIND: ONLINE. ID ACTUAL: {ultimo_id}"

@app.route('/enviar_tarea', methods=['POST'])
def enviar():
    global ultima_tarea, ultimos_minutos, ultimo_id
    try:
        data = request.json
        if data:
            ultima_tarea = data.get('tarea', 'Sin nombre')
            ultimos_minutos = data.get('mins', 25)
            ultimo_id += 1
            return jsonify({"status": "recibido", "id": ultimo_id}), 200
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 400
    return jsonify({"status": "no data"}), 400

@app.route('/obtener_tarea', methods=['GET'])
def obtener():
    return jsonify({
        "tarea": ultima_tarea,
        "mins": ultimos_minutos,
        "id": ultimo_id
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
