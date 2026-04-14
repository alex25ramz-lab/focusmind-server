html_template = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>FocusMind Ultimate</title>
    <style>
        :root {
            --bg: #05070a;
            --glass: rgba(255, 255, 255, 0.03);
            --border: rgba(255, 255, 255, 0.1);
            --accent: #00d2ff;
            --accent-2: #3a7bd5;
            --success: #00ff88;
        }

        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: radial-gradient(circle at top, #1a2a44 0%, #05070a 100%);
            color: #ffffff;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            overflow: hidden;
        }

        .glass-card {
            background: var(--glass);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--border);
            border-radius: 32px;
            padding: 40px 25px;
            width: 85%;
            max-width: 360px;
            text-align: center;
            box-shadow: 0 25px 50px rgba(0,0,0,0.5);
        }

        .logo-area {
            margin-bottom: 30px;
        }

        h1 {
            font-size: 1.5rem;
            font-weight: 800;
            letter-spacing: 4px;
            text-transform: uppercase;
            background: linear-gradient(to right, var(--accent), var(--accent-2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
        }

        .input-group {
            margin-bottom: 20px;
            text-align: left;
        }

        label {
            font-size: 0.75rem;
            color: var(--accent);
            margin-left: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: bold;
        }

        input {
            width: 100%;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 15px;
            color: white;
            font-size: 1rem;
            margin-top: 8px;
            box-sizing: border-box;
            outline: none;
            transition: 0.3s;
        }

        input:focus {
            border-color: var(--accent);
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.2);
        }

        button {
            width: 100%;
            background: linear-gradient(45deg, var(--accent-2), var(--accent));
            border: none;
            padding: 18px;
            border-radius: 18px;
            color: white;
            font-weight: 800;
            font-size: 1rem;
            cursor: pointer;
            margin-top: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: 0.3s;
            box-shadow: 0 10px 20px rgba(0, 210, 255, 0.3);
        }

        button:active {
            transform: scale(0.95);
            filter: brightness(1.2);
        }

        .status-badge {
            margin-top: 30px;
            font-size: 0.7rem;
            color: var(--success);
            background: rgba(0, 255, 136, 0.1);
            padding: 8px 16px;
            border-radius: 100px;
            display: inline-block;
            border: 1px solid rgba(0, 255, 136, 0.2);
            text-transform: uppercase;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="glass-card">
        <div class="logo-area">
            <h1>FOCUSMIND</h1>
            <p style="font-size: 0.8rem; opacity: 0.5;">Remote Interface V4.0</p>
        </div>

        <form action="/actualizar" method="post">
            <div class="input-group">
                <label>Misión / Tarea</label>
                <input type="text" name="ultima_tarea" placeholder="Ej: Estudiar Dinámica" required>
            </div>
            
            <div class="input-group">
                <label>Cronómetro (MIN)</label>
                <input type="number" name="tiempo_meta" value="25">
            </div>

            <button type="submit">DESPLEGAR COMANDO</button>
        </form>

        <div class="status-badge">
            ● SISTEMA EN LÍNEA
        </div>
    </div>
</body>
</html>
'''
