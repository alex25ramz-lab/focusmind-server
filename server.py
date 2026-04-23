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
        "historial": [],
        "rendimiento": {"exitos": 0, "retrasos": 0, "total": 0},
        "ultimo_msj": f"Sistemas LUMINA inicializados para {nombre}."
    }

def cargar_db():
    cuentas_maestras = {
        "operador1": {"password": "123", "datos": inicializar_perfil("Operador 1")},
        "compa": {"password": "123", "datos": inicializar_perfil("Compa")}
    }
    if not os.path.exists(DB_FILE): return cuentas_maestras
    with open(DB_FILE, "r") as f:
        try: 
            data = json.load(f)
            for user, info in cuentas_maestras.items():
                if user not in data: data[user] = info
            return data
        except: return cuentas_maestras

def guardar_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

usuarios_db = cargar_db()

# --- HTML DE REGISTRO SIMPLIFICADO (SOLO NOMBRE) ---
HTML_AUTH = """
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>LUMINA - Registro</title>
<style>
    body { background: #050505; color: white; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .card { background: #0d0d0d; padding: 30px; border-radius: 15px; border: 1px solid #00ffaa; text-align: center; width: 300px; }
    input { width: 100%; padding: 12px; margin: 10px 0; background: #000; border: 1px solid #333; color: white; border-radius: 8px; box-sizing: border-box; }
    button { width: 100%; padding: 12px; background: #00ffaa; color: black; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; }
    a { color: #00ffaa; text-decoration: none; font-size: 12px; display: block; margin-top: 15px; }
</style>
</head>
<body>
    <div class="card">
        <h2 style="color:#00ffaa; letter-spacing:3px;">{{ 'ENTRAR' if modo=='login' else 'NUEVO OPERADOR' }}</h2>
        <form method="POST">
            <input type="text" name="usuario" placeholder="NOMBRE DEL OPERADOR" required autofocus>
            {% if modo == 'login' %}
            <input type="password" name="password" placeholder="CÓDIGO (123 por defecto)">
            {% endif %}
            <button type="submit">SISTEMA LISTO</button>
        </form>
        <a href="{{ '/registro' if modo=='login' else '/login' }}">
            {{ '¿No tienes cuenta? Regístrate' if modo=='login' else 'Volver al Login' }}
        </a>
    </div>
</body>
</html>
"""

