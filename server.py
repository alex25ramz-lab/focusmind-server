from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from datetime import datetime
import os
import random
import json

app = Flask(__name__)
app.secret_key = "lumina_proto_2026_key_ultra_secure"

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
    "Lumina en linea. Iniciando secuencia de productividad.",
    "Sistemas listos. La disciplina es el puente al exito.",
    "Enfoque de ingenieria establecido. Adelante.",
    "Mision desplegada. El equipo esta en movimiento.",
    "Transmision confirmada. Operador en modo activo."
]

# ── ENDPOINTS COMUNICACION CON LAPTOP (LOGIC.PY / MAIN.PY) ──

@app.route("/get_data", methods=["GET"])
def get_data():
    usuario = request.args.get("user", "").strip()
    if not usuario:
        return jsonify({"error": "Usuario requerido"}), 400
    db = cargar_db()
    if usuario in db and usuario != "log_global":
        datos_op = db[usuario]["datos"]
        if datos_op.get("_ui_consumida", False):
            return jsonify({"tarea": "Esperando mando...", "tiempo": 0, "id": 0})
        return jsonify({
            "tarea":  datos_op.get("tarea_actual", "Esperando mando..."),
            "tiempo": datos_op.get("tiempo_actual", 0),
            "id":     datos_op.get("id_envio", 0)
        })
    return jsonify({"tarea": "Esperando mando...", "tiempo": 0, "id": 0})


@app.route("/ack_tarea", methods=["POST"])
def ack_tarea():
    data = request.get_json() or {}
    usuario  = data.get("user")
    id_tarea = data.get("id")
    if not usuario:
        return jsonify({"success": False, "error": "Datos invalidos"}), 400
    db = cargar_db()
    if usuario in db:
        if db[usuario]["datos"].get("id_envio") == id_tarea:
            db[usuario]["datos"]["_ui_consumida"] = True
        guardar_db(db)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Usuario no encontrado"}), 404


@app.route("/reportar_progreso", methods=["POST"])
def reportar_progreso():
    data    = request.get_json() or {}
    usuario = data.get("user")
    estado  = data.get("estado")
    if not usuario:
        return jsonify({"success": False, "error": "Faltan datos de usuario"}), 400
    db = cargar_db()
    if usuario in db:
        if estado == "Mision Cumplida":
            db[usuario]["datos"]["rendimiento"]["exitos"] += 1
        elif estado == "Finalizada con Retraso":
            db[usuario]["datos"]["rendimiento"]["retrasos"] += 1
        db[usuario]["datos"]["rendimiento"]["total"] += 1
        db[usuario]["datos"]["tarea_actual"]  = "Esperando mando..."
        db[usuario]["datos"]["tiempo_actual"] = 0
        db[usuario]["datos"]["_ui_consumida"] = True
        guardar_db(db)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Operador no registrado"}), 404


# ── INTERFAZ WEB ──

@app.route("/", methods=["GET", "POST"])
def login():
    if "usuario" in session:
        return redirect(url_for("panel"))
    error = None
    if request.method == "POST":
        usuario  = request.form.get("usuario", "").strip()
        password = request.form.get("password", "").strip()
        if not usuario:
            error = "El identificador no puede estar vacio."
            return render_template_string(HTML_AUTH, error=error)
        db = cargar_db()
        if usuario in db and usuario != "log_global":
            if db[usuario]["password"] == password:
                session["usuario"] = usuario
                return redirect(url_for("panel"))
            else:
                error = "Codigo de acceso incorrecto."
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
    ultimo_msj   = db[usuario_actual]["datos"].get("ultimo_msj", "Sistemas listos.")
    lista_usuarios = [k for k in db.keys() if k != "log_global"]
    log_global   = db.get("log_global", [])
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
        return jsonify({"success": False, "error": "Sesion caducada"}), 403
    destinatario = request.form.get("destinatario")
    mins         = request.form.get("mins")
    tarea        = request.form.get("tarea")
    if not destinatario or not mins or not tarea:
        return jsonify({"success": False, "error": "Campos incompletos"}), 400
    db = cargar_db()
    if destinatario in db and destinatario != "log_global":
        db[destinatario]["datos"]["tarea_actual"]  = tarea
        db[destinatario]["datos"]["tiempo_actual"] = int(mins)
        db[destinatario]["datos"]["id_envio"]      = random.randint(1000, 9999)
        db[destinatario]["datos"]["enviado_por"]   = session["usuario"]
        db[destinatario]["datos"]["ultimo_msj"]    = random.choice(FRASES_LUMINA)
        db[destinatario]["datos"]["_ui_consumida"] = False
        nuevo_log = {
            "usuario":    destinatario,
            "tarea":      tarea,
            "mins":       int(mins),
            "enviado_por": session["usuario"],
            "retraso":    False,
            "fecha":      datetime.now().strftime("%d/%m/%Y"),
            "hora":       datetime.now().strftime("%H:%M")
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
        return jsonify({"success": False, "error": "Sesion caducada"}), 403
    nuevo_op = request.form.get("nuevo_usuario", "").strip()
    if not nuevo_op or nuevo_op == "log_global":
        return jsonify({"success": False, "error": "ID Invalido"}), 400
    db = cargar_db()
    if nuevo_op in db:
        return jsonify({"success": False, "error": "El operador ya existe"}), 400
    db[nuevo_op] = {"password": "", "datos": inicializar_perfil(nuevo_op)}
    guardar_db(db)
    return jsonify({
        "success":   True,
        "nombre":    nuevo_op,
        "iniciales": nuevo_op[:2].upper(),
        "frase":     f"Enlace establecido. {nuevo_op} se ha unido a la red Lumina."
    })


@app.route("/eliminar_usuario_ajax/<nombre>", methods=["POST"])
def eliminar_usuario_ajax(nombre):
    if "usuario" not in session:
        return jsonify({"success": False, "error": "Sesion caducada"}), 403
    if nombre == "operador1":
        return jsonify({"success": False, "error": "No se puede dar de baja al nodo maestro"}), 400
    db = cargar_db()
    if nombre in db:
        del db[nombre]
        guardar_db(db)
        return jsonify({"success": True, "frase": f"Enlace cerrado. {nombre} desconectado."})
    return jsonify({"success": False, "error": "Operador no localizado"}), 404


@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))


