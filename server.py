from flask import Flask, request, jsonify
from flask_cors import CORS  # Importante para que el cel conecte
from datetime import datetime

app = Flask(__name__)
CORS(app) # Esto permite que tu celular acceda a los datos

# Base de datos temporal
historial_tareas = []
ultimo_id = 0

# 1. RUTA DE INICIO (Para que tu link principal no dé error)
@app.route('/')
def home():
    return jsonify({
        "sistema": "FocusMind Server",
        "estado": "Online",
        "tareas_activas": len([t for t in historial_tareas if t['estado'] == 'Pendiente']),
        "endpoints": ["/historial", "/enviar_tarea"]
    }), 200

# 2. ENVIAR TAREA DESDE EL CELULAR
@app.route('/enviar_tarea', methods=['POST'])
def enviar_tarea():
    global ultimo_id
    data = request.json
    tarea = data.get('tarea')
    mins = data.get('mins', 25)
    
    if tarea:
        ultimo_id += 1
        nueva_entrada = {
            "id": ultimo_id,
            "tarea": tarea,
            "mins": mins,
            "estado": "Pendiente",
            "fecha": datetime.now().strftime("%H:%M:%S")
        }
        historial_tareas.insert(0, nueva_entrada) # Lo más nuevo arriba
        if len(historial_tareas) > 20: historial_tareas.pop()
        return jsonify({"status": "success", "id": ultimo_id}), 200
    return jsonify({"status": "error"}), 400

# 3. OBTENER TAREA EN LA PC
@app.route('/obtener_tarea', methods=['GET'])
def obtener_tarea():
    for t in historial_tareas:
        if t["estado"] == "Pendiente":
            return jsonify({"tarea": t["tarea"], "mins": t["mins"], "id": t["id"]}), 200
    return jsonify({"tarea": None}), 200

# 4. VER EL REGISTRO EN EL CELULAR
@app.route('/historial', methods=['GET'])
def obtener_historial():
    return jsonify(historial_tareas), 200

# 5. ACTUALIZAR ESTADO DESDE LA PC
@app.route('/actualizar_estado', methods=['POST'])
def actualizar_estado():
    data = request.json
    t_id = data.get('id')
    nuevo_estado = data.get('estado')
    for t in historial_tareas:
        if t["id"] == t_id:
            t["estado"] = nuevo_estado
            return jsonify({"status": "updated"}), 200
    return jsonify({"status": "not_found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
