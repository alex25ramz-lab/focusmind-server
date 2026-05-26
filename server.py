from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from datetime import datetime
import os
import random
import json

app = Flask(__name__)
app.secret_key = "lumina_proto_2026_key_ultra_secure"

# En Render, se usará una ruta local temporal para guardar la sesión si es necesario
DB_FILE = "/tmp/database.json" if os.environ.get("RENDER") else "database.json"

def inicializar_perfil(nombre):
    return {
        "tarea_actual": "Esperando mando...",
        "tiempo_actual": 0,
        "id_envio": 0,
        "enviado_por": "Sistema",
        "historial": [],
        "rendimiento": {"exitos": 0, "retrasos": 0, "total": 0},
        "ultimo_msj": f"Sistemas LUMINA inicializados para {nombre}.",
        "_ui_consumida": True  # Asegura el estado limpio inicial
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

# ── ENDPOINTS DE COMUNICACIÓN CON LA LAPTOP (LOGIC.PY) ──

@app.route("/get_data", methods=["GET"])
def get_data():
    usuario = request.args.get("user", "").strip()
    if not usuario:
        return jsonify({"error": "Usuario requerido"}), 400
        
    db = cargar_db()
    if usuario in db and usuario != "log_global":
        datos_op = db[usuario]["datos"]
        
        if datos_op.get("_ui_consumida", False):
            return jsonify({
                "tarea": "Esperando mando...",
                "tiempo": 0,
                "id": 0
            })
            
        return jsonify({
            "tarea": datos_op.get("tarea_actual", "Esperando mando..."),
            "tiempo": datos_op.get("tiempo_actual", 0),
            "id": datos_op.get("id_envio", 0)
        })
    return jsonify({"tarea": "Esperando mando...", "tiempo": 0, "id": 0})


@app.route("/ack_tarea", methods=["POST"])
def ack_tarea():
    data = request.get_json() or {}
    usuario = data.get("user")
    id_tarea = data.get("id")
    
    if not usuario:
        return jsonify({"success": False, "error": "Datos inválidos"}), 400
        
    db = cargar_db()
    if usuario in db:
        if db[usuario]["datos"].get("id_envio") == id_tarea:
            db[usuario]["datos"]["_ui_consumida"] = True
            
            # Buscamos en el log global para cambiar el estado de "Desplegada" a "En ejecución"
            for log in db.get("log_global", []):
                if log.get("id_mision") == id_tarea:
                    log["estado"] = "En ejecución"
                    break
        guardar_db(db)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Usuario no encontrado"}), 404


@app.route("/reportar_progreso", methods=["POST"])
def reportar_progreso():
    data = request.get_json() or {}
    usuario = data.get("user")
    estado = data.get("estado")
    id_tarea = data.get("id")
    
    if not usuario:
        return jsonify({"success": False, "error": "Faltan datos de usuario"}), 400
        
    db = cargar_db()
    if usuario in db:
        if estado == "Misión Cumplida":
            db[usuario]["datos"]["rendimiento"]["exitos"] += 1
        elif estado == "Finalizada con Retraso":
            db[usuario]["datos"]["rendimiento"]["retrasos"] += 1
            
        db[usuario]["datos"]["rendimiento"]["total"] += 1
        
        # Actualizamos el estado en el log histórico global
        for log in db.get("log_global", []):
            if log.get("id_mision") == id_tarea or (log.get("usuario") == usuario and log.get("estado") in ["Desplegada", "En ejecución"]):
                log["estado"] = estado
                break
        
        # Reseteamos el estado en el servidor central
        db[usuario]["datos"]["tarea_actual"] = "Esperando mando..."
        db[usuario]["datos"]["tiempo_actual"] = 0
        db[usuario]["datos"]["_ui_consumida"] = True
        
        guardar_db(db)
        return jsonify({"success": True})
        
    return jsonify({"success": False, "error": "Operador no registrado"}), 404


# ── INTERFAZ WEB CONTROL INTERNO ──

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
        return jsonify({"success": False, "error": "Sesión caducada"}), 403
        
    destinatario = request.form.get("destinatario")
    mins = request.form.get("mins")
    tarea = request.form.get("tarea")
    
    if not destinatario or not mins or not tarea:
        return jsonify({"success": False, "error": "Campos incompletos"}), 400
        
    db = cargar_db()
    if destinatario in db and destinatario != "log_global":
        id_mision_generada = random.randint(1000, 9999)
        
        db[destinatario]["datos"]["tarea_actual"] = tarea
        db[destinatario]["datos"]["tiempo_actual"] = int(mins)
        db[destinatario]["datos"]["id_envio"] = id_mision_generada
        db[destinatario]["datos"]["enviado_por"] = session["usuario"]
        db[destinatario]["datos"]["ultimo_msj"] = random.choice(FRASES_LUMINA)
        db[destinatario]["datos"]["_ui_consumida"] = False  

        nuevo_log = {
            "id_mision": id_mision_generada,
            "usuario": destinatario,
            "tarea": tarea,
            "tiempo_asignado": f"{mins} min",
            "enviado_por": session["usuario"],
            "estado": "Desplegada",
            "fecha": datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
        }
        if "log_global" not in db:
            db["log_global"] = []
        db["log_global"].append(nuevo_log)
        
        guardar_db(db)
        return jsonify({"success": True, "frase": db[destinatario]["datos"]["ultimo_msj"]})
        
    return jsonify({"success": False, "error": "El destino no existe"}), 400


@app.route("/agregar_usuario_ajax", methods=["POST"])
def agregar_usuario_ajax():
    if "usuario" not in session:
        return jsonify({"success": False, "error": "Sesión caducada"}), 403
    
    nuevo_op = request.form.get("nuevo_usuario", "").strip()
    if not nuevo_op or nuevo_op == "log_global":
        return jsonify({"success": False, "error": "ID Inválido"}), 400
        
    db = cargar_db()
    if nuevo_op in db:
        return jsonify({"success": False, "error": "El operador ya se encuentra registrado"}), 400
        
    db[nuevo_op] = {"password": "", "datos": inicializar_perfil(nuevo_op)}
    guardar_db(db)
    
    return jsonify({
        "success": True, 
        "nombre": nuevo_op,
        "iniciales": nuevo_op[:2].upper(),
        "frase": f"Enlace establecido. {nuevo_op} se ha unido a la red Lumina."
    })


@app.route("/eliminar_usuario_ajax/<nombre>", methods=["POST"])
def eliminar_usuario_ajax(nombre):
    if "usuario" not in session:
        return jsonify({"success": False, "error": "Sesión caducada"}), 403
    
    if nombre == "operador1":
        return jsonify({"success": False, "error": "No se puede dar de baja al nodo troncal maestro"}), 400
        
    db = cargar_db()
    if nombre in db:
        del db[nombre]
        guardar_db(db)
        return jsonify({"success": True, "frase": f"Enlace cerrado. {nombre} desconectado de la red."})
        
    return jsonify({"success": False, "error": "Operador no localizado"}), 404


@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))


