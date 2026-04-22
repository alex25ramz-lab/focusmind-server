from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# BASE DE DATOS EN MEMORIA
db = {
    "tarea_actual": None,
    "tiempo_actual": None,
    "id_envio": 0,
    "historial": [],
    "rendimiento": {"exitos": 0, "retrasos": 0, "total": 0}
}

@app.route('/enviar_tarea', methods=['POST'])
def enviar_tarea():
    # Esta ruta la usas tú para mandar tareas desde el panel
    data = request.json
    db['tarea_actual'] = data.get('tarea')
    db['tiempo_actual'] = data.get('mins')
    db['id_envio'] += 1
    
    nuevo_registro = {
        "id": db['id_envio'],
        "tarea": db['tarea_actual'],
        "estado": "PENDIENTE",
        "hora": datetime.now().strftime("%H:%M:%S")
    }
    db['historial'].append(nuevo_registro)
    db['rendimiento']['total'] += 1
    return jsonify({"status": "ok"})

@app.route('/get_data')
def get_data():
    # Esta es la que consulta tu main.py cada 5 segundos
    return jsonify({
        "tarea": db['tarea_actual'],
        "tiempo": db['tiempo_actual'],
        "id": db['id_envio']
    })

@app.route('/reportar_progreso', methods=['POST'])
def reportar_progreso():
    # Aquí es donde el main.py avisa si terminaste a tiempo o no
    data = request.json
    id_tarea = data.get('id')
    estado = data.get('estado') # Ejemplo: "HECHO" o "HECHO (CON RETRASO)"

    for t in db['historial']:
        if t['id'] == id_tarea:
            t['estado'] = estado
            if "RETRASO" in estado:
                db['rendimiento']['retrasos'] += 1
            else:
                db['rendimiento']['exitos'] += 1
            break
    return jsonify({"status": "recibido"})

@app.route('/status_total')
def status_total():
    # Esta ruta es para que tú veas el rendimiento total en una web simple
    return jsonify({
        "historial_completo": db['historial'],
        "rendimiento_general": db['rendimiento']
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
