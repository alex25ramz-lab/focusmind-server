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
    # El operador maestro tiene esta clave por defecto.
    # Cámbiala aquí para mayor seguridad.
    cuentas_maestras = {
        "operador1": {"password": "123", "datos": inicializar_perfil("Operador 1")}
    }
    if not os.path.exists(DB_FILE):
        return cuentas_maestras
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
        .auth-card { background: #0d0d0d; padding: 40px; border-radius: 20px; border: 1px solid var(--neon); width: 320px; text-align: center; box-shadow: 0 0 20px rgba(0,255,170,0.2); }
        h1 { color: var(--neon); letter-spacing: 5px; margin-bottom: 30px; font-size: 24px; text-shadow: 0 0 10px var(--neon); }
        input { width: 100%; padding: 12px; margin: 10px 0; background: #000; border: 1px solid #333; color: white; border-radius: 8px; box-sizing: border-box; outline: none; transition: 0.3s; }
        input:focus { border-color: var(--neon); }
        button { width: 100%; padding: 12px; background: var(--neon); color: black; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; margin-top: 15px; text-transform: uppercase; }
        .error { color: #ff4444; font-size: 11px; margin-top: 15px; font-weight: bold; }
        .switch { font-size: 10px; margin-top: 20px; color: #555; text-decoration: none; display: block; }
    </style>
</head>
<body>
    <div class="auth-card">
        <h1>LUMINA OS</h1>
        <form method="POST">
            <input type="text" name="usuario" placeholder="IDENTIFICADOR" required autofocus>
            <input type="password" name="password" placeholder="CONTRASEÑA" required>
            <button type="submit">{{ 'CREAR CUENTA' if modo == 'registro' else 'INICIAR SESIÓN' }}</button>
        </form>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        
        {% if modo == 'login' %}
            <a href="/registro" class="switch">¿No tienes cuenta? REGÍSTRATE</a>
        {% else %}
            <a href="/login" class="switch">¿Ya eres operador? LOGIN</a>
        {% endif %}
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
        .container { max-width: 600px; margin: auto; }
        .user-bar { display: flex; justify-content: space-between; font-size: 10px; color: var(--neon); margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; }
        h1 { color: var(--neon); text-align: center; letter-spacing: 5px; text-shadow: 0 0 10px var(--neon); }
        .console { background: rgba(0,255,170,0.05); border-left: 3px solid var(--neon); padding: 15px; margin-bottom: 20px; font-family: monospace; color: var(--neon); min-height: 40px; }
        .card { background: var(--card); border: 1px solid #222; border-radius: 15px; padding: 20px; margin-bottom: 20px; position: relative; }
        input, select { width: 100%; padding: 12px; margin: 5px 0 15px 0; border-radius: 8px; border: 1px solid #333; background: #000; color: white; box-sizing: border-box; outline: none; }
        .main-btn { width: 100%; padding: 15px; border-radius: 10px; background: var(--neon); color: black; font-weight: bold; border: none; cursor: pointer; text-transform: uppercase; transition: 0.3s; }
        .main-btn:hover { box-shadow: 0 0 15px var(--neon); }
        table { width: 100%; margin-top: 10px; font-size: 12px; border-collapse: collapse; }
        td { padding: 12px 5px; border-bottom: 1px solid #222; }
        .badge-ok { color: var(--neon); font-weight: bold; font-size: 14px; }
        .del-btn { color: var(--red); text-decoration: none; font-size: 10px; border: 1px solid var(--red); padding: 4px 8px; border-radius: 4px; transition: 0.3s; }
        .del-btn:hover { background: var(--red); color: white; }
        .label-neon { font-size: 10px; color: var(--neon); text-transform: uppercase; display: block; margin-bottom: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="user-bar">
            <span>OPERADOR: {{ usuario }}</span>
            <a href="/logout" style="color:var(--red); text-decoration:none;">[ CERRAR SISTEMA ]</a>
        </div>
        <h1>LUMINA OS</h1>
        <div class="console">> STATUS: {{ ultimo_msj }}</div>

        {% if usuario == 'operador1' %}
        <div class="card">
            <span class="label-neon">CENTRO DE MANDO (ADMIN)</span>
            <form action="/enviar_tarea_web" method="POST">
                <select name="destinatario">
                    {% for user in lista_usuarios %}
                        <option value="{{ user }}">{{ user }}</option>
                    {% endfor %}
                </select>
                <input type="text" name="tarea" placeholder="Misión / Objetivo de Ingeniería" required>
                <input type="number" name="mins" placeholder="Minutos" required>
                <button type="submit" class="main-btn">Transmitir Instrucción</button>
            </form>
        </div>
        {% else %}
        <div class="card">
            <span class="label-neon">MI MISIÓN ACTUAL</span>
            <div style="font-size: 18px; margin: 10px 0;">{{ tarea_actual }}</div>
            <div style="color: #555; font-size: 12px;">Tiempo restante: {{ tiempo_actual }} mins</div>
        </div>
        {% endif %}

        <div class="card">
            <span class="label-neon">Telemetría de Unidades</span>
            <table>
                <tr style="color:#555; font-size:9px;">
                    <td>ID UNIDAD</td>
                    <td>ESTADO</td>
                    <td style="text-align:center;">ÉXITOS</td>
                    <td style="text-align:right;">CONTROL</td>
                </tr>
                {% for op_name, op_info in equipo.items() %}
                <tr>
                    <td style="color:var(--neon);">{{ op_name }}</td>
                    <td style="font-size:11px;">{{ op_info.datos.tarea_actual }}</td>
                    <td style="text-align:center;" class="badge-ok">{{ op_info.datos.rendimiento.exitos }}</td>
                    <td style="text-align:right;">
                        {% if usuario == 'operador1' and op_name != 'operador1' %}
                            <a href="/eliminar_operador/{{ op_name }}" class="del-btn" onclick="return confirm('¿Eliminar unidad de la red?')">BORRAR</a>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
    <script>
        // Recarga automática si hay cambios en el servidor
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

# --- CONTROLADORES ---

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        u = request.form.get('usuario').strip()
        p = request.form.get('password').strip()
        
        if u in usuarios_db:
            return render_template_string(HTML_AUTH, modo='registro', error="EL IDENTIFICADOR YA EXISTE")
        
        # Crear usuario con su password y perfil
        usuarios_db[u] = {"password": p, "datos": inicializar_perfil(u)}
        guardar_db(usuarios_db)
        session['user'] = u
        return redirect(url_for('home'))
    return render_template_string(HTML_AUTH, modo='registro')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('usuario').strip()
        p = request.form.get('password').strip()
        
        if u in usuarios_db and usuarios_db[u]['password'] == p:
            session['user'] = u
            return redirect(url_for('home'))
        else:
            return render_template_string(HTML_AUTH, modo='login', error="CREDENCIALES INVÁLIDAS")
    return render_template_string(HTML_AUTH, modo='login')

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
    if session.get('user') != 'operador1': return redirect(url_for('home'))
    
    dest = request.form.get('destinatario')
    if dest in usuarios_db:
        db = usuarios_db[dest]['datos']
        db['id_envio'] += 1
        db['tarea_actual'] = request.form.get('tarea')
        db['tiempo_actual'] = int(request.form.get('mins'))
        db['ultimo_msj'] = random.choice(FRASES_LUMINA)
        db['rendimiento']['total'] += 1
        guardar_db(usuarios_db)
    return redirect(url_for('home'))

# --- API PARA HARDWARE EXTERNO (LAPTOP/ESP32) ---

@app.route('/get_data')
def get_data():
    user = request.args.get('user')
    if user in usuarios_db:
        db = usuarios_db[user]['datos']
        return jsonify({
            "tarea": db['tarea_actual'], 
            "tiempo": db['tiempo_actual'], 
            "id": db['id_envio']
        })
    return jsonify({"error": "No user"}), 404

@app.route('/reportar_progreso', methods=['POST'])
def reportar():
    data = request.json
    user = data.get('user')
    if user in usuarios_db:
        db = usuarios_db[user]['datos']
        if data.get('estado') == "HECHO":
            db['rendimiento']['exitos'] += 1
            db['tarea_actual'] = "Misión Finalizada"
        else:
            db['rendimiento']['retrasos'] += 1
        guardar_db(usuarios_db)
        return jsonify({"ok": True})
    return jsonify({"ok": False}), 400

@app.route('/verificar_cambios')
def verificar_cambios():
    if 'user' not in session: return jsonify({"update": False})
    # Detecta cambios en cualquier parte de la red para actualizar la vista
    estado_equipo = "-".join([f"{u}:{usuarios_db[u]['datos']['rendimiento']['exitos']}:{usuarios_db[u]['datos']['tarea_actual']}" for u in usuarios_db])
    if session.get('last_state') != estado_equipo:
        session['last_state'] = estado_equipo
        return jsonify({"update": True})
    return jsonify({"update": False})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Configuración para despliegue
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
