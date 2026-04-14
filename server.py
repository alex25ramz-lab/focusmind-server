html_template = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>FocusMind Hub</title>
    <style>
        :root {
            --bg: #0d1117;
            --card: #161b22;
            --accent: #58a6ff;
            --text: #c9d1d9;
            --success: #238636;
        }

        body {
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px;
            box-sizing: border-box;
        }

        .container {
            width: 100%;
            max-width: 400px;
            background: var(--card);
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            border: 1px solid #30363d;
            text-align: center;
        }

        h1 {
            color: var(--accent);
            font-size: 1.8rem;
            margin-bottom: 5px;
            letter-spacing: 1px;
        }

        p {
            font-size: 0.9rem;
            opacity: 0.7;
            margin-bottom: 25px;
        }

        input[type="text"], input[type="number"] {
            width: 100%;
            padding: 15px;
            margin-bottom: 15px;
            background: var(--bg);
            border: 1px solid #30363d;
            border-radius: 10px;
            color: white;
            font-size: 1rem;
            box-sizing: border-box;
            outline: none;
            transition: border 0.3s;
        }

        input:focus {
            border-color: var(--accent);
        }

        button {
            width: 100%;
            padding: 18px;
            background-color: var(--success);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.1s, background 0.3s;
            box-shadow: 0 4px 15px rgba(35, 134, 54, 0.3);
        }

        button:active {
            transform: scale(0.97);
            background-color: #2ea043;
        }

        .status {
            margin-top: 20px;
            padding: 10px;
            border-radius: 8px;
            font-size: 0.85rem;
            background: rgba(88, 166, 255, 0.1);
            color: var(--accent);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>FOCUSMIND</h1>
        <p>Remote Command Center</p>
        
        <form action="/actualizar" method="post">
            <input type="text" name="ultima_tarea" placeholder="¿En qué vamos a trabajar?" required>
            <input type="number" name="tiempo_meta" placeholder="Tiempo (minutos)" value="25">
            <button type="submit">ENVIAR A LA LAPTOP</button>
        </form>

        <div class="status">
            Conectado al servidor de Render v3.0
        </div>
    </div>
</body>
</html>
'''
