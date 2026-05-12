from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from datetime import datetime
import os
import random
import json

app = Flask(__name__)
app.secret_key = "lumina_proto_2026_key_ultra_secure"

# --- SISTEMA DE PERSISTENCIA ---
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
    cuentas_maestras = {
        "operador1": {"password": "123", "datos": inicializar_perfil("Operador 1")}
    }
    if not os.path.exists(DB_FILE):
        return cuentas_maestras
    with open(DB_FILE, "r") as f:
        try: 
            data = json.load(f)
            if "operador1" not in data: data["operador1"] = cuentas_maestras["operador1"]
            if "log_global" not in data: data["log_global"] = []
            return data
        except: return cuentas_maestras

def guardar_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

usuarios_db = cargar_db()

FRASES_LUMINA = [
    "Objetivo detectado. Optimizando frecuencia de enfoque.",
    "Lumina en línea. Iniciando secuencia de productividad.",
    "Sistemas listos. La disciplina es el puente al éxito.",
    "Enfoque de ingeniería establecido. Adelante."
]

# (Omitiendo HTML_AUTH y HTML_PANEL por brevedad, son los mismos que tienes)

# --- RUTAS ---

@app.route('/reportar_progreso', methods=['POST'])
def reportar():
    data = request.json
    user = data.get('user')
    
    if user in usuarios_db:
        db_user = usuarios_db[user]['datos']
        es_retraso = str(data.get('estado')).upper() == "RETRASO"
        
        # 1. Recuperar nombre de tarea con "Plan B"
        # Si la app no lo manda, usamos el que el servidor tiene guardado.
        tarea_nombre = data.get('tarea_nombre') or db_user.get('tarea_actual')
        
        # 2. Limpieza de nombres genéricos para el log
        if not tarea_nombre or tarea_nombre in ["Esperando mando...", "Misión Cumplida", "Finalizada con Retraso"]:
            # Si el servidor ya marcó la tarea como terminada, pero llega un retraso, 
            # intentamos no perder el registro.
            if es_retraso:
                tarea_nombre = "Tarea Finalizada (Retraso Detectado)"
            else:
                return jsonify({"ok": True, "info": "Estado ya actualizado"})

        # 3. Crear la entrada del historial
        nueva_entrada = {
            "usuario": user,
            "tarea": tarea_nombre, 
            "fecha": datetime.now().strftime("%H:%M - %d/%m"),
            "enviado_por": db_user.get('enviado_por', 'Sistema'),
            "retraso": es_retraso
        }
        
        if "log_global" not in usuarios_db: usuarios_db["log_global"] = []
        usuarios_db["log_global"].append(nueva_entrada)
        
        # 4. Actualizar contadores y estado
        if es_retraso:
            db_user['rendimiento']['retrasos'] += 1
            db_user['tarea_actual'] = "Finalizada con Retraso"
        else:
            db_user['rendimiento']['exitos'] += 1
            db_user['tarea_actual'] = "Misión Cumplida"
            
        guardar_db(usuarios_db)
        return jsonify({"ok": True, "status": "Registrado"})
    
    return jsonify({"ok": False, "error": "Usuario no encontrado"}), 404

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

@app.route('/enviar_tarea_web', methods=['POST'])
def enviar_tarea_web():
    if 'user' not in session: return redirect(url_for('registro'))
    dest = request.form.get('destinatario')
    if dest in usuarios_db:
        d = usuarios_db[dest]['datos']
        d['id_envio'] += 1
        d['tarea_actual'] = request.form.get('tarea')
        d['tiempo_actual'] = int(request.form.get('mins'))
        d['enviado_por'] = session['user'] 
        d['ultimo_msj'] = random.choice(FRASES_LUMINA)
        d['rendimiento']['total'] += 1
        guardar_db(usuarios_db)
    return redirect(url_for('home'))

@app.route('/get_data')
def get_data():
    user = request.args.get('user')
    if user in usuarios_db:
        d = usuarios_db[user]['datos']
        return jsonify({"tarea": d['tarea_actual'], "tiempo": d['tiempo_actual'], "id": d['id_envio'], "remitente": d['enviado_por']})
    return jsonify({"error": "No user"}), 404

@app.route('/verificar_cambios')
def verificar_cambios():
    if 'user' not in session: return jsonify({"update": False})
    num_logs = len(usuarios_db.get('log_global', []))
    # Creamos un "huella digital" del estado actual para saber si algo cambió
    estado_equipo = f"logs:{num_logs}-" + "-".join([f"{u}:{usuarios_db[u]['datos']['rendimiento']['exitos']}" for u in usuarios_db if u != 'log_global'])
    if session.get('last_state') != estado_equipo:
        session['last_state'] = estado_equipo
        return jsonify({"update": True})
    return jsonify({"update": False})

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        u = request.form.get('usuario').strip()
        p = request.form.get('password', '').strip()
        if u.lower() == 'operador1':
            if p == usuarios_db['operador1']['password']:
                session['user'] = 'operador1'
                return redirect(url_for('home'))
            return render_template_string(HTML_AUTH, error="CÓDIGO INCORRECTO")
        if u not in usuarios_db:
            usuarios_db[u] = {"password": "123", "datos": inicializar_perfil(u)}
            guardar_db(usuarios_db)
        session['user'] = u
        return redirect(url_for('home'))
    return render_template_string(HTML_AUTH)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('registro'))

@app.route('/eliminar_operador/<u_name>')
def eliminar_operador(u_name):
    if 'user' in session and session['user'] == 'operador1':
        if u_name in usuarios_db and u_name != 'operador1':
            del usuarios_db[u_name]
            guardar_db(usuarios_db)
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
