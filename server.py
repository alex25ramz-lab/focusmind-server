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
        except: return cuentas_maestras

def guardar_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

usuarios_db = cargar_db()

FRASES_LUMINA = [
    "Objetivo detectado. Optimizando frecuencia de enfoque.",
    "Lumina en línea. Iniciando secuencia de productividad.",
    "Sistemas listos. La disciplina es el puente al éxito.",
    "Enfoque de ingeniería establecido. Adelante.",
    "Misión desplegada. El equipo está en movimiento."
]

# ─── AUTH ────────────────────────────────────────────────────────────────────

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
      background: var(--bg);
      color: #ddd;
      font-family: 'Syne', sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
    }
    /* faint grid bg */
    body::before {
      content: '';
      position: fixed;
      inset: 0;
      background-image:
        linear-gradient(rgba(0,229,160,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,229,160,0.03) 1px, transparent 1px);
      background-size: 40px 40px;
      pointer-events: none;
    }

    .auth-wrap {
      position: relative;
      width: 340px;
      background: var(--card);
      border: 0.5px solid var(--border);
      border-radius: 18px;
      padding: 40px 36px 36px;
    }

    .auth-glow {
      position: absolute;
      top: -60px; left: 50%;
      transform: translateX(-50%);
      width: 180px; height: 180px;
      background: radial-gradient(circle, rgba(0,229,160,0.12) 0%, transparent 70%);
      pointer-events: none;
    }

    .logo-block { text-align: center; margin-bottom: 32px; }
    .logo-block h1 {
      font-family: 'Share Tech Mono', monospace;
      font-size: 26px;
      letter-spacing: 10px;
      color: var(--neon);
      font-weight: 400;
    }
    .logo-block .sub {
      font-size: 9px;
      color: rgba(0,229,160,0.4);
      letter-spacing: 4px;
      margin-top: 6px;
      text-transform: uppercase;
    }
    .logo-block .status-line {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      margin-top: 10px;
    }
    .dot-live { width: 6px; height: 6px; border-radius: 50%; background: var(--neon); animation: pulse 1.8s infinite; }

    label { display: block; font-size: 9px; color: rgba(0,229,160,0.55); letter-spacing: 2px; text-transform: uppercase; margin-bottom: 6px; }
    input {
      width: 100%;
      padding: 11px 14px;
      background: #080909;
      border: 0.5px solid rgba(255,255,255,0.08);
      color: #e8e8e8;
      border-radius: 8px;
      font-family: 'Share Tech Mono', monospace;
      font-size: 13px;
      outline: none;
      transition: border 0.25s;
    }
    input:focus { border-color: var(--border); }
    .field { margin-bottom: 16px; }

    .submit-btn {
      width: 100%;
      padding: 12px;
      background: var(--neon);
      color: #051a10;
      font-family: 'Syne', sans-serif;
      font-weight: 600;
      font-size: 11px;
      letter-spacing: 3px;
      text-transform: uppercase;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      margin-top: 4px;
      transition: opacity 0.2s, transform 0.1s;
    }
    .submit-btn:hover { opacity: 0.85; }
    .submit-btn:active { transform: scale(0.98); }

    .error-msg {
      background: rgba(255,60,60,0.08);
      border: 0.5px solid rgba(255,60,60,0.3);
      color: #ff6b6b;
      font-size: 11px;
      text-align: center;
      padding: 10px;
      border-radius: 6px;
      margin-top: 14px;
      font-family: 'Share Tech Mono', monospace;
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
      document.getElementById('pass_field').style.display =
        v.toLowerCase() === 'operador1' ? 'block' : 'none';
    }
  </script>
