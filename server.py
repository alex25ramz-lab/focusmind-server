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
    "Enfoque de ingeniería establecido. Adelante.",
    "Misión desplegada. El equipo está en movimiento.",
    "Transmisión confirmada. Operador en modo activo."
]

# ── RUTA DE AUTENTICACIÓN ──
@app.route("/", methods=["GET", "POST"])
def login():
    if "usuario" in session:
        return redirect(url_for("panel"))
    error = None
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "").strip()
        
        db = cargar_db()
        if usuario in db:
            if db[usuario]["password"] == password:
                session["usuario"] = usuario
                return redirect(url_for("panel"))
            else:
                error = "Código de acceso incorrecto."
        else:
            # Registro automático si no existe
            db[usuario] = {"password": "", "datos": inicializar_perfil(usuario)}
            guardar_db(db)
            session["usuario"] = usuario
            return redirect(url_for("panel"))
            
    return render_template_string(HTML_AUTH, error=error)

# ── RUTA PANEL PRINCIPAL ──
@app.route("/panel")
def panel():
    if "usuario" not in session:
        return redirect(url_for("login"))
    
    db = cargar_db()
    usuario_actual = session["usuario"]
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

# ── RUTA AJAX: ENVIAR TAREA ──
@app.route("/enviar_tarea_web", methods=["POST"])
def enviar_tarea_web():
    if "usuario" not in session:
        return jsonify({"success": False, "error": "Sesión no válida"}), 403
        
    destinatario = request.form.get("destinatario")
    mins = request.form.get("mins")
    tarea = request.form.get("tarea")
    
    db = cargar_db()
    if destinatario in db:
        db[destinatario]["datos"]["tarea_actual"] = tarea
        db[destinatario]["datos"]["tiempo_actual"] = int(mins)
        db[destinatario]["datos"]["enviado_por"] = session["usuario"]
        db[destinatario]["datos"]["ultimo_msj"] = random.choice(FRASES_LUMINA)
        
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

# ── RUTA backend: REGISTRAR NUEVO OPERADOR ──
@app.route("/agregar_usuario", methods=["POST"])
def agregar_usuario():
    if "usuario" not in session:
        return redirect(url_for("login"))
    
    nuevo_op = request.form.get("nuevo_usuario", "").strip()
    if nuevo_op:
        db = cargar_db()
        if nuevo_op not in db and nuevo_op != "log_global":
            db[nuevo_op] = {"password": "", "datos": inicializar_perfil(nuevo_op)}
            guardar_db(db)
    return redirect(url_for("panel"))

# ── RUTA backend: ELIMINAR OPERADOR ──
@app.route("/eliminar_usuario/<nombre>")
def eliminar_usuario(nombre):
    if "usuario" not in session:
        return redirect(url_for("login"))
    
    db = cargar_db()
    # Evita que se elimine la cuenta maestra por seguridad básica
    if nombre in db and nombre != "operador1":
        del db[nombre]
        guardar_db(db)
    return redirect(url_for("panel"))

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))


