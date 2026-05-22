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
    "Misión desplegada. El equipo está en movimiento.",
    "Transmisión confirmada. Operador en modo activo."
]

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
      background-image:
        linear-gradient(rgba(0,229,160,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,229,160,0.025) 1px, transparent 1px);
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

    /* ── BOTÓN DEPLOY con barra de progreso ── */
    .deploy-btn {
      width: 100%; padding: 13px; background: var(--neon); color: #041a0e;
      font-family: 'Syne', sans-serif; font-weight: 600; font-size: 11px;
      letter-spacing: 3px; text-transform: uppercase; border: none; border-radius: 8px;
      cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;
      transition: opacity 0.2s, transform 0.1s, background 0.4s, color 0.4s;
      position: relative; overflow: hidden;
    }
    .deploy-btn:hover { opacity: 0.85; }
    .deploy-btn:active { transform: scale(0.985); }
    .deploy-btn.sending { pointer-events: none; background: #0a2e1e; color: var(--neon); border: 0.5px solid var(--neon-border); }
    .deploy-btn.done    { pointer-events: none; background: #0a2e1e; color: var(--neon); border: 0.5px solid var(--neon-border); }
    .btn-bar {
      position: absolute; left: 0; bottom: 0; height: 2px;
      background: rgba(0,229,160,0.55); width: 0%;
      border-radius: 0 0 8px 8px; transition: none;
    }

    /* ── TOAST de confirmación ── */
    .toast {
      position: absolute; top: 14px; right: 18px; z-index: 30;
      background: #061c11; border: 0.5px solid var(--neon-border); color: var(--neon);
      font-family: 'Share Tech Mono', monospace; font-size: 11px;
      padding: 8px 14px; border-radius: 8px; letter-spacing: 1px;
      display: flex; align-items: center; gap: 7px;
      opacity: 0; transform: translateY(-8px) scale(0.96);
      transition: opacity 0.3s, transform 0.3s; pointer-events: none;
    }
    .toast.show { opacity: 1; transform: translateY(0) scale(1); }
    .toast-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--neon); animation: pulse 1s infinite; }

    /* ── FILAS de equipo ── */
    .op-row {
      display: grid; grid-template-columns: 40px 1fr auto auto; gap: 14px;
      align-items: center; padding: 13px 6px; border-bottom: 0.5px solid var(--border);
      border-radius: 8px; margin: 0 -6px; position: relative;
      transition: background 0.4s;
    }
    .op-row:last-child { border-bottom: none; }

    /* flash de highlight en la fila */
    .row-flash {
      position: absolute; inset: 0; border-radius: 8px;
      background: rgba(0,229,160,0.06); border: 0.5px solid var(--neon-border);
      opacity: 0; pointer-events: none; transition: opacity 0.35s;
    }
    .op-row.targeted .row-flash { opacity: 1; }

    /* scan line */
    .scan-line {
      position: absolute; left: 0; right: 0; height: 1px;
      background: var(--neon); opacity: 0; pointer-events: none; z-index: 5;
    }

    .op-avatar {
      width: 38px; height: 38px; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-family: 'Share Tech Mono', monospace; font-size: 10px; font-weight: 600;
      flex-shrink: 0; transition: transform 0.4s, box-shadow 0.4s;
    }
    .op-row.targeted .op-avatar { transform: scale(1.14); }
    .av-neon  { background: rgba(0,229,160,0.1);  color: var(--neon);  border: 0.5px solid var(--neon-border); }
    .av-blue  { background: rgba(90,120,255,0.1); color: #8fa8ff; border: 0.5px solid rgba(90,120,255,0.25); }
    .av-amber { background: rgba(245,166,35,0.1); color: var(--amber); border: 0.5px solid rgba(245,166,35,0.25); }

    .op-name { font-size: 13px; color: #eee; font-weight: 500; }
    .op-task { font-size: 10px; color: var(--muted); margin-top: 3px; display: flex; align-items: center; gap: 5px; font-family: 'Share Tech Mono', monospace; transition: color 0.4s; }
    .op-row.targeted .op-task { color: var(--neon); }
    .op-via { font-size: 9px; color: #2a2a2a; font-family: 'Share Tech Mono', monospace; }

    .sdot { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; transition: all 0.4s; }
    .sdot-active { background: var(--neon); }
    .sdot-idle   { background: #333; }
    .sdot-delay  { background: var(--red); }
    .op-row.targeted .sdot { background: var(--neon); box-shadow: 0 0 6px rgba(0,229,160,0.7); }

    .op-stats { display: flex; gap: 10px; }
    .stat-chip { font-size: 12px; font-weight: 600; display: flex; align-items: center; gap: 3px; font-family: 'Share Tech Mono', monospace; }
    .stat-ok  { color: var(--neon); }
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
    .log-entry { display: grid; grid-template-columns: 84px 1fr auto; gap: 10px; align-items: center; padding: 11px 0; border-bottom: 0.5px solid var(--border); }
    .log-entry:last-child { border-bottom: none; }
    .log-entry.new-entry { animation: fadeSlide 0.4s ease both; }
    .log-user { font-size: 11px; color: var(--neon); font-weight: 600; font-family: 'Share Tech Mono', monospace; }
    .log-name { font-size: 12px; color: #ccc; }
    .log-via  { font-size: 9px; color: #333; margin-top: 2px; font-family: 'Share Tech Mono', monospace; }
    .tag-ok    { font-size: 8px; color: var(--neon); border: 0.5px solid var(--neon-border); padding: 2px 6px; border-radius: 3px; display: inline-block; margin-top: 4px; letter-spacing: 0.5px; font-family: 'Share Tech Mono', monospace; }
    .tag-delay { font-size: 8px; color: var(--red); border: 0.5px solid rgba(255,79,79,0.35); padding: 2px 6px; border-radius: 3px; display: inline-block; margin-top: 4px; letter-spacing: 0.5px; font-family: 'Share Tech Mono', monospace; text-transform: uppercase; }
    .tag-deploy { font-size: 8px; color: #8fa8ff; border: 0.5px solid rgba(90,120,255,0.3); padding: 2px 6px; border-radius: 3px; display: inline-block; margin-top: 4px; letter-spacing: 0.5px; font-family: 'Share Tech Mono', monospace; }
    .log-time  { font-size: 9px; color: #393939; text-align: right; white-space: nowrap; font-family: 'Share Tech Mono', monospace; }
    .empty-log { color: var(--muted); font-size: 11px; text-align: center; padding: 28px 0; font-family: 'Share Tech Mono', monospace; }

    /* partículas */
    .particle {
      position: fixed; width: 4px; height: 4px; border-radius: 50%;
      background: var(--neon); pointer-events: none; z-index: 9999;
    }

    @keyframes pulse     { 0%,100%{opacity:1} 50%{opacity:0.25} }
    @keyframes blink     { 0%,100%{opacity:1} 50%{opacity:0} }
    @keyframes fadeSlide { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:none} }
    @keyframes particleFly { 0%{opacity:1;transform:translate(0,0) scale(1)} 100%{opacity:0;transform:translate(var(--tx),var(--ty)) scale(0)} }
    @keyframes scanDown  { 0%{top:0;opacity:0.8} 100%{top:100%;opacity:0} }
    .fade-in { animation: fadeSlide 0.35s ease both; }
  </style>
</head>
<body>
<div class="wrap">

  <div class="top-bar">
    <div class="session-info"><span class="dot-live"></span>SESIÓN: {{ usuario }}</div>
    <a href="/logout" class="logout-link">[ SALIR ]</a>
  </div>

  <div class="logo">
    <h1>LUMINA OS</h1>
    <div class="sub">Sistema de gestión de misiones</div>
  </div>

  <div class="console">
    <span class="prompt">&gt;</span>
    <span class="msg" id="console-msg">{{ ultimo_msj }}<span class="cursor"></span></span>
  </div>

  <!-- DESPLEGAR ACTIVIDAD -->
  <div class="card fade-in" id="form-card">
    <div class="toast" id="toast"><span class="toast-dot"></span><span id="toast-txt">Misión desplegada</span></div>
    <div class="card-label"><i class="ti ti-rocket"></i> Desplegar actividad</div>
    <form id="deploy-form" action="/enviar_tarea_web" method="POST" onsubmit="return interceptDeploy(event)">
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

  <!-- MONITOR -->
  <div class="card fade-in">
    <div class="card-label"><i class="ti ti-radar"></i> Monitor de equipo</div>
    {% set avatares = ['av-neon','av-blue','av-amber'] %}
    {% for op_name, op_info in equipo.items() if op_name != 'log_global' %}
    {% set loop_idx = loop.index0 %}
    <div class="op-row" id="row-{{ op_name }}" data-user="{{ op_name }}">
      <div class="row-flash"></div>
      <div class="scan-line" id="scan-{{ op_name }}"></div>
      <div class="op-avatar {{ avatares[loop_idx % 3] }}">{{ op_name[:2].upper() }}</div>
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

  <!-- LOG -->
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
const FRASES = [
  "Objetivo detectado. Optimizando frecuencia de enfoque.",
  "Lumina en línea. Iniciando secuencia de productividad.",
  "Sistemas listos. La disciplina es el puente al éxito.",
  "Misión desplegada. El equipo está en movimiento.",
  "Transmisión confirmada. Operador en modo activo."
];

function spawnParticles(fromEl, toEl) {
  const fR = fromEl.getBoundingClientRect();
  const tR = toEl.getBoundingClientRect();
  const sx = fR.left + fR.width / 2;
  const sy = fR.top  + fR.height / 2;
  for (let i = 0; i < 12; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    const spread = (Math.random() - 0.5) * 60;
    const tx = (tR.left + tR.width / 2 - sx) + spread;
    const ty = (tR.top  + tR.height / 2 - sy) + spread;
    const delay = i * 0.035;
    const dur   = 0.45 + Math.random() * 0.35;
    p.style.cssText = `left:${sx}px;top:${sy}px;--tx:${tx}px;--ty:${ty}px;animation:particleFly ${dur}s ease-out ${delay}s both;`;
    document.body.appendChild(p);
    setTimeout(() => p.remove(), (dur + delay) * 1000 + 100);
  }
}

function triggerScanLine(destUser) {
  const scan = document.getElementById('scan-' + destUser);
  if (!scan) return;
  scan.style.cssText = 'top:0;opacity:0.85;animation:scanDown 0.5s linear forwards;';
  setTimeout(() => { scan.style.animation = ''; scan.style.opacity = '0'; }, 560);
}

function highlightRow(destUser) {
  document.querySelectorAll('.op-row').forEach(r => r.classList.remove('targeted'));
  const row = document.getElementById('row-' + destUser);
  if (row) row.classList.add('targeted');
  return row;
}

function prependLog(destUser, tarea, sessionUser) {
  const list = document.getElementById('log-list');
  const empty = list.querySelector('.empty-log');
  if (empty) empty.remove();
  const now  = new Date();
  const hora = now.getHours().toString().padStart(2,'0') + ':' + now.getMinutes().toString().padStart(2,'0');
  const dia  = now.getDate().toString().padStart(2,'0') + '/' + (now.getMonth()+1).toString().padStart(2,'0');
  const entry = document.createElement('div');
  entry.className = 'log-entry new-entry';
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

function interceptDeploy(e) {
  const btn      = document.getElementById('deploy-btn');
  const btnTxt   = document.getElementById('btn-txt');
  const btnIcon  = document.getElementById('btn-icon');
  const bar      = document.getElementById('btn-bar');
  const destUser = document.getElementById('dest-select').value;
  const tarea    = document.getElementById('tarea-input').value.trim();
  const mins     = document.getElementById('mins-input').value;
  if (!tarea || !mins) return true;

  e.preventDefault();

  btn.classList.add('sending');
  btnIcon.className = 'ti ti-loader-2';
  btnTxt.textContent = 'Transmitiendo...';
  bar.style.transition = 'none';
  bar.style.width = '0%';
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      bar.style.transition = 'width 1.3s linear';
      bar.style.width = '100%';
    });
  });

  const destAvatar = document.querySelector('#row-' + destUser + ' .op-avatar');

  setTimeout(() => {
    spawnParticles(btn, destAvatar);
    triggerScanLine(destUser);
    const row = highlightRow(destUser);

    const toast = document.getElementById('toast');
    document.getElementById('toast-txt').textContent = 'Misión enviada → ' + destUser;
    toast.classList.add('show');

    document.getElementById('console-msg').innerHTML =
      FRASES[Math.floor(Math.random() * FRASES.length)] + '<span class="cursor"></span>';

    btn.classList.remove('sending');
    btn.classList.add('done');
    btnIcon.className = 'ti ti-check';
    btnTxt.textContent = 'Desplegada';

    prependLog(destUser, tarea, '{{ usuario }}');

    setTimeout(() => {
      toast.classList.remove('show');
      if (row) row.classList.remove('targeted');
      document.getElementById('deploy-form').submit();
    }, 1800);
  }, 1350);

  return false;
}

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
