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
        "historial": [],
        "rendimiento": {"exitos": 0, "retrasos": 0, "total": 0},
        "ultimo_msj": f"Sistemas LUMINA inicializados para {nombre}."
    }

def cargar_db():
    cuentas_maestras = {
        "operador1": {"password": "123", "datos": inicializar_perfil("Operador 1")}
    }
    if not os.path.exists(DB_FILE): return cuentas_maestras
    with open(DB_FILE, "r") as f:
        try: 
            data = json.load(f)
            if "operador1" not in data: data["operador1"] = cuentas_maestras["operador1"]
            return data
        except: return cuentas_maestras

def guardar_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

usuarios_db = cargar_db()
FRASES_LUMINA = ["Objetivo detectado.", "Secuencia de productividad iniciada.", "Sistemas listos.", "Enfoque establecido."]

# --- VISTA HTML (CON GESTIÓN DE USUARIOS) ---

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
        .card { background: var(--card); border: 1px solid #222; border-radius: 15px; padding: 20px; margin-bottom: 20px; }
        input, select { width: 100%; padding: 12px; margin: 5px 0 15px 0; border-radius: 8px; border: 1px solid #333; background: #000; color: white; box-sizing: border-box; outline: none; }
        .main-btn { width: 100%; padding: 15px; border-radius: 10px; background: var(--neon); color: black; font-weight: bold; border: none; cursor: pointer; text-transform: uppercase; }
        .mini-btn { background: #111; color: var(--neon); border: 1px solid var(--neon); padding: 8px; border-radius: 5px; cursor: pointer; font-size: 10px; }
        table { width: 100%; margin-top: 10px; font-size: 12px; border-collapse: collapse; }
        td { padding: 12px 5px; border-bottom: 1px solid #222; }
        .del-btn { color: var(--red); text-decoration: none; font-size: 10px; border: 1px solid var(--red); padding: 2px 5px; border-radius: 4px; }
        .label-neon { font-size: 10px; color: var(--neon); text-transform: uppercase; display: block; margin-bottom: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="user-bar"><span>OPERADOR: {{ usuario }}</span> <a href="/logout" style="color:var(--red); text-decoration:none;">[ SALIR ]</a></div>
        <h1>LUMINA OS</h1>

        <div class="card">
            <span class="label-neon">Frecuencia de Mando:</span>
            <form action="/enviar_tarea_web" method="POST">
                <select name="destinatario">
                    {% for user in lista_usuarios %}
                        <option value="{{ user }}">{{ user }}</option>
                    {% endfor %}
                </select>
                <input type="text" name="tarea" placeholder="Misión / Objetivo" required>
                <input type="number" name="mins" placeholder="Minutos" required>
                <button type="submit" class="main-btn">Transmitir Instrucción</button>
            </form>
        </div>

        <div class="card">
            <span class="label-neon">Telemetría de Equipo</span>
            <table>
                {% for op_name, op_info in equipo.items() %}
                <tr>
                    <td style="color:var(--neon);">{{ op_name }}</td>
                    <td style="font-size:11px;">{{ op_info.datos.tarea_actual }}</td>
                    <td style="text-align:right;">
                        {% if usuario == 'operador1' and op_name != 'operador1' %}
                            <a href="/eliminar_operador/{{ op_name }}" class="del-btn" onclick="return confirm('¿Eliminar unidad?')">BORRAR</a>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>

        <div class="card" style="border-style: dashed; opacity: 0.8;">
            <span class="label-neon">+ Registrar Nueva Unidad</span>
            <form action="/admin_registrar" method="POST" style="display: flex; gap: 5px;">
                <input type="text" name="nuevo_usuario" placeholder="ID" required style="margin:0; padding:8px;">
                <input type="password" name="nuevo_pass" placeholder="PASS" required style="margin:0; padding:8px;">
                <button type="submit" class="mini-btn">AÑADIR</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

# --- RUTAS DE LÓGICA ---

@app.route('/')
def home():
    if 'user' not in session: return redirect(url_for('login'))
    user = session['user']
    return render_template_string(HTML_PANEL, usuario=user, lista_usuarios=list(usuarios_db.keys()), equipo=usuarios_db, **usuarios_db[user]['datos'])

@app.route('/admin_registrar', methods=['POST'])
def admin_registrar():
    # Permite añadir usuarios desde el panel
    u = request.form.get('nuevo_usuario').strip()
    p = request.form.get('nuevo_pass').strip()
    if u and u not in usuarios_db:
        usuarios_db[u] = {"password": p, "datos": inicializar_perfil(u)}
        guardar_db(usuarios_db)
    return redirect(url_for('home'))

@app.route('/eliminar_operador/<nombre>')
def eliminar_operador(nombre):
    if session.get('user') == 'operador1' and nombre != 'operador1':
        if nombre in usuarios_db:
            del usuarios_db[nombre]
            guardar_db(usuarios_db)
    return redirect(url_for('home'))

@app.route('/enviar_tarea_web', methods=['POST'])
def enviar_tarea_web():
    dest = request.form.get('destinatario')
    if dest in usuarios_db:
        db = usuarios_db[dest]['datos']
        db['tarea_actual'] = request.form.get('tarea')
        db['tiempo_actual'] = int(request.form.get('mins'))
        db['id_envio'] += 1
        guardar_db(usuarios_db)
    return redirect(url_for('home'))

# --- RUTAS DE ACCESO (MANTENIDAS) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form.get('usuario'), request.form.get('password')
        if u in usuarios_db and usuarios_db[u]['password'] == p:
            session['user'] = u
            return redirect(url_for('home'))
    return render_template_string(HTML_AUTH_BASE) # Usa tu HTML_AUTH previo

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

HTML_AUTH_BASE = """
<!DOCTYPE html>
<html><head><title>LUMINA</title><style>body{background:#050505;color:white;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;} .card{border:1px solid #00ffaa;padding:20px;border-radius:10px;}</style></head>
<body><div class="card"><h2>LUMINA LOGIN</h2><form method="POST"><input name="usuario" placeholder="Usuario"><br><input type="password" name="password" placeholder="Pass"><br><br><button>ENTRAR</button></form></div></body></html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
