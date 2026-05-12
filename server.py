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

# --- VISTAS HTML (Simplificadas para estabilidad) ---

HTML_AUTH = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><title>LUMINA OS - Auth</title>
    <style>
        :root { --neon: #00ffaa; --bg: #050505; }
        body { background: var(--bg); color: white; font-family: 'Segoe UI', sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .auth-card { background: #0d0d0d; padding: 40px; border-radius: 20px; border: 1px solid var(--neon); width: 320px; text-align: center; }
        h1 { color: var(--neon); letter-spacing: 5px; }
        input { width: 100%; padding: 12px; margin: 10px 0; background: #000; border: 1px solid #333; color: white; border-radius: 8px; box-sizing: border-box; outline: none; }
        button { width: 100%; padding: 12px; background: var(--neon); color: black; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="auth-card">
        <h1>LUMINA OS</h1>
        <form method="POST">
            <input type="text" name="usuario" placeholder="ID OPERADOR" required autofocus>
            <input type="password" name="password" placeholder="CÓDIGO">
            <button type="submit">INICIAR SISTEMA</button>
        </form>
    </div>
</body>
</html>
"""

HTML_PANEL = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><title>LUMINA OS - Panel</title>
    <style>
        :root { --neon: #00ffaa; --bg: #050505; --card: #0d0d0d; --red: #ff4444; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: white; padding: 20px; }
        .container { max-width: 550px; margin: auto; }
        h1 { color: var(--neon); text-align: center; letter-spacing: 5px; text-shadow: 0 0 10px var(--neon); }
        .card { background: var(--card); border: 1px solid #222; border-radius: 15px; padding: 20px; margin-bottom: 20px; }
        .log-item { border-bottom: 1px solid #1a1a1a; padding: 10px 0; display: flex; justify-content: space-between; font-size: 11px; }
        .status-retraso { color: var(--red); font-weight: bold; border: 1px solid var(--red); padding: 1px 4px; border-radius: 3px; }
        .neon-text { color: var(--neon); }
    </style>
</head>
<body>
    <div class="container">
        <div style="text-align:right; font-size:10px;"><a href="/logout" style="color:var(--red);">[ SALIR ]</a></div>
        <h1>LUMINA OS</h1>
        <div class="card">
            <p class="neon-text">> {{ ultimo_msj }}</p>
            <form action="/enviar_tarea_web" method="POST">
                <select name="destinatario" style="width:100%; padding:10px; margin-bottom:10px; background:#000; color:white;">
                    {% for user in lista_usuarios %}<option value="{{ user }}">{{ user }}</option>{% endfor %}
                </select>
                <input type="text" name="tarea" placeholder="Misión" required style="width:100%; padding:10px; margin-bottom:10px; background:#000; color:white;">
                <input type="number" name="mins" placeholder="Minutos" required style="width:100%; padding:10px; margin-bottom:10px; background:#000; color:white;">
                <button type="submit" style="width:100%; padding:10px; background:var(--neon); border:none; font-weight:bold;">DESPLEGAR</button>
            </form>
        </div>

        <div class="card">
            <span style="color:var(--neon); font-size:10px;">REGISTRO DE MISIONES</span>
            <div style="margin-top:10px;">
                {% for log in log_global[::-1] %}
                <div class="log-item">
                    <span><b class="neon-text">{{ log.usuario }}</b>: {{ log.tarea }}</span>
                    <span style="text-align:right;">
                        {% if log.retraso %}<span class="status-retraso">RETRASO</span><br>{% endif %}
                        <small style="color:#555;">{{ log.fecha }}</small>
                    </span>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    <script>
        setInterval(async () => {
            const r = await fetch('/verificar_cambios');
            const d = await r.json();
            if (d.update) window.location.reload();
        }, 3000);
    </script>
</body>
</html>
"""

# --- RUTAS ---

@app.route('/reportar_progreso', methods=['POST'])
def reportar():
    data = request.json
    user = data.get('user')
    if user in usuarios_db:
        db_user = usuarios_db[user]['datos']
        es_retraso = data.get('estado') == "RETRASO"
        
        # PRIORIDAD: Si la App no mandó el nombre, usamos el que el servidor tiene en memoria
        tarea_nombre = data.get('tarea_nombre') or db_user.get('tarea_actual') or "Misión Finalizada"

        # No registrar si ya se marcó como finalizada para evitar spam de logs
        if not es_retraso and db_user['tarea_actual'] in ["Misión Cumplida", "Finalizada con Retraso"]:
            return jsonify({"ok": True})

        nueva_entrada = {
            "usuario": user,
            "tarea": tarea_nombre, 
            "fecha": datetime.now().strftime("%H:%M - %d/%m"),
            "enviado_por": db_user.get('enviado_por', 'Admin'),
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

@app.route('/')
def home():
    if 'user' not in session: return redirect(url_for('registro'))
    user = session['user']
    return render_template_string(HTML_PANEL, 
                                usuario=user, 
                                lista_usuarios=[k for k in usuarios_db.keys() if k != 'log_global'],
                                log_global=usuarios_db.get('log_global', []),
                                **usuarios_db[user]['datos'])

@app.route('/enviar_tarea_web', methods=['POST'])
def enviar_tarea_web():
    dest = request.form.get('destinatario')
    if dest in usuarios_db:
        d = usuarios_db[dest]['datos']
        d['id_envio'] += 1
        d['tarea_actual'] = request.form.get('tarea')
        d['tiempo_actual'] = int(request.form.get('mins'))
        d['enviado_por'] = session.get('user', 'Admin')
        d['ultimo_msj'] = random.choice(FRASES_LUMINA)
        guardar_db(usuarios_db)
    return redirect(url_for('home'))

@app.route('/get_data')
def get_data():
    user = request.args.get('user')
    if user in usuarios_db:
        d = usuarios_db[user]['datos']
        return jsonify({"tarea": d['tarea_actual'], "tiempo": d['tiempo_actual'], "id": d['id_envio']})
    return jsonify({"error": "No user"}), 404

@app.route('/verificar_cambios')
def verificar_cambios():
    num_logs = len(usuarios_db.get('log_global', []))
    if session.get('last_log_count') != num_logs:
        session['last_log_count'] = num_logs
        return jsonify({"update": True})
    return jsonify({"update": False})

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        u = request.form.get('usuario').strip()
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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