# ── INTERFAZ DE LOGIN (HTML_AUTH) ──
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
    body {
      background: var(--bg); color: #ddd;
      font-family: 'Syne', sans-serif;
      display: flex; align-items: center; justify-content: center; min-height: 100vh;
    }
    body::before {
      content: ''; position: fixed; inset: 0;
      background-image:
        linear-gradient(rgba(0,229,160,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,229,160,0.03) 1px, transparent 1px);
      background-size: 40px 40px; pointer-events: none;
    }
    .auth-wrap {
      position: relative; width: 340px; background: var(--card);
      border: 0.5px solid var(--border); border-radius: 18px; padding: 40px 36px 36px;
    }
    .auth-glow {
      position: absolute; top: -60px; left: 50%; transform: translateX(-50%);
      width: 180px; height: 180px;
      background: radial-gradient(circle, rgba(0,229,160,0.12) 0%, transparent 70%);
      pointer-events: none;
    }
    .logo-block { text-align: center; margin-bottom: 32px; }
    .logo-block h1 { font-family: 'Share Tech Mono', monospace; font-size: 26px; letter-spacing: 10px; color: var(--neon); font-weight: 400; }
    .logo-block .sub { font-size: 9px; color: rgba(0,229,160,0.4); letter-spacing: 4px; margin-top: 6px; text-transform: uppercase; }
    .logo-block .status-line { display: flex; align-items: center; justify-content: center; gap: 6px; margin-top: 10px; }
    .dot-live { width: 6px; height: 6px; border-radius: 50%; background: var(--neon); animation: pulse 1.8s infinite; }
    label { display: block; font-size: 9px; color: rgba(0,229,160,0.55); letter-spacing: 2px; text-transform: uppercase; margin-bottom: 6px; }
    input {
      width: 100%; padding: 11px 14px; background: #080909;
      border: 0.5px solid rgba(255,255,255,0.08); color: #e8e8e8;
      border-radius: 8px; font-family: 'Share Tech Mono', monospace; font-size: 13px;
      outline: none; transition: border 0.25s;
    }
    input:focus { border-color: var(--border); }
    .field { margin-bottom: 16px; }
    .submit-btn {
      width: 100%; padding: 12px; background: var(--neon); color: #051a10;
      font-family: 'Syne', sans-serif; font-weight: 600; font-size: 11px;
      letter-spacing: 3px; text-transform: uppercase; border: none; border-radius: 8px;
      cursor: pointer; margin-top: 4px; transition: opacity 0.2s, transform 0.1s;
    }
    .submit-btn:hover { opacity: 0.85; }
    .submit-btn:active { transform: scale(0.98); }
    .error-msg {
      background: rgba(255,60,60,0.08); border: 0.5px solid rgba(255,60,60,0.3);
      color: #ff6b6b; font-size: 11px; text-align: center; padding: 10px;
      border-radius: 6px; margin-top: 14px; font-family: 'Share Tech Mono', monospace;
    }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.25} }
  </style>
</head>
<body>
  <div class="auth-wrap">
    <div class="auth-glow"></div>
    <div class="logo-block">
      <h1>LUMINA OS</h1>
      <div class="sub">Sistema de gestión de misiones</div>
      <div class="status-line">
        <span class="dot-live"></span>
        <span style="font-size:9px;color:rgba(0,229,160,0.4);letter-spacing:2px;font-family:'Share Tech Mono',monospace;">ONLINE</span>
      </div>
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


