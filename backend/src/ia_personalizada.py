from flask import Flask, request, jsonify
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import speech_recognition as sr
import os

# Inicializar el servidor Flask
app = Flask(__name__)

# Cargar el modelo y el tokenizador de GPT-2
model_name = 'gpt2'
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

# Inicializar el reconocimiento de voz
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Función para generar una respuesta a partir del mensaje del usuario
def generar_respuesta(mensaje_usuario):
    inputs = tokenizer.encode(mensaje_usuario, return_tensors='pt')
    outputs = model.generate(inputs, max_length=100, num_return_sequences=1)
    respuesta = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return respuesta

# Ruta para la raíz del servidor
@app.route('/')
def home():
    return jsonify({"message": "Bienvenido a PersonaAI"})

# Ruta para interactuar con la IA por texto
@app.route('/interactuar', methods=['POST'])
def interactuar():
    datos = request.json
    mensaje_usuario = datos.get('mensaje', '')
    
    if not mensaje_usuario:
        return jsonify({'error': 'No se proporcionó ningún mensaje.'}), 400
    
    respuesta = generar_respuesta(mensaje_usuario)
    return jsonify({'respuesta': respuesta})

# Ruta para interactuar con la IA por voz
@app.route('/interactuar_voz', methods=['GET'])
def interactuar_voz():
    with microphone as source:
        print("Calibrando el micrófono...")
        recognizer.adjust_for_ambient_noise(source)
        print("Di algo...")
        audio = recognizer.listen(source)
    
    try:
        mensaje_usuario = recognizer.recognize_google(audio, language="es-ES")
        print(f"Has dicho: {mensaje_usuario}")
    except sr.UnknownValueError:
        return jsonify({'error': 'No se pudo entender el audio'}), 400
    except sr.RequestError as e:
        return jsonify({'error': f'Error del servicio de reconocimiento de voz; {e}'}), 500
    
    respuesta = generar_respuesta(mensaje_usuario)
    return jsonify({'mensaje': mensaje_usuario, 'respuesta': respuesta})

# Ruta para configurar recordatorios
recordatorios = {}

@app.route('/configurar_recordatorio', methods=['POST'])
def configurar_recordatorio():
    datos = request.json
    usuario = datos.get('usuario', '')
    mensaje = datos.get('mensaje', '')
    fecha_hora = datos.get('fecha_hora', '')
    
    if not usuario or not mensaje or not fecha_hora:
        return jsonify({'error': 'Faltan datos.'}), 400
    
    if usuario not in recordatorios:
        recordatorios[usuario] = []
    
    recordatorios[usuario].append({
        'mensaje': mensaje,
        'fecha_hora': fecha_hora
    })
    
    return jsonify({'mensaje': 'Recordatorio configurado correctamente.'})

# Ruta para obtener recordatorios
@app.route('/obtener_recordatorios', methods=['GET'])
def obtener_recordatorios():
    usuario = request.args.get('usuario', '')
    
    if not usuario:
        return jsonify({'error': 'No se proporcionó ningún usuario.'}), 400
    
    if usuario not in recordatorios:
        return jsonify({'recordatorios': []})
    
    return jsonify({'recordatorios': recordatorios[usuario]})

# Iniciar el servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)

