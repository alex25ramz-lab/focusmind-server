from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Almacén temporal de la tarea
datos_tarea = {"tarea": "", "mins": "25"}

HTML_BASE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FocusMind Server</title>
    <style>
        body {
            background-color: #000;
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }

        /* Contenedor Principal con borde Neón */
        .card-principal {
            background-color: #0a0a0a;
            border: 2px solid #00ffff;
            border-radius: 25px;
            padding: 40px;
            width: 85%;
            max-width: 400px;
            text-align: center;
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
        }

        h1 {
            color: #00ffff;
            font-size: 32px;
            letter-spacing: 5px;
            margin-bottom: 30px;
            text-transform: uppercase;
            text-shadow: 0 0 10px #00ffff;
        }

        /* Inputs Estilizados */
        input {
            width: 100%;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 10px;
            border: 2px solid transparent;
            background-color: #fff;
            color: #000;
            font-size: 16px;
            box-sizing: border-box;
            transition: all 0.3s ease;
        }

        input:focus {
            outline: none;
            border: 2px solid #00ffff;
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.5);
        }

        /* BOTÓN ESTILO ROCKSTAR CON GLOW */
        .btn-sincronizar {
            width: 100%;
            padding: 18px;
            background-color: #00ffff;
            color: #000;
            border: 2px solid #fff;
            border-radius: 12px;
            font-size: 18px;
            font-weight: bold;
            text-transform: uppercase;
            cursor: pointer;
            transition: all 0.3s ease;
            /* Efecto de Brillo */
            box-shadow: 0 0 15px #00ffff, 0 0 30px rgba(0, 255, 255, 0.5);
        }

        /* Efecto 3D al presionar en el celular */
        .btn-sincronizar:active {
            transform: scale(0.96);
            box-shadow: 0 0 5px #00ffff;
            background-color: #33ffff;
        }

        .status {
            margin-top: 20px;
            font-size: 12px;
            color: #555;
        }
    </style>
</head>
<body>
    <div class="card-principal">
        <h1>FOCUSMIND</h1>
        
        <form action="/enviar" method="POST">
            <input type="text" name="tarea" placeholder="¿Qué tarea harás?" required>
            <input type="number" name="mins" placeholder="Minutos" value="25">
            
            <button type="submit" class="btn-sincronizar">
                SINCRONIZAR
            </button>
        </form>

        <div class="status">SISTEMA MECATRÓNICO ACTIVO v3.0</div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_BASE)

@app.route('/enviar', methods=['POST'])
def enviar():
    global datos_tarea
    datos_tarea["tarea"] = request.form.get("tarea")
    datos_tarea["mins"] = request.form.get("mins")
    return render_template_string(HTML_BASE + "<script>alert('Sincronizado con la Laptop');</script>")

@app.route('/get_tarea', methods=['GET'])
def get_tarea():
    return jsonify(datos_tarea)

if __name__ == '__main__':
    app.run(debug=True)
