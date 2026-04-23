from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from datetime import datetime
import os
import random
import json

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "lumina_ultra_secret_8891")

# --- CONFIGURACIÓN ---
DB_FILE = "database.json"
API_KEY = "LUMINA_SECURE_TOKEN_2026" # Puedes usar esto para validar peticiones de la laptop

def cargar_db():
    if not os.path.exists(DB_FILE):
        return {
            "operador1": {"password": "123", "datos": inicializar_datos("Operador 1")},
            "compa": {"password": "456", "datos": inicializar_datos("Compa")}
        }
    with open(DB_FILE, "r") as f:
        return json.load(f)

def guardar_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

def inicializar_datos(nombre):
    return {
        "tarea_actual": "Esperando mando...",
        "tiempo_actual": 0,
        "id_envio": 0,
        "historial": [],
        "rendimiento": {"exitos": 0, "retrasos": 0, "total": 0},
        "ultimo_msj": f"Sistema LUMINA vinculado a {nombre}."
    }

usuarios_db = cargar_db()

FRASES_LUMINA = [
    "Objetivo detectado. Optimizando frecuencia de enfoque.",
    "Lumina en línea. Iniciando secuencia de productividad.",
    "Sistemas listos. La disciplina es el puente al éxito.",
    "Procesando nueva meta. Ejecución prioritaria activada.",
    "Enfoque de ingeniería establecido. Adelante."
]

# --- HTML (Mantenemos tu estilo pero optimizado) ---
# ... (Aquí irían tus constantes HTML_LOGIN y HTML_PANEL que ya tienes)

# --- DECORADOR DE SEGURIDAD ---
def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# --- RUTAS DE SESIÓN ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('usuario')
        pwd = request.form.get('password')
        if user in usuarios_db and usuarios_db[user]['password'] == pwd:
            session['user'] = user
            return redirect(url_for('home'))
        return render_template_string(HTML_LOGIN, error="Acceso denegado: Credenciales inválidas")
    return render_template_string(HTML_LOGIN)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- RUTAS DE LA INTERFAZ WEB ---

@app.route('/')
@login_required
def home():
    db = usuarios_db[session['user']]['datos']
    return render_template_string(HTML_PANEL, 
                                 usuario=session['user'],
                                 historial=db['historial'], 
                                 rendimiento=db['rendimiento'], 
                                 ultimo_msj=db['ultimo_msj'])

@app.route('/enviar_tarea_web', methods=['POST'])
@login_required
def enviar_tarea_web():
    user = session['user']
    db = usuarios_db[user]['datos']
    
    tarea = request.form.get('tarea')
    mins = request.form.get('mins')
    
    db['id_envio'] += 1
    db['tarea_actual'] = tarea
    db['tiempo_actual'] = mins
    db['ultimo_msj'] = random.choice(FRASES_LUMINA)
    db['historial'].append({
        "id": db['id_envio'], 
        "tarea": tarea, 
        "estado": "PENDIENTE",
        "fecha": datetime.now().strftime("%H:%M")
    })
    db['rendimiento']['total'] += 1
    
    guardar_db(usuarios_db) # Persistencia inmediata
    return redirect(url_for('home'))

# --- API PARA LA LAPTOP (LÓGICA MEJORADA) ---

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
    return jsonify({"error": "No auth"}), 401

@app.route('/reportar_progreso', methods=['POST'])
def reportar_progreso():
    data = request.json
    user = data.get('user')
    
    if user not in usuarios_db:
        return jsonify({"error": "Auth failed"}), 401
    
    db = usuarios_db[user]['datos']
    id_t = data.get('id')
    estado = data.get('estado', '').upper()
    
    for t in db['historial']:
        if t['id'] == id_t and t['estado'] == "PENDIENTE":
            t['estado'] = estado
            if "HECHO" in estado:
                db['rendimiento']['exitos'] += 1
                db['ultimo_msj'] = f"Operador {user}: Objetivo #{id_t} neutralizado con éxito."
            else:
                db['rendimiento']['retrasos'] += 1
                db['ultimo_msj'] = f"Operador {user}: Sistema en alerta por retraso en #{id_t}."
            
            guardar_db(usuarios_db)
            return jsonify({"status": "sincronizado"})
            
    return jsonify({"status": "no_change"})

if __name__ == '__main__':
    # Render usa la variable de entorno PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
