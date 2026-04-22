from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURACIÓN DE BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Tabla de tareas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            minutos INTEGER NOT NULL,
            estado TEXT DEFAULT 'PENDIENTE',
            fecha_creacion DATETIME
        )
    ''')
    # Tabla de estadísticas globales
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estadisticas (
            id INTEGER PRIMARY KEY,
            a_tiempo INTEGER DEFAULT 0,
            con_retraso INTEGER DEFAULT 0,
            expiradas INTEGER DEFAULT 0
        )
    ''')
    # Inicializar fila de estadísticas si no existe
    cursor.execute('INSERT OR IGNORE INTO estadisticas (id, a_tiempo, con_retraso, expiradas) VALUES (1, 0, 0, 0)')
    conn.commit()
    conn.close()

# --- RUTAS DE LA API ---

@app.route('/nueva_tarea', methods=['POST'])
def nueva_tarea():
    """Ruta para que tú (u otro sistema) mandes tareas a la App"""
    data = request.json
    descripcion = data.get('tarea')
    minutos = data.get('minutos')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tareas (descripcion, minutos, fecha_creacion) VALUES (?, ?, ?)',
                   (descripcion, minutos, datetime.now()))
    tarea_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({"status": "ok", "id": tarea_id}), 201

@app.route('/obtener_tarea', methods=['GET'])
def obtener_tarea():
    """Ruta que consulta la App FocusMind cada 5 segundos"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Obtenemos la última tarea pendiente
    cursor.execute('SELECT descripcion, minutos, id FROM tareas WHERE estado = "PENDIENTE" ORDER BY id DESC LIMIT 1')
    res = cursor.fetchone()
    conn.close()
    
    if res:
        return jsonify({"tarea": res[0], "minutos": res[1], "id": res[2]})
    return jsonify({"tarea": None})

@app.route('/reportar_estado', methods=['POST'])
def reportar_estado():
    """Ruta donde la App reporta si terminó a tiempo o con retraso"""
    data = request.json
    id_tarea = data.get('id')
    nuevo_estado = data.get('estado') # Esperamos: 'HECHO', 'RETARDO' o 'EXPIRADA'
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 1. Actualizar el estado de la tarea específica
    cursor.execute('UPDATE tareas SET estado = ? WHERE id = ?', (nuevo_estado, id_tarea))
    
    # 2. LÓGICA DE ESTADÍSTICAS (Aquí corregimos tu error)
    if nuevo_estado == "HECHO":
        cursor.execute('UPDATE estadisticas SET a_tiempo = a_tiempo + 1 WHERE id = 1')
    elif nuevo_estado == "RETARDO":
        cursor.execute('UPDATE estadisticas SET con_retraso = con_retraso + 1 WHERE id = 1')
    elif nuevo_estado == "EXPIRADA":
        cursor.execute('UPDATE estadisticas SET expiradas = expiradas + 1 WHERE id = 1')
    
    conn.commit()
    conn.close()
    return jsonify({"status": "actualizado", "estado_registrado": nuevo_estado})

@app.route('/stats', methods=['GET'])
def ver_stats():
    """Ruta para ver cómo va tu rendimiento"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT a_tiempo, con_retraso, expiradas FROM estadisticas WHERE id = 1')
    res = cursor.fetchone()
    conn.close()
    
    return jsonify({
        "tareas_a_tiempo": res[0],
        "tareas_con_retraso": res[1],
        "tareas_expiradas": res[2],
        "total_finalizadas": res[0] + res[1]
    })

if __name__ == '__main__':
    init_db()
    # Cambia host='0.0.0.0' para que sea accesible desde tu red local
    app.run(debug=True, port=5000, host='0.0.0.0')
