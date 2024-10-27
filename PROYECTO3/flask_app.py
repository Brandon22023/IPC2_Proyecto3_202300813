import re
from flask import Flask, request, jsonify, session
import os
import json
import traceback
import xml.etree.ElementTree as ET
app = Flask(__name__)
UPLOAD_FOLDER = './uploads'  # Carpeta donde se guardarán los archivos
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'  # Necesario para usar sesiones
archivo_cargado=False
@app.route('/cargar_archivo', methods=['POST'])
def cargar_archivo():
    global archivo_cargado

    try:
        # Si ya se cargó un archivo, retorna un mensaje
        if archivo_cargado:
            archivo_cargado = False
            print("el archivo_cargado es:", archivo_cargado)
            ruta_archivo_json = os.path.join(UPLOAD_FOLDER, 'archivo_info.json')
            # Verifica si el archivo JSON existe y lee su contenido
            if os.path.exists(ruta_archivo_json):
                with open(ruta_archivo_json, 'r', encoding='utf-8') as json_file:
                    contenido_json = json.load(json_file)  # Cargar el contenido del JSON
                print("Contenido del archivo JSON:", contenido_json)  # Log para verificar el contenido
                return jsonify({'mensaje': 'Ya se ha cargado un archivo previamente.', 'contenido_json': contenido_json}), 200
            else:
                return jsonify({'error': 'El archivo JSON no existe'}), 404
            
        else:
            print("Paso 1: Iniciando carga de archivo")
            
            # Intenta acceder al archivo
            archivo_global = request.files.get('archivo')

            if archivo_global is None:
                return jsonify({'error': 'No se ha enviado ningún archivo'}), 400

            if archivo_global.filename == '':
                return jsonify({'error': 'No se ha seleccionado ningún archivo'}), 400

            if not archivo_global.filename.endswith('.xml'):
                return jsonify({'error': 'El archivo debe ser un archivo XML'}), 400

            ruta_archivo_xml = os.path.join(UPLOAD_FOLDER, 'entrada_mandado_flask.xml')
            
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)

            archivo_global.save(ruta_archivo_xml)
            session['archivo_cargado'] = True  # Marcar que el archivo ha sido cargado
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
            #archivo_cargado = True
            print("el archiov cargado es:", archivo_cargado)
            #leer_y_mostrar_archivo()
            obtener_sentimientos()
            # Llamar directamente al método y mostrar la lista de empresas y servicios
            lista_empresas = cargar_empresas_desde_xml()
            lista_empresas.imprimir()
            # Llamar al método para analizar y mostrar mensajes
            analizar_mensajes()
            # Devolver el contenido JSON en la respuesta
            return jsonify(contenido_json), 200
            
            

    except Exception as e:
        print("Error inesperado:", e)
        print(traceback.format_exc())  # Imprime el traceback del error
        return jsonify({'error': str(e)}), 500

def leer_y_mostrar_archivo():
    try:
        # Define la ruta del archivo XML
        ruta_archivo_xml = os.path.join(UPLOAD_FOLDER, 'entrada_mandado_flask.xml')
        
        # Verifica si el archivo existe
        if not os.path.exists(ruta_archivo_xml):
            print("El archivo XML no existe en la ruta especificada.")
            return
        
        # Lee el contenido del archivo XML
        with open(ruta_archivo_xml, 'r', encoding='utf-8') as file:
            contenido_xml = file.read()
        
        # Imprime el contenido en la consola
        print("Contenido del archivo XML:")
        print(contenido_xml)
        
    except Exception as e:
        print("Error al leer el archivo:", e)
