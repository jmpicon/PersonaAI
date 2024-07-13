import random
import time
from flask import Flask, jsonify

app = Flask(__name__)

# Simulación de datos de sensores
def generar_datos_sensores():
    # Generar datos de posición aleatorios
    posicion = {
        "x": random.uniform(0, 10),
        "y": random.uniform(0, 10),
        "z": random.uniform(0, 10)
    }
    return posicion

# Simulación de detección de caídas
def detectar_caida(posicion_actual, posicion_anterior):
    if posicion_anterior and (posicion_anterior["z"] - posicion_actual["z"]) > 2:
        return True
    return False

posicion_anterior = None

@app.route('/monitoreo', methods=['GET'])
def monitoreo():
    global posicion_anterior
    posicion_actual = generar_datos_sensores()
    caida = detectar_caida(posicion_actual, posicion_anterior)
    posicion_anterior = posicion_actual

    return jsonify({
        "posicion": posicion_actual,
        "caida": caida
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002)
