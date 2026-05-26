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
        "ultimo_msj": f"Sistemas LUMINA inicializados para {nombre}.",
        "_ui_consumida": True
    }

def cargar_db():
    cuentas_maestras = {
        "operador1": {"password": "123", "datos": inicializar_perfil("Operador 1")},
        "log_global": []
    }
    if not os.path.exists(DB_FILE):
        guardar_db(cuentas_maestras)
        return cuentas_maestras
    with open(DB_FILE, "r") as f:
        try:
            data = json.load(f)
            if "operador1" not in data:
                data["operador1"] = cuentas_maestras["operador1"]
            if "log_global" not in data:
                data["log_global"] = []
            return data
        except:
            guardar_db(cuentas_maestras)
            return cuentas_maestras

def guardar_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

FRASES_LUMINA = [
    "Objetivo detectado. Optimizando frecuencia de enfoque.",
    "Lumina en línea. Iniciando secuencia de productividad.",
    "Sistemas listos. La disciplina es el puente al éxito.",
    "Enfoque de ingeniería establecido. Adelante.",
    "Misión desplegada. El equipo está en movimiento.",
    "Transmisión confirmada. Operador en modo activo."
]

# ── ENLACE DIRECTO PARA TU LAPTOP (OBTENER TAREA) ──
@app.route("/get_data", methods=["GET"])
def get_data():
    usuario = request.args.get("user", "").strip()
    if not usuario:
        return jsonify({"error": "Usuario requerido"}), 400
        
    db = cargar_db()
    if usuario in db and usuario != "log_global":
        datos_op = db[usuario]["datos"]
        # Entrega el formato exacto que tu archivo logic.py lee e interpreta
        return jsonify({
            "tarea": datos_op.get("tarea_actual", "Esperando mando..."),
            "tiempo": datos_op.get("tiempo_actual", 0),
            "id": datos_op.get("id_envio", 0),
            "_ui_consumida": datos_op.get("_ui_consumida", True)
        })
    return jsonify({"tarea": "Esperando mando...", "tiempo": 0, "id": 0, "_ui_consumida": True})

# ── ENLACE DIRECTO PARA TU LAPTOP (CONFIRMACIÓN ACK) ──
@app.route("/ack_tarea", methods=["POST"])
def ack_tarea():
    data = request.get_json() or {}
    usuario = data.get("user")
    
    if not usuario:
        return jsonify({"success": False, "error": "Datos inválidos"}), 400
        
    db = cargar_db()
    if usuario in db:
        # Setea que la UI de la laptop ya consumió la tarea para que no repita alertas
        db[usuario]["datos"]["_ui_consumida"] = True
        guardar_db(db)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Usuario no encontrado"}), 404

# ── RUTAS DE LA INTERFAZ WEB ──
@app.route("/", methods=["GET", "POST"])
def login():
    if "usuario" in session:
        return redirect(url_for("panel"))
    error = None
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "").strip()
        
        if not usuario:
            error = "El identificador no puede estar vacío."
            return render_template_string(HTML_AUTH, error=error)
            
        db = cargar_db()
        if usuario in db and usuario != "log_global":
            if db[usuario]["password"] == password:
                session["usuario"] = usuario
                return redirect(url_for("panel"))
            else:
                error = "Código de acceso incorrecto."
        else:
            db[usuario] = {"password": "", "datos": inicializar_perfil(usuario)}
            guardar_db(db)
            session["usuario"] = usuario
            return redirect(url_for("panel"))
            
    return render_template_string(HTML_AUTH, error=error)

@app.route("/panel")
def panel():
    if "usuario" not in session:
        return redirect(url_for("login"))
    
    db = cargar_db()
    usuario_actual = session["usuario"]
    
    if usuario_actual not in db:
        db[usuario_actual] = {"password": "", "datos": inicializar_perfil(usuario_actual)}
        guardar_db(db)
        
    ultimo_msj = db[usuario_actual]["datos"].get("ultimo_msj", "Sistemas listos.")
    lista_usuarios = [k for k in db.keys() if k != "log_global"]
    log_global = db.get("log_global", [])
    
    return render_template_string(
        HTML_PANEL, 
        usuario=usuario_actual, 
        ultimo_msj=ultimo_msj, 
        equipo=db, 
        lista_usuarios=lista_usuarios, 
        log_global=log_global
    )