# Método para obtener sentimientos positivos y negativos
def obtener_sentimientos():
    ruta_archivo_xml = './uploads/entrada_mandado_flask.xml'
    
    # Verifica si el archivo XML existe
    if not os.path.exists(ruta_archivo_xml):
        print("El archivo XML no existe en la ruta especificada.")
        return [], []

    try:
        # Cargar y parsear el archivo XML
        tree = ET.parse(ruta_archivo_xml)
        root = tree.getroot()

        # Inicializar listas para los sentimientos
        sentimientos_positivos = []
        sentimientos_negativos = []

        # Encontrar el diccionario en el XML
        diccionario = root.find('diccionario')
        if diccionario is not None:
            # Extraer sentimientos positivos
            positivos = diccionario.find('sentimientos_positivos')
            if positivos is not None:
                for palabra in positivos.findall('palabra'):
                    sentimientos_positivos.append(palabra.text.strip())

            # Extraer sentimientos negativos
            negativos = diccionario.find('sentimientos_negativos')
            if negativos is not None:
                for palabra in negativos.findall('palabra'):
                    sentimientos_negativos.append(palabra.text.strip())

        return sentimientos_positivos, sentimientos_negativos

    except ET.ParseError as e:
        print("Error al parsear el archivo XML:", e)
        return [], []
    except Exception as e:
        print("Error inesperado:", e)
        return [], []
    
# Método para analizar mensajes y contar sentimientos
def analizar_mensajes():
    # Cargar sentimientos desde el archivo XML
    sentimientos_positivos, sentimientos_negativos = obtener_sentimientos()
    
    ruta_archivo_xml = './uploads/entrada_mandado_flask.xml'
    
    if not os.path.exists(ruta_archivo_xml):
        print("El archivo XML no existe en la ruta especificada.")
        return

    try:
        tree = ET.parse(ruta_archivo_xml)
        root = tree.getroot()
        
        # Diccionario para almacenar mensajes clasificados por fecha
        mensajes_por_fecha = {}
        
        # Contadores para total de mensajes positivos, negativos y neutros
        total_positivos = 0
        total_negativos = 0
        total_neutros = 0

        # Contadores para el total absoluto de sentimientos
        total_sentimientos_positivos = 0
        total_sentimientos_negativos = 0
        total_sentimientos_neutros = 0

        # Procesa cada mensaje en la lista de mensajes
        lista_mensajes = root.find('lista_mensajes')
        if lista_mensajes is not None:
            for mensaje_element in lista_mensajes.findall('mensaje'):
                mensaje_texto = mensaje_element.text.strip()
                
                # Extraer la fecha y el lugar usando una expresión regular
                fecha_lugar_match = re.search(r"Lugar y fecha:\s*([^,]+),\s*(\d{2}/\d{2}/\d{4})", mensaje_texto)
                if fecha_lugar_match:
                    lugar = fecha_lugar_match.group(1)
                    fecha = fecha_lugar_match.group(2)
                else:
                    lugar, fecha = "Desconocido", "Fecha desconocida"

                # Contar sentimientos en el mensaje
                positivos_count = sum(1 for palabra in sentimientos_positivos if re.search(r'\b' + re.escape(palabra) + r'\b', mensaje_texto, re.IGNORECASE))
                negativos_count = sum(1 for palabra in sentimientos_negativos if re.search(r'\b' + re.escape(palabra) + r'\b', mensaje_texto, re.IGNORECASE))

                # Clasificar el mensaje como positivo, negativo o neutro
                if positivos_count > negativos_count:
                    total_positivos += 1
                elif negativos_count > positivos_count:
                    total_negativos += 1
                else:
                    total_neutros += 1
                    total_sentimientos_neutros += 1  # Contador de mensajes neutros totales

                # Actualizar los totales absolutos de sentimientos
                total_sentimientos_positivos += positivos_count
                total_sentimientos_negativos += negativos_count

                # Organizar el mensaje por fecha en el diccionario
                if fecha not in mensajes_por_fecha:
                    mensajes_por_fecha[fecha] = []
                
                mensajes_por_fecha[fecha].append({
                    "lugar": lugar,
                    "mensaje": mensaje_texto,
                    "positivos_count": positivos_count,
                    "negativos_count": negativos_count
                })
        
        # Imprimir los resultados
        for fecha, mensajes in mensajes_por_fecha.items():
            print(f"\nFecha: {fecha}")
            for mensaje in mensajes:
                print(f"Lugar: {mensaje['lugar']}")
                print(f"Mensaje: {mensaje['mensaje']}")
                print(f"Sentimientos positivos en el mensaje: {mensaje['positivos_count']}")
                print(f"Sentimientos negativos en el mensaje: {mensaje['negativos_count']}")

        # Imprimir totales de mensajes y total absoluto de sentimientos
        print(f"\nTotal de mensajes positivos: {total_positivos}")
        print(f"Total de mensajes negativos: {total_negativos}")
        print(f"Total de mensajes neutros: {total_neutros}")
        print(f"Total absoluto de sentimientos positivos encontrados: {total_sentimientos_positivos}")
        print(f"Total absoluto de sentimientos negativos encontrados: {total_sentimientos_negativos}")
        print(f"Total absoluto de mensajes neutros: {total_sentimientos_neutros}")

    except ET.ParseError as e:
        print("Error al parsear el archivo XML:", e)
    except Exception as e:
        print("Error inesperado:", e)





    