</body>
</html>
"""

# ─── PANEL ───────────────────────────────────────────────────────────────────

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
      --neon: #00e5a0;
      --neon-dim: rgba(0,229,160,0.10);
      --neon-border: rgba(0,229,160,0.22);
      --bg: #060708;
      --card: #0d0e10;
      --border: rgba(255,255,255,0.065);
      --red: #ff4f4f;
      --amber: #f5a623;
      --muted: #555;
    }
    body {
      background: var(--bg);
      color: #e0e0e0;
      font-family: 'Syne', sans-serif;
      padding: 20px 16px 60px;
    }
    body::before {
      content: '';
      position: fixed; inset: 0;
      background-image:
        linear-gradient(rgba(0,229,160,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,229,160,0.025) 1px, transparent 1px);
      background-size: 40px 40px;
      pointer-events: none;
      z-index: 0;
    }
    .wrap { position: relative; z-index: 1; max-width: 580px; margin: 0 auto; }

    /* top bar */
    .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
    .session-info { display: flex; align-items: center; gap: 7px; font-size: 10px; color: var(--neon); letter-spacing: 2px; text-transform: uppercase; font-family: 'Share Tech Mono', monospace; }
    .dot-live { width: 6px; height: 6px; border-radius: 50%; background: var(--neon); flex-shrink: 0; animation: pulse 1.8s infinite; }
    .logout-link { font-size: 10px; color: var(--red); text-decoration: none; letter-spacing: 1px; border: 0.5px solid rgba(255,79,79,0.28); padding: 5px 11px; border-radius: 5px; font-family: 'Share Tech Mono', monospace; transition: background 0.2s; }
    .logout-link:hover { background: rgba(255,79,79,0.08); }

    /* logo */
    .logo { text-align: center; margin-bottom: 22px; }
    .logo h1 { font-family: 'Share Tech Mono', monospace; font-size: 30px; letter-spacing: 12px; color: var(--neon); font-weight: 400; }
    .logo .sub { font-size: 9px; color: rgba(0,229,160,0.35); letter-spacing: 4px; margin-top: 5px; text-transform: uppercase; }

    /* console */
    .console {
      background: var(--neon-dim);
      border-left: 2px solid var(--neon);
      padding: 13px 16px;
      border-radius: 0 8px 8px 0;
      margin-bottom: 20px;
      display: flex;
      align-items: flex-start;
      gap: 10px;
    }
    .console .prompt { color: var(--neon); font-family: 'Share Tech Mono', monospace; font-size: 13px; flex-shrink: 0; }
    .console .msg { color: #7fffd4; font-family: 'Share Tech Mono', monospace; font-size: 12px; line-height: 1.6; }
    .cursor { display: inline-block; width: 7px; height: 13px; background: var(--neon); margin-left: 3px; vertical-align: text-bottom; animation: blink 1s step-end infinite; }

    /* cards */
    .card { background: var(--card); border: 0.5px solid var(--border); border-radius: 16px; padding: 20px 22px; margin-bottom: 16px; }
    .card-label {
      font-size: 9px; color: var(--neon); letter-spacing: 3px; text-transform: uppercase;
      margin-bottom: 18px; display: flex; align-items: center; gap: 8px;
      font-family: 'Share Tech Mono', monospace;
    }
    .card-label i { font-size: 14px; }
    .card-label::after { content: ''; flex: 1; height: 0.5px; background: var(--neon-border); }

    /* form */
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
    .form-group { display: flex; flex-direction: column; gap: 5px; }
    .form-group label { font-size: 9px; color: var(--muted); letter-spacing: 2px; text-transform: uppercase; }
    select, input[type="text"], input[type="number"] {
      background: #080909;
      border: 0.5px solid rgba(255,255,255,0.08);
      color: #e8e8e8;
      padding: 10px 13px;
      border-radius: 8px;
      font-family: 'Share Tech Mono', monospace;
      font-size: 13px;
      outline: none;
      transition: border 0.2s;
      width: 100%;
    }
    select:focus, input:focus { border-color: var(--neon-border); }
    .full-field { margin-bottom: 14px; }

    .deploy-btn {
      width: 100%;
      padding: 13px;
      background: var(--neon);
      color: #041a0e;
      font-family: 'Syne', sans-serif;
      font-weight: 600;
      font-size: 11px;
      letter-spacing: 3px;
      text-transform: uppercase;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: opacity 0.2s, transform 0.1s;
    }
    .deploy-btn:hover { opacity: 0.85; }
    .deploy-btn:active { transform: scale(0.985); }
    .deploy-btn i { font-size: 15px; }

    /* team monitor */
    .op-row {
      display: grid;
      grid-template-columns: 40px 1fr auto auto;
      gap: 14px;
      align-items: center;
      padding: 13px 0;
      border-bottom: 0.5px solid var(--border);
    }
    .op-row:last-child { border-bottom: none; }
    .op-avatar {
      width: 38px; height: 38px; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-family: 'Share Tech Mono', monospace;
      font-size: 10px; font-weight: 600; flex-shrink: 0;
    }
    .av-neon { background: rgba(0,229,160,0.1); color: var(--neon); border: 0.5px solid var(--neon-border); }
    .av-blue { background: rgba(90,120,255,0.1); color: #8fa8ff; border: 0.5px solid rgba(90,120,255,0.25); }
    .av-amber { background: rgba(245,166,35,0.1); color: var(--amber); border: 0.5px solid rgba(245,166,35,0.25); }
    .op-name { font-size: 13px; color: #eee; font-weight: 500; }
    .op-task { font-size: 10px; color: var(--muted); margin-top: 3px; display: flex; align-items: center; gap: 5px; font-family: 'Share Tech Mono', monospace; }
    .op-via { font-size: 9px; color: #333; font-family: 'Share Tech Mono', monospace; }
    .sdot { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; }
    .sdot-active { background: var(--neon); box-shadow: 0 0 5px rgba(0,229,160,0.6); }
    .sdot-idle { background: #333; }
    .sdot-delay { background: var(--red); }
    .op-stats { display: flex; gap: 10px; }
    .stat-chip { font-size: 12px; font-weight: 600; display: flex; align-items: center; gap: 3px; font-family: 'Share Tech Mono', monospace; }
    .stat-ok { color: var(--neon); }
    .stat-bad { color: var(--red); }
    .stat-chip i { font-size: 12px; }
    .del-btn { font-size: 9px; color: var(--red); border: 0.5px solid rgba(255,79,79,0.25); padding: 4px 8px; border-radius: 5px; text-decoration: none; font-family: 'Share Tech Mono', monospace; transition: background 0.2s; }
    .del-btn:hover { background: rgba(255,79,79,0.08); }
    .add-link { display: inline-flex; align-items: center; gap: 5px; font-size: 11px; color: var(--neon); text-decoration: none; opacity: 0.7; margin-top: 14px; font-family: 'Share Tech Mono', monospace; }
    .add-link:hover { opacity: 1; }
    .add-link i { font-size: 13px; }

    /* log */
    .log-scroll { max-height: 260px; overflow-y: auto; }
    .log-scroll::-webkit-scrollbar { width: 3px; }
    .log-scroll::-webkit-scrollbar-thumb { background: var(--neon-border); border-radius: 3px; }
    .log-entry {
      display: grid;
      grid-template-columns: 84px 1fr auto;
      gap: 10px;
      align-items: center;
      padding: 11px 0;
      border-bottom: 0.5px solid var(--border);
    }
    .log-entry:last-child { border-bottom: none; }
    .log-user { font-size: 11px; color: var(--neon); font-weight: 600; font-family: 'Share Tech Mono', monospace; }
    .log-name { font-size: 12px; color: #ccc; }
    .log-via { font-size: 9px; color: #333; margin-top: 2px; font-family: 'Share Tech Mono', monospace; }
    .tag-ok  { font-size: 8px; color: var(--neon); border: 0.5px solid var(--neon-border); padding: 2px 6px; border-radius: 3px; display: inline-block; margin-top: 4px; letter-spacing: 0.5px; font-family: 'Share Tech Mono', monospace; }
    .tag-delay { font-size: 8px; color: var(--red); border: 0.5px solid rgba(255,79,79,0.35); padding: 2px 6px; border-radius: 3px; display: inline-block; margin-top: 4px; letter-spacing: 0.5px; font-family: 'Share Tech Mono', monospace; text-transform: uppercase; }
    .log-time { font-size: 9px; color: #393939; text-align: right; white-space: nowrap; font-family: 'Share Tech Mono', monospace; }
    .empty-log { color: var(--muted); font-size: 11px; text-align: center; padding: 28px 0; font-family: 'Share Tech Mono', monospace; }

    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.25} }
    @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
    @keyframes fadeSlide { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:none} }
    .fade-in { animation: fadeSlide 0.35s ease both; }
  </style>
</head>
<body>
<div class="wrap">

  <div class="top-bar">
    <div class="session-info">
      <span class="dot-live"></span>
      SESIÓN: {{ usuario }}
    </div>
    <a href="/logout" class="logout-link">[ SALIR ]</a>
  </div>

  <div class="logo">
    <h1>LUMINA OS</h1>
    <div class="sub">Sistema de gestión de misiones</div>
  </div>

  <div class="console">
    <span class="prompt">&gt;</span>
    <span class="msg">{{ ultimo_msj }}<span class="cursor"></span></span>
  </div>

  <!-- DESPLEGAR ACTIVIDAD -->
  <div class="card fade-in">
    <div class="card-label"><i class="ti ti-rocket"></i> Desplegar actividad</div>
    <form action="/enviar_tarea_web" method="POST">
      <div class="form-row">
        <div class="form-group">
          <label>Asignar a</label>
          <select name="destinatario">
            {% for user in lista_usuarios %}
              <option value="{{ user }}">{{ user }}</option>
            {% endfor %}
          </select>
        </div>
        <div class="form-group">
          <label>Minutos</label>
          <input type="number" name="mins" placeholder="25" required min="1">
        </div>
      </div>
      <div class="form-group full-field">
        <label>Misión / Objetivo</label>
        <input type="text" name="tarea" placeholder="Ej: Revisar módulo de facturación" required>
      </div>
      <button type="submit" class="deploy-btn">
        <i class="ti ti-player-play"></i> Desplegar misión
      </button>
    </form>
  </div>

  <!-- MONITOR DE EQUIPO -->
  <div class="card fade-in">
    <div class="card-label"><i class="ti ti-radar"></i> Monitor de equipo</div>
    {% set avatares = ['av-neon','av-blue','av-amber'] %}
    {% for op_name, op_info in equipo.items() if op_name != 'log_global' %}
    {% set loop_idx = loop.index0 %}
    <div class="op-row">
      <div class="op-avatar {{ avatares[loop_idx % 3] }}">
        {{ op_name[:2].upper() }}
      </div>
      <div>
        <div class="op-name">{{ op_name }}</div>
        <div class="op-task">
          {% if op_info.datos.tarea_actual == 'Esperando mando...' %}
            <span class="sdot sdot-idle"></span>
          {% elif 'Retraso' in op_info.datos.tarea_actual %}
            <span class="sdot sdot-delay"></span>
          {% else %}
            <span class="sdot sdot-active"></span>
          {% endif %}
          {{ op_info.datos.tarea_actual }}
        </div>
        <div class="op-via">vía: {{ op_info.datos.enviado_por }}</div>
      </div>
      <div class="op-stats">
        <span class="stat-chip stat-ok"><i class="ti ti-check"></i>{{ op_info.datos.rendimiento.exitos }}</span>
        <span class="stat-chip stat-bad"><i class="ti ti-clock"></i>{{ op_info.datos.rendimiento.retrasos }}</span>
      </div>
      <div>
        {% if op_name != 'operador1' %}
          <a href="/eliminar_operador/{{ op_name }}" class="del-btn" onclick="return confirm('¿Eliminar operador?')">BORRAR</a>
        {% endif %}
      </div>
    </div>
    {% endfor %}
    <div style="text-align:center;">
      <a href="/registro" class="add-link"><i class="ti ti-plus"></i> Añadir nuevo miembro</a>
    </div>
  </div>

  <!-- LOG GLOBAL -->
  <div class="card fade-in">
    <div class="card-label"><i class="ti ti-list-check"></i> Registro de misiones</div>
    <div class="log-scroll">
      {% if log_global %}
        {% for log in log_global[::-1] %}
        <div class="log-entry">
          <span class="log-user">{{ log.usuario }}</span>
          <div>
            <div class="log-name">{{ log.tarea }}</div>
            <div class="log-via">Por: {{ log.enviado_por }}</div>
            {% if log.retraso %}
              <span class="tag-delay">! Retraso</span>
            {% else %}
              <span class="tag-ok">Completada</span>
            {% endif %}
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
  setInterval(async () => {
    try {
      const r = await fetch('/verificar_cambios');
      const d = await r.json();
      if (d.update) window.location.reload();
    } catch(e) {}
  }, 3000);
</script>
</body>
</html>
"""

