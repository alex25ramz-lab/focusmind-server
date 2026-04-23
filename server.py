from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from datetime import datetime
import os
import random
import json

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "lumina_ultra_secret_2026")

# --- CONFIGURACIÓN DE BASE DE DATOS ---
DB_FILE = "database.json"

def cargar_db():
    if not os.path.exists(DB_FILE):
        return {} # Empezamos con base de datos vacía
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def guardar_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

def inicializar_datos_usuario(nombre):
    return {
        "tarea_actual": "Esperando mando...",
        "tiempo_actual": 0,
        "id_envio": 0,
        "historial": [],
        "rendimiento": {"exitos": 0, "retrasos": 0, "total": 0},
        "ultimo_msj": f"Sistema LUMINA vinculado a {nombre}."
    }

# Cargar usuarios al iniciar
usuarios_db = cargar_db()

# --- ESTILOS Y PLANTILLAS ---

HTML_AUTH = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><title>LUMINA OS - Auth</title>
    <style>
        :root { --neon: #00ffaa; --bg: #050505; }
        body { background: var(--bg); color: white; font-family: 'Segoe UI', sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .auth-card { background: #0d0d0d; padding: 40px; border-radius: 20px; border: 1px solid var(--neon); box-shadow: 0 0 20px rgba(0,255,170,0.2); width: 320px; text-align: center; }
        h1 { color: var(--neon); letter-spacing: 5px; font-size: 24px; margin-bottom: 30px; }
        input { width: 100%; padding: 12px; margin: 10px 0; background: #000; border: 1px solid #333; color: white; border-radius: 8px; box-sizing: border-box; outline: none; }
        input:focus { border-color: var(--neon); }
        button { width: 100%; padding: 12px; background: var(--neon); color: black; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; margin-top: 10px; text-transform: uppercase; }
        .toggle-link { margin-top: 20px; font-size: 13px; color: #666; }
        .toggle-link a { color: var(--neon); text-decoration: none; }
        .error { color: #ff4444; font-size: 12px; margin-top: 15px; }
        .success { color: var(--neon); font-size: 12px; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="auth-card">
        <h1>LUMINA OS</h1>
        
        {% if modo == 'login' %}
        <form method="POST" action="/login">
            <input type="text" name="usuario" placeholder="ID OPERADOR" required>
            <input type="password" name="password" placeholder="CÓDIGO SECRETO" required>
            <button type="submit">INICIAR SESIÓN</button>
        </form>
        <div class="toggle-link">¿No tienes cuenta? <a href="/registro">Registrar Operador</a></div>
        {% else %}
        <form method="POST" action="/registro">
            <input type="text" name="usuario" placeholder="NUEVO ID OPERADOR" required>
            <input type="password" name="password" placeholder="CREAR CÓDIGO" required>
            <button type="submit">CREAR CUENTA</button>
        </form>
        <div class="toggle-link">¿Ya tienes cuenta? <a href="/login">Volver al Login</a></div>
        {% endif %}

        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        {% if success %}<div class="success">{{ success }}</div>{% endif %}
    </div>
</body>
</html>
"""

# --- RUTAS DE AUTENTICACIÓN (REGISTRO Y LOGIN) ---

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        user = request.form.get('usuario').strip()
        pwd = request.form.get('password').strip()

        if user in usuarios_db:
            return render_template_string(HTML_AUTH, modo='registro', error="El ID de operador ya existe.")
        
        # Crear nuevo usuario en la DB
        usuarios_db[user] = {
            "password": pwd,
            "datos": inicializar_datos_usuario(user)
        }
        guardar_db(usuarios_db)
        return render_template_string(HTML_AUTH, modo='login', success="Cuenta creada. Ya puedes iniciar sesión.")
    
    return render_template_string(HTML_AUTH, modo='registro')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('usuario').strip()
        pwd = request.form.get('password').strip()

        if user in usuarios_db and usuarios_db[user]['password'] == pwd:
            session['user'] = user
            return redirect(url_for('home'))
        
        return render_template_string(HTML_AUTH, modo='login', error="Credenciales incorrectas.")
    
    return render_template_string(HTML_AUTH, modo='login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- EL RESTO DEL CÓDIGO (HOME, API, ETC) SIGUE IGUAL ---
# (Asegúrate de mantener las rutas de /get_data y /reportar_progreso que ya tenías)
