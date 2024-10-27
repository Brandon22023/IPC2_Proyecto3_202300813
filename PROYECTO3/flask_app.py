import datetime
import re
from flask import Flask, Response, request, jsonify, session
import os
import json
from collections import Counter, defaultdict
import traceback
import xml.etree.ElementTree as ET
from xml.dom import minidom
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
        # Si ya se cargó un archivo, retorna un mensaje
        # Si ya se cargó un archivo, retorna un mensaje
        if archivo_cargado:
            archivo_cargado = False
            print("El estado de archivo_cargado es:", archivo_cargado)
            
            # Ruta del archivo JSON a leer
            ruta_json_completa = os.path.join(UPLOAD_FOLDER, 'resultado_analisis.json')
            
            # Verificar si el archivo JSON existe y leer su contenido
            if os.path.exists(ruta_json_completa):
                try:
                    with open(ruta_json_completa, 'r', encoding='utf-8') as archivo_json:
                        contenido_completo_json = archivo_json.read()  # Leer el archivo completo como texto
                    
                    print("Contenido completo del archivo JSON:", contenido_completo_json)  # Log para verificación
                    
                    # Devolver el contenido del JSON como respuesta directa
                    return Response(contenido_completo_json, mimetype='application/json'), 200
                except Exception as e:
                    print(f"Error al leer el archivo JSON: {e}")
                    return jsonify({'error': 'No se pudo leer el archivo JSON.'}), 500
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
            #obtener_sentimientos()
            #cargar_empresas_desde_xml()
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

        # Imprimir las listas de sentimientos
        print("Sentimientos Positivos:")
        print(sentimientos_positivos)
        
        print("Sentimientos Negativos:")
        print(sentimientos_negativos)

        return sentimientos_positivos, sentimientos_negativos

    except ET.ParseError as e:
        print("Error al parsear el archivo XML:", e)
        return [], []
    except Exception as e:
        print("Error inesperado:", e)
        return [], []



def cargar_empresas_desde_xml():
    """Carga empresas y servicios desde un archivo XML a una lista de diccionarios y los imprime."""
    archivo_empresas = './uploads/entrada_mandado_flask.xml'
    empresas = []

    try:
        tree = ET.parse(archivo_empresas)
        root = tree.getroot()
        
        # Buscar dentro de diccionario/empresas_analizar
        for empresa_element in root.find('diccionario/empresas_analizar').findall('empresa'):
            nombre_empresa = empresa_element.find('nombre').text.strip()
            servicios = []
            for servicio_element in empresa_element.findall('servicio'):
                nombre_servicio = servicio_element.get('nombre').strip()  # Obtener el nombre del servicio
                aliases = [alias.text.strip() for alias in servicio_element.findall('alias')]
                
                # Agregar el nombre del servicio a la lista de aliases
                aliases.append(nombre_servicio)
                
                servicios.append({"nombre": nombre_servicio, "aliases": aliases})
            
            empresa = {"nombre": nombre_empresa, "servicios": servicios}
            empresas.append(empresa)
            
            # Imprimir la información de la empresa y sus servicios
            print(f"Empresa cargada: {empresa['nombre']}")
            for servicio in empresa["servicios"]:
                print(f"  Servicio: {servicio['nombre']} | Aliases: {servicio['aliases']}")
        
        print("Empresas cargadas desde XML.")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {archivo_empresas}")
    except ET.ParseError:
        print(f"Error: No se pudo parsear el archivo {archivo_empresas}")
    
    return empresas