# ─── RUTAS ───────────────────────────────────────────────────────────────────

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        u = request.form.get('usuario').strip()
        p = request.form.get('password', '').strip()
        if u.lower() == 'operador1':
            if p == usuarios_db['operador1']['password']:
                session['user'] = 'operador1'
                return redirect(url_for('home'))
            else:
                return render_template_string(HTML_AUTH, error="CÓDIGO INCORRECTO")
        if u not in usuarios_db:
            usuarios_db[u] = {"password": "123", "datos": inicializar_perfil(u)}
            guardar_db(usuarios_db)
        session['user'] = u
        return redirect(url_for('home'))
    return render_template_string(HTML_AUTH, error=None)

@app.route('/')
def home():
    if 'user' not in session: return redirect(url_for('registro'))
    user = session['user']
    if user not in usuarios_db: return redirect(url_for('logout'))
    return render_template_string(HTML_PANEL,
        usuario=user,
        lista_usuarios=[k for k in usuarios_db.keys() if k != 'log_global'],
        equipo={k: v for k, v in usuarios_db.items() if k != 'log_global'},
        log_global=usuarios_db.get('log_global', []),
        **usuarios_db[user]['datos'])

@app.route('/reportar_progreso', methods=['POST'])
def reportar():
    data = request.json
    user = data.get('user')
    if user in usuarios_db:
        db_user = usuarios_db[user]['datos']
        es_retraso = data.get('estado') == "RETRASO"
        tarea_nombre = data.get('tarea_nombre', db_user['tarea_actual'])
        if tarea_nombre == "Esperando mando..." and not es_retraso:
            return jsonify({"ok": True})
        nueva_entrada = {
            "usuario": user,
            "tarea": tarea_nombre,
            "fecha": datetime.now().strftime("%H:%M - %d/%m"),
            "enviado_por": db_user.get('enviado_por', 'Sistema'),
            "retraso": es_retraso
        }
        if "log_global" not in usuarios_db: usuarios_db["log_global"] = []
        usuarios_db["log_global"].append(nueva_entrada)
        if es_retraso:
            db_user['rendimiento']['retrasos'] += 1
            db_user['tarea_actual'] = "Finalizada con Retraso"
        else:
            db_user['rendimiento']['exitos'] += 1
            db_user['tarea_actual'] = "Misión Cumplida"
        guardar_db(usuarios_db)
        return jsonify({"ok": True, "msg": "Misión registrada en el servidor"})
    return jsonify({"ok": False}), 400