# ── VISTAS HTML INTEGRADAS ──

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
      <div class="sub">Sistema de misiones</div>
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
      --red: #ff4f4f; --amber: #f5a623; --muted: #555; --blue: #3b82f6;
    }
    body { background: var(--bg); color: #e0e0e0; font-family: 'Syne', sans-serif; padding: 20px 16px 60px; }
    body::before { content: ''; position: fixed; inset: 0; background-image: linear-gradient(rgba(0,229,160,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(0,229,160,0.025) 1px, transparent 1px); background-size: 40px 40px; pointer-events: none; z-index: 0; }
    .wrap { position: relative; z-index: 1; max-width: 680px; margin: 0 auto; }
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
    
    /* ── TABLA DE LOGS MEJORADA REQUERIDA ── */
    .table-container { width: 100%; overflow-x: auto; margin-top: 5px; }
    table { width: 100%; border-collapse: collapse; font-family: 'Share Tech Mono', monospace; font-size: 12px; text-align: left; }
    th { padding: 10px; color: var(--neon); border-bottom: 1px solid var(--neon-border); font-size: 10px; letter-spacing: 1px; text-transform: uppercase; }
    td { padding: 12px 10px; border-bottom: 0.5px solid var(--border); color: #ccc; vertical-align: middle; }
    tr:hover { background: rgba(255,255,255,0.02); }
    
    .badge { padding: 3px 7px; border-radius: 4px; font-size: 10px; font-weight: bold; text-transform: uppercase; display: inline-block; }
    .bg-desplegada { background: rgba(59,130,246,0.15); color: #60a5fa; border: 0.5px solid rgba(59,130,246,0.3); }
    .bg-ejecucion { background: rgba(245,166,35,0.15); color: #fbbf24; border: 0.5px solid rgba(245,166,35,0.3); }
    .bg-cumplida { background: rgba(0,229,160,0.15); color: var(--neon); border: 0.5px solid var(--neon-border); }
    .bg-retraso { background: rgba(255,79,79,0.15); color: #f87171; border: 0.5px solid rgba(255,79,79,0.3); }

    .launch-overlay { position: fixed; inset: 0; z-index: 8000; display: flex; align-items: center; justify-content: center; pointer-events: none; opacity: 0; transition: opacity 0.25s; }
    .launch-overlay.active { opacity: 1; }
    .launch-box { background: #080d0b; border: 0.5px solid var(--neon-border); border-radius: 16px; padding: 28px 40px; text-align: center; font-family: 'Share Tech Mono', monospace; transform: scale(0.88); transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1); }
    .launch-overlay.active .launch-box { transform: scale(1); }
    .launch-title { font-size: 10px; color: rgba(0,229,160,0.5); letter-spacing: 4px; margin-bottom: 10px; }
    .launch-name { font-size: 22px; color: var(--neon); letter-spacing: 3px; }
    
    @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
    .fade-in { animation: fadeSlide 0.35s ease both; }
    @keyframes fadeSlide { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:none} }
  </style>
</head>
<body>

<div class="launch-overlay" id="launch-overlay">
  <div class="launch-box">
    <div class="launch-title">MISIÓN ENVIADA A RENDER</div>
    <div class="launch-name" id="launch-dest">—</div>
  </div>
</div>

<div class="wrap">
  <div class="top-bar">
    <div class="session-info"><span class="dot-live"></span>RED EN LA NUBE: {{ usuario }}</div>
    <a href="/logout" class="logout-link">[ SALIR ]</a>
  </div>
  <div class="logo"><h1>LUMINA OS</h1><div class="sub">Consola de Misiones Globales</div></div>
  
  <div class="console">
    <span class="prompt">&gt;</span>
    <span class="msg" id="console-msg">{{ ultimo_msj }}<span class="cursor"></span></span>
  </div>

  <div class="card fade-in">
    <div class="card-label"><i class="ti ti-rocket"></i> Desplegar Actividad Global</div>
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
        <input type="text" name="tarea" id="tarea-input" placeholder="Escribe la actividad técnica..." required>
      </div>
      <button type="submit" class="deploy-btn" id="deploy-btn">
        <i class="ti ti-player-play"></i>
        <span>Desplegar misión global</span>
        <div class="btn-bar" id="btn-bar"></div>
      </button>
    </form>
  </div>

  <div class="card fade-in">
    <div class="card-label"><i class="ti ti-radar"></i> Monitor de Operadores</div>
    <div id="operator-rows-container">
      {% set avatares = ['av-neon','av-blue','av-amber'] %}
      {% for op_name, op_info in equipo.items() if op_name != 'log_global' %}
      <div class="op-row" id="row-{{ op_name }}">
        <div class="op-avatar {{ avatares[loop.index0 % 3] }}">{{ op_name[:2].upper() }}</div>
        <div>
          <div class="op-name">{{ op_name }}</div>
          <div class="op-task">
            {% if op_info.datos.tarea_actual == 'Esperando mando...' or op_info.datos._ui_consumida %}
              <span class="sdot sdot-idle"></span><span>Esperando mando...</span>
            {% else %}
              <span class="sdot sdot-active"></span><span>{{ op_info.datos.tarea_actual }}</span>
            {% endif %}
          </div>
          <div class="op-via">Enviado por: {{ op_info.datos.enviado_por }}</div>
        </div>
        <div class="op-stats">
          <span class="stat-chip stat-ok"><i class="ti ti-check"></i>{{ op_info.datos.rendimiento.exitos }}</span>
          <span class="stat-chip stat-bad"><i class="ti ti-clock"></i>{{ op_info.datos.rendimiento.retrasos }}</span>
        </div>
        <div>
          {% if op_name != 'operador1' %}
            <div onclick="eliminarOperadorAjax('{{ op_name }}')" class="del-btn"><i class="ti ti-trash"></i></div>
          {% else %}
            <div style="width:28px;"></div>
          {% endif %}
        </div>
      </div>
      {% endfor %}
    </div>
  </div>

  <div class="card fade-in">
    <div class="card-label"><i class="ti ti-table-share"></i> Registro Histórico de Auditoría</div>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Operador</th>
            <th>Actividad Asignada</th>
            <th>Duración</th>
            <th>Mando Por</th>
            <th>Estado Actual</th>
            <th>Fecha y Hora</th>
          </tr>
        </thead>
        <tbody id="log-table-body">
          {% if log_global %}
            {% for log in log_global[::-1] %}
            <tr>
              <td style="color: var(--neon); font-weight: bold;">{{ log.usuario }}</td>
              <td>{{ log.tarea }}</td>
              <td><i class="ti ti-hourglass-high" style="margin-right:3px;"></i>{{ log.tiempo_asignado }}</td>
              <td style="color: #8fa8ff;">{{ log.enviado_por }}</td>
              <td>
                {% if log.estado == 'Desplegada' %}
                  <span class="badge bg-desplegada">Desplegada</span>
                {% elif log.estado == 'En ejecución' %}
                  <span class="badge bg-ejecucion">En ejecución</span>
                {% elif log.estado == 'Misión Cumplida' %}
                  <span class="badge bg-cumplida">Cumplida</span>
                {% elif log.estado == 'Finalizada con Retraso' %}
                  <span class="badge bg-retraso">Con Retraso</span>
                {% else %}
                  <span class="badge bg-desplegada">{{ log.estado }}</span>
                {% endif %}
              </td>
              <td style="color: #666; font-size: 11px;">{{ log.fecha }}</td>
            </tr>
            {% endfor %}
          {% else %}
            <tr>
              <td colspan="6" style="text-align: center; color: var(--muted); padding: 30px;">
                No se registran actividades en el historial global.
              </td>
            </tr>
          {% endif %}
        </tbody>
      </table>
    </div>
  </div>
</div>

<script>
function typeConsole(txt){ document.getElementById('console-msg').textContent = txt; }

function interceptDeploy(e) {
  e.preventDefault();
  const destUser = document.getElementById('dest-select').value;
  
  const formData = new FormData(document.getElementById('deploy-form'));
  
  fetch('/enviar_tarea_web', { method: 'POST', body: formData })
  .then(res => res.json())
  .then(data => {
    if(data.success) {
      const ov = document.getElementById('launch-overlay');
      document.getElementById('launch-dest').textContent = destUser.toUpperCase();
      ov.classList.add('active'); 
      setTimeout(() => { ov.classList.remove('active'); location.reload(); }, 1100);
    }
  });
}

function eliminarOperadorAjax(nombre) {
  if (!confirm('¿Desconectar operador '+nombre+' de Render?')) return;
  fetch('/eliminar_usuario_ajax/'+nombre, { method: 'POST' })
  .then(r => r.json())
  .then(data => { if(data.success) location.reload(); });
}
</script>
</body>
</html>