def analizar_mensajes():
    # Obtener listas de sentimientos y empresas
    sentimientos_positivos, sentimientos_negativos = obtener_sentimientos()
    empresas = cargar_empresas_desde_xml()

    try:
        # Parsear el archivo de mensajes
        tree = ET.parse('./uploads/entrada_mandado_flask.xml')
        root = tree.getroot()

        # Inicializar la lista de respuestas
        respuestas = []

        # Verificar que la lista de mensajes fue cargada
        lista_mensajes = root.find('lista_mensajes')
        if lista_mensajes is not None:
            print("Lista de mensajes cargada. Iniciando procesamiento de mensajes...")

            # Recorrer cada mensaje en lista_mensajes
            for mensaje in lista_mensajes.findall('mensaje'):
                texto_mensaje = mensaje.text.strip().replace('\n', ' ')
                fecha_mensaje = None

                # Buscar la fecha usando expresiones regulares
                fecha_match = re.search(r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2})', texto_mensaje)
                if fecha_match:
                    fecha_mensaje = fecha_match.group(1)
                    texto_mensaje = re.sub(r'Lugar y fecha: .*?(\d{2}/\d{2}/\d{4} \d{2}:\d{2})', '', texto_mensaje)

                # Contadores iniciales para el mensaje
                mensaje_positivos, mensaje_negativos, mensaje_neutros = 0, 0, 0

                # Contar palabras en el mensaje usando expresiones regulares
                palabras = re.findall(r'\b\w+\b', texto_mensaje)
                for palabra in palabras:
                    if palabra in sentimientos_positivos:
                        mensaje_positivos += 1
                    elif palabra in sentimientos_negativos:
                        mensaje_negativos += 1

                # Calcular neutros
                mensaje_neutros = 1 if mensaje_positivos == mensaje_negativos and mensaje_positivos > 0 else 0

                # Inicializar el diccionario del análisis del mensaje
                resultado_analisis = {
                    'fecha': fecha_mensaje if fecha_mensaje else "Fecha no encontrada",
                    'total': 0,
                    'positivos': 0,
                    'negativos': 0,
                    'neutros': 0,
                    'empresa_analisis': []
                }

                # Análisis por empresas y sus servicios/alias
                for empresa in empresas:
                    empresa_datos = {
                        'nombre': empresa['nombre'],
                        'total': 0,
                        'positivos': 0,
                        'negativos': 0,
                        'neutros': 0,
                        'servicios': []
                    }

                    # Chequeo del nombre de la empresa
                    if empresa['nombre'] in texto_mensaje:
                        empresa_datos['positivos'] += mensaje_positivos
                        empresa_datos['negativos'] += mensaje_negativos
                        empresa_datos['neutros'] += mensaje_neutros
                        empresa_datos['total'] = empresa_datos['positivos'] + empresa_datos['negativos'] + empresa_datos['neutros']

                    # Chequeo de alias de cada servicio
                    for servicio in empresa['servicios']:
                        servicio_datos = {
                            'nombre': servicio['nombre'],
                            'total': 0,
                            'positivos': 0,
                            'negativos': 0,
                            'neutros': 0
                        }

                        # Verificar cada alias en el mensaje
                        for alias in servicio['aliases']:
                            if alias in texto_mensaje:
                                servicio_datos['positivos'] = mensaje_positivos
                                servicio_datos['negativos'] = mensaje_negativos
                                servicio_datos['neutros'] = mensaje_neutros
                                servicio_datos['total'] = servicio_datos['positivos'] + servicio_datos['negativos'] + servicio_datos['neutros']

                                # Acumular en el total de la empresa y del mensaje
                                empresa_datos['positivos'] += servicio_datos['positivos']
                                empresa_datos['negativos'] += servicio_datos['negativos']
                                empresa_datos['neutros'] += servicio_datos['neutros']
                                empresa_datos['total'] = empresa_datos['positivos'] + empresa_datos['negativos'] + empresa_datos['neutros']

                        if servicio_datos['total'] > 0:
                            empresa_datos['servicios'].append(servicio_datos)

                    if empresa_datos['total'] > 0 or any(s['total'] > 0 for s in empresa_datos['servicios']):
                        resultado_analisis['empresa_analisis'].append(empresa_datos)

                # Ajustar los valores acumulativos para el total general de positivos, negativos y neutros de empresas y servicios
                total_positivos = sum(e['positivos'] for e in resultado_analisis['empresa_analisis'])
                total_negativos = sum(e['negativos'] for e in resultado_analisis['empresa_analisis'])
                total_neutros = sum(e['neutros'] for e in resultado_analisis['empresa_analisis'])

                for empresa in resultado_analisis['empresa_analisis']:
                    for servicio in empresa['servicios']:
                        total_positivos += servicio['positivos']
                        total_negativos += servicio['negativos']
                        total_neutros += servicio['neutros']

                # Asignar los totales acumulados a los primeros contadores en la respuesta
                resultado_analisis['positivos'] = total_positivos
                resultado_analisis['negativos'] = total_negativos
                resultado_analisis['neutros'] = total_neutros
                resultado_analisis['total'] = total_positivos + total_negativos + total_neutros

                # Agregar el resultado al listado de respuestas
                respuestas.append(resultado_analisis)

            print(f"Total de mensajes procesados: {len(respuestas)}")
        else:
            print("No se encontró la lista de mensajes en el archivo XML.")

        # Crear la estructura del archivo XML de salida
        root_respuesta = ET.Element("lista_respuestas")
        for respuesta in respuestas:
            respuesta_elemento = ET.SubElement(root_respuesta, "respuesta")
            ET.SubElement(respuesta_elemento, "fecha").text = respuesta['fecha']

            mensajes_elemento = ET.SubElement(respuesta_elemento, "mensajes")
            ET.SubElement(mensajes_elemento, "total").text = str(respuesta['total'])
            ET.SubElement(mensajes_elemento, "positivos").text = str(respuesta['positivos'])
            ET.SubElement(mensajes_elemento, "negativos").text = str(respuesta['negativos'])
            ET.SubElement(mensajes_elemento, "neutros").text = str(respuesta['neutros'])

            analisis_elemento = ET.SubElement(respuesta_elemento, "analisis")
            for empresa_datos in respuesta['empresa_analisis']:
                empresa_elemento = ET.SubElement(analisis_elemento, "empresa", nombre=empresa_datos['nombre'])

                mensajes_empresa = ET.SubElement(empresa_elemento, "mensajes")
                # Actualizar el total para la empresa basado en la suma de positivos, negativos y neutros
                empresa_datos['total'] = empresa_datos['positivos'] + empresa_datos['negativos'] + empresa_datos['neutros']
                ET.SubElement(mensajes_empresa, "total").text = str(empresa_datos['total'])
                ET.SubElement(mensajes_empresa, "positivos").text = str(empresa_datos['positivos'])
                ET.SubElement(mensajes_empresa, "negativos").text = str(empresa_datos['negativos'])
                ET.SubElement(mensajes_empresa, "neutros").text = str(empresa_datos['neutros'])

                servicios_elemento = ET.SubElement(empresa_elemento, "servicios")
                for servicio in empresa_datos['servicios']:
                    servicio_elemento = ET.SubElement(servicios_elemento, "servicio", nombre=servicio['nombre'])

                    mensajes_servicio = ET.SubElement(servicio_elemento, "mensajes")
                    # Actualizar el total para el servicio basado en la suma de positivos, negativos y neutros
                    servicio['total'] = servicio['positivos'] + servicio['negativos'] + servicio['neutros']
                    ET.SubElement(mensajes_servicio, "total").text = str(servicio['total'])
                    ET.SubElement(mensajes_servicio, "positivos").text = str(servicio['positivos'])
                    ET.SubElement(mensajes_servicio, "negativos").text = str(servicio['negativos'])
                    ET.SubElement(mensajes_servicio, "neutros").text = str(servicio['neutros'])

        # Guardar el resultado en el archivo de salida con formato
        xml_str = ET.tostring(root_respuesta, encoding="utf-8")
        parsed_str = minidom.parseString(xml_str).toprettyxml(indent="  ")
        with open('./uploads/resultado_analisis.xml', 'w', encoding='utf-8') as f:
            f.write(parsed_str)
        # Guardar el resultado en un archivo JSON
        with open('./uploads/resultado_analisis.json', 'w', encoding='utf-8') as f:
            json.dump(respuestas, f, ensure_ascii=False, indent=2)
        print("Proceso de análisis y escritura del archivo completado correctamente.")

    except Exception as e:
        print(f"Error inesperado: {e}")
    
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