# ── INTERFAZ DEL PANEL DE CONTROL (HTML_PANEL) ──
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
    body::before {
      content: ''; position: fixed; inset: 0;
      background-image: linear-gradient(rgba(0,229,160,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(0,229,160,0.025) 1px, transparent 1px);
      background-size: 40px 40px; pointer-events: none; z-index: 0;
    }
    .wrap { position: relative; z-index: 1; max-width: 580px; margin: 0 auto; }
    .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
    .session-info { display: flex; align-items: center; gap: 7px; font-size: 10px; color: var(--neon); letter-spacing: 2px; text-transform: uppercase; font-family: 'Share Tech Mono', monospace; }
    .dot-live { width: 6px; height: 6px; border-radius: 50%; background: var(--neon); flex-shrink: 0; animation: pulse 1.8s infinite; }
    .logout-link { font-size: 10px; color: var(--red); text-decoration: none; letter-spacing: 1px; border: 0.5px solid rgba(255,79,79,0.28); padding: 5px 11px; border-radius: 5px; font-family: 'Share Tech Mono', monospace; transition: background 0.2s; }
    .logout-link:hover { background: rgba(255,79,79,0.08); }
    .logo { text-align: center; margin-bottom: 22px; }
    .logo h1 { font-family: 'Share Tech Mono', monospace; font-size: 30px; letter-spacing: 12px; color: var(--neon); font-weight: 400; }
    .logo .sub { font-size: 9px; color: rgba(0,229,160,0.35); letter-spacing: 4px; margin-top: 5px; text-transform: uppercase; }
    .console { background: var(--neon-dim); border-left: 2px solid var(--neon); padding: 13px 16px; border-radius: 0 8px 8px 0; margin-bottom: 20px; display: flex; align-items: flex-start; gap: 10px; }
    .console .prompt { color: var(--neon); font-family: 'Share Tech Mono', monospace; font-size: 13px; flex-shrink: 0; }
    .console .msg { color: #7fffd4; font-family: 'Share Tech Mono', monospace; font-size: 12px; line-height: 1.6; }
    .cursor { display: inline-block; width: 7px; height: 13px; background: var(--neon); margin-left: 3px; vertical-align: text-bottom; animation: blink 1s step-end infinite; }
    .card { background: var(--card); border: 0.5px solid var(--border); border-radius: 16px; padding: 20px 22px; margin-bottom: 16px; position: relative; overflow: hidden; }
    .card-label { font-size: 9px; color: var(--neon); letter-spacing: 3px; text-transform: uppercase; margin-bottom: 18px; display: flex; align-items: center; gap: 8px; font-family: 'Share Tech Mono', monospace; }
    .card-label i { font-size: 14px; }
    .card-label::after { content: ''; flex: 1; height: 0.5px; background: var(--neon-border); }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
    .form-group { display: flex; flex-direction: column; gap: 5px; }
    .form-group label { font-size: 9px; color: var(--muted); letter-spacing: 2px; text-transform: uppercase; }
    select, input[type="text"], input[type="number"] {
      background: #080909; border: 0.5px solid rgba(255,255,255,0.08); color: #e8e8e8;
      padding: 10px 13px; border-radius: 8px; font-family: 'Share Tech Mono', monospace;
      font-size: 13px; outline: none; transition: border 0.2s; width: 100%;
    }
    select:focus, input:focus { border-color: var(--neon-border); }
    .full-field { margin-bottom: 14px; }
    .deploy-btn {
      width: 100%; padding: 13px; background: var(--neon); color: #041a0e;
      font-family: 'Syne', sans-serif; font-weight: 600; font-size: 11px;
      letter-spacing: 3px; text-transform: uppercase; border: none; border-radius: 8px;
      cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;
      position: relative; overflow: hidden; transition: opacity 0.2s, transform 0.1s;
    }
    .deploy-btn:hover { opacity: 0.88; }
    .deploy-btn:active { transform: scale(0.985); }
    .deploy-btn i { font-size: 15px; transition: transform 0.3s; }
    .deploy-btn.sending { background: #071a10; color: var(--neon); border: 0.5px solid var(--neon-border); pointer-events: none; }
    .deploy-btn.done    { background: #071a10; color: var(--neon); border: 0.5px solid var(--neon-border); pointer-events: none; }
    .deploy-btn.sending i { animation: spinIcon 0.7s linear infinite; }
    .deploy-btn.done i { animation: popIn 0.3s cubic-bezier(0.34,1.56,0.64,1) both; }
    .btn-bar { position: absolute; left: 0; bottom: 0; height: 2px; background: var(--neon); width: 0%; border-radius: 0 0 8px 8px; box-shadow: 0 0 8px rgba(0,229,160,0.6); }
    .toast {
      position: absolute; top: 14px; right: 14px; background: rgba(0,229,160,0.08); border: 0.5px solid var(--neon-border);
      color: var(--neon); font-family: 'Share Tech Mono', monospace; font-size: 10px; letter-spacing: 1px; padding: 6px 12px; border-radius: 6px;
      display: flex; align-items: center; gap: 7px; opacity: 0; transform: translateY(-6px) scale(0.95); transition: opacity 0.3s ease, transform 0.3s ease; pointer-events: none; z-index: 10; white-space: nowrap;
    }
    .toast.show { opacity: 1; transform: translateY(0) scale(1); }
    .toast-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--neon); animation: pulse 1s infinite; flex-shrink: 0; }
    
    .op-row { display: grid; grid-template-columns: 40px 1fr auto auto; gap: 14px; align-items: center; padding: 13px 0; border-bottom: 0.5px solid var(--border); position: relative; transition: background 0.4s; border-radius: 8px; }
    .op-row:last-child { border-bottom: none; }
    .op-row.targeted { background: rgba(0,229,160,0.04); }
    .op-row .row-ripple { position: absolute; left: 0; top: 0; right: 0; bottom: 0; border-radius: 8px; pointer-events: none; border: 1.5px solid var(--neon); opacity: 0; }
    .op-row.targeted .row-ripple { animation: rippleRow 0.7s ease-out forwards; }
    .scan-line { position: absolute; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, var(--neon), transparent); top: 0; opacity: 0; pointer-events: none; z-index: 5; box-shadow: 0 0 8px rgba(0,229,160,0.5); }
    .scan-line.scanning { animation: scanDown 0.55s linear forwards; }
    .op-avatar { width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-family: 'Share Tech Mono', monospace; font-size: 10px; font-weight: 600; flex-shrink: 0; transition: box-shadow 0.3s, transform 0.3s; }
    .op-row.targeted .op-avatar { box-shadow: 0 0 14px rgba(0,229,160,0.45); transform: scale(1.08); }
    .av-neon  { background: rgba(0,229,160,0.1);  color: var(--neon);  border: 0.5px solid var(--neon-border); }
    .av-blue  { background: rgba(90,120,255,0.1); color: #8fa8ff; border: 0.5px solid rgba(90,120,255,0.25); }
    .av-amber { background: rgba(245,166,35,0.1); color: var(--amber); border: 0.5px solid rgba(245,166,35,0.25); }
    .op-name { font-size: 13px; color: #eee; font-weight: 500; }
    .op-task { font-size: 10px; color: var(--muted); margin-top: 3px; display: flex; align-items: center; gap: 5px; font-family: 'Share Tech Mono', monospace; }
    .op-via   { font-size: 9px; color: #333; font-family: 'Share Tech Mono', monospace; }
    .sdot { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; }
    .sdot-active { background: var(--neon); box-shadow: 0 0 5px rgba(0,229,160,0.6); }
    .sdot-idle   { background: #333; }
    .sdot-delay  { background: var(--red); }
    .op-stats { display: flex; gap: 10px; margin-right: 4px; }
    .stat-chip { font-size: 12px; font-weight: 600; display: flex; align-items: center; gap: 3px; font-family: 'Share Tech Mono', monospace; }
    .stat-ok  { color: var(--neon); }
    .stat-bad { color: var(--red); }
    
    /* Botón eliminar */
    .del-btn { font-size: 12px; color: rgba(255,79,79,0.45); text-decoration: none; display: flex; align-items: center; justify-content: center; width: 26px; height: 26px; border-radius: 6px; border: 0.5px solid rgba(255,79,79,0.15); transition: all 0.25s; }
    .del-btn:hover { color: var(--red); background: rgba(255,79,79,0.08); border-color: rgba(255,79,79,0.4); }
    
    /* Enlace y caja para registrar operadores */
    .add-link { display: inline-flex; align-items: center; gap: 6px; font-size: 10px; color: var(--neon); text-decoration: none; opacity: 0.65; margin-top: 14px; font-family: 'Share Tech Mono', monospace; letter-spacing: 1px; cursor: pointer; text-transform: uppercase; border: 0.5px dashed var(--neon-border); padding: 5px 12px; border-radius: 6px; }
    .add-link:hover { opacity: 1; background: rgba(0,229,160,0.03); }
    .add-box-wrap { display: none; margin-top: 12px; padding: 14px; background: #080909; border: 0.5px solid var(--neon-border); border-radius: 10px; animation: fadeSlide 0.25s ease both; }
    .add-box-form { display: flex; gap: 8px; }

    .log-scroll { max-height: 260px; overflow-y: auto; }
    .log-scroll::-webkit-scrollbar { width: 3px; }
    .log-scroll::-webkit-scrollbar-thumb { background: var(--neon-border); border-radius: 3px; }
    .log-entry { display: grid; grid-template-columns: 84px 1fr auto; gap: 10px; align-items: center; padding: 11px 0; border-bottom: 0.5px solid var(--border); }
    .log-entry:last-child { border-bottom: none; }
    .log-user   { font-size: 11px; color: var(--neon); font-weight: 600; font-family: 'Share Tech Mono', monospace; }
    .log-name   { font-size: 12px; color: #ccc; }
    .log-via    { font-size: 9px; color: #333; margin-top: 2px; font-family: 'Share Tech Mono', monospace; }
    .tag-ok     { font-size: 8px; color: var(--neon); border: 0.5px solid var(--neon-border); padding: 2px 6px; border-radius: 3px; display: inline-block; margin-top: 4px; letter-spacing: 0.5px; font-family: 'Share Tech Mono', monospace; }
    .tag-delay  { font-size: 8px; color: var(--red); border: 0.5px solid rgba(255,79,79,0.35); padding: 2px 6px; border-radius: 3px; display: inline-block; margin-top: 4px; letter-spacing: 0.5px; font-family: 'Share Tech Mono', monospace; text-transform: uppercase; }
    .tag-deploy { font-size: 8px; color: #8fa8ff; border: 0.5px solid rgba(90,120,255,0.3); padding: 2px 6px; border-radius: 3px; display: inline-block; margin-top: 4px; letter-spacing: 0.5px; font-family: 'Share Tech Mono', monospace; }
    .log-time   { font-size: 9px; color: #555; text-align: right; white-space: nowrap; font-family: 'Share Tech Mono', monospace; }
    .empty-log  { color: var(--muted); font-size: 11px; text-align: center; padding: 28px 0; font-family: 'Share Tech Mono', monospace; }
    .particle { position: fixed; border-radius: 50%; pointer-events: none; z-index: 9999; animation: particleFly var(--dur) ease-out var(--delay) both; }
    .launch-overlay { position: fixed; inset: 0; z-index: 8000; display: flex; align-items: center; justify-content: center; pointer-events: none; opacity: 0; transition: opacity 0.25s; }
    .launch-overlay.active { opacity: 1; }
    .launch-box { background: #080d0b; border: 0.5px solid var(--neon-border); border-radius: 16px; padding: 28px 40px; text-align: center; font-family: 'Share Tech Mono', monospace; transform: scale(0.88); transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1); }
    .launch-overlay.active .launch-box { transform: scale(1); }
    .launch-title { font-size: 10px; color: rgba(0,229,160,0.5); letter-spacing: 4px; margin-bottom: 10px; }
    .launch-name  { font-size: 22px; color: var(--neon); letter-spacing: 3px; margin-bottom: 6px; }
    .launch-sub   { font-size: 10px; color: #444; letter-spacing: 2px; }
    .launch-rings { position: relative; width: 80px; height: 80px; margin: 18px auto 0; }
    .ring { position: absolute; border-radius: 50%; border: 1px solid var(--neon); top: 50%; left: 50%; transform: translate(-50%,-50%) scale(0); opacity: 0; }
    .launch-overlay.active .ring:nth-child(1) { animation: ringExpand 1s ease-out 0.0s both; }
    .launch-overlay.active .ring:nth-child(2) { animation: ringExpand 1s ease-out 0.2s both; }
    .launch-overlay.active .ring:nth-child(3) { animation: ringExpand 1s ease-out 0.4s both; }
    .ring:nth-child(1) { width: 30px;  height: 30px; }
    .ring:nth-child(2) { width: 55px;  height: 55px; }
    .ring:nth-child(3) { width: 80px;  height: 80px; }
    .launch-icon-center { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); font-size: 26px; color: var(--neon); }
    .flash-bg { animation: bgFlash 0.4s ease-out both; }
    @keyframes pulse       { 0%,100%{opacity:1} 50%{opacity:0.25} }
    @keyframes blink       { 0%,100%{opacity:1} 50%{opacity:0} }
    @keyframes fadeSlide   { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:none} }
    @keyframes particleFly { 0%{opacity:1;transform:translate(0,0) scale(1)} 100%{opacity:0;transform:translate(var(--tx),var(--ty)) scale(0)} }
    @keyframes scanDown    { 0%{top:0;opacity:0.9} 100%{top:100%;opacity:0} }
    @keyframes rippleRow   { 0%{opacity:0.8;transform:scale(1)} 100%{opacity:0;transform:scale(1.03)} }
    @keyframes ringExpand  { 0%{transform:translate(-50%,-50%) scale(0);opacity:0.9} 100%{transform:translate(-50%,-50%) scale(1.8);opacity:0} }
    @keyframes spinIcon    { to{transform:rotate(360deg)} }
    @keyframes popIn       { 0%{transform:scale(0.5)} 100%{transform:scale(1)} }
    @keyframes bgFlash     { 0%{background:rgba(0,229,160,0.04)} 100%{background:transparent} }
    @keyframes beamTravel  { 0% { stroke-dashoffset: 300; opacity: 1; } 80% { opacity: 1; } 100% { stroke-dashoffset: 0;   opacity: 0; } }
    .fade-in { animation: fadeSlide 0.35s ease both; }
  </style>
</head>
<body>

<div class="launch-overlay" id="launch-overlay">
  <div class="launch-box">
    <div class="launch-title">MISIÓN DESPLEGADA</div>
    <div class="launch-name" id="launch-dest">—</div>
    <div class="launch-sub" id="launch-task-label">objetivo asignado</div>
    <div class="launch-rings">
      <div class="ring"></div>
      <div class="ring"></div>
      <div class="ring"></div>
      <i class="ti ti-rocket launch-icon-center"></i>
    </div>
  </div>
</div>

<svg id="beam-svg" style="position:fixed;inset:0;width:100%;height:100%;pointer-events:none;z-index:7999;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="glow-filter">
      <feGaussianBlur stdDeviation="2.5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
</svg>

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
    <div class="toast" id="toast"><span class="toast-dot"></span><span id="toast-txt">Misión desplegada</span></div>
    <div class="card-label"><i class="ti ti-rocket"></i> Desplegar actividad</div>
    <form id="deploy-form" action="/enviar_tarea_web" method="POST" onsubmit="interceptDeploy(event)">
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
        <input type="text" name="tarea" id="tarea-input" placeholder="Ej: Revisar módulo de facturación" required>
      </div>
      <button type="submit" class="deploy-btn" id="deploy-btn">
        <i class="ti ti-player-play" id="btn-icon"></i>
        <span id="btn-txt">Desplegar misión</span>
        <div class="btn-bar" id="btn-bar"></div>
      </button>
    </form>
  </div>

  <div class="card fade-in" id="monitor-card">
    <div class="card-label"><i class="ti ti-radar"></i> Monitor de equipo</div>
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
          {% elif 'Retraso' in op_info.datos.tarea_actual %}
            <span class="sdot sdot-delay"></span>
          {% else %}
            <span class="sdot sdot-active"></span>
          {% endif %}
          <span id="task-txt-{{ op_name }}">{{ op_info.datos.tarea_actual }}</span>
        </div>
        <div class="op-via">vía: {{ op_info.datos.enviado_por }}</div>
      </div>
      <div class="op-stats">
        <span class="stat-chip stat-ok"><i class="ti ti-check"></i>{{ op_info.datos.rendimiento.exitos }}</span>
        <span class="stat-chip stat-bad"><i class="ti ti-clock"></i>{{ op_info.datos.rendimiento.retrasos }}</span>
      </div>
      
      <div>
        {% if op_name != 'operador1' %}
          <a href="/eliminar_usuario/{{ op_name }}" class="del-btn" title="Dar de baja operador">
            <i class="ti ti-trash"></i>
          </a>
        {% else %}
          <div style="width: 26px;"></div>
        {% endif %}
      </div>
    </div>
    {% endfor %}

    <div class="add-link" onclick="toggleAddBox()"><i class="ti ti-user-plus"></i> Registrar nuevo operador</div>
    
    <div class="add-box-wrap" id="add-box">
      <form class="add-box-form" action="/agregar_usuario" method="POST">
        <input type="text" name="nuevo_usuario" placeholder="ID del nuevo operador (Ej: Operador 2)" required>
        <button type="submit" class="deploy-btn" style="width: auto; padding: 0 16px; margin: 0;"><i class="ti ti-plus"></i></button>
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
            {% if log.retraso %}<span class="tag-delay">! Retraso</span>{% else %}<span class="tag-ok">Completada</span>{% endif %}
          </div>
          <div class="log-time">{{ log.fecha }}</div>
        </div>
        {% endfor %}
      {% else %}
        <div class="empty-log">Esperando reportes de misión...</div>
      {% endif %}
    </div>
  </div>
</div>

<script>
function toggleAddBox() {
  const box = document.getElementById('add-box');
  box.style.display = (box.style.display === 'block') ? 'none' : 'block';
}

function spawnParticles(fromEl, toEl, count = 18) {
  const fR = fromEl.getBoundingClientRect();
  const tR = toEl.getBoundingClientRect();
  const sx = fR.left + fR.width / 2;
  const sy = fR.top + fR.height / 2;
  const tx0 = tR.left + tR.width / 2 - sx;
  const ty0 = tR.top + tR.height / 2 - sy;
  const colors = ['#00e5a0','#7fffd4','#00c884','#a0ffe0'];
  for (let i = 0; i < count; i++) {
    const p = document.createElement('div');
    const sz = 3 + Math.random() * 4;
    const spread = (Math.random() - 0.5) * 80;
    const tx = tx0 + spread;
    const ty = ty0 + (Math.random() - 0.5) * 50;
    const dur = 0.45 + Math.random() * 0.4;
    const del = i * 0.028;
    const col = colors[Math.floor(Math.random() * colors.length)];
    p.className = 'particle';
    p.style.cssText = `width:${sz}px;height:${sz}px;background:${col};left:${sx}px;top:${sy}px;--tx:${tx}px;--ty:${ty}px;--dur:${dur}s;--delay:${del}s;`;
    document.body.appendChild(p);
    setTimeout(() => p.remove(), (dur + del) * 1000 + 150);
  }
}

function fireBeam(fromEl, toEl) {
  const svg = document.getElementById('beam-svg');
  const fR = fromEl.getBoundingClientRect();
  const tR = toEl.getBoundingClientRect();
  const x1 = fR.left + fR.width / 2;
  const y1 = fR.top + fR.height / 2;
  const x2 = tR.left + tR.width / 2;
  const y2 = tR.top + tR.height / 2;
  const len = Math.hypot(x2 - x1, y2 - y1);

  const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
  line.setAttribute('x1', x1); line.setAttribute('y1', y1);
  line.setAttribute('x2', x2); line.setAttribute('y2', y2);
  line.setAttribute('stroke', '#00e5a0');
  line.setAttribute('stroke-width', '1.5');
  line.setAttribute('stroke-dasharray', len);
  line.setAttribute('stroke-dashoffset', len);
  line.setAttribute('filter', 'url(#glow-filter)');
  line.style.animation = `beamTravel 0.55s ease-in-out forwards`;
  svg.appendChild(line);
  setTimeout(() => line.remove(), 700);
}

function triggerScanLine(destUser) {
  const scan = document.getElementById('scan-' + destUser);
  if (!scan) return;
  scan.classList.remove('scanning');
  void scan.offsetWidth;
  scan.classList.add('scanning');
}

function highlightRow(destUser) {
  document.querySelectorAll('.op-row').forEach(r => r.classList.remove('targeted'));
  const row = document.getElementById('row-' + destUser);
  if (row) row.classList.add('targeted');
  return row;
}

function typeTask(destUser, text) {
  const el = document.getElementById('task-txt-' + destUser);
  if (!el) return;
  let i = 0; el.textContent = '';
  const iv = setInterval(() => {
    el.textContent += text[i] || '';
    i++;
    if (i >= text.length) clearInterval(iv);
  }, 38);
}

function showLaunchOverlay(destUser, tarea) {
  const ov = document.getElementById('launch-overlay');
  document.getElementById('launch-dest').textContent = destUser.toUpperCase();
  document.getElementById('launch-task-label').textContent = tarea.length > 32 ? tarea.slice(0,32) + '…' : tarea;
  ov.classList.add('active');
  setTimeout(() => ov.classList.remove('active'), 1600);
}

function prependLog(destUser, tarea, sessionUser) {
  const list = document.getElementById('log-list');
  const empty = list.querySelector('.empty-log');
  if (empty) empty.remove();
  const now = new Date();
  const hora = now.getHours().toString().padStart(2,'0') + ':' + now.getMinutes().toString().padStart(2,'0');
  const dia = now.getDate().toString().padStart(2,'0') + '/' + (now.getMonth()+1).toString().padStart(2,'0');
  const entry = document.createElement('div');
  entry.className = 'log-entry';
  entry.innerHTML = `
    <span class="log-user">${destUser}</span>
    <div>
      <div class="log-name">${tarea}</div>
      <div class="log-via">Por: ${sessionUser}</div>
      <span class="tag-deploy">Desplegada</span>
    </div>
    <div class="log-time">${hora}<br>${dia}</div>
  `;
  list.prepend(entry);
}

function bodyFlash() {
  document.body.classList.remove('flash-bg');
  void document.body.offsetWidth;
  document.body.classList.add('flash-bg');
}

function interceptDeploy(e) {
  e.preventDefault();
  const btn = document.getElementById('deploy-btn');
  const btnTxt = document.getElementById('btn-txt');
  const bar = document.getElementById('btn-bar');
  const destUser = document.getElementById('dest-select').value;
  const tarea = document.getElementById('tarea-input').value.trim();
  const mins = document.getElementById('mins-input').value;
  
  if (!tarea || !mins) return;

  btn.classList.add('sending');
  btnTxt.textContent = "TRANSMITIENDO...";
  bar.style.width = "100%";
  bar.style.transition = "width 0.5s ease";

  const formData = new FormData(document.getElementById('deploy-form'));
  
  fetch('/enviar_tarea_web', {
    method: 'POST',
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    if(data.success) {
      bodyFlash();
      showLaunchOverlay(destUser, tarea);
      const row = highlightRow(destUser);
      if(row) {
        fireBeam(btn, row);
        setTimeout(() => {
          spawnParticles(btn, row);
          triggerScanLine(destUser);
          typeTask(destUser, tarea);
          prependLog(destUser, tarea, "{{ usuario }}");
          document.getElementById('console-msg').textContent = data.frase;
        }, 550);
      }
      
      setTimeout(() => {
        btn.classList.remove('sending');
        btn.classList.add('done');
        btnTxt.textContent = "MISIÓN ENVIADA";
        setTimeout(() => {
          btn.classList.remove('done');
          btnTxt.textContent = "Desplegar misión";
          bar.style.width = "0%";
        }, 1000);
      }, 600);
    }
  }).catch(() => {
    btn.classList.remove('sending');
    btnTxt.textContent = "Desplegar misión";
    bar.style.width = "0%";
  });
}
</script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
