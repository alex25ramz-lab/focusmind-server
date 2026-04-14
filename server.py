from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Base de datos simplificada
datos_compartidos = {
    "tarea": "Esperando...",
    "tiempo": "25"
}

@app.route('/')
def index():
    return "Servidor FocusMind Operativo"

@app.route('/actualizar', methods=['POST'])
def actualizar():
    # Guardamos con nombres simples: 'tarea' y 'tiempo'
    datos_compartidos["tarea"] = request.form.get("ultima_tarea")
    datos_compartidos["tiempo"] = request.form.get("tiempo_meta")
    return 'OK'

@app.route('/get_data')
def get_data():
    return jsonify(datos_compartidos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
