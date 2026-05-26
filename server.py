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
        
        for log in db.get("log_global", []):
            if log.get("id_mision") == id_tarea or (log.get("usuario") == usuario and log.get("estado") in ["Desplegada", "En ejecución"]):
                log["estado"] = estado
                break
        
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
            "tiempo_assigned": f"{mins} min",
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
  <meta charset="UTF-8"><title>LUMINA OS — Kinetic Core</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Syne:wght@300;400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.34.0/dist/tabler-icons.min.css">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --neon: #00e5a0; --neon-dim: rgba(0,229,160,0.04); --neon-border: rgba(0,229,160,0.22);
      --bg: #030405; --card: rgba(11, 13, 16, 0.75); --border: rgba(255,255,255,0.04);
      --red: #ff4f4f; --amber: #f5a623; --muted: #4e5256; --blue: #3b82f6;
    }
    
    /* Fondo con Interferencia CRT Continua y Matriz de Red */
    body { background: var(--bg); color: #e0e0e0; font-family: 'Syne', sans-serif; padding: 20px 16px 60px; overflow-x: hidden; position: relative; }
    body::before { 
      content: ''; position: fixed; inset: 0; 
      background-image: linear-gradient(rgba(0,229,160,0.015) 1px, transparent 1px), linear-gradient(90deg, rgba(0,229,160,0.015) 1px, transparent 1px); 
      background-size: 40px 40px; pointer-events: none; z-index: 0;
      animation: matrixShift 25s linear infinite;
    }
    body::after {
      content: ''; position: fixed; inset: 0;
      background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.2) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.04), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.04));
      background-size: 100% 3px, 3px 100%; pointer-events: none; z-index: 9999; opacity: 0.7;
    }
    @keyframes matrixShift { from { background-position: 0 0; } to { background-position: 40px 80px; } }

    .wrap { position: relative; z-index: 1; max-width: 680px; margin: 0 auto; }
    .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
    
    .session-info { display: flex; align-items: center; gap: 7px; font-size: 10px; color: var(--neon); letter-spacing: 2px; text-transform: uppercase; font-family: 'Share Tech Mono', monospace; text-shadow: 0 0 8px rgba(0,229,160,0.3); }
    .dot-live { width: 8px; height: 8px; border-radius: 50%; background: var(--neon); flex-shrink: 0; animation: pulseRadar 1.2s cubic-bezier(0.24, 0, 0.38, 1) infinite; box-shadow: 0 0 8px var(--neon); }
    @keyframes pulseRadar { 0% { transform: scale(0.8); opacity: 0.5; box-shadow: 0 0 0 0 rgba(0,229,160,0.7); } 70% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 0 6px rgba(0,229,160,0); } 100% { transform: scale(0.8); opacity: 0.5; box-shadow: 0 0 0 0 rgba(0,229,160,0); } }
    
    .logout-link { font-size: 10px; color: var(--red); text-decoration: none; letter-spacing: 1px; border: 0.5px solid rgba(255,79,79,0.2); padding: 5px 11px; border-radius: 5px; font-family: 'Share Tech Mono', monospace; transition: all 0.3s; }
    .logout-link:hover { background: rgba(255,79,79,0.15); border-color: var(--red); box-shadow: 0 0 10px rgba(255,79,79,0.2); }
    
    /* Efecto Glitch continuo en el Título */
    .logo h1 { font-family: 'Share Tech Mono', monospace; font-size: 34px; letter-spacing: 14px; color: var(--neon); font-weight: 400; text-align: center; position: relative; animation: glitchText 4s linear infinite; margin-left: 14px; }
    @keyframes glitchText {
      0%, 95%, 100% { text-shadow: 0 0 10px rgba(0,229,160,0.3); }
      96% { text-shadow: -2px -2px #ff4f4f, 2px 2px #3b82f6; }
      97% { text-shadow: 3px -1px #ff4f4f, -2px 3px var(--neon); }
      99% { text-shadow: -1px 2px #3b82f6, 1px -2px #ff4f4f; }
    }
    .logo .sub { font-size: 9px; color: rgba(0,229,160,0.35); letter-spacing: 4px; margin-top: 5px; text-transform: uppercase; text-align: center; margin-bottom: 22px; }
    
    /* Consola Dinámica Inteligente */
    .console { position: relative; background: var(--neon-dim); border-left: 3px solid var(--neon); padding: 14px 16px; border-radius: 0 10px 10px 0; margin-bottom: 24px; display: flex; align-items: flex-start; gap: 10px; overflow: hidden; backdrop-filter: blur(4px); }
    .console::after {
      content: ''; position: absolute; left: 0; right: 0; height: 100%; top: -100%;
      background: linear-gradient(to bottom, transparent, rgba(0,229,160,0.06), transparent);
      animation: laserScan 3s linear infinite;
    }
    @keyframes laserScan { 0% { top: -100%; } 100% { top: 100%; } }
    .console .prompt { color: var(--neon); font-family: 'Share Tech Mono', monospace; font-size: 14px; animation: flashPrompt 1s infinite alternate; }
    @keyframes flashPrompt { from { opacity: 0.6; } to { opacity: 1; } }
    .console .msg { color: #baffeb; font-family: 'Share Tech Mono', monospace; font-size: 12px; line-height: 1.6; }
    .cursor { display: inline-block; width: 7px; height: 13px; background: var(--neon); margin-left: 3px; animation: blink 0.8s step-end infinite; box-shadow: 0 0 6px var(--neon); }
    
    /* Tarjetas Modulares con Escaneo Perimetral */
    .card { background: var(--card); border: 0.5px solid var(--border); border-radius: 16px; padding: 22px 24px; margin-bottom: 18px; position: relative; overflow: hidden; backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
    .card::before {
      content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 1px;
      background: linear-gradient(90deg, transparent, rgba(0,229,160,0.15), transparent);
      transform: translateX(-100%); animation: borderWave 6s linear infinite;
    }
    @keyframes borderWave { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }
    .card:hover { border-color: rgba(0,229,160,0.22); box-shadow: 0 12px 35px rgba(0,0,0,0.5), inset 0 0 15px rgba(0,229,160,0.02); transform: scale(1.005) translateY(-1px); }
    
    /* Entrada Kinetic Cascade */
    .stagger-1 { animation: cardEnter 0.6s cubic-bezier(0.16, 1, 0.3, 1) both; animation-delay: 0.05s; }
    .stagger-2 { animation: cardEnter 0.6s cubic-bezier(0.16, 1, 0.3, 1) both; animation-delay: 0.12s; }
    .stagger-3 { animation: cardEnter 0.6s cubic-bezier(0.16, 1, 0.3, 1) both; animation-delay: 0.20s; }
    .stagger-4 { animation: cardEnter 0.6s cubic-bezier(0.16, 1, 0.3, 1) both; animation-delay: 0.28s; }
    @keyframes cardEnter { from { opacity: 0; transform: translateY(15px); filter: blur(5px); } to { opacity: 1; transform: translateY(0); filter: blur(0); } }

    .card-label { font-size: 9px; color: var(--neon); letter-spacing: 3px; text-transform: uppercase; margin-bottom: 18px; display: flex; align-items: center; gap: 8px; font-family: 'Share Tech Mono', monospace; }
    .card-label::after { content: ''; flex: 1; height: 0.5px; background: linear-gradient(90deg, var(--neon-border), transparent); }
    
    select, input[type="text"], input[type="number"] { background: #060708; border: 0.5px solid rgba(255,255,255,0.06); color: #e8e8e8; padding: 11px 14px; border-radius: 9px; font-family: 'Share Tech Mono', monospace; font-size: 13px; outline: none; width: 100%; transition: all 0.3s; }
    select:focus, input:focus { border-color: var(--neon); box-shadow: 0 0 12px rgba(0,229,160,0.15); background: #090a0c; }
    
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }
    .form-group { display: flex; flex-direction: column; gap: 6px; }
    .form-group label { font-size: 9px; color: #555; letter-spacing: 2px; text-transform: uppercase; font-family: 'Share Tech Mono', monospace; }

    /* Botón Súper Cargado */
    .deploy-btn { width: 100%; padding: 14px; background: var(--neon); color: #020c07; font-family: 'Syne', sans-serif; font-weight: 600; font-size: 11px; letter-spacing: 3px; text-transform: uppercase; border: none; border-radius: 9px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; position: relative; transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); overflow: hidden; box-shadow: 0 4px 15px rgba(0,229,160,0.2); }
    .deploy-btn:hover { background: #00ffb3; transform: translateY(-1px) scale(1.01); box-shadow: 0 8px 25px rgba(0,229,160,0.35); }
    .deploy-btn::before { content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent); transform: skewX(-25deg); transition: none; animation: lightningSweeper 3.5s infinite linear; }
    @keyframes lightningSweeper { 0% { left: -120%; } 30% { left: 150%; } 100% { left: 150%; } }

    /* Componentes del Monitor con Radar Ondulante Continuo */
    .op-row { display: grid; grid-template-columns: 40px 1fr auto auto; gap: 14px; align-items: center; padding: 12px 10px; border-bottom: 0.5px solid var(--border); border-radius: 8px; transition: all 0.35s cubic-bezier(0.2,1,0.2,1); }
    .op-row:hover { background: rgba(0,229,160,0.02); padding-left: 15px; }
    
    .avatar-wrapper { position: relative; width: 36px; height: 36px; }
    .op-avatar { width: 100%; height: 100%; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-family: 'Share Tech Mono', monospace; font-size: 11px; font-weight: 600; position: relative; z-index: 2; }
    .av-neon { background: #05140f; color: var(--neon); border: 0.5px solid var(--neon-border); }
    .av-blue { background: #050a14; color: #8fa8ff; border: 0.5px solid rgba(59,130,246,0.2); }
    
    /* Ondas de radar infinitas para operadores activos */
    .row-active-pulse::before {
      content: ''; position: absolute; inset: 0; border-radius: 50%;
      box-shadow: 0 0 0 2px var(--neon); animation: radarRing 2s infinite linear; z-index: 1;
    }
    @keyframes radarRing { 0% { transform: scale(0.95); opacity: 0.8; } 100% { transform: scale(1.4); opacity: 0; } }

    .op-name { font-size: 13px; color: #eee; font-weight: 500; }
    .op-task { font-size: 10px; color: #666; margin-top: 3px; display: flex; align-items: center; gap: 6px; font-family: 'Share Tech Mono', monospace; }
    
    .sdot { width: 6px; height: 6px; border-radius: 50%; }
    .sdot-active { background: var(--neon); box-shadow: 0 0 10px var(--neon); animation: blink 0.6s step-end infinite; }
    .sdot-idle { background: #2a2c2e; }
    
    .op-via { font-size: 9px; color: #444; margin-top: 2px; font-family: 'Share Tech Mono', monospace; }
    .stat-chip { font-size: 11px; font-weight: 600; display: flex; align-items: center; gap: 3px; font-family: 'Share Tech Mono', monospace; padding: 3px 6px; background: rgba(255,255,255,0.01); border-radius: 4px; }
    .stat-ok { color: var(--neon); } .stat-bad { color: var(--red); }
    
    .del-btn { font-size: 12px; color: rgba(255,79,79,0.4); cursor: pointer; border: 0.5px solid rgba(255,79,79,0.15); padding: 5px 8px; border-radius: 6px; transition: all 0.25s; display: flex; align-items: center; justify-content: center; }
    .del-btn:hover { color: var(--red); background: rgba(255,79,79,0.12); border-color: var(--red); transform: rotate(90deg); }
    
    .log-scroll { max-height: 140px; overflow-y: auto; }
    .log-entry { display: flex; justify-content: space-between; align-items: center; padding: 10px 6px; border-bottom: 0.5px solid var(--border); font-family: 'Share Tech Mono', monospace; font-size: 12px; }

    /* Tabla de Registros Animada en Vivo */
    .table-container { width: 100%; overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; font-family: 'Share Tech Mono', monospace; font-size: 12px; }
    th { padding: 12px 10px; color: var(--neon); border-bottom: 1px solid var(--neon-border); font-size: 10px; letter-spacing: 1px; text-transform: uppercase; text-align: left; }
    td { padding: 13px 10px; border-bottom: 0.5px solid var(--border); color: #ccc; }
    tr { transition: background 0.2s; }
    tr:hover { background: rgba(255,255,255,0.015); }
    
    /* Barras de Estado en Carga Infinita */
    .badge { padding: 3px 8px; border-radius: 4px; font-size: 9px; font-weight: bold; text-transform: uppercase; position: relative; overflow: hidden; display: inline-block; }
    .bg-desplegada { background: rgba(59,130,246,0.12); color: #60a5fa; border: 0.5px solid rgba(59,130,246,0.25); }
    
    .bg-ejecucion { background: rgba(245,166,35,0.12); color: #fbbf24; border: 0.5px solid rgba(245,166,35,0.25); position: relative; }
    /* Animación de líneas oblicuas moviéndose solas para simular procesamiento activo */
    .bg-ejecucion::before {
      content: ''; position: absolute; inset: 0; opacity: 0.15;
      background-image: linear-gradient(45deg, #fbbf24 25%, transparent 25%, transparent 50%, #fbbf24 50%, #fbbf24 75%, transparent 75%, transparent);
      background-size: 10px 10px; animation: progressStripes 1s linear infinite;
    }
    @keyframes progressStripes { from { background-position: 0 0; } to { background-position: 10px 0; } }
    
    .bg-cumplida { background: rgba(0,229,160,0.1); color: var(--neon); border: 0.5px solid var(--neon-border); box-shadow: 0 0 8px rgba(0,229,160,0.15); }
    .bg-retraso { background: rgba(255,79,79,0.12); color: #f87171; border: 0.5px solid rgba(255,79,79,0.25); }

    /* Overlay Cuántico de Lanzamiento */
    .launch-overlay { position: fixed; inset: 0; z-index: 8000; display: flex; align-items: center; justify-content: center; pointer-events: none; opacity: 0; backdrop-filter: blur(0px); -webkit-backdrop-filter: blur(0px); transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
    .launch-overlay.active { opacity: 1; pointer-events: auto; background: rgba(3,4,5,0.65); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); }
    .launch-box { background: #030806; border: 1px solid var(--neon); border-radius: 20px; padding: 35px 50px; text-align: center; font-family: 'Share Tech Mono', monospace; transform: scale(0.6); transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1); box-shadow: 0 0 40px rgba(0,229,160,0.3); }
    .launch-overlay.active .launch-box { transform: scale(1); }
    .launch-title { font-size: 10px; color: rgba(0,229,160,0.4); letter-spacing: 5px; margin-bottom: 12px; animation: blink 0.5s step-end infinite; }
    .launch-name { font-size: 28px; color: var(--neon); letter-spacing: 4px; text-shadow: 0 0 15px var(--neon); font-weight: bold; }
    
    @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
  </style>
</head>
<body>

<div class="launch-overlay" id="launch-overlay">
  <div class="launch-box">
    <div class="launch-title">&gt;&gt; RED DE DATOS INTERMITENTE: ENVIANDO MANDO_</div>
    <div class="launch-name" id="launch-dest">—</div>
  </div>
</div>

<div class="wrap">
  <div class="top-bar">
    <div class="session-info"><span class="dot-live"></span>RED EN LA NUBE: {{ usuario }}</div>
    <a href="/logout" class="logout-link">[ APAGAR NODO ]</a>
  </div>
  
  <div class="logo"><h1>LUMINA OS</h1><div class="sub">Consola de Misiones Globales</div></div>
  
  <div class="console">
    <span class="prompt">&gt;</span>
    <span class="msg" id="console-msg">{{ ultimo_msj }}<span class="cursor"></span></span>
  </div>

  <div class="card stagger-1">
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
        <i class="ti ti-player-play-filled"></i>
        <span>Desplegar misión global</span>
      </button>
    </form>
  </div>

  <div class="card stagger-2">
    <div class="card-label"><i class="ti ti-radar"></i> Monitor de Operadores</div>
    <div id="operator-rows-container">
      {% set avatares = ['av-neon','av-blue'] %}
      {% for op_name, op_info in equipo.items() if op_name != 'log_global' %}
      {% set esta_activo = op_info.datos.tarea_actual != 'Esperando mando...' and not op_info.datos._ui_consumida %}
      <div class="op-row" id="row-{{ op_name }}">
        <div class="avatar-wrapper {% if esta_activo %}row-active-pulse{% endif %}">
          <div class="op-avatar {{ avatares[loop.index0 % 2] }}">{{ op_name[:2].upper() }}</div>
        </div>
        <div>
          <div class="op-name">{{ op_name }}</div>
          <div class="op-task">
            {% if not esta_activo %}
              <span class="sdot sdot-idle"></span><span>Esperando mando...</span>
            {% else %}
              <span class="sdot sdot-active"></span><span style="color:#fff;">{{ op_info.datos.tarea_actual }}</span>
            {% endif %}
          </div>
          <div class="op-via">Mando: {{ op_info.datos.enviado_por }}</div>
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

  <div class="card stagger-3">
    <div class="card-label"><i class="ti ti-history"></i> Transmisiones Recientes</div>
    <div class="log-scroll">
      {% if log_global %}
        {% for log in log_global[::-1] %}
          <div class="log-entry">
            <div>
              <span style="color: var(--neon); font-weight: bold;">[{{ log.usuario }}]</span> 
              <span>Misión: {{ log.tarea }}</span>
            </div>
            <div style="color: #555; font-size: 11px;">{{ log.fecha.split(' - ')[0] }}</div>
          </div>
        {% endfor %}
      {% else %}
        <div style="text-align: center; color: var(--muted); padding: 15px; font-family: 'Share Tech Mono', monospace; font-size: 12px;">
          Esperando transmisiones...
        </div>
      {% endif %}
    </div>
  </div>

  <div class="card stagger-4">
    <div class="card-label"><i class="ti ti-table-share"></i> Tabla de Registro de Actividades (Auditoría Global)</div>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Operador</th>
            <th>Actividad Enviada</th>
            <th>Duración</th>
            <th>Mando Por</th>
            <th>Estado de Misión</th>
            <th>Fecha / Hora Exacta</th>
          </tr>
        </thead>
        <tbody id="log-table-body">
          {% if log_global %}
            {% for log in log_global[::-1] %}
            <tr>
              <td style="color: var(--neon); font-weight: bold;">{{ log.usuario }}</td>
              <td>{{ log.tarea }}</td>
              <td><i class="ti ti-hourglass-high" style="margin-right:3px; color: var(--amber)"></i>{{ log.tiempo_assigned if log.tiempo_assigned else log.tiempo_asignado }}</td>
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
              <td style="color: #555; font-size: 11px;">{{ log.fecha }}</td>