# --- PANEL PRINCIPAL CON TABLA DE ÉXITOS ---
HTML_PANEL = """
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>LUMINA OS</title>
<style>
    :root { --neon: #00ffaa; --bg: #050505; --red: #ff4444; }
    body { font-family: sans-serif; background: var(--bg); color: white; padding: 20px; }
    .container { max-width: 550px; margin: auto; }
    h1 { color: var(--neon); text-align: center; letter-spacing: 5px; }
    .card { background: #0d0d0d; border: 1px solid #222; border-radius: 15px; padding: 20px; margin-bottom: 20px; }
    input, select { width: 100%; padding: 12px; margin: 5px 0 15px 0; border-radius: 8px; background: #000; color: white; border: 1px solid #333; box-sizing: border-box; }
    .btn { width: 100%; padding: 15px; background: var(--neon); color: black; font-weight: bold; border: none; border-radius: 10px; cursor: pointer; text-transform: uppercase; }
    table { width: 100%; margin-top: 10px; font-size: 13px; border-collapse: collapse; }
    td { padding: 12px 5px; border-bottom: 1px solid #222; }
    .num-exitos { color: var(--neon); font-weight: bold; font-size: 16px; }
    .del-btn { color: var(--red); text-decoration: none; border: 1px solid var(--red); padding: 3px 6px; border-radius: 5px; font-size: 10px; }
</style>
</head>
<body>
    <div class="container">
        <div style="display:flex; justify-content:space-between; font-size:10px; color:var(--neon);">
            <span>ID: {{ usuario }}</span> <a href="/logout" style="color:var(--red); text-decoration:none;">[ SALIR ]</a>
        </div>
        <h1>LUMINA OS</h1>

        <div class="card">
            <form action="/enviar_tarea_web" method="POST">
                <span style="font-size:10px; color:var(--neon);">ASIGNAR A:</span>
                <select name="destinatario">
                    {% for user in lista_usuarios %}<option value="{{ user }}">{{ user | upper }}</option>{% endfor %}
                </select>
                <input type="text" name="tarea" placeholder="Misión / Objetivo" required>
                <input type="number" name="mins" placeholder="Minutos" required>
                <button type="submit" class="btn">DESPLEGAR</button>
            </form>
        </div>

        <div class="card">
            <span style="font-size:10px; color:var(--neon);">TELEMETRÍA DE EQUIPO</span>
            <table>
                <tr style="color:#555; font-size:9px;">
                    <td>OPERADOR</td><td>TAREA</td><td style="text-align:center;">ÉXITOS</td><td style="text-align:right;">GESTIÓN</td>
                </tr>
                {% for op_name, op_info in equipo.items() %}
                <tr>
                    <td style="color:var(--neon);">{{ op_name }}</td>
                    <td style="font-size:11px;">{{ op_info.datos.tarea_actual }}</td>
                    <td style="text-align:center;" class="num-exitos">{{ op_info.datos.rendimiento.exitos }}</td>
                    <td style="text-align:right;">
                        {% if op_name != 'operador1' %}
                            <a href="/eliminar_operador/{{ op_name }}" class="del-btn" onclick="return confirm('¿Borrar?')">ELIMINAR</a>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </table>
            <div style="text-align:center; margin-top:20px;">
                <a href="/registro" style="color:var(--neon); text-decoration:none; font-size:12px;">+ AÑADIR NUEVO MIEMBRO</a>
            </div>
        </div>
    </div>
    <script>
        setInterval(async () => {
            const r = await fetch('/verificar_changes');
            const d = await r.json();
            if (d.update) window.location.reload();
        }, 3000);
    </script>
</body>
</html>
"""

# --- RUTAS ---
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        u = request.form.get('usuario').strip().lower()
        if u in usuarios_db: return render_template_string(HTML_AUTH, modo='registro', error="Ya existe")
        # Registramos con password '123' por defecto para que no lo pida
        usuarios_db[u] = {"password": "123", "datos": inicializar_perfil(u)}
        guardar_db(usuarios_db)
        return redirect(url_for('login'))
    return render_template_string(HTML_AUTH, modo='registro')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('usuario').strip().lower()
        p = request.form.get('password', '123').strip()
        if u in usuarios_db and usuarios_db[u]['password'] == p:
            session['user'] = u
            return redirect(url_for('home'))
    return render_template_string(HTML_AUTH, modo='login')

@app.route('/')
def home():
    if 'user' not in session: return redirect(url_for('login'))
    u = session['user']
    return render_template_string(HTML_PANEL, usuario=u, lista_usuarios=list(usuarios_db.keys()), 
                                 equipo=usuarios_db, **usuarios_db[u]['datos'])

@app.route('/eliminar_operador/<nombre>')
def eliminar_operador(nombre):
    # Ahora permitimos eliminar si el nombre existe y no es la cuenta maestra
    if nombre in usuarios_db and nombre != 'operador1':
        del usuarios_db[nombre]
        guardar_db(usuarios_db)
    return redirect(url_for('home'))

@app.route('/enviar_tarea_web', methods=['POST'])
def enviar_tarea_web():
    dest = request.form.get('destinatario')
    if dest in usuarios_db:
        db = usuarios_db[dest]['datos']
        db['tarea_actual'] = request.form.get('tarea')
        db['tiempo_actual'] = request.form.get('mins')
        db['rendimiento']['total'] += 1
        guardar_db(usuarios_db)
    return redirect(url_for('home'))

@app.route('/verificar_changes')
def verificar():
    # Detecta cambios en los éxitos de cualquier usuario para refrescar la tabla
    estado = "-".join([f"{u}:{usuarios_db[u]['datos']['rendimiento']['exitos']}" for u in usuarios_db])
    if session.get('old_state') != estado:
        session['old_state'] = estado
        return jsonify({"update": True})
    return jsonify({"update": False})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