# Nodo para los servicios de una empresa (con lista de alias)
class Servicio:
    def __init__(self, nombre):
        self.nombre = nombre
        self.aliases = []  # Lista de alias para el servicio
        self.next = None   # Apunta al siguiente servicio en la lista circular

    def agregar_alias(self, alias):
        self.aliases.append(alias)


# Nodo para cada empresa (con una lista circular de servicios)
class Empresa:
    def __init__(self, nombre):
        self.nombre = nombre
        self.servicios = None  # Lista circular de servicios
        self.next = None       # Apunta a la siguiente empresa en la lista circular

    def agregar_servicio(self, servicio):
        if self.servicios is None:
            self.servicios = servicio
            servicio.next = servicio  # Enlaza a sí mismo, formando la circularidad
        else:
            # Inserta el servicio al final de la lista circular de servicios
            ultimo_servicio = self.servicios
            while ultimo_servicio.next != self.servicios:
                ultimo_servicio = ultimo_servicio.next
            ultimo_servicio.next = servicio
            servicio.next = self.servicios


# Lista circular de empresas
class ListaCircular:
    def __init__(self):
        self.primero = None

    def agregar_empresa(self, empresa):
        if self.primero is None:
            self.primero = empresa
            empresa.next = empresa  # Enlaza a sí misma, formando la circularidad
        else:
            # Inserta la empresa al final de la lista circular de empresas
            ultima_empresa = self.primero
            while ultima_empresa.next != self.primero:
                ultima_empresa = ultima_empresa.next
            ultima_empresa.next = empresa
            empresa.next = self.primero

    def imprimir(self):
        if self.primero is None:
            print("La lista de empresas está vacía.")
            return
        actual = self.primero
        while True:
            print(f"Empresa: {actual.nombre}")
            servicio_actual = actual.servicios
            if servicio_actual:
                while True:
                    print(f"  Servicio: {servicio_actual.nombre}")
                    print(f"    Alias: {', '.join(servicio_actual.aliases)}")
                    servicio_actual = servicio_actual.next
                    if servicio_actual == actual.servicios:
                        break
            actual = actual.next
            if actual == self.primero:
                break


# Función para cargar empresas y servicios desde el XML (sin parámetros)
def cargar_empresas_desde_xml():
    # Define la ruta del archivo XML
    UPLOAD_FOLDER = './uploads'  # Asegúrate de definir la ruta donde se almacena el archivo
    ruta_archivo_xml = os.path.join(UPLOAD_FOLDER, 'entrada_mandado_flask.xml')
    
    # Cargar el archivo XML y parsear
    tree = ET.parse(ruta_archivo_xml)
    root = tree.getroot()

    lista_empresas = ListaCircular()
    
    # Navega hasta la sección de empresas en el XML
    empresas_element = root.find('diccionario/empresas_analizar')
    if empresas_element is not None:
        for empresa_element in empresas_element.findall('empresa'):
            nombre_empresa = empresa_element.find('nombre').text
            empresa = Empresa(nombre_empresa)
            
            # Procesa los servicios de la empresa
            for servicio_element in empresa_element.findall('servicio'):
                nombre_servicio = servicio_element.get('nombre')
                servicio = Servicio(nombre_servicio)
                
                # Agrega los alias al servicio
                for alias_element in servicio_element.findall('alias'):
                    alias_texto = alias_element.text.strip()
                    servicio.agregar_alias(alias_texto)
                
                # Agrega el servicio a la empresa
                empresa.agregar_servicio(servicio)
            
            # Agrega la empresa a la lista circular de empresas
            lista_empresas.agregar_empresa(empresa)

    return lista_empresas

    
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