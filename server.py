import os
import sqlite3
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# --- GESTIÓN DE BASE DE DATOS ---
DB_PATH = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Tabla de Tareas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            minutos INTEGER NOT NULL,
            estado TEXT DEFAULT 'PENDIENTE',
            fecha_creacion DATETIME
        )
    ''')
    # Tabla de Estadísticas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estadisticas (
            id INTEGER PRIMARY KEY,
            a_tiempo INTEGER DEFAULT 0,
            con_retraso INTEGER DEFAULT 0,
            expiradas INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('INSERT OR IGNORE INTO estadisticas (id, a_tiempo, con_retraso, expiradas) VALUES (1, 0, 0, 0)')
    conn.commit()
    conn.close()

# --- RUTAS ---

@app.route('/')
def index():
    """Evita el Error 404 al entrar al link directo"""
    return jsonify({
        "servidor": "FocusMind OS",
        "estado": "Online",
        "mensaje": "Si ves esto, el servidor está funcionando correctamente.",
        "comandos_disponibles": ["/stats", "/obtener_tarea", "/reportar_estado"]
    })

@app.route('/nueva_tarea', methods=['POST'])
def nueva_tarea():
    data = request.json
    tarea = data.get('tarea')
    mins = data.get('minutos')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tareas (descripcion, minutos, fecha_creacion) VALUES (?, ?, ?)',
                   (tarea, mins, datetime.now()))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"status": "creada", "id": new_id}), 201

@app.route('/obtener_tarea', methods=['GET'])
def obtener_tarea():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT descripcion, minutos, id FROM tareas WHERE estado = "PENDIENTE" ORDER BY id DESC LIMIT 1')
    res = cursor.fetchone()
    conn.close()
    
    if res:
        return jsonify({"tarea": res['descripcion'], "minutos": res['minutos'], "id": res['id']})
    return jsonify({"tarea": None})

@app.route('/reportar_estado', methods=['POST'])
def reportar_estado():
    data = request.json
    id_tarea = data.get('id')
    nuevo_estado = data.get('estado') # Esperamos: 'HECHO', 'RETARDO' o 'EXPIRADA'
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Actualizamos la tarea
    cursor.execute('UPDATE tareas SET estado = ? WHERE id = ?', (nuevo_estado, id_tarea))
    
    # 2. Lógica de contadores CORREGIDA
    if nuevo_estado == "HECHO":
        cursor.execute('UPDATE estadisticas SET a_tiempo = a_tiempo + 1 WHERE id = 1')
    elif nuevo_estado == "RETARDO":
        cursor.execute('UPDATE estadisticas SET con_retraso = con_retraso + 1 WHERE id = 1')
    elif nuevo_estado == "EXPIRADA":
        cursor.execute('UPDATE estadisticas SET expiradas = expiradas + 1 WHERE id = 1')
    
    conn.commit()
    conn.close()
    return jsonify({"status": "ok", "estado_final": nuevo_estado})

@app.route('/stats', methods=['GET'])
def ver_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT a_tiempo, con_retraso, expiradas FROM estadisticas WHERE id = 1')
    res = cursor.fetchone()
    conn.close()
    
    return jsonify({
        "a_tiempo": res['a_tiempo'],
        "con_retraso": res['con_retraso'],
        "expiradas": res['expiradas'],
        "total_logradas": res['a_tiempo'] + res['con_retraso']
    })

if __name__ == '__main__':
    init_db()
    # Render usa la variable de entorno PORT, si no existe usa 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
