from flask import Flask, request, jsonify
import json
import os
import requests # Necesario para las notificaciones al celular

app = Flask(__name__)
DATA_FILE = "servidor_datos.json"

# --- CONFIGURACIÓN DE NOTIFICACIONES ---
# Cambia 'mi_canal_focusmind_alex' por un nombre único para que solo te lleguen a ti
NTFY_TOPIC = "focusmind_notificaciones_ingenieria" 

def enviar_notificacion(titulo, mensaje):
    """Envía una alerta push directamente a tu celular usando ntfy.sh"""
    try:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=mensaje.encode('utf-8'),
                      headers={"Title": titulo, "Priority": "high"})
    except:
        print("⚠️ No se pudo enviar la notificación push.")

# --- LÓGICA DE DATOS ---
def cargar_db():
    if not os.path.exists(DATA_FILE): return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

def guardar_db(datos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

# --- RUTAS API ---
@app.route('/tareas', methods=['GET'])
def listar(): return jsonify(cargar_db())

@app.route('/agregar', methods=['POST'])
def agregar():
    tarea = request.json
    db = cargar_db()
    db.append(tarea)
    guardar_db(db)
    # Enviamos notificación al celular cuando se agrega algo desde la PC
    enviar_notificacion("🚀 Nueva Tarea", f"Se agregó: {tarea['titulo']}")
    return jsonify({"status": "ok"})

@app.route('/completar', methods=['POST'])
def completar():
    tid = request.json.get("id")
    db = cargar_db()
    for t in db:
        if str(t['id']) == str(tid):
            t['completada'] = True
            enviar_notificacion("✅ Tarea Lista", f"Terminaste: {t['titulo']}")
            break
    guardar_db(db)
    return jsonify({"status": "ok"})

# --- INTERFAZ MÓVIL GRÁFICA (DASHBOARD) ---
@app.route('/movil')
def dashboard():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FocusMind Cloud</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { background: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', sans-serif; }
            .glass-card { background: #161b22; border: 1px solid #30363d; border-radius: 15px; padding: 20px; margin-bottom: 20px; }
            .btn-primary { background: #238636; border: none; font-weight: bold; width: 100%; padding: 12px; }
            .chart-container { position: relative; height: 180px; margin: 0 auto; }
            .task-item { border-left: 4px solid #58a6ff; background: #0d1117; margin-bottom: 10px; padding: 10px; border-radius: 5px; }
            .done { border-left-color: #238636; opacity: 0.6; }
        </style>
    </head>
    <body>
        <div class="container py-4">
            <h5 class="text-center mb-4">📊 DASHBOARD DE INGENIERÍA</h5>
            
            <div class="glass-card text-center">
                <h6>Progreso de Hoy</h6>
                <div class="chart-container">
                    <canvas id="myChart"></canvas>
                </div>
            </div>

            <div class="glass-card">
                <input type="text" id="t" class="form-control mb-2 bg-dark text-white border-secondary" placeholder="Nueva tarea...">
                <input type="text" id="m" class="form-control mb-3 bg-dark text-white border-secondary" placeholder="Tiempo (ej: 20 min)">
                <button class="btn btn-primary" onclick="mandar()">MANDAR A LA PC</button>
            </div>

            <div id="lista"></div>
        </div>

        <script>
            let myChart;
            async function refresh() {
                const r = await fetch('/tareas');
                const data = await r.json();
                
                const completas = data.filter(t => t.completada).length;
                const total = data.length;

                // Actualizar Gráfica
                const ctx = document.getElementById('myChart').getContext('2d');
                if(myChart) myChart.destroy();
                myChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        datasets: [{ data: [completas, total-completas || 1], backgroundColor: ['#238636', '#30363d'], borderWidth: 0 }]
                    },
                    options: { cutout: '80%', plugins: { legend: { display: false } } }
                });

                // Actualizar Lista
                document.getElementById('lista').innerHTML = data.reverse().map(t => `
                    <div class="task-item ${t.completada?'done':''}">
                        <div class="d-flex justify-content-between">
                            <strong>${t.titulo}</strong>
                            <span class="badge ${t.completada?'bg-success':'bg-primary'}">${t.deadline}</span>
                        </div>
                    </div>
                `).join('');
            }

            async function mandar() {
                const t = document.getElementById('t').value;
                const m = document.getElementById('m').value;
                if(!t) return;
                await fetch('/agregar', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({id: Date.now(), titulo: t, deadline: m||'--', completada: false})
                });
                document.getElementById('t').value = '';
                document.getElementById('m').value = '';
                refresh();
            }
            setInterval(refresh, 5000);
            refresh();
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("🚀 Servidor FocusMind con Gráficas y Notificaciones Activo")
    app.run(host='0.0.0.0', port=5000)