from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Base de datos temporal (Se limpia si el servidor de Render se reinicia)
# Estructura: {"id": 1, "tarea": "Nombre", "mins": 25, "estado": "Pendiente", "fecha": "..."}
historial_tareas = []
ultimo_id = 0

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
        # Insertar al inicio para que lo más nuevo salga primero
        historial_tareas.insert(0, nueva_entrada)
        
        # Mantener solo las últimas 20 tareas para no saturar la memoria
        if len(historial_tareas) > 20:
            historial_tareas.pop()
            
        return jsonify({"status": "success", "tarea_id": ultimo_id}), 200
    return jsonify({"status": "error", "message": "Falta el nombre de la tarea"}), 400

@app.route('/obtener_tarea', methods=['GET'])
def obtener_tarea():
    # Retorna la tarea más reciente que esté pendiente para la PC
    for t in historial_tareas:
        if t["estado"] == "Pendiente":
            return jsonify({
                "tarea": t["tarea"],
                "mins": t["mins"],
                "id": t["id"]
            }), 200
    return jsonify({"tarea": None}), 200

@app.route('/historial', methods=['GET'])
def obtener_historial():
    # Esta es la ruta que usará tu celular para mostrar la lista
    return jsonify(historial_tareas), 200

@app.route('/actualizar_estado', methods=['POST'])
def actualizar_estado():
    # Ruta para que la PC avise cuando terminó una tarea
    data = request.json
    t_id = data.get('id')
    nuevo_estado = data.get('estado') # Ej: "Completada" o "Expirada"
    
    for t in historial_tareas:
        if t["id"] == t_id:
            t["estado"] = nuevo_estado
            return jsonify({"status": "updated"}), 200
    return jsonify({"status": "not_found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
