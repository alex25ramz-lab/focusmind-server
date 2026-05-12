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

# --- VISTAS HTML (Sin cambios en diseño, solo lógica de visualización) ---

HTML_AUTH = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><title>LUMINA OS - Auth</title>
    <style>
        :root { --neon: #00ffaa; --bg: #050505; }
        body { background: var(--bg); color: white; font-family: 'Segoe UI', sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .auth-card { background: #0d0d0d; padding: 40px; border-radius: 20px; border: 1px solid var(--neon); width: 320px; text-align: center; box-shadow: 0 0 20px rgba(0,255,170,0.1); }
        h1 { color: var(--neon); letter-spacing: 5px; margin-bottom: 30px; font-size: 24px; }
        input { width: 100%; padding: 12px; margin: 10px 0; background: #000; border: 1px solid #333; color: white; border-radius: 8px; box-sizing: border-box; outline: none; transition: 0.3s; }
        input:focus { border-color: var(--neon); }
        button { width: 100%; padding: 12px; background: var(--neon); color: black; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; margin-top: 10px; }
        .error { color: #ff4444; font-size: 12px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="auth-card">
        <h1>LUMINA OS</h1>
        <form method="POST">
            <input type="text" id="user_input" name="usuario" placeholder="ID OPERADOR / NOMBRE" required autofocus oninput="checkUser()">
            <div id="pass_field" style="display:none;">
                <input type="password" name="password" placeholder="CÓDIGO DE ACCESO">
            </div>
            <button type="submit">INICIAR SISTEMA</button>
        </form>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
    </div>
    <script>
        function checkUser() {
            const user = document.getElementById('user_input').value;
            const passField = document.getElementById('pass_field');
            if (user.toLowerCase() === 'operador1') { passField.style.display = 'block'; } 
            else { passField.style.display = 'none'; }
        }
    </script>
</body>
</html>
"""

HTML_PANEL = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><title>LUMINA OS - Panel</title>
    <style>
        :root { --neon: #00ffaa; --bg: #050505; --card: #0d0d0d; --red: #ff4444; --gray: #888; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: white; padding: 20px; }
        .container { max-width: 550px; margin: auto; }
        .user-bar { display: flex; justify-content: space-between; font-size: 10px; color: var(--neon); margin-bottom: 15px; text-transform: uppercase; }
        h1 { color: var(--neon); text-align: center; letter-spacing: 5px; text-shadow: 0 0 10px var(--neon); }
        .console { background: rgba(0,255,170,0.05); border-left: 3px solid var(--neon); padding: 15px; margin-bottom: 20px; font-family: monospace; color: var(--neon); min-height: 40px; }
        .card { background: var(--card); border: 1px solid #222; border-radius: 15px; padding: 20px; margin-bottom: 20px; }
        input, select { width: 100%; padding: 12px; margin: 5px 0 15px 0; border-radius: 8px; border: 1px solid #333; background: #000; color: white; box-sizing: border-box; outline: none; }
        .main-btn { width: 100%; padding: 15px; border-radius: 10px; background: var(--neon); color: black; font-weight: bold; border: none; cursor: pointer; text-transform: uppercase; }
        table { width: 100%; margin-top: 10px; font-size: 12px; border-collapse: collapse; }
        td { padding: 12px 5px; border-bottom: 1px solid #222; }
        .badge-ok { color: var(--neon); font-weight: bold; font-size: 15px; }
        .badge-red { color: var(--red); font-weight: bold; font-size: 15px; }
        .del-btn { color: var(--red); text-decoration: none; font-size: 10px; border: 1px solid var(--red); padding: 2px 5px; border-radius: 4px; }
        .label-neon { font-size: 10px; color: var(--neon); text-transform: uppercase; display: block; margin-bottom: 5px; }
        
        .log-item { border-bottom: 1px solid #1a1a1a; padding: 8px 0; display: flex; align-items: center; font-size: 11px; }
        .log-user { color: var(--neon); font-weight: bold; width: 85px; flex-shrink: 0; }
        .log-task { color: #eee; flex-grow: 1; margin: 0 10px; }
        .log-meta { color: var(--gray); font-size: 9px; text-align: right; line-height: 1.2; }
        .status-retraso { 
            color: var(--red); 
            font-weight: bold; 
            font-size: 9px; 
            text-transform: uppercase; 
            display: inline-block;
            border: 1px solid var(--red);
            padding: 1px 4px;
            margin-top: 3px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="user-bar"><span>SESIÓN: {{ usuario }}</span> <a href="/logout" style="color:var(--red); text-decoration:none;">[ SALIR ]</a></div>
        <h1>LUMINA OS</h1>
        <div class="console">> LUMINA: {{ ultimo_msj }}</div>

        <div class="card">
            <form action="/enviar_tarea_web" method="POST">
                <span class="label-neon">Asignar a:</span>
                <select name="destinatario">
                    {% for user in lista_usuarios %}
                        <option value="{{ user }}">{{ user }}</option>
                    {% endfor %}
                </select>
                <input type="text" name="tarea" placeholder="Misión / Objetivo" required>
                <input type="number" name="mins" placeholder="Minutos" required>
                <button type="submit" class="main-btn">DESPLEGAR ACTIVIDAD</button>
            </form>
        </div>

        <div class="card">
            <span class="label-neon">Monitor de Equipo (Telemetría)</span>
            <table>
                <tr style="color:#555; font-size:9px;">
                    <td>OPERADOR</td>
                    <td>ESTADO ACTUAL</td>
                    <td style="text-align:center;">ÉXITOS / RETRASOS</td>
                    <td style="text-align:right;">GESTIÓN</td>
                </tr>
                {% for op_name, op_info in equipo.items() if op_name != 'log_global' %}
                <tr>
                    <td style="color:var(--neon);">{{ op_name }}</td>
                    <td style="font-size:11px;">{{ op_info.datos.tarea_actual }} <br> <small style="color:#555;">vía: {{ op_info.datos.enviado_por }}</small></td>
                    <td style="text-align:center;">
                        <span class="badge-ok">{{ op_info.datos.rendimiento.exitos }}</span> / 
                        <span class="badge-red">{{ op_info.datos.rendimiento.retrasos }}</span>
                    </td>
                    <td style="text-align:right;">
                        {% if op_name != 'operador1' %}
                            <a href="/eliminar_operador/{{ op_name }}" class="del-btn" onclick="return confirm('¿Eliminar?')">BORRAR</a>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </table>
            <div style="text-align:center; margin-top:15px;">
                <a href="/registro" style="color:var(--neon); font-size:11px; text-decoration:none;">+ AÑADIR NUEVO MIEMBRO</a>
            </div>
        </div>

        <div class="card">
            <span class="label-neon">Registro de Misiones Completadas</span>
            <div style="max-height: 250px; overflow-y: auto; margin-top: 10px;">
                {% if log_global %}
                    {% for log in log_global[::-1] %}
                    <div class="log-item">
                        <span class="log-user">{{ log.usuario }}</span>
                        <span class="log-task">
                            {{ log.tarea }}<br>
                            {% if log.retraso %}<span class="status-retraso">! Misión con Retraso</span>{% endif %}
                        </span>
                        <div class="log-meta">
                            {{ log.fecha }}<br>
                            <span style="color:#444;">Por: {{ log.enviado_por }}</span>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <div style="color:#444; font-size:11px; text-align:center;">Esperando reportes...</div>
                {% endif %}
            </div>
        </div>
    </div>
    <script>
        setInterval(async () => {
            try {
                const r = await fetch('/verificar_cambios');
                const d = await r.json();
                if (d.update) window.location.reload();
            } catch (e) {}
        }, 3000);
    </script>
</body>
</html>
"""

# --- RUTAS ---

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        u = request.form.get('usuario').strip()
        p = request.form.get('password', '').strip()
        if u.lower() == 'operador1':
            if p == usuarios_db['operador1']['password']:
                session['user'] = 'operador1'
                return redirect(url_for('home'))
            else: return render_template_string(HTML_AUTH, error="CÓDIGO INCORRECTO")
        if u not in usuarios_db:
            usuarios_db[u] = {"password": "123", "datos": inicializar_perfil(u)}
            guardar_db(usuarios_db)
        session['user'] = u
        return redirect(url_for('home'))
    return render_template_string(HTML_AUTH)

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
        es_retraso = data.get('estado') == "RETRASO"
        
        # --- LÓGICA DE REGISTRO COMPLETA ---
        # 1. Obtenemos el nombre de la tarea (el programa debe enviarlo en el JSON)
        # Si no viene en el JSON, usamos lo último que tenemos en la DB
        tarea_nombre = data.get('tarea_nombre', db_user['tarea_actual'])
        
        # 2. Ignoramos si es un mensaje de estado vacío
        if tarea_nombre == "Esperando mando..." and not es_retraso:
             return jsonify({"ok": True})

        # 3. Creamos la entrada para el Log Global del Restaurante
        nueva_entrada = {
            "usuario": user,
            "tarea": tarea_nombre, 
            "fecha": datetime.now().strftime("%H:%M - %d/%m"),
            "enviado_por": db_user.get('enviado_por', 'Sistema'),
            "retraso": es_retraso
        }
        
        if "log_global" not in usuarios_db: usuarios_db["log_global"] = []
        usuarios_db["log_global"].append(nueva_entrada)
        
        # 4. Actualizamos estadísticas del operador
        if es_retraso:
            db_user['rendimiento']['retrasos'] += 1
            db_user['tarea_actual'] = "Finalizada con Retraso"
        else:
            db_user['rendimiento']['exitos'] += 1
            db_user['tarea_actual'] = "Misión Cumplida"
            
        guardar_db(usuarios_db)
        return jsonify({"ok": True, "msg": "Misión registrada en el servidor"})
    return jsonify({"ok": False}), 400

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
        return jsonify({
            "tarea": d['tarea_actual'], 
            "tiempo": d['tiempo_actual'], 
            "id": d['id_envio'], 
            "remitente": d['enviado_por']
        })
    return jsonify({"error": "No user"}), 404

@app.route('/verificar_cambios')
def verificar_cambios():
    if 'user' not in session: return jsonify({"update": False})
    num_logs = len(usuarios_db.get('log_global', []))
    estado_equipo = f"logs:{num_logs}-" + "-".join([f"{u}:{usuarios_db[u]['datos']['rendimiento']['exitos']}:{usuarios_db[u]['datos']['rendimiento']['retrasos']}" for u in usuarios_db if u != 'log_global'])
    if session.get('last_state') != estado_equipo:
        session['last_state'] = estado_equipo
        return jsonify({"update": True})
    return jsonify({"update": False})

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
