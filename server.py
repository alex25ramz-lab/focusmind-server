from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from datetime import datetime
import os
import random
import json

app = Flask(__name__)
app.secret_key = "lumina_proto_2026_key_ultra_secure"

# --- SISTEMA DE PERSISTENCIA ROBUSTO ---
DB_FILE = "database.json"

def inicializar_perfil(nombre):
    return {
        "tarea_actual": "Esperando mando...",
        "tiempo_actual": 0,
        "id_envio": 0,
        "historial": [],
        "rendimiento": {"exitos": 0, "retrasos": 0, "total": 0},
        "ultimo_msj": f"Sistemas LUMINA inicializados para {nombre}."
    }

def cargar_db():
    cuentas_maestras = {
        "operador1": {"password": "123", "datos": inicializar_perfil("Operador 1")},
        "compa": {"password": "456", "datos": inicializar_perfil("Compa")}
    }
    if not os.path.exists(DB_FILE):
        return cuentas_maestras
    with open(DB_FILE, "r") as f:
        try: 
            data = json.load(f)
            for user, info in cuentas_maestras.items():
                if user not in data:
                    data[user] = info
            return data
        except: 
            return cuentas_maestras

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

# --- HTML ACTUALIZADO CON TELEMETRÍA DETALLADA ---

HTML_PANEL = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><title>LUMINA OS - Panel</title>
    <style>
        :root { --neon: #00ffaa; --bg: #050505; --card: #0d0d0d; --red: #ff4444; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: white; padding: 20px; }
        .container { max-width: 600px; margin: auto; }
        .user-bar { display: flex; justify-content: space-between; font-size: 10px; color: var(--neon); margin-bottom: 15px; text-transform: uppercase; }
        h1 { color: var(--neon); text-align: center; letter-spacing: 5px; text-shadow: 0 0 10px var(--neon); }
        .console { background: rgba(0,255,170,0.05); border-left: 3px solid var(--neon); padding: 15px; margin-bottom: 20px; font-family: monospace; color: var(--neon); min-height: 40px; }
        .card { background: var(--card); border: 1px solid #222; border-radius: 15px; padding: 20px; margin-bottom: 20px; }
        input, select { width: 100%; padding: 12px; margin: 5px 0 15px 0; border-radius: 8px; border: 1px solid #333; background: #000; color: white; box-sizing: border-box; outline: none; }
        .main-btn { width: 100%; padding: 15px; border-radius: 10px; background: var(--neon); color: black; font-weight: bold; border: none; cursor: pointer; text-transform: uppercase; box-shadow: 0 0 10px var(--neon); }
        
        /* Tabla de Telemetría Mejorada */
        table { width: 100%; margin-top: 10px; font-size: 12px; border-collapse: collapse; }
        th { text-align: left; color: #555; font-size: 9px; padding: 10px 5px; text-transform: uppercase; border-bottom: 1px solid #222; }
        td { padding: 12px 5px; border-bottom: 1px solid #111; }
        .badge-ok { color: var(--neon); font-weight: bold; }
        .del-btn { color: var(--red); text-decoration: none; font-size: 9px; border: 1px solid var(--red); padding: 2px 5px; border-radius: 4px; }
        .del-btn:hover { background: var(--red); color: white; }
        .add-link { display: block; text-align: center; margin-top: 15px; color: var(--neon); text-decoration: none; font-size: 11px; letter-spacing: 1px; }
        .label-neon { font-size: 10px; color: var(--neon); text-transform: uppercase; display: block; margin-bottom: 5px; }
        
        .stats-grid { display: flex; justify-content: space-around; text-align: center; margin-top: 10px; }
        .stat-item { flex: 1; }
        .stat-val { display: block; font-size: 22px; color: var(--neon); font-weight: bold; }
        .stat-lab { font-size: 8px; color: #666; text-transform: uppercase; }
    </style>
</head>
<body>
    <div class="container">
        <div class="user-bar"><span>OPERADOR: {{ usuario }}</span> <a href="/logout" style="color:var(--red); text-decoration:none;">[ SALIR ]</a></div>
        <h1>LUMINA OS</h1>
        <div class="console" id="msj-texto">> LUMINA: {{ ultimo_msj }}</div>

        <div class="card">
            <form action="/enviar_tarea_web" method="POST">
                <span class="label-neon">Asignar Misión A:</span>
                <select name="destinatario">
                    {% for user in lista_usuarios %}
                        <option value="{{ user }}">{{ user | upper }}</option>
                    {% endfor %}
                </select>
                <input type="text" name="tarea" placeholder="Descripción de la tarea" required>
                <input type="number" name="mins" placeholder="Tiempo (min)" required>
                <button type="submit" class="main-btn">Desplegar Objetivo</button>
            </form>
        </div>

        <div class="card">
            <span class="label-neon">Tu Rendimiento Personal</span>
            <div class="stats-grid">
                <div class="stat-item"><span class="stat-val">{{ rendimiento.total }}</span><span class="stat-lab">Asignadas</span></div>
                <div class="stat-item"><span class="stat-val">{{ rendimiento.exitos }}</span><span class="stat-lab">Éxitos</span></div>
                <div class="stat-item"><span class="stat-item"><span class="stat-val" style="color:var(--red);">{{ rendimiento.retrasos }}</span><span class="stat-lab">Retrasos</span></div>
            </div>
        </div>

        <div class="card">
            <span class="label-neon">Monitor de Equipo (Telemetría Real)</span>
            <table>
                <thead>
                    <tr>
                        <th>Operador</th>
                        <th>Tarea Actual</th>
                        <th style="text-align:center;">Éxitos</th>
                        <th style="text-align:right;">Gestión</th>
                    </tr>
                </thead>
                <tbody>
                    {% for op_name, op_info in equipo.items() %}
                    <tr>
                        <td style="color:var(--neon); font-weight:bold;">{{ op_name }}</td>
                        <td style="font-size:11px;">{{ op_info.datos.tarea_actual }}</td>
                        <td style="text-align:center;" class="badge-ok">{{ op_info.datos.rendimiento.exitos }}</td>
                        <td style="text-align:right;">
                            {% if usuario == 'operador1' and op_name != 'operador1' %}
                                <a href="/eliminar_operador/{{ op_name }}" class="del-btn" onclick="return confirm('¿Confirmar baja de operador?')">ELIMINAR</a>
                            {% else %}
                                <span style="color:#222; font-size:8px;">MAESTRO</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            <a href="/registro" class="add-link">+ REGISTRAR NUEVO OPERADOR</a>
        </div>
    </div>

    <script>
        function hablar(t) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                const m = new SpeechSynthesisUtterance(t.replace("> LUMINA:", ""));
                m.lang = 'es-MX'; window.speechSynthesis.speak(m);
            }
        }
        window.onload = () => { hablar(document.getElementById('msj-texto').innerText); };

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
        u, p = request.form.get('usuario').strip().lower(), request.form.get('password').strip()
        if u in usuarios_db: return render_template_string(HTML_AUTH, modo='registro', error="ID ya existe")
        usuarios_db[u] = {"password": p, "datos": inicializar_perfil(u)}
        guardar_db(usuarios_db)
        return redirect(url_for('login'))
    return render_template_string(HTML_AUTH, modo='registro')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form.get('usuario').strip().lower(), request.form.get('password').strip()
        if u in usuarios_db and usuarios_db[u]['password'] == p:
            session['user'] = u
            db = usuarios_db[u]['datos']
            session['last_state'] = f"{len(db['historial'])}-{db['rendimiento']['exitos']}-{db['tarea_actual']}"
            return redirect(url_for('home'))
        return render_template_string(HTML_AUTH, modo='login', error="Datos de acceso incorrectos")
    return render_template_string(HTML_AUTH, modo='login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def home():
    if 'user' not in session: return redirect(url_for('login'))
    user = session['user']
    if user not in usuarios_db: return redirect(url_for('logout'))
    return render_template_string(HTML_PANEL, 
                                usuario=user, 
                                lista_usuarios=list(usuarios_db.keys()),
                                equipo=usuarios_db,
                                **usuarios_db[user]['datos'])

@app.route('/eliminar_operador/<nombre>')
def eliminar_operador(nombre):
    if session.get('user') == 'operador1':
        if nombre in usuarios_db and nombre != 'operador1':
            del usuarios_db[nombre]
            guardar_db(usuarios_db)
    return redirect(url_for('home'))

@app.route('/enviar_tarea_web', methods=['POST'])
def enviar_tarea_web():
    if 'user' not in session: return redirect(url_for('login'))
    dest = request.form.get('destinatario')
    if dest in usuarios_db:
        db = usuarios_db[dest]['datos']
        db['id_envio'] += 1
        db['tarea_actual'] = request.form.get('tarea')
        db['tiempo_actual'] = request.form.get('mins')
        db['ultimo_msj'] = random.choice(FRASES_LUMINA)
        db['historial'].append({
            "id": db['id_envio'], "tarea": db['tarea_actual'], 
            "estado": "PENDIENTE", "fecha": datetime.now().strftime("%H:%M")
        })
        db['rendimiento']['total'] += 1
        guardar_db(usuarios_db)
    return redirect(url_for('home'))

@app.route('/get_data')
def get_data():
    user = request.args.get('user')
    if user in usuarios_db:
        db = usuarios_db[user]['datos']
        return jsonify({"tarea": db['tarea_actual'], "tiempo": db['tiempo_actual'], "id": db['id_envio']})
    return jsonify({"error": "No user"}), 404

@app.route('/reportar_progreso', methods=['POST'])
def reportar():
    data = request.json
    user = data.get('user')
    if user in usuarios_db:
        db = usuarios_db[user]['datos']
        for t in db['historial']:
            if t['id'] == data.get('id') and t['estado'] == "PENDIENTE":
                t['estado'] = data.get('estado', '').upper()
                if t['estado'] == "HECHO":
                    db['rendimiento']['exitos'] += 1
                    db['ultimo_msj'] = f"Operador {user}: Tarea completada."
                else:
                    db['rendimiento']['retrasos'] += 1
                    db['ultimo_msj'] = f"Operador {user}: Alerta de retraso."
                guardar_db(usuarios_db)
                return jsonify({"ok": True})
    return jsonify({"ok": False}), 400

@app.route('/verificar_cambios')
def verificar_cambios():
    if 'user' not in session: return jsonify({"update": False})
    user = session['user']
    if user not in usuarios_db: return jsonify({"update": True})
    db = usuarios_db[user]['datos']
    
    # Esta línea es CLAVE: detectamos cambios en todo el equipo para refrescar la tabla
    estado_equipo = "-".join([f"{u}:{usuarios_db[u]['datos']['rendimiento']['exitos']}" for u in usuarios_db])
    estado_actual = f"{len(db['historial'])}-{db['tarea_actual']}-{estado_equipo}"
    
    if session.get('last_state') != estado_actual:
        session['last_state'] = estado_actual
        return jsonify({"update": True})
    return jsonify({"update": False})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
