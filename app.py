from flask import Flask, request, render_template, url_for
from deepface import DeepFace
import os
from werkzeug.utils import secure_filename
import time

app = Flask(__name__)

# Configuración para subir archivos
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Crear el directorio de uploads si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    name, ext = os.path.splitext(filename)
    return f"{name}_{int(time.time())}{ext}"

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    result = None
    similarity = None
    image_paths = {'file1': None, 'file2': None}
    
    if request.method == 'POST':
        if 'file1' not in request.files or 'file2' not in request.files:
            return 'No se han subido los archivos'
        
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        if file1.filename == '' or file2.filename == '':
            return 'No se han seleccionado archivos'
        
        if file1 and allowed_file(file1.filename) and file2 and allowed_file(file2.filename):
            filename1 = generate_unique_filename(secure_filename(file1.filename))
            filename2 = generate_unique_filename(secure_filename(file2.filename))
            
            filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
            filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], filename2)
            
            file1.save(filepath1)
            file2.save(filepath2)
            
            image_paths['file1'] = filename1
            image_paths['file2'] = filename2
            
            try:
                # Realizar la verificación con DeepFace
                verification = DeepFace.verify(filepath1, filepath2)
                result = verification['verified']
                # Calcular el porcentaje de similitud (convertir la distancia a similitud)
                distance = verification['distance']
                # Convertir la distancia a un porcentaje de similitud (0 es perfecta similitud)
                similarity = max(0, min(100, (1 - distance) * 100))
            except Exception as e:
                result = f"Error en la verificación: {str(e)}"
            
    return render_template('upload.html', result=result, image_paths=image_paths, similarity=similarity)

if __name__ == '__main__':
    app.run(debug=True)
