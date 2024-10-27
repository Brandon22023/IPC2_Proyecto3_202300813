from flask import Flask, request, jsonify
import os
import json
app = Flask(__name__)
UPLOAD_FOLDER = './uploads'  # Carpeta donde se guardarán los archivos
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/cargar_archivo', methods=['POST'])
def cargar_archivo():
    try:
        print("Paso 1: Iniciando carga de archivo")

        # Verificar que el archivo esté en la solicitud y se pueda leer
        if 'archivo' not in request.files:
            print("Error: No se encontró el archivo en la solicitud")
            return jsonify({'error': 'No se encontró archivo en la solicitud'}), 400

        # Guardar el archivo XML
        archivo = request.files['archivo']
        print("Paso 2: Archivo recibido en la solicitud:", archivo)

        ruta_archivo_xml = os.path.join(UPLOAD_FOLDER, 'entrada_mandado_flask.xml')
        archivo.save(ruta_archivo_xml)
        print("Paso 3: Archivo guardado en la ruta:", ruta_archivo_xml)

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
        print("Paso 5: Preparación del contenido JSON completada")

        # Guardar el archivo JSON
        with open(ruta_archivo_json, 'w', encoding='utf-8') as json_file:
            json.dump(contenido_json, json_file, ensure_ascii=False, indent=4)
        print("Paso 6: Archivo JSON guardado en la ruta:", ruta_archivo_json)

        # Verificar si el archivo JSON fue creado exitosamente
        if not os.path.exists(ruta_archivo_json):
            print("Error: El archivo JSON no fue creado")
            return jsonify({'error': 'Hubo un problema al crear el archivo JSON'}), 500
        print("Paso 7: Verificación del archivo JSON completada")

        # Retornar el contenido JSON como respuesta si se creó correctamente
        print("Paso 8: Retornando el contenido JSON como respuesta")
        return jsonify(contenido_json), 200

    except Exception as e:
        # Imprimir el error exacto para rastrear dónde ocurre
        print("Error inesperado al procesar el archivo:", str(e))
        return jsonify({'error': f"Error inesperado: {str(e)}"}), 500
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