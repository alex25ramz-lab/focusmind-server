from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from datetime import datetime
import os
import random
import json

app = Flask(__name__)
app.secret_key = "lumina_proto_2026_key_ultra_secure"

DB_FILE = "database.json"

def inicializar_perfil(nombre):
    return {
        "tarea_actual": "Esperando mando...",
        "tiempo_actual": 0,
        "id_envio": 0,
        "enviado_por": "Sistema", 
        "historial": [], 
        "rendimiento": {"exitos": 0, "retrasos": 0, "total": 0},
        "ultimo_msj": f"Sistemas LUMINA inicializados para {nombre}."
    }

def cargar_db():
    cuentas_maestras = {"operador1": {"password": "123", "datos": inicializar_perfil("Operador 1")}}
    if not os.path.exists(DB_FILE): return cuentas_maestras
    with open(DB_FILE, "r") as f:
        try: 
            data = json.load(f)
            if "log_global" not in data: data["log_global"] = []
            return data
        except: return cuentas_maestras

def guardar_db(db):
    with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)

usuarios_db = cargar_db()

# --- VISTAS HTML (Simplificadas para el código) ---
# Usa los mismos HTML_AUTH y HTML_PANEL que ya tienes guardados

@app.route('/')
def home():
    if 'user' not in session: return redirect(url_for('registro'))
    user = session['user']
    if user not in usuarios_db: return redirect(url_for('logout'))
    return render_template_string(HTML_PANEL, 
                                usuario=user, 
                                lista_usuarios=[k for k in usuarios_db.keys() if k != 'log_global'],
                                equipo={k: v for k, v in usuarios_db.items() if k != 'log_global'},
                                log_global=usuarios_db.get('log_global', []),
                                **usuarios_db[user]['datos'])

@app.route('/reportar_progreso', methods=['POST'])
def reportar():
    data = request.json
    user = data.get('user')
    
    if user in usuarios_db:
        db_user = usuarios_db[user]['datos']
        
        # Si la app ya marcó éxito, no duplicamos (Lógica original)
        if db_user['tarea_actual'] in ["Misión Cumplida", "Finalizada con Retraso"]:
            return jsonify({"ok": True, "info": "Ya registrado"})

        tarea_nombre = db_user['tarea_actual']
        es_retraso = data.get('estado') == "RETRASO"

        nueva_entrada = {
            "usuario": user,
            "tarea": tarea_nombre, 
            "fecha": datetime.now().strftime("%H:%M - %d/%m"),
            "enviado_por": db_user.get('enviado_por', 'Sistema'),
            "retraso": es_retraso
        }
        
        if "log_global" not in usuarios_db: usuarios_db["log_global"] = []
        usuarios_db["log_global"].append(nueva_entrada)
        
        if es_retraso:
            db_user['rendimiento']['retrasos'] += 1
            db_user['tarea_actual'] = "Finalizada con Retraso"
        else:
            db_user['rendimiento']['exitos'] += 1
            db_user['tarea_actual'] = "Misión Cumplida"
            
        guardar_db(usuarios_db)
        return jsonify({"ok": True})
    return jsonify({"ok": False}), 400

@app.route('/get_data')
def get_data():
    user = request.args.get('user')
    if user in usuarios_db:
        d = usuarios_db[user]['datos']
        return jsonify({"tarea": d['tarea_actual'], "tiempo": d['tiempo_actual'], "id": d['id_envio']})
    return jsonify({"error": "No user"}), 404

# --- EL RESTO DE TUS RUTAS (registro, logout, enviar_tarea_web, etc.) ---
# Mantén el archivo tal cual lo tenías antes.
