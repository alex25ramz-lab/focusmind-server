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
    # Cuentas que NO se pueden borrar y siempre se restauran si el archivo se daña
    cuentas_maestras = {
        "operador1": {"password": "123", "datos": inicializar_perfil("Operador 1")},
        "compa": {"password": "456", "datos": inicializar_perfil("Compa")}
    }

    if not os.path.exists(DB_FILE):
        return cuentas_maestras
    
    with open(DB_FILE, "r") as f:
        try: 
            data = json.load(f)
            # Asegurar que las maestras siempre estén presentes
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

# --- VISTAS HTML ---

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
        input { width: 100%; padding: 12px; margin: 10px 0; background: #000; border: 1px solid #333; color: white; border-radius: 8px; box-sizing: border-box; outline: none; }
        input:focus { border-color: var(--neon); }
        button { width: 100%; padding: 12px; background: var(--neon); color: black; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; margin-top: 10px; }
        .toggle-link { margin-top: 20px; font-size: 13px; color: #555; }
        .toggle-link a { color: var(--neon); text-decoration: none; }
        .error { color: #ff4444; font-size: 12px; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="auth-card">
        <h1>LUMINA OS</h1>
        <form method="POST">
            <input type="text" name="usuario" placeholder="ID OPERADOR" required>
            <input type="password" name="password" placeholder="CÓDIGO" required>
            <button type="submit">{{ 'ENTRAR' if modo == 'login' else 'REGISTRAR' }}</button>
        </form>
        <div class="toggle-link">
            {% if modo == 'login' %} ¿Nuevo aquí? <a href="/registro">Crear cuenta</a>
            {% else %} ¿Ya tienes cuenta? <a href="/login">Ir al Login</a> {% endif %}
        </div>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
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
        .user-bar { display: flex; justify-content: space-between; font-size: 10px; color: var(--neon); margin-bottom: 15px; text-transform: uppercase; }
        h1 { color: var(--neon); text-align: center; letter-spacing: 5px; text-shadow: 0 0 10px var(--neon); }
        .console { background: rgba(0,255,170,0.05); border-left: 3px solid var(--neon); padding: 15px; margin-bottom: 20px; font-family: monospace; color: var(--neon); min-height: 40px; }
        .card { background: var(--card); border: 1px solid #222; border-radius: 15px; padding: 20px; margin-bottom: 20px; position: relative; }
        input, select { width: 100%; padding: 12px; margin: 5px 0 15px 0; border-radius: 8px; border: 1px solid #333; background: #000; color: white; box-sizing: border-box; outline: none; }
        input:focus, select:focus { border-color: var(--neon); }
        .main-btn { width: 100%; padding: 15px; border-radius: 10px; background: var(--neon); color: black; font-weight: bold; border: none; cursor: pointer; box-shadow: 0 0 10px var(--neon); text-transform: uppercase; }
        .stats { display: flex; justify-content: space-around; text-align: center; }
        .stat-num { display: block; font-size: 24px; color: var(--neon); font-weight: bold; }
        .stat-label { font-size: 9px; color: #666; text-transform: uppercase; }
        table { width: 100%; margin-top: 10px; font-size: 12px; border-collapse: collapse; }
        td { padding: 12px 5px; border-bottom: 1px solid #222; }
        .badge { padding: 3px 7px; border-radius: 4px; font-size: 10px; border: 1px solid; text-transform: uppercase; }
        .label-neon { font-size: 10px; color: var(--neon); text-transform: uppercase; display: block; margin-bottom: 5px; }
        .del-btn { color: var(--red); text-decoration: none; font-size: 10px; border: 1px solid var(--red); padding: 2px 5px; border-radius: 4px; transition: 0.3s; }
        .del-btn:hover { background: var(--red); color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="user-bar"><span>ID: {{ usuario }}</span> <a href="/logout" style="color:var(--red); text-decoration:none;">[ SALIR ]</a></div>
        <h1>LUMINA OS</h1>
        <div class="console" id="msj-texto">> LUMINA: {{ ultimo_msj }}</div>

        <div class="card">
            <form action="/enviar_tarea_web" method="POST">
                <span class="label-neon">Asignar a:</span>
                <select name="destinatario">
                    {% for user in lista_usuarios %}
                        <option value="{{ user }}" {% if user == usuario %}selected{% endif %}>{{ user | upper }}</option>
                    {% endfor %}
                </select>
                <input type="text" name="tarea" placeholder="Misión / Objetivo" required>
                <input type="number" name="mins" placeholder="Minutos" required>
                <button type="submit" class="main-btn">Desplegar Actividad</button>
            </form>
        </div>

        <div class="card stats">
            <div><span class="stat-num">{{ rendimiento.total }}</span><span class="stat-label">Total</span></div>
            <div><span class="stat-num">{{ rendimiento.exitos }}</span><span class="stat-label">Éxitos</span></div>
            <div><span class="stat-num" style="color:var(--red);">{{ rendimiento.retrasos }}</span><span class="stat-label">Retrasos</span></div>
        </div>

        <div class="card">
            <span class="label-neon">Estado del Equipo en Tiempo Real</span>
            <table>
                <tr style="color:#555; font-size:9px;">
                    <td>OPERADOR</td>
                    <td>ACTIVIDAD</td>
                    <td style="text-align:right;">ACCIONES</td>
                </tr>
                {% for op_name, op_info in equipo.items() %}
                <tr>
                    <td style="color:var(--neon);">{{ op_name }}</td>
                    <td style="font-size:11px;">{{ op_info.datos.tarea_actual }}</td>
                    <td style="text-align:right;">
                        {% if usuario == 'operador1' and op_name != 'operador1' %}
                            <a href="/eliminar_operador/{{ op_name }}" class="del-btn" onclick="return confirm('¿Eliminar operador?')">ELIMINAR</a>
                        {% else %}
                            <span style="color:#333; font-size:9px;">ACTIVO</span>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </table>
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

# --- RUTAS DE SISTEMA ---

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
            session['last_state'] = f"{len(db['historial'])}-{db['rendimiento']['exitos']}"
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

# --- GESTIÓN DE EQUIPO ---

@app.route('/eliminar_operador/<nombre>')
def eliminar_operador(nombre):
    if session.get('user') == 'operador1': # Solo tú puedes borrar
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

# --- API PARA LAPTOPS Y SINCRONIZACIÓN ---

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
                    db['ultimo_msj'] = f"Operador {user}: Se ha registrado un retraso."
                guardar_db(usuarios_db)
                return jsonify({"ok": True})
    return jsonify({"ok": False}), 400

@app.route('/verificar_cambios')
def verificar_cambios():
    if 'user' not in session: return jsonify({"update": False})
    user = session['user']
    if user not in usuarios_db: return jsonify({"update": True}) # Forzar recarga si el usuario fue borrado
    db = usuarios_db[user]['datos']
    estado_actual = f"{len(db['historial'])}-{db['rendimiento']['exitos']}-{db['tarea_actual']}"
    if session.get('last_state') != estado_actual:
        session['last_state'] = estado_actual
        return jsonify({"update": True})
    return jsonify({"update": False})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