@app.route("/enviar_tarea_web", methods=["POST"])
def enviar_tarea_web():
    if "usuario" not in session:
        return jsonify({"success": False, "error": "Sesión no válida"}), 403
        
    destinatario = request.form.get("destinatario")
    mins = request.form.get("mins")
    tarea = request.form.get("tarea")
    
    if not destinatario or not mins or not tarea:
        return jsonify({"success": False, "error": "Datos incompletos"}), 400
        
    db = cargar_db()
    if destinatario in db and destinatario != "log_global":
        db[destinatario]["datos"]["tarea_actual"] = tarea
        db[destinatario]["datos"]["tiempo_actual"] = int(mins)
        db[destinatario]["datos"]["id_envio"] = random.randint(1000, 9999)
        db[destinatario]["datos"]["enviado_por"] = session["usuario"]
        db[destinatario]["datos"]["ultimo_msj"] = random.choice(FRASES_LUMINA)
        db[destinatario]["datos"]["_ui_consumida"] = False  # Informa a la lap que hay nueva tarea
        
        nuevo_log = {
            "usuario": destinatario,
            "tarea": tarea,
            "enviado_por": session["usuario"],
            "retraso": False,
            "fecha": datetime.now().strftime("%H:%M \n %d/%m")
        }
        if "log_global" not in db:
            db["log_global"] = []
        db["log_global"].append(nuevo_log)
        
        guardar_db(db)
        return jsonify({"success": True, "frase": db[destinatario]["datos"]["ultimo_msj"]})
        
    return jsonify({"success": False, "error": "Destinatario no encontrado"}), 400

@app.route("/agregar_usuario_ajax", methods=["POST"])
def agregar_usuario_ajax():
    if "usuario" not in session:
        return jsonify({"success": False, "error": "Sesión no válida"}), 403
    
    nuevo_op = request.form.get("nuevo_usuario", "").strip()
    if not nuevo_op or nuevo_op == "log_global":
        return jsonify({"success": False, "error": "ID de operador inválido"}), 400
        
    db = cargar_db()
    if nuevo_op in db:
        return jsonify({"success": False, "error": "El operador ya existe"}), 400
        
    db[nuevo_op] = {"password": "", "datos": inicializar_perfil(nuevo_op)}
    guardar_db(db)
    
    return jsonify({
        "success": True, 
        "nombre": nuevo_op,
        "iniciales": nuevo_op[:2].upper(),
        "frase": f"Frecuencia vinculada. {nuevo_op} añadido a la red."
    })

@app.route("/eliminar_usuario_ajax/<nombre>", methods=["POST"])
def eliminar_usuario_ajax(nombre):
    if "usuario" not in session:
        return jsonify({"success": False, "error": "Sesión no válida"}), 403
    
    if nombre == "operador1":
        return jsonify({"success": False, "error": "Núcleo maestro protegido"}), 400
        
    db = cargar_db()
    if nombre in db:
        del db[nombre]
        guardar_db(db)
        return jsonify({"success": True, "frase": f"Enlace interrumpido. {nombre} fuera de línea."})
        
    return jsonify({"success": False, "error": "Operador no encontrado"}), 404

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))