@app.route('/enviar_tarea_web', methods=['POST'])
def enviar_tarea_web():
    if 'user' not in session: return redirect(url_for('registro'))
    dest = request.form.get('destinatario')
    if dest in usuarios_db:
        d = usuarios_db[dest]['datos']
        d['id_envio'] += 1
        d['tarea_actual'] = request.form.get('tarea')
        d['tiempo_actual'] = int(request.form.get('mins'))
        d['enviado_por'] = session['user']
        d['ultimo_msj'] = random.choice(FRASES_LUMINA)
        d['rendimiento']['total'] += 1
        guardar_db(usuarios_db)
    return redirect(url_for('home'))

@app.route('/get_data')
def get_data():
    user = request.args.get('user')
    if user in usuarios_db:
        d = usuarios_db[user]['datos']
        return jsonify({
            "tarea": d['tarea_actual'],
            "tiempo": d['tiempo_actual'],
            "id": d['id_envio'],
            "remitente": d['enviado_por']
        })
    return jsonify({"error": "No user"}), 404

@app.route('/verificar_cambios')
def verificar_cambios():
    if 'user' not in session: return jsonify({"update": False})
    num_logs = len(usuarios_db.get('log_global', []))
    estado_equipo = f"logs:{num_logs}-" + "-".join([
        f"{u}:{usuarios_db[u]['datos']['rendimiento']['exitos']}:{usuarios_db[u]['datos']['rendimiento']['retrasos']}"
        for u in usuarios_db if u != 'log_global'
    ])
    if session.get('last_state') != estado_equipo:
        session['last_state'] = estado_equipo
        return jsonify({"update": True})
    return jsonify({"update": False})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('registro'))

@app.route('/eliminar_operador/<u_name>')
def eliminar_operador(u_name):
    if 'user' in session and session['user'] == 'operador1':
        if u_name in usuarios_db and u_name != 'operador1':
            del usuarios_db[u_name]
            guardar_db(usuarios_db)
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
