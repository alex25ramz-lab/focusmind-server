import os
from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURACIÓN DE BASE DE DATOS ---
def get_db_connection():
    # Nota: En Render, los cambios en este archivo .db se perderán al reiniciar.
    # Para persistencia real, se recomienda usar una base de datos externa (PostgreSQL).
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            minutos INTEGER NOT NULL,
            estado TEXT DEFAULT 'PENDIENTE',
            fecha_creacion DATETIME
        )
    ''')
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
def home():
    """Ruta principal para evitar el error 'Not Found' en el navegador"""
    return jsonify({
        "status": "online",
        "message": "Servidor FocusMind OS operando en Render",
        "endpoints": {
            "stats": "/stats",
            "obtener_tarea": "/obtener_tarea"
        }
    })

@app.route('/nueva_tarea', methods=['POST'])
def nueva_tarea():
    data = request.json
    descripcion = data.get('tarea')
    minutos = data.get('minutos')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tareas (descripcion, minutos, fecha_creacion) VALUES (?, ?, ?)',
                   (descripcion, minutos, datetime.now()))
    tarea_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"status": "ok", "id": tarea_id}), 201

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
    nuevo_estado = data.get('estado') # 'HECHO', 'RETARDO' o 'EXPIRADA'
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Actualizar estado de la tarea
    cursor.execute('UPDATE tareas SET estado = ? WHERE id = ?', (nuevo_estado, id_tarea))
    
    # 2. Corregir contadores de estadísticas
    if nuevo_estado == "HECHO":
        cursor.execute('UPDATE estadisticas SET a_tiempo = a_tiempo + 1 WHERE id = 1')
    elif nuevo_estado == "RETARDO":
        cursor.execute('UPDATE estadisticas SET con_retraso = con_retraso + 1 WHERE id = 1')
    elif nuevo_estado == "EXPIRADA":
        cursor.execute('UPDATE estadisticas SET expiradas = expiradas + 1 WHERE id = 1')
    
    conn.commit()
    conn.close()
    return jsonify({"status": "actualizado", "reporte": nuevo_estado})

@app.route('/stats', methods=['GET'])
def ver_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT a_tiempo, con_retraso, expiradas FROM estadisticas WHERE id = 1')
    res = cursor.fetchone()
    conn.close()
    
    return jsonify({
        "tareas_a_tiempo": res['a_tiempo'],
        "tareas_con_retraso": res['con_retraso'],
        "tareas_expiradas": res['expiradas']
    })

if __name__ == '__main__':
    init_db()
    # Render usa la variable de entorno PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