# Templates HTML integrados
HTML_AUTH = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"><title>LUMINA OS — Auth</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Syne:wght@300;400;600&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root { --neon: #00e5a0; --bg: #060708; --card: #0d0e10; --border: rgba(0,229,160,0.18); }
    body { background: var(--bg); color: #ddd; font-family: 'Syne', sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; }
    body::before { content: ''; position: fixed; inset: 0; background-image: linear-gradient(rgba(0,229,160,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,229,160,0.03) 1px, transparent 1px); background-size: 40px 40px; pointer-events: none; }
    .auth-wrap { position: relative; width: 340px; background: var(--card); border: 0.5px solid var(--border); border-radius: 18px; padding: 40px 36px 36px; }
    .logo-block { text-align: center; margin-bottom: 32px; }
    .logo-block h1 { font-family: 'Share Tech Mono', monospace; font-size: 26px; letter-spacing: 10px; color: var(--neon); font-weight: 400; }
    .logo-block .sub { font-size: 9px; color: rgba(0,229,160,0.4); letter-spacing: 4px; margin-top: 6px; text-transform: uppercase; }
    input { width: 100%; padding: 11px 14px; background: #080909; border: 0.5px solid rgba(255,255,255,0.08); color: #e8e8e8; border-radius: 8px; font-family: 'Share Tech Mono', monospace; font-size: 13px; outline: none; }
    .field { margin-bottom: 16px; }
    label { display: block; font-size: 9px; color: rgba(0,229,160,0.55); letter-spacing: 2px; text-transform: uppercase; margin-bottom: 6px; }
    .submit-btn { width: 100%; padding: 12px; background: var(--neon); color: #051a10; font-family: 'Syne', sans-serif; font-weight: 600; font-size: 11px; letter-spacing: 3px; text-transform: uppercase; border: none; border-radius: 8px; cursor: pointer; }
    .error-msg { background: rgba(255,60,60,0.08); border: 0.5px solid rgba(255,60,60,0.3); color: #ff6b6b; font-size: 11px; text-align: center; padding: 10px; border-radius: 6px; margin-top: 14px; font-family: 'Share Tech Mono', monospace; }
  </style>
</head>
<body>
  <div class="auth-wrap">
    <div class="logo-block">
      <h1>LUMINA OS</h1>
      <div class="sub">Sistema de gestión de misiones</div>
    </div>
    <form method="POST">
      <div class="field">
        <label>ID Operador / Nombre</label>
        <input type="text" id="user_input" name="usuario" placeholder="Identificador" required autofocus oninput="checkUser()">
      </div>
      <div class="field" id="pass_field" style="display:none;">
        <label>Código de acceso</label>
        <input type="password" name="password" placeholder="••••••••">
      </div>
      <button type="submit" class="submit-btn">Iniciar sistema</button>
    </form>
    {% if error %}<div class="error-msg">{{ error }}</div>{% endif %}
  </div>
  <script>
    function checkUser() {
      const v = document.getElementById('user_input').value;
      document.getElementById('pass_field').style.display = v.toLowerCase() === 'operador1' ? 'block' : 'none';
    }
  </script>
</body>
</html>
"""

HTML_PANEL = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"><title>LUMINA OS — Panel</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Syne:wght@300;400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.34.0/dist/tabler-icons.min.css">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --neon: #00e5a0; --neon-dim: rgba(0,229,160,0.10); --neon-border: rgba(0,229,160,0.22);
      --bg: #060708; --card: #0d0e10; --border: rgba(255,255,255,0.065);
      --red: #ff4f4f; --amber: #f5a623; --muted: #555;
    }
    body { background: var(--bg); color: #e0e0e0; font-family: 'Syne', sans-serif; padding: 20px 16px 60px; }
    body::before { content: ''; position: fixed; inset: 0; background-image: linear-gradient(rgba(0,229,160,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(0,229,160,0.025) 1px, transparent 1px); background-size: 40px 40px; pointer-events: none; z-index: 0; }
    .wrap { position: relative; z-index: 1; max-width: 580px; margin: 0 auto; }
    .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
    .session-info { display: flex; align-items: center; gap: 7px; font-size: 10px; color: var(--neon); letter-spacing: 2px; text-transform: uppercase; font-family: 'Share Tech Mono', monospace; }
    .dot-live { width: 6px; height: 6px; border-radius: 50%; background: var(--neon); flex-shrink: 0; animation: pulse 1.8s infinite; }
    .logout-link { font-size: 10px; color: var(--red); text-decoration: none; letter-spacing: 1px; border: 0.5px solid rgba(255,79,79,0.28); padding: 5px 11px; border-radius: 5px; font-family: 'Share Tech Mono', monospace; }
    .logo h1 { font-family: 'Share Tech Mono', monospace; font-size: 30px; letter-spacing: 12px; color: var(--neon); font-weight: 400; text-align: center; }
    .logo .sub { font-size: 9px; color: rgba(0,229,160,0.35); letter-spacing: 4px; margin-top: 5px; text-transform: uppercase; text-align: center; margin-bottom: 22px; }
    .console { background: var(--neon-dim); border-left: 2px solid var(--neon); padding: 13px 16px; border-radius: 0 8px 8px 0; margin-bottom: 20px; display: flex; align-items: flex-start; gap: 10px; }
    .console .prompt { color: var(--neon); font-family: 'Share Tech Mono', monospace; font-size: 13px; }
    .console .msg { color: #7fffd4; font-family: 'Share Tech Mono', monospace; font-size: 12px; line-height: 1.6; }
    .cursor { display: inline-block; width: 7px; height: 13px; background: var(--neon); margin-left: 3px; animation: blink 1s step-end infinite; }
    .card { background: var(--card); border: 0.5px solid var(--border); border-radius: 16px; padding: 20px 22px; margin-bottom: 16px; position: relative; overflow: hidden; }
    .card-label { font-size: 9px; color: var(--neon); letter-spacing: 3px; text-transform: uppercase; margin-bottom: 18px; display: flex; align-items: center; gap: 8px; font-family: 'Share Tech Mono', monospace; }
    .card-label::after { content: ''; flex: 1; height: 0.5px; background: var(--neon-border); }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
    .form-group { display: flex; flex-direction: column; gap: 5px; }
    .form-group label { font-size: 9px; color: var(--muted); letter-spacing: 2px; text-transform: uppercase; }
    select, input[type="text"], input[type="number"] { background: #080909; border: 0.5px solid rgba(255,255,255,0.08); color: #e8e8e8; padding: 10px 13px; border-radius: 8px; font-family: 'Share Tech Mono', monospace; font-size: 13px; outline: none; width: 100%; }
    .full-field { margin-bottom: 14px; }
    .deploy-btn { width: 100%; padding: 13px; background: var(--neon); color: #041a0e; font-family: 'Syne', sans-serif; font-weight: 600; font-size: 11px; letter-spacing: 3px; text-transform: uppercase; border: none; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; position: relative; }
    .btn-bar { position: absolute; left: 0; bottom: 0; height: 2px; background: var(--neon); width: 0%; box-shadow: 0 0 8px rgba(0,229,160,0.6); }
    
    .op-row { display: grid; grid-template-columns: 40px 1fr auto auto; gap: 14px; align-items: center; padding: 13px 0; border-bottom: 0.5px solid var(--border); position: relative; transition: all 0.4s ease; border-radius: 8px; }
    .op-row.targeted { background: rgba(0,229,160,0.04); }
    .op-row .row-ripple { position: absolute; left: 0; top: 0; right: 0; bottom: 0; border-radius: 8px; pointer-events: none; border: 1.5px solid var(--neon); opacity: 0; }
    .op-row.targeted .row-ripple { animation: rippleRow 0.7s ease-out forwards; }
    .scan-line { position: absolute; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, var(--neon), transparent); top: 0; opacity: 0; pointer-events: none; }
    .scan-line.scanning { animation: scanDown 0.55s linear forwards; }
    .op-avatar { width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-family: 'Share Tech Mono', monospace; font-size: 10px; font-weight: 600; }
    .av-neon { background: rgba(0,229,160,0.1); color: var(--neon); border: 0.5px solid var(--neon-border); }
    .av-blue { background: rgba(90,120,255,0.1); color: #8fa8ff; border: 0.5px solid rgba(90,120,255,0.25); }
    .av-amber { background: rgba(245,166,35,0.1); color: var(--amber); border: 0.5px solid rgba(245,166,35,0.25); }
    .op-name { font-size: 13px; color: #eee; font-weight: 500; }
    .op-task { font-size: 10px; color: var(--muted); margin-top: 3px; display: flex; align-items: center; gap: 5px; font-family: 'Share Tech Mono', monospace; }
    .sdot { width: 5px; height: 5px; border-radius: 50%; }
    .sdot-active { background: var(--neon); box-shadow: 0 0 5px rgba(0,229,160,0.6); }
    .sdot-idle { background: #333; }
    .op-via { font-size: 9px; color: #444; margin-top: 2px; }
    .op-stats { display: flex; gap: 10px; }
    .stat-chip { font-size: 12px; font-weight: 600; display: flex; align-items: center; gap: 3px; font-family: 'Share Tech Mono', monospace; }
    .stat-ok { color: var(--neon); }
    .stat-bad { color: var(--red); }
    
    .del-btn { font-size: 12px; color: rgba(255,79,79,0.5); cursor: pointer; border: 0.5px solid rgba(255,79,79,0.2); padding: 5px 8px; border-radius: 6px; transition: all 0.2s; display: flex; align-items: center; justify-content: center; }
    .del-btn:hover { color: var(--red); background: rgba(255,79,79,0.1); border-color: var(--red); }
    .add-link { display: inline-flex; align-items: center; gap: 6px; font-size: 11px; color: var(--neon); opacity: 0.7; margin-top: 14px; font-family: 'Share Tech Mono', monospace; cursor: pointer; border: 0.5px dashed var(--neon-border); padding: 6px 12px; border-radius: 6px; }
    .add-link:hover { opacity: 1; background: rgba(0,229,160,0.02); }
    .add-box-wrap { display: none; margin-top: 12px; padding: 12px; background: #080909; border: 0.5px solid var(--neon-border); border-radius: 8px; animation: fadeSlide 0.2s ease both; }
    .add-box-form { display: flex; gap: 8px; }

    .log-scroll { max-height: 260px; overflow-y: auto; }
    .log-entry { display: grid; grid-template-columns: 84px 1fr auto; gap: 10px; align-items: center; padding: 11px 0; border-bottom: 0.5px solid var(--border); }
    .log-user { font-size: 11px; color: var(--neon); font-family: 'Share Tech Mono', monospace; }
    .log-name { font-size: 12px; color: #ccc; }
    .log-via { font-size: 9px; color: #444; font-family: 'Share Tech Mono', monospace; }
    .tag-deploy { font-size: 8px; color: #8fa8ff; border: 0.5px solid rgba(90,120,255,0.3); padding: 2px 6px; border-radius: 3px; font-family: 'Share Tech Mono', monospace; }
    .log-time { font-size: 9px; color: #555; text-align: right; font-family: 'Share Tech Mono', monospace; }
    .empty-log { color: var(--muted); font-size: 11px; text-align: center; padding: 28px 0; }
    .particle { position: fixed; border-radius: 50%; pointer-events: none; z-index: 9999; animation: particleFly var(--dur) ease-out var(--delay) both; }
    
    .launch-overlay { position: fixed; inset: 0; z-index: 8000; display: flex; align-items: center; justify-content: center; pointer-events: none; opacity: 0; transition: opacity 0.25s; }
    .launch-overlay.active { opacity: 1; }
    .launch-box { background: #080d0b; border: 0.5px solid var(--neon-border); border-radius: 16px; padding: 28px 40px; text-align: center; font-family: 'Share Tech Mono', monospace; transform: scale(0.88); transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1); }
    .launch-overlay.active .launch-box { transform: scale(1); }
    .launch-title { font-size: 10px; color: rgba(0,229,160,0.5); letter-spacing: 4px; margin-bottom: 10px; }
    .launch-name { font-size: 22px; color: var(--neon); letter-spacing: 3px; }
    
    @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
    @keyframes fadeSlide { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:none} }
    @keyframes particleFly { 0%{opacity:1;transform:translate(0,0) scale(1)} 100%{opacity:0;transform:translate(var(--tx),var(--ty)) scale(0)} }
    @keyframes scanDown { 0%{top:0;opacity:0.9} 100%{top:100%;opacity:0} }
    @keyframes rippleRow { 0%{opacity:0.8;transform:scale(1)} 100%{opacity:0;transform:scale(1.03)} }
    @keyframes beamTravel { 0% { stroke-dashoffset: 300; opacity: 1; } 100% { stroke-dashoffset: 0; opacity: 0; } }
    .fade-in { animation: fadeSlide 0.35s ease both; }
  </style>
</head>
<body>

<div class="launch-overlay" id="launch-overlay">
  <div class="launch-box">
    <div class="launch-title">MISIÓN DESPLEGADA</div>
    <div class="launch-name" id="launch-dest">—</div>
  </div>
</div>

<svg id="beam-svg" style="position:fixed;inset:0;width:100%;height:100%;pointer-events:none;z-index:7999;" xmlns="http://www.w3.org/2000/svg"></svg>

<div class="wrap">
  <div class="top-bar">
    <div class="session-info"><span class="dot-live"></span>SESIÓN: {{ usuario }}</div>
    <a href="/logout" class="logout-link">[ SALIR ]</a>
  </div>
  <div class="logo"><h1>LUMINA OS</h1><div class="sub">Sistema de gestión de misiones</div></div>
  
  <div class="console">
    <span class="prompt">&gt;</span>
    <span class="msg" id="console-msg">{{ ultimo_msj }}<span class="cursor"></span></span>
  </div>

  <div class="card fade-in" id="form-card">
    <div class="card-label"><i class="ti ti-rocket"></i> Desplegar actividad</div>
    <form id="deploy-form" onsubmit="interceptDeploy(event)">
      <div class="form-row">
        <div class="form-group">
          <label>Asignar a</label>
          <select name="destinatario" id="dest-select">
            {% for user in lista_usuarios %}
              <option value="{{ user }}">{{ user }}</option>
            {% endfor %}
          </select>
        </div>
        <div class="form-group">
          <label>Minutos</label>
          <input type="number" name="mins" id="mins-input" placeholder="25" required min="1">
        </div>
      </div>
      <div class="form-group full-field">
        <label>Misión / Objetivo</label>
        <input type="text" name="tarea" id="tarea-input" placeholder="Ej: Revisar módulo de misiones" required>
      </div>
      <button type="submit" class="deploy-btn" id="deploy-btn">
        <i class="ti ti-player-play"></i>
        <span id="btn-txt">Desplegar misión</span>
        <div class="btn-bar" id="btn-bar"></div>
      </button>
    </form>
  </div>

  <div class="card fade-in" id="monitor-card">
    <div class="card-label"><i class="ti ti-radar"></i> Monitor de equipo</div>
    <div id="operator-rows-container">
      {% set avatares = ['av-neon','av-blue','av-amber'] %}
      {% for op_name, op_info in equipo.items() if op_name != 'log_global' %}
      {% set loop_idx = loop.index0 %}
      <div class="op-row" id="row-{{ op_name }}" data-user="{{ op_name }}">
        <div class="row-ripple"></div>
        <div class="scan-line" id="scan-{{ op_name }}"></div>
        <div class="op-avatar {{ avatares[loop_idx % 3] }}" id="av-{{ op_name }}">{{ op_name[:2].upper() }}</div>
        <div>
          <div class="op-name">{{ op_name }}</div>
          <div class="op-task" id="task-label-{{ op_name }}">
            {% if op_info.datos.tarea_actual == 'Esperando mando...' %}
              <span class="sdot sdot-idle"></span>
            {% else %}
              <span class="sdot sdot-active"></span>
            {% endif %}
            <span id="task-txt-{{ op_name }}">{{ op_info.datos.tarea_actual }}</span>
          </div>
          <div class="op-via" id="via-{{ op_name }}">vía: {{ op_info.datos.enviado_por }}</div>
        </div>
        <div class="op-stats">
          <span class="stat-chip stat-ok"><i class="ti ti-check"></i>{{ op_info.datos.rendimiento.exitos }}</span>
          <span class="stat-chip stat-bad"><i class="ti ti-clock"></i>{{ op_info.datos.rendimiento.retrasos }}</span>
        </div>
        <div>
          {% if op_name != 'operador1' %}
            <div onclick="eliminarOperadorAjax('{{ op_name }}')" class="del-btn" title="Dar de baja">
              <i class="ti ti-trash"></i>
            </div>
          {% else %}
            <div style="width:28px;"></div>
          {% endif %}
        </div>
      </div>
      {% endfor %}
    </div>

    <div class="add-link" onclick="toggleAddBox()"><i class="ti ti-user-plus"></i> Registrar nuevo operador</div>
    <div class="add-box-wrap" id="add-box">
      <form class="add-box-form" onsubmit="agregarOperadorAjax(event)">
        <input type="text" id="nuevo-usuario-input" placeholder="ID del nuevo operador" required>
        <button type="submit" class="deploy-btn" style="width: auto; padding: 0 16px;"><i class="ti ti-plus"></i></button>
      </form>
    </div>
  </div>

  <div class="card fade-in">
    <div class="card-label"><i class="ti ti-list-check"></i> Registro de misiones</div>
    <div class="log-scroll" id="log-list">
      {% if log_global %}
        {% for log in log_global[::-1] %}
        <div class="log-entry">
          <span class="log-user">{{ log.usuario }}</span>
          <div>
            <div class="log-name">{{ log.tarea }}</div>
            <div class="log-via">Por: {{ log.enviado_por }}</div>
            <span class="tag-deploy">Desplegada</span>
          </div>
          <div class="log-time">{{ log.fecha }}</div>
        </div>
        {% endfor %}
      {% else %}
        <div class="empty-log">Esperando misiones...</div>
      {% endif %}
    </div>
  </div>
</div>

<script>
function typeConsole(txt){
  document.getElementById('console-msg').textContent = txt;
}
function toggleAddBox() {
  const box = document.getElementById('add-box');
  box.style.display = (box.style.display === 'block') ? 'none' : 'block';
  if(box.style.display === 'block') document.getElementById('nuevo-usuario-input').focus();
}

function agregarOperadorAjax(e) {
  e.preventDefault();
  const input = document.getElementById('nuevo-usuario-input');
  const nombre = input.value.trim();
  if(!nombre) return;

  const formData = new FormData();
  formData.append('nuevo_usuario', nombre);

  fetch('/agregar_usuario_ajax', { method: 'POST', body: formData })
  .then(res => res.json())
  .then(data => {
    if(data.success) {
      typeConsole(data.frase);
      input.value = '';
      toggleAddBox();

      const container = document.getElementById('operator-rows-container');
      const totalRows = container.querySelectorAll('.op-row').length;
      const avClasses = ['av-neon', 'av-blue', 'av-amber'];
      const currentAv = avClasses[totalRows % 3];

      const newRow = document.createElement('div');
      newRow.className = 'op-row fade-in';
      newRow.id = 'row-'+data.nombre;
      newRow.innerHTML = '<div class="row-ripple"></div><div class="scan-line" id="scan-'+data.nombre+'"></div><div class="op-avatar '+currentAv+'">'+data.iniciales+'</div><div><div class="op-name">'+data.nombre+'</div><div class="op-task" id="task-label('+data.nombre+')"><span class="sdot sdot-idle"></span><span id="task-txt-'+data.nombre+'">Esperando mando...</span></div><div class="op-via" id="via-'+data.nombre+'">vía: Sistema</div></div><div class="op-stats"><span class="stat-chip stat-ok"><i class="ti ti-check"></i>0</span><span class="stat-chip stat-bad"><i class="ti ti-clock"></i>0</span></div><div><div onclick="eliminarOperadorAjax(\''+data.nombre+'\')" class="del-btn"><i class="ti ti-trash"></i></div></div>';
      container.appendChild(newRow);
      var opt = document.createElement('option'); opt.value = data.nombre; opt.textContent = data.nombre;
      document.getElementById('dest-select').appendChild(opt);
    } else { typeConsole('ERROR: '+data.error); }
  });
}

function eliminarOperadorAjax(nombre) {
  if (!confirm('¿Desconectar frecuencia de '+nombre+'?')) return;
  fetch('/eliminar_usuario_ajax/'+nombre, { method: 'POST' })
  .then(function(r){ return r.json(); })
  .then(function(data){
    if (data.success) {
      typeConsole(data.frase);
      var row = document.getElementById('row-'+nombre);
      if (row) { row.style.transition = 'opacity 0.35s,transform 0.35s'; row.style.opacity = '0'; row.style.transform = 'translateX(-20px)'; setTimeout(function(){ row.remove(); }, 400); }
      var opt = document.querySelector('#dest-select option[value="'+nombre+'"]');
      if (opt) opt.remove();
    } else { typeConsole('ERROR: '+data.error); }
  });
}

function spawnParticles(fromEl, toEl) {
  const fR = fromEl.getBoundingClientRect(); const tR = toEl.getBoundingClientRect();
  const sx = fR.left + fR.width/2; const sy = fR.top + fR.height/2;
  const tx0 = tR.left + tR.width/2 - sx; const ty0 = tR.top + tR.height/2 - sy;
  for (let i = 0; i < 12; i++) {
    const p = document.createElement('div');
    const sz = 3 + Math.random() * 3;
    const tx = tx0 + (Math.random() - 0.5) * 40; const ty = ty0 + (Math.random() - 0.5) * 40;
    const dur = 0.4 + Math.random() * 0.3; const del = i * 0.02;
    p.className = 'particle';
    p.style.cssText = `width:${sz}px;height:${sz}px;background:#00e5a0;left:${sx}px;top:${sy}px;--tx:${tx}px;--ty:${ty}px;--dur:${dur}s;--delay:${del}s;`;
    document.body.appendChild(p);
    setTimeout(() => p.remove(), (dur + del) * 1000 + 100);
  }
}

function fireBeam(fromEl, toEl) {
  const svg = document.getElementById('beam-svg');
  const fR = fromEl.getBoundingClientRect(); const tR = toEl.getBoundingClientRect();
  const x1 = fR.left + fR.width/2; const y1 = fR.top + fR.height/2;
  const x2 = tR.left + tR.width/2; const y2 = tR.top + tR.height/2;
  const len = Math.hypot(x2 - x1, y2 - y1);
  const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
  line.setAttribute('x1', x1); line.setAttribute('y1', y1);
  line.setAttribute('x2', x2); line.setAttribute('y2', y2);
  line.setAttribute('stroke', '#00e5a0'); line.setAttribute('stroke-width', '1.5');
  line.setAttribute('stroke-dasharray', len); line.setAttribute('stroke-dashoffset', len);
  line.style.animation = `beamTravel 0.45s ease-in-out forwards`;
  svg.appendChild(line);
  setTimeout(() => line.remove(), 500);
}

function interceptDeploy(e) {
  e.preventDefault();
  const btn = document.getElementById('deploy-btn');
  const bar = document.getElementById('btn-bar');
  const destUser = document.getElementById('dest-select').value;
  const tarea = document.getElementById('tarea-input').value.trim();
  
  if (!tarea || !destUser) return;
  btn.style.pointerEvents = 'none';
  bar.style.width = "100%";
  bar.style.transition = "width 0.4s ease";

  const formData = new FormData(document.getElementById('deploy-form'));
  
  fetch('/enviar_tarea_web', { method: 'POST', body: formData })
  .then(res => res.json())
  .then(data => {
    if(data.success) {
      const ov = document.getElementById('launch-overlay');
      document.getElementById('launch-dest').textContent = destUser.toUpperCase();
      ov.classList.add('active'); setTimeout(() => ov.classList.remove('active'), 1200);

      const row = document.getElementById('row-' + destUser);
      if(row) {
        fireBeam(btn, row);
        setTimeout(() => {
          spawnParticles(btn, row);
          const scan = document.getElementById('scan-' + destUser);
          if(scan) { scan.classList.remove('scanning'); void scan.offsetWidth; scan.classList.add('scanning'); }
          
          document.getElementById('task-txt-' + destUser).textContent = tarea;
          const indicator = document.querySelector(`#task-label-${destUser} .sdot`);
          if(indicator) { indicator.className = 'sdot sdot-active'; }
          
          typeConsole(data.frase);
          
          const logList = document.getElementById('log-list');
          const emptyLog = logList.querySelector('.empty-log');
          if(emptyLog) emptyLog.remove();
          
          const now = new Date();
          const timeStr = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;
          const dateStr = `${String(now.getDate()).padStart(2,'0')}/${String(now.getMonth()+1).padStart(2,'0')}`;
          
          const logEntry = document.createElement('div');
          logEntry.className = 'log-entry fade-in';
          logEntry.innerHTML = `
            <span class="log-user">${destUser}</span>
            <div>
              <div class="log-name">${tarea}</div>
              <div class="log-via">Por: {{ usuario }}</div>
              <span class="tag-deploy">Desplegada</span>
            </div>
            <div class="log-time">${timeStr} <br> ${dateStr}</div>
          `;
          logList.insertBefore(logEntry, logList.firstChild);
        }, 450);
      }
      setTimeout(() => { bar.style.width = "0%"; btn.style.pointerEvents = 'auto'; }, 600);
    }
  });
}
</script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
