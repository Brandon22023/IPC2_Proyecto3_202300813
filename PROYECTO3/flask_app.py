from flask import Flask, request, jsonify
import os
import json
import traceback
app = Flask(__name__)
UPLOAD_FOLDER = './uploads'  # Carpeta donde se guardarán los archivos
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

archivo_cargado = False  # Variable para rastrear si el archivo ya fue cargado

@app.route('/cargar_archivo', methods=['POST'])
def cargar_archivo():
    global archivo_cargado  # Utiliza la variable global

    try:
        if archivo_cargado:  # Si ya se cargó un archivo, retorna un mensaje
            return jsonify({'mensaje': 'Ya se ha cargado un archivo previamente.'}), 200
        else:
            print("Paso 1: Iniciando carga de archivo")
            
            # Intenta acceder al archivo
            archivo_global = request.files.get('archivo')

            if archivo_global is None:
                return jsonify({'error': 'No se ha enviado ningún archivo'}), 200

            if archivo_global.filename == '':
                return jsonify({'error': 'No se ha seleccionado ningún archivo'}), 200

            if not archivo_global.filename.endswith('.xml'):
                return jsonify({'error': 'El archivo debe ser un archivo XML'}), 200

            ruta_archivo_xml = os.path.join(UPLOAD_FOLDER, 'entrada_mandado_flask.xml')
            
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)

            archivo_global.save(ruta_archivo_xml)
            archivo_cargado = True  # Marcar que el archivo ha sido cargado
            print(f"Paso 3: Archivo guardado en la ruta: {ruta_archivo_xml}")

            # Leer el contenido del archivo XML guardado
            with open(ruta_archivo_xml, 'r', encoding='utf-8') as file:
                contenido_xml = file.read()
            print("Paso 4: Contenido del archivo XML leído")

            # Crear el contenido JSON y definir la ruta para el archivo JSON
            contenido_json = {
                'mensaje': 'Archivo cargado con éxito',
                'contenido_xml': contenido_xml,
                'ruta_archivo': os.path.abspath(ruta_archivo_xml)
            }
            
            ruta_archivo_json = os.path.join(UPLOAD_FOLDER, 'archivo_info.json')
            
            # Guardar el archivo JSON
            with open(ruta_archivo_json, 'w', encoding='utf-8') as json_file:
                json.dump(contenido_json, json_file, ensure_ascii=False, indent=4)
            print(f"Paso 6: Archivo JSON guardado en la ruta: {ruta_archivo_json}")

            # Verificar la existencia del archivo JSON
            if not os.path.exists(ruta_archivo_json):
                return jsonify({'error': 'Hubo un problema al crear el archivo JSON'}), 500

            print("Paso 7: Verificación del archivo JSON completada")
            
            # Devolver el contenido JSON en la respuesta
            return jsonify(contenido_json), 200

    except Exception as e:
        print("Error inesperado:", e)
        print(traceback.format_exc())  # Imprime el traceback del error
        return jsonify({'error': str(e)}), 500
    
@app.route('/modelo', methods=['POST'])
def modelo():
    print("Recibiendo solicitud...")  
    print("Datos recibidos:", request.data)  
    
    try:
        if not request.data:
            print("Error: El cuerpo de la solicitud está vacío.")  # Mensaje más claro
            return jsonify({'error': 'El cuerpo de la solicitud está vacío.'}), 400
        
        modelo = request.json.get('modelo')
        print("Modelo recibido:", modelo)  

        modelo_titulo = ""
        modelo_text = ""

        if modelo == 'modelo1':
            modelo_titulo = "Datos del Estudiante"
            modelo_text = "Nombre: Brandon Antonio Marroquín Pérez <br> Carnet: 202300813 <br> Carrera: Ingeniería en Ciencias y Sistemas <br> Curso: INTRODUCCIÓN A LA PROGRAMACIÓN Y COMPUTACIÓN 2 Sección N <br> CUI: 3045062060114 <br> Semestre: 4"
        elif modelo == 'modelo2':
            modelo_titulo = "Documentación"
            modelo_text = "Link de la documentacion: ------------------------------------------------------------------"
        else:
            return jsonify({'error': 'Modelo no válido'}), 400  

        return jsonify({'titulo': modelo_titulo, 'texto': modelo_text})
    except Exception as e:
        print("Error al procesar la solicitud:", e)
        return jsonify({'error': 'Error procesando la solicitud'}), 400
    

if __name__ == '__main__':
    app.run(port=5000, debug=True)