# ════════════════════════════════════════════════════════
#  HTML
# ════════════════════════════════════════════════════════

HTML_AUTH = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"><title>LUMINA OS — Auth</title>
  <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Syne:wght@300;400;600&display=swap" rel="stylesheet">
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    :root{--neon:#00e5a0;--bg:#060708;--card:#0d0e10;--border:rgba(0,229,160,0.18)}
    body{background:var(--bg);color:#ddd;font-family:'Syne',sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh}
    body::before{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(0,229,160,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(0,229,160,0.03) 1px,transparent 1px);background-size:40px 40px;pointer-events:none}
    .auth-wrap{width:340px;background:var(--card);border:0.5px solid var(--border);border-radius:18px;padding:40px 36px 36px}
    .logo-block{text-align:center;margin-bottom:32px}
    .logo-block h1{font-family:'Share Tech Mono',monospace;font-size:26px;letter-spacing:10px;color:var(--neon);font-weight:400}
    .logo-block .sub{font-size:9px;color:rgba(0,229,160,0.4);letter-spacing:4px;margin-top:6px;text-transform:uppercase}
    input{width:100%;padding:11px 14px;background:#080909;border:0.5px solid rgba(255,255,255,0.08);color:#e8e8e8;border-radius:8px;font-family:'Share Tech Mono',monospace;font-size:13px;outline:none;transition:border .2s}
    input:focus{border-color:var(--border)}
    .field{margin-bottom:16px}
    label{display:block;font-size:9px;color:rgba(0,229,160,0.55);letter-spacing:2px;text-transform:uppercase;margin-bottom:6px}
    .submit-btn{width:100%;padding:12px;background:var(--neon);color:#051a10;font-family:'Syne',sans-serif;font-weight:600;font-size:11px;letter-spacing:3px;text-transform:uppercase;border:none;border-radius:8px;cursor:pointer;transition:opacity .2s}
    .submit-btn:hover{opacity:.85}
    .error-msg{background:rgba(255,60,60,0.08);border:0.5px solid rgba(255,60,60,0.3);color:#ff6b6b;font-size:11px;text-align:center;padding:10px;border-radius:6px;margin-top:14px;font-family:'Share Tech Mono',monospace}
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
      <div class="field" id="pass_field" style="display:none">
        <label>Codigo de acceso</label>
        <input type="password" name="password" placeholder="••••••••">
      </div>
      <button type="submit" class="submit-btn">Iniciar sistema</button>
    </form>
    {% if error %}<div class="error-msg">{{ error }}</div>{% endif %}
  </div>
  <script>
    function checkUser(){
      document.getElementById('pass_field').style.display=
        document.getElementById('user_input').value.toLowerCase()==='operador1'?'block':'none';
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
  <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Syne:wght@300;400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.34.0/dist/tabler-icons.min.css">
  <style>
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    :root{
      --neon:#00e5a0;--neon-dim:rgba(0,229,160,0.10);--neon-border:rgba(0,229,160,0.22);
      --bg:#060708;--card:#0d0e10;--border:rgba(255,255,255,0.065);
      --red:#ff4f4f;--amber:#f5a623;--muted:#555;
    }
    body{background:var(--bg);color:#e0e0e0;font-family:'Syne',sans-serif;padding:20px 16px 60px}
    body::before{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(0,229,160,0.025) 1px,transparent 1px),linear-gradient(90deg,rgba(0,229,160,0.025) 1px,transparent 1px);background-size:40px 40px;pointer-events:none;z-index:0}
    .wrap{position:relative;z-index:1;max-width:620px;margin:0 auto}

    /* top */
    .top-bar{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px}
    .session-info{display:flex;align-items:center;gap:7px;font-size:10px;color:var(--neon);letter-spacing:2px;text-transform:uppercase;font-family:'Share Tech Mono',monospace}
    .dot-live{width:6px;height:6px;border-radius:50%;background:var(--neon);flex-shrink:0;animation:pulse 1.8s infinite}
    .logout-link{font-size:10px;color:var(--red);text-decoration:none;letter-spacing:1px;border:0.5px solid rgba(255,79,79,0.28);padding:5px 11px;border-radius:5px;font-family:'Share Tech Mono',monospace;transition:background .2s}
    .logout-link:hover{background:rgba(255,79,79,0.08)}
    .logo h1{font-family:'Share Tech Mono',monospace;font-size:30px;letter-spacing:12px;color:var(--neon);font-weight:400;text-align:center}
    .logo .sub{font-size:9px;color:rgba(0,229,160,0.35);letter-spacing:4px;margin-top:5px;text-transform:uppercase;text-align:center;margin-bottom:22px}

    /* console */
    .console{background:var(--neon-dim);border-left:2px solid var(--neon);padding:13px 16px;border-radius:0 8px 8px 0;margin-bottom:20px;display:flex;align-items:flex-start;gap:10px}
    .console .prompt{color:var(--neon);font-family:'Share Tech Mono',monospace;font-size:13px}
    .console .msg{color:#7fffd4;font-family:'Share Tech Mono',monospace;font-size:12px;line-height:1.6}
    .cursor{display:inline-block;width:7px;height:13px;background:var(--neon);margin-left:3px;animation:blink 1s step-end infinite}

    /* cards */
    .card{background:var(--card);border:0.5px solid var(--border);border-radius:16px;padding:20px 22px;margin-bottom:16px;position:relative;overflow:hidden}
    .card-label{font-size:9px;color:var(--neon);letter-spacing:3px;text-transform:uppercase;margin-bottom:18px;display:flex;align-items:center;gap:8px;font-family:'Share Tech Mono',monospace}
    .card-label::after{content:'';flex:1;height:0.5px;background:var(--neon-border)}

    /* form */
    .form-row{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}
    .form-group{display:flex;flex-direction:column;gap:5px}
    .form-group label{font-size:9px;color:var(--muted);letter-spacing:2px;text-transform:uppercase}
    select,input[type="text"],input[type="number"]{background:#080909;border:0.5px solid rgba(255,255,255,0.08);color:#e8e8e8;padding:10px 13px;border-radius:8px;font-family:'Share Tech Mono',monospace;font-size:13px;outline:none;width:100%;transition:border .2s}
    select:focus,input:focus{border-color:var(--neon-border)}
    .full-field{margin-bottom:14px}

    /* deploy button */
    .deploy-btn{width:100%;padding:13px;background:var(--neon);color:#041a0e;font-family:'Syne',sans-serif;font-weight:600;font-size:11px;letter-spacing:3px;text-transform:uppercase;border:none;border-radius:8px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;position:relative;overflow:hidden;transition:opacity .2s,transform .1s,box-shadow .3s}
    .deploy-btn:hover{opacity:.88;box-shadow:0 0 22px rgba(0,229,160,0.3)}
    .deploy-btn:active{transform:scale(0.985)}
    .deploy-btn.sending{background:#060e0a;color:var(--neon);border:0.5px solid var(--neon-border);pointer-events:none}
    .deploy-btn.done{background:#060e0a;color:var(--neon);border:0.5px solid var(--neon-border);pointer-events:none}
    .deploy-btn i{font-size:15px}
    .deploy-btn.sending i{animation:spinIcon .65s linear infinite}
    .deploy-btn.done i{animation:popCheck .4s cubic-bezier(0.34,1.56,0.64,1) both}
    .btn-bar{position:absolute;left:0;bottom:0;height:2px;background:linear-gradient(90deg,var(--neon),#00ffcc);width:0%;box-shadow:0 0 10px rgba(0,229,160,0.7)}

    /* operator rows */
    .op-row{display:grid;grid-template-columns:40px 1fr auto auto;gap:14px;align-items:center;padding:13px 0;border-bottom:0.5px solid var(--border);position:relative;border-radius:8px;transition:background .5s}
    .op-row:last-child{border-bottom:none}
    .op-row.targeted{background:rgba(0,229,160,0.04)}
    .row-ripple{position:absolute;left:0;top:0;right:0;bottom:0;border-radius:8px;pointer-events:none;border:1.5px solid var(--neon);opacity:0}
    .op-row.targeted .row-ripple{animation:rippleRow .8s ease-out forwards}
    .scan-line{position:absolute;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--neon),#00ffcc,transparent);top:0;opacity:0;pointer-events:none;z-index:5;box-shadow:0 0 10px rgba(0,229,160,0.6)}
    .scan-line.scanning{animation:scanDown .6s linear forwards}
    .op-avatar{width:38px;height:38px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'Share Tech Mono',monospace;font-size:10px;font-weight:600;flex-shrink:0;transition:box-shadow .4s,transform .4s}
    .op-row.targeted .op-avatar{box-shadow:0 0 20px rgba(0,229,160,0.5);transform:scale(1.1)}
    .av-neon{background:rgba(0,229,160,0.1);color:var(--neon);border:0.5px solid var(--neon-border)}
    .av-blue{background:rgba(90,120,255,0.1);color:#8fa8ff;border:0.5px solid rgba(90,120,255,0.25)}
    .av-amber{background:rgba(245,166,35,0.1);color:var(--amber);border:0.5px solid rgba(245,166,35,0.25)}
    .op-name{font-size:13px;color:#eee;font-weight:500}
    .op-task{font-size:10px;color:var(--muted);margin-top:3px;display:flex;align-items:center;gap:5px;font-family:'Share Tech Mono',monospace}
    .op-via{font-size:9px;color:#444;margin-top:2px;font-family:'Share Tech Mono',monospace}
    .sdot{width:5px;height:5px;border-radius:50%;flex-shrink:0}
    .sdot-active{background:var(--neon);box-shadow:0 0 5px rgba(0,229,160,0.6);animation:pulseDot 2s infinite}
    .sdot-idle{background:#333}
    .op-stats{display:flex;gap:10px}
    .stat-chip{font-size:12px;font-weight:600;display:flex;align-items:center;gap:3px;font-family:'Share Tech Mono',monospace}
    .stat-ok{color:var(--neon)}
    .stat-bad{color:var(--red)}
    .del-btn{font-size:13px;color:rgba(255,79,79,0.5);cursor:pointer;border:0.5px solid rgba(255,79,79,0.2);padding:5px 8px;border-radius:6px;transition:all .2s;display:flex;align-items:center;justify-content:center}
    .del-btn:hover{color:var(--red);background:rgba(255,79,79,0.1);border-color:var(--red)}
    .add-link{display:inline-flex;align-items:center;gap:6px;font-size:11px;color:var(--neon);opacity:.7;margin-top:14px;font-family:'Share Tech Mono',monospace;cursor:pointer;border:0.5px dashed var(--neon-border);padding:6px 12px;border-radius:6px;transition:opacity .2s}
    .add-link:hover{opacity:1}
    .add-box-wrap{display:none;margin-top:12px;padding:12px;background:#080909;border:0.5px solid var(--neon-border);border-radius:8px}
    .add-box-form{display:flex;gap:8px}

    /* log */
    .log-scroll{max-height:320px;overflow-y:auto}
    .log-scroll::-webkit-scrollbar{width:3px}
    .log-scroll::-webkit-scrollbar-thumb{background:var(--neon-border);border-radius:3px}
    .log-entry{display:grid;grid-template-columns:80px 1fr auto;gap:10px;align-items:start;padding:12px 0;border-bottom:0.5px solid var(--border);transition:opacity .4s,transform .4s}
    .log-entry:last-child{border-bottom:none}
    .log-user{font-size:11px;color:var(--neon);font-weight:600;font-family:'Share Tech Mono',monospace;padding-top:2px}
    .log-body{}
    .log-tarea{font-size:12px;color:#ddd;margin-bottom:3px}
    .log-meta{font-size:9px;color:#444;font-family:'Share Tech Mono',monospace;display:flex;gap:8px;flex-wrap:wrap}
    .log-meta span{display:flex;align-items:center;gap:3px}
    .tag-ok{font-size:8px;color:var(--neon);border:0.5px solid var(--neon-border);padding:2px 6px;border-radius:3px;display:inline-block;margin-top:4px;font-family:'Share Tech Mono',monospace}
    .tag-new{font-size:8px;color:#8fa8ff;border:0.5px solid rgba(90,120,255,0.3);padding:2px 6px;border-radius:3px;display:inline-block;margin-top:4px;font-family:'Share Tech Mono',monospace}
    .log-time-block{text-align:right;font-family:'Share Tech Mono',monospace}
    .log-hora{font-size:13px;color:var(--neon);font-weight:600}
    .log-fecha{font-size:9px;color:#444;margin-top:2px}
    .log-mins{font-size:9px;color:var(--amber);margin-top:2px}
    .empty-log{color:var(--muted);font-size:11px;text-align:center;padding:28px 0;font-family:'Share Tech Mono',monospace}

    /* particles */
    .particle{position:fixed;border-radius:50%;pointer-events:none;z-index:9999;animation:particleFly var(--dur) ease-out var(--delay) both}

    /* launch overlay */
    .launch-overlay{position:fixed;inset:0;z-index:8000;display:flex;align-items:center;justify-content:center;pointer-events:none;opacity:0;transition:opacity .3s;backdrop-filter:blur(0px)}
    .launch-overlay.active{opacity:1;backdrop-filter:blur(2px)}
    .launch-box{background:rgba(6,10,8,0.97);border:0.5px solid var(--neon-border);border-radius:20px;padding:32px 48px;text-align:center;font-family:'Share Tech Mono',monospace;transform:scale(0.8) translateY(20px);transition:transform .35s cubic-bezier(0.34,1.56,0.64,1);box-shadow:0 0 60px rgba(0,229,160,0.08)}
    .launch-overlay.active .launch-box{transform:scale(1) translateY(0)}
    .launch-title{font-size:9px;color:rgba(0,229,160,0.45);letter-spacing:5px;margin-bottom:12px;text-transform:uppercase}
    .launch-name{font-size:26px;color:var(--neon);letter-spacing:4px;margin-bottom:4px;text-shadow:0 0 20px rgba(0,229,160,0.4)}
    .launch-tarea{font-size:10px;color:#555;letter-spacing:1px;margin-bottom:20px;max-width:220px}
    .launch-rings{position:relative;width:90px;height:90px;margin:0 auto}
    .ring{position:absolute;border-radius:50%;border:1px solid rgba(0,229,160,0.6);top:50%;left:50%;transform:translate(-50%,-50%) scale(0);opacity:0}
    .launch-overlay.active .ring:nth-child(1){animation:ringExpand 1.1s ease-out .05s both}
    .launch-overlay.active .ring:nth-child(2){animation:ringExpand 1.1s ease-out .22s both}
    .launch-overlay.active .ring:nth-child(3){animation:ringExpand 1.1s ease-out .39s both}
    .ring:nth-child(1){width:32px;height:32px}
    .ring:nth-child(2){width:58px;height:58px}
    .ring:nth-child(3){width:90px;height:90px}
    .launch-icon{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:28px;color:var(--neon)}
    .launch-overlay.active .launch-icon{animation:rocketPop .5s cubic-bezier(0.34,1.56,0.64,1) .1s both}

    /* screen flash */
    #screen-flash{position:fixed;inset:0;pointer-events:none;z-index:7998;background:rgba(0,229,160,0.0);transition:background .08s}
    #screen-flash.flash{background:rgba(0,229,160,0.07)}

    /* svg beam */
    #beam-svg{position:fixed;inset:0;width:100%;height:100%;pointer-events:none;z-index:7999}

    /* keyframes */
    @keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
    @keyframes pulseDot{0%,100%{box-shadow:0 0 5px rgba(0,229,160,.6)}50%{box-shadow:0 0 10px rgba(0,229,160,1)}}
    @keyframes blink{0%,100%{opacity:1}50%{opacity:0}}
    @keyframes fadeSlide{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
    @keyframes particleFly{0%{opacity:1;transform:translate(0,0) scale(1)}100%{opacity:0;transform:translate(var(--tx),var(--ty)) scale(0)}}
    @keyframes scanDown{0%{top:0;opacity:1}100%{top:100%;opacity:0}}
    @keyframes rippleRow{0%{opacity:1;transform:scale(1)}100%{opacity:0;transform:scale(1.04)}}
    @keyframes ringExpand{0%{transform:translate(-50%,-50%) scale(0);opacity:.8}100%{transform:translate(-50%,-50%) scale(2);opacity:0}}
    @keyframes spinIcon{to{transform:rotate(360deg)}}
    @keyframes popCheck{0%{transform:scale(0) rotate(-20deg)}100%{transform:scale(1) rotate(0deg)}}
    @keyframes rocketPop{0%{transform:translate(-50%,-50%) scale(.3) rotate(-20deg);opacity:0}100%{transform:translate(-50%,-50%) scale(1) rotate(0);opacity:1}}
    @keyframes beamTravel{0%{stroke-dashoffset:var(--blen);opacity:.9}100%{stroke-dashoffset:0;opacity:0}}
    @keyframes shakeRow{0%,100%{transform:translateX(0)}25%{transform:translateX(-3px)}75%{transform:translateX(3px)}}
    .fade-in{animation:fadeSlide .35s ease both}
  </style>
</head>
<body>

<!-- screen flash -->
<div id="screen-flash"></div>

<!-- launch overlay -->
<div class="launch-overlay" id="launch-overlay">
  <div class="launch-box">
    <div class="launch-title">Mision desplegada</div>
    <div class="launch-name" id="launch-dest">—</div>
    <div class="launch-tarea" id="launch-tarea-txt"></div>
    <div class="launch-rings">
      <div class="ring"></div><div class="ring"></div><div class="ring"></div>
      <i class="ti ti-rocket launch-icon"></i>
    </div>
  </div>
</div>

<!-- svg beam -->
<svg id="beam-svg" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="ng"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
</svg>

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

  <!-- FORM -->
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
        <label>Mision / Objetivo</label>
        <input type="text" name="tarea" id="tarea-input" placeholder="Escribe la actividad tecnica..." required>
      </div>
      <button type="submit" class="deploy-btn" id="deploy-btn">
        <i class="ti ti-player-play" id="btn-icon"></i>
        <span id="btn-txt">Desplegar mision global</span>
        <div class="btn-bar" id="btn-bar"></div>
      </button>
    </form>
  </div>

  <!-- MONITOR -->
  <div class="card fade-in">
    <div class="card-label"><i class="ti ti-radar"></i> Monitor de Operadores</div>
    <div id="operator-rows-container">
      {% set avatares = ['av-neon','av-blue','av-amber'] %}
      {% for op_name, op_info in equipo.items() if op_name != 'log_global' %}
      <div class="op-row" id="row-{{ op_name }}">
        <div class="row-ripple"></div>
        <div class="scan-line" id="scan-{{ op_name }}"></div>
        <div class="op-avatar {{ avatares[loop.index0 % 3] }}" id="av-{{ op_name }}">{{ op_name[:2].upper() }}</div>
        <div>
          <div class="op-name">{{ op_name }}</div>
          <div class="op-task" id="task-row-{{ op_name }}">
            {% if op_info.datos.tarea_actual == 'Esperando mando...' or op_info.datos._ui_consumida %}
              <span class="sdot sdot-idle" id="sdot-{{ op_name }}"></span>
              <span id="task-txt-{{ op_name }}">Esperando mando...</span>
            {% else %}
              <span class="sdot sdot-active" id="sdot-{{ op_name }}"></span>
              <span id="task-txt-{{ op_name }}">{{ op_info.datos.tarea_actual }}</span>
            {% endif %}
          </div>
          <div class="op-via" id="via-{{ op_name }}">Enviado por: {{ op_info.datos.enviado_por }}</div>
        </div>
        <div class="op-stats">
          <span class="stat-chip stat-ok"><i class="ti ti-check"></i>{{ op_info.datos.rendimiento.exitos }}</span>
          <span class="stat-chip stat-bad"><i class="ti ti-clock"></i>{{ op_info.datos.rendimiento.retrasos }}</span>
        </div>
        <div>
          {% if op_name != 'operador1' %}
            <div onclick="eliminarOperadorAjax('{{ op_name }}')" class="del-btn" title="Dar de baja"><i class="ti ti-trash"></i></div>
          {% else %}
            <div style="width:28px"></div>
          {% endif %}
        </div>
      </div>
      {% endfor %}
    </div>
    <div class="add-link" onclick="toggleAddBox()"><i class="ti ti-user-plus"></i> Registrar nuevo operador</div>
    <div class="add-box-wrap" id="add-box">
      <form class="add-box-form" onsubmit="agregarOperadorAjax(event)">
        <input type="text" id="nuevo-usuario-input" placeholder="ID del nuevo operador" required>
        <button type="submit" class="deploy-btn" style="width:auto;padding:0 16px"><i class="ti ti-plus"></i></button>
      </form>
    </div>
  </div>

  <!-- LOG DE ACTIVIDADES -->
  <div class="card fade-in">
    <div class="card-label"><i class="ti ti-list-check"></i> Registro de Actividades Desplegadas</div>
    <div class="log-scroll" id="log-list">
      {% if log_global %}
        {% for log in log_global|reverse %}
        <div class="log-entry">
          <span class="log-user">{{ log.usuario }}</span>
          <div class="log-body">
            <div class="log-tarea">{{ log.tarea }}</div>
            <div class="log-meta">
              <span><i class="ti ti-user" style="font-size:9px;color:var(--muted)"></i>{{ log.enviado_por }}</span>
              <span><i class="ti ti-clock" style="font-size:9px;color:var(--amber)"></i>{{ log.mins }} min</span>
            </div>
            <span class="tag-ok">Desplegada</span>
          </div>
          <div class="log-time-block">
            <div class="log-hora">{{ log.hora }}</div>
            <div class="log-fecha">{{ log.fecha }}</div>
            <div class="log-mins">{{ log.mins }} min</div>
          </div>
        </div>
        {% endfor %}
      {% else %}
        <div class="empty-log" id="empty-log-msg">Sin actividades registradas aun...</div>
      {% endif %}
    </div>
  </div>
</div>

<script>
/* ── UTILS ── */
function typeConsole(txt) {
  var el = document.getElementById('console-msg');
  el.innerHTML = '';
  var i = 0;
  var iv = setInterval(function(){
    el.innerHTML = txt.slice(0,i) + '<span class="cursor"></span>';
    i++;
    if(i > txt.length) clearInterval(iv);
  }, 28);
}

/* ── PARTICLES ── */
function spawnParticles(fromEl, toEl, n) {
  n = n || 20;
  var fR = fromEl.getBoundingClientRect(), tR = toEl.getBoundingClientRect();
  var sx = fR.left+fR.width/2, sy = fR.top+fR.height/2;
  var tx0 = tR.left+tR.width/2-sx, ty0 = tR.top+tR.height/2-sy;
  var cols = ['#00e5a0','#7fffd4','#00c884','#a0ffe0','#fff'];
  for(var i=0;i<n;i++){
    var p=document.createElement('div'), sz=2.5+Math.random()*4;
    var tx=tx0+(Math.random()-.5)*80, ty=ty0+(Math.random()-.5)*60;
    var dur=.45+Math.random()*.4, del=i*.026;
    p.className='particle';
    p.style.cssText='width:'+sz+'px;height:'+sz+'px;background:'+cols[~~(Math.random()*cols.length)]+';left:'+sx+'px;top:'+sy+'px;--tx:'+tx+'px;--ty:'+ty+'px;--dur:'+dur+'s;--delay:'+del+'s;';
    document.body.appendChild(p);
    setTimeout((function(el){return function(){el.remove()}})(p),(dur+del)*1000+200);
  }
}

function burstParticles(el, n) {
  n = n || 14;
  var r=el.getBoundingClientRect(), cx=r.left+r.width/2, cy=r.top+r.height/2;
  var cols=['#00e5a0','#7fffd4','#00c884'];
  for(var i=0;i<n;i++){
    var ang=(i/n)*Math.PI*2, dist=40+Math.random()*50;
    var p=document.createElement('div'), sz=2+Math.random()*3;
    var tx=Math.cos(ang)*dist, ty=Math.sin(ang)*dist;
    var dur=.4+Math.random()*.3, del=Math.random()*.05;
    p.className='particle';
    p.style.cssText='width:'+sz+'px;height:'+sz+'px;background:'+cols[~~(Math.random()*cols.length)]+';left:'+cx+'px;top:'+cy+'px;--tx:'+tx+'px;--ty:'+ty+'px;--dur:'+dur+'s;--delay:'+del+'s;';
    document.body.appendChild(p);
    setTimeout((function(el){return function(){el.remove()}})(p),(dur+del)*1000+200);
  }
}

/* ── BEAM ── */
function fireBeam(fromEl, toEl) {
  var svg=document.getElementById('beam-svg');
  var fR=fromEl.getBoundingClientRect(), tR=toEl.getBoundingClientRect();
  var x1=fR.left+fR.width/2, y1=fR.top+fR.height/2;
  var x2=tR.left+tR.width/2, y2=tR.top+tR.height/2;
  var len=Math.hypot(x2-x1,y2-y1);
  function makeLine(stroke,width,filter){
    var l=document.createElementNS('http://www.w3.org/2000/svg','line');
    l.setAttribute('x1',x1);l.setAttribute('y1',y1);
    l.setAttribute('x2',x2);l.setAttribute('y2',y2);
    l.setAttribute('stroke',stroke);l.setAttribute('stroke-width',width);
    l.setAttribute('stroke-dasharray',len);l.setAttribute('stroke-dashoffset',len);
    if(filter) l.setAttribute('filter','url(#ng)');
    l.style.setProperty('--blen',len);
    l.style.animation='beamTravel .5s ease-in-out forwards';
    svg.appendChild(l);
    setTimeout(function(){l.remove()},600);
  }
  makeLine('rgba(0,229,160,0.35)','7',true);
  makeLine('#00e5a0','1.5',false);
}

/* ── SCREEN FLASH ── */
function screenFlash(){
  var fl=document.getElementById('screen-flash');
  fl.classList.add('flash');
  setTimeout(function(){fl.classList.remove('flash')},120);
}

/* ── SCAN LINE ── */
function triggerScanLine(user){
  var s=document.getElementById('scan-'+user);
  if(!s)return;
  s.classList.remove('scanning');
  void s.offsetWidth;
  s.classList.add('scanning');
  setTimeout(function(){s.classList.remove('scanning')},700);
}

/* ── HIGHLIGHT ROW ── */
function highlightRow(user){
  document.querySelectorAll('.op-row').forEach(function(r){r.classList.remove('targeted')});
  var row=document.getElementById('row-'+user);
  if(row){
    row.classList.add('targeted');
    row.style.animation='shakeRow .25s ease both';
    setTimeout(function(){row.style.animation=''},300);
  }
}

/* ── LAUNCH OVERLAY ── */
function showLaunchOverlay(user, tarea){
  var ov=document.getElementById('launch-overlay');
  document.getElementById('launch-dest').textContent=user.toUpperCase();
  document.getElementById('launch-tarea-txt').textContent=tarea.length>36?tarea.slice(0,36)+'...':tarea;
  ov.classList.add('active');
  setTimeout(function(){ov.classList.remove('active')},1800);
}

/* ── TYPEWRITER TASK ── */
function typeTask(user, text){
  var el=document.getElementById('task-txt-'+user);
  if(!el)return;
  var i=0; el.textContent='';
  el.style.color='var(--neon)';
  var iv=setInterval(function(){
    el.textContent=text.slice(0,i)+(i<text.length?'|':'');
    i++;
    if(i>text.length){clearInterval(iv);el.style.color=''}
  },36);
}

/* ── PREPEND LOG ── */
function prependLog(user, tarea, mins, enviador){
  var list=document.getElementById('log-list');
  var empty=list.querySelector('#empty-log-msg');
  if(empty) empty.remove();
  var now=new Date();
  var hora=String(now.getHours()).padStart(2,'0')+':'+String(now.getMinutes()).padStart(2,'0');
  var fecha=String(now.getDate()).padStart(2,'0')+'/'+String(now.getMonth()+1).padStart(2,'0')+'/'+now.getFullYear();
  var entry=document.createElement('div');
  entry.className='log-entry';
  entry.style.opacity='0'; entry.style.transform='translateY(-10px)';
  entry.innerHTML=
    '<span class="log-user">'+user+'</span>'+
    '<div class="log-body">'+
      '<div class="log-tarea">'+tarea+'</div>'+
      '<div class="log-meta">'+
        '<span><i class="ti ti-user" style="font-size:9px;color:var(--muted)"></i>'+enviador+'</span>'+
        '<span><i class="ti ti-clock" style="font-size:9px;color:var(--amber)"></i>'+mins+' min</span>'+
      '</div>'+
      '<span class="tag-new">Recien desplegada</span>'+
    '</div>'+
    '<div class="log-time-block">'+
      '<div class="log-hora">'+hora+'</div>'+
      '<div class="log-fecha">'+fecha+'</div>'+
      '<div class="log-mins">'+mins+' min</div>'+
    '</div>';
  list.insertBefore(entry, list.firstChild);
  requestAnimationFrame(function(){requestAnimationFrame(function(){
    entry.style.transition='opacity .4s,transform .4s';
    entry.style.opacity='1'; entry.style.transform='none';
  })});
}

/* ── MAIN INTERCEPT ── */
var _deploying = false;
function interceptDeploy(e){
  e.preventDefault();
  if(_deploying) return;

  var btn=document.getElementById('deploy-btn');
  var btnIcon=document.getElementById('btn-icon');
  var btnTxt=document.getElementById('btn-txt');
  var bar=document.getElementById('btn-bar');
  var destUser=document.getElementById('dest-select').value;
  var tarea=document.getElementById('tarea-input').value.trim();
  var mins=document.getElementById('mins-input').value;
  if(!tarea||!destUser||!mins) return;

  _deploying=true;
  btn.style.pointerEvents='none';

  function resetBtn(){
    _deploying=false;
    btn.style.pointerEvents='auto';
    btn.classList.remove('sending','done');
    btnIcon.className='ti ti-player-play';
    btnTxt.textContent='Desplegar mision global';
    bar.style.transition='none'; bar.style.width='0%';
  }

  /* FASE 1: boton sending + barra */
  btn.classList.add('sending');
  btnIcon.className='ti ti-loader-2';
  btnTxt.textContent='Transmitiendo...';
  bar.style.transition='none'; bar.style.width='0%';
  requestAnimationFrame(function(){requestAnimationFrame(function(){
    bar.style.transition='width 1.1s linear'; bar.style.width='100%';
  })});

  /* FASE 2: 400ms → beam */
  setTimeout(function(){
    var av=document.getElementById('av-'+destUser);
    if(av) fireBeam(btn,av);
  },400);

  /* FASE 3: 700ms → todo lo visual + fetch */
  setTimeout(function(){
    var av=document.getElementById('av-'+destUser);
    if(av) spawnParticles(btn,av);
    screenFlash();
    triggerScanLine(destUser);
    highlightRow(destUser);
    var sdot=document.getElementById('sdot-'+destUser);
    if(sdot) sdot.className='sdot sdot-active';

    var formData=new FormData(document.getElementById('deploy-form'));
    fetch('/enviar_tarea_web',{method:'POST',body:formData})
    .then(function(r){return r.json()})
    .then(function(data){
      if(data.success){
        showLaunchOverlay(destUser,tarea);
        setTimeout(function(){
          var av=document.getElementById('av-'+destUser);
          if(av) burstParticles(av);
        },180);
        typeTask(destUser,tarea);
        typeConsole(data.frase);
        prependLog(destUser,tarea,mins,'{{ usuario }}');

        bar.style.transition='none'; bar.style.width='0%';
        btn.classList.remove('sending');
        btn.classList.add('done');
        btnIcon.className='ti ti-check';
        btnTxt.textContent='Desplegada';

        setTimeout(function(){
          resetBtn();
          document.getElementById('tarea-input').value='';
        },2500);
      } else {
        typeConsole('ERROR: '+(data.error||'Fallo de transmision'));
        resetBtn();
      }
    })
    .catch(function(){
      typeConsole('ERROR: Sin conexion con el servidor');
      resetBtn();
    });
  },700);
}

/* ── AGREGAR OPERADOR ── */
function toggleAddBox(){
  var b=document.getElementById('add-box');
  b.style.display=(b.style.display==='block')?'none':'block';
  if(b.style.display==='block') document.getElementById('nuevo-usuario-input').focus();
}

function agregarOperadorAjax(e){
  e.preventDefault();
  var input=document.getElementById('nuevo-usuario-input');
  var nombre=input.value.trim();
  if(!nombre) return;
  var fd=new FormData(); fd.append('nuevo_usuario',nombre);
  fetch('/agregar_usuario_ajax',{method:'POST',body:fd})
  .then(function(r){return r.json()})
  .then(function(data){
    if(data.success){
      typeConsole(data.frase);
      input.value=''; toggleAddBox();
      var container=document.getElementById('operator-rows-container');
      var total=container.querySelectorAll('.op-row').length;
      var avs=['av-neon','av-blue','av-amber'];
      var newRow=document.createElement('div');
      newRow.className='op-row fade-in'; newRow.id='row-'+data.nombre;
      newRow.innerHTML=
        '<div class="row-ripple"></div>'+
        '<div class="scan-line" id="scan-'+data.nombre+'"></div>'+
        '<div class="op-avatar '+avs[total%3]+'" id="av-'+data.nombre+'">'+data.iniciales+'</div>'+
        '<div>'+
          '<div class="op-name">'+data.nombre+'</div>'+
          '<div class="op-task"><span class="sdot sdot-idle" id="sdot-'+data.nombre+'"></span><span id="task-txt-'+data.nombre+'">Esperando mando...</span></div>'+
          '<div class="op-via" id="via-'+data.nombre+'">Enviado por: Sistema</div>'+
        '</div>'+
        '<div class="op-stats">'+
          '<span class="stat-chip stat-ok"><i class="ti ti-check"></i>0</span>'+
          '<span class="stat-chip stat-bad"><i class="ti ti-clock"></i>0</span>'+
        '</div>'+
        '<div><div onclick="eliminarOperadorAjax(\''+data.nombre+'\')" class="del-btn"><i class="ti ti-trash"></i></div></div>';
      container.appendChild(newRow);
      var opt=document.createElement('option');
      opt.value=data.nombre; opt.textContent=data.nombre;
      document.getElementById('dest-select').appendChild(opt);
    } else {
      typeConsole('ERROR: '+data.error);
    }
  });
}

/* ── ELIMINAR OPERADOR ── */
function eliminarOperadorAjax(nombre){
  if(!confirm('Desconectar operador '+nombre+' de la red?')) return;
  fetch('/eliminar_usuario_ajax/'+nombre,{method:'POST'})
  .then(function(r){return r.json()})
  .then(function(data){
    if(data.success){
      typeConsole(data.frase);
      var row=document.getElementById('row-'+nombre);
      if(row){
        row.style.transition='opacity .35s,transform .35s';
        row.style.opacity='0'; row.style.transform='translateX(-20px)';
        setTimeout(function(){row.remove()},400);
      }
      var opt=document.querySelector('#dest-select option[value="'+nombre+'"]');
      if(opt) opt.remove();
    } else {
      typeConsole('ERROR: '+data.error);
    }
  });
}
</script>
</body>
</html>
"""

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=puerto)
