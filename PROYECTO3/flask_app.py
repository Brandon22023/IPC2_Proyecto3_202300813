import datetime
import re
from flask import Flask, Response, make_response, render_template, request, jsonify, session, send_file
import os
import matplotlib
matplotlib.use('Agg')  # Establecer el backend a 'Agg' para guardar imágenes sin mostrar
import matplotlib.pyplot as plt
import json
from collections import Counter, defaultdict
import traceback
import xml.etree.ElementTree as ET
from xml.dom import minidom
from fpdf import FPDF
from PyPDF2 import PdfMerger  # Asegúrate de instalar PyPDF2 si aún no lo tienes
app = Flask(__name__)
UPLOAD_FOLDER = './uploads'  # Carpeta donde se guardarán los archivos
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'  # Necesario para usar sesiones
archivo_cargado=False


@app.route('/RESET', methods=['POST'])
def RESET():
    uploads_dir = './uploads'
        
        # Eliminar todos los archivos en la carpeta, excepto 'archivo_mensaje_prueba.xml'
    for filename in os.listdir(uploads_dir):
        if filename != 'archivo_mensaje_prueba.xml':
            file_path = os.path.join(uploads_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)  # Eliminar el archivo
            except Exception as e:
                print(f"Error al eliminar {file_path}: {e}")

@app.route('/cargar_archivo', methods=['POST'])
def cargar_archivo():
    global archivo_cargado

    try:
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
            analizar_mensajes()  # Ejecutar el método para analizar mensajes

            # Leer el archivo resultado_analisis.xml y enviarlo junto al JSON
            ruta_resultado_analisis_xml = os.path.join(UPLOAD_FOLDER, 'resultado_analisis.xml')
            with open(ruta_resultado_analisis_xml, 'r', encoding='utf-8') as resultado_file:
                contenido_resultado_xml = resultado_file.read()

            # Añadir el contenido del resultado a la respuesta
            contenido_json['contenido_resultado_xml'] = contenido_resultado_xml

            # Devolver el contenido JSON en la respuesta
            return jsonify(contenido_json), 200
            
    except Exception as e:
        print("Error inesperado:", e)
        print(traceback.format_exc())  # Imprime el traceback del error
        return jsonify({'error': str(e)}), 500

@app.route('/cargar_archivo_json', methods=['GET'])
def cargar_archivo_json():
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


@app.route('/consultar_datos', methods=['POST'])
def consultar_datos():
    # Ruta del archivo XML
    ruta_xml = "./uploads/resultado_analisis.xml"
    # Ruta del archivo JSON (se procesará pero no se enviará)
    ruta_json = "./uploads/resultado_analisis.json"
    
    # Leer el contenido del archivo XML y preparar la respuesta
    try:
        with open(ruta_xml, "r") as file:
            contenido_xml = file.read()
    except FileNotFoundError:
        contenido_xml = "<error>No se encontró el archivo XML en la ruta especificada.</error>"

    # Leer el archivo JSON solo para procesamiento interno, no se incluye en la respuesta
    if os.path.exists(ruta_json):
        try:
            with open(ruta_json, "r", encoding="utf-8") as archivo_json:
                contenido_json = archivo_json.read()
                # Aquí podrías procesar el JSON, pero no se enviará a la respuesta
                print("Contenido completo del archivo JSON:", contenido_json)
        except Exception as e:
            print(f"Error al leer el archivo JSON: {e}")
    generar_pdf_consultar_datos()
    # Devolver solo el contenido XML como respuesta
    return Response(contenido_xml, mimetype='application/xml')


def generar_pdf_consultar_datos():
    # Ruta del archivo XML
    ruta_xml = "./uploads/resultado_analisis.xml"
    # Ruta del archivo JSON (se procesará pero no se enviará)
    ruta_json = "./uploads/resultado_analisis.json"
    
    # Ruta de salida para el archivo PDF
    ruta_pdf = "./Reportes/REPORTES.pdf"

    # Verificar si la carpeta de reportes existe, si no, crearla
    os.makedirs(os.path.dirname(ruta_pdf), exist_ok=True)
    # Leer el contenido del archivo XML y preparar la respuesta
    try:
        with open(ruta_xml, "r") as file:
            contenido_xml = file.read()
    except FileNotFoundError:
        contenido_xml = "<error>No se encontró el archivo XML en la ruta especificada.</error>"

    # Leer el archivo JSON solo para procesamiento interno, no se incluye en la respuesta
    if os.path.exists(ruta_json):
        try:
            with open(ruta_json, "r", encoding="utf-8") as archivo_json:
                contenido_json = archivo_json.read()
                # Aquí podrías procesar el JSON, pero no se enviará a la respuesta
                print("Contenido completo del archivo JSON:", contenido_json)
        except Exception as e:
            print(f"Error al leer el archivo JSON: {e}")
    # Crear el archivo PDF con el contenido del XML usando FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    
    # Configurar el título en el PDF
    pdf.set_font("Arial", "B", 16)  # Fuente en negrita para el título
    pdf.cell(0, 10, "1. CONSULTA DE DATOS", ln=True, align="C")  # Centrar título
    pdf.ln(10)  # Línea en blanco después del título
    # Agregar contenido XML al PDF, dividiendo líneas largas
    # Configurar el contenido en el PDF
    pdf.set_font("Arial", size=12)
    for linea in contenido_xml.splitlines():
        pdf.cell(0, 10, txt=linea, ln=True)
    
    # Guardar el PDF
    pdf.output(ruta_pdf)


@app.route('/archivo_prueba', methods=['POST'])
def archivo_prueba():
    # Ruta del archivo XML
    ruta_xml = "./uploads/archivo_mensaje_prueba.xml"

    # Leer el contenido del archivo XML y preparar la respuesta
    try:
        with open(ruta_xml, "r") as file:
            archivo_prueba_xml = file.read()
    except FileNotFoundError:
        archivo_prueba_xml = "<error>No se encontró el archivo XML en la ruta especificada.</error>"


    # Devolver solo el contenido XML como respuesta
    return Response(archivo_prueba_xml, mimetype='application/xml')
# Ruta para recibir el contenido y guardar el archivo XML
@app.route('/prueba_mensaje', methods=['POST'])
def prueba_mensaje():
    # Recibe el contenido del textarea desde el formulario
    contenido_xml = request.form.get('salida')
    print("el contenido de contenido_xml es: ", contenido_xml)
    directorio = './uploads'
    archivo_path = os.path.join(directorio, 'mensaje_prueba.xml')
    
    # Verificar si el directorio existe, y si no, crearlo
    if not os.path.exists(directorio):
        os.makedirs(directorio)
    
    # Guardar el contenido en el archivo XML
    with open(archivo_path, 'w', encoding='utf-8') as archivo:
        archivo.write(contenido_xml)
    
    # Leer el archivo guardado
    with open(archivo_path, 'r', encoding='utf-8') as archivo:
        contenido_leido = archivo.read()
    
    # Extraer fecha, red social y usuario
    fecha_match = re.search(r'\d{2}/\d{2}/\d{4}', contenido_leido)
    red_social_match = re.search(r'Red social:\s*(\w+)', contenido_leido)
    usuario_match = re.search(r'Usuario:\s*([\w\.\@\d]+)', contenido_leido)
    
    fecha = fecha_match.group() if fecha_match else "No encontrada"
    red_social = red_social_match.group(1) if red_social_match else "No encontrada"
    usuario = usuario_match.group(1) if usuario_match else "No encontrado"
    
    # Obtener listas de palabras positivas y negativas
    sentimientos_positivos, sentimientos_negativos = obtener_sentimientos()

    # Crear patrones de regex para palabras positivas y negativas, ignorando mayúsculas y minúsculas
    patrones_positivos = [re.compile(rf'\b{re.escape(palabra)}\b', re.IGNORECASE) for palabra in sentimientos_positivos]
    patrones_negativos = [re.compile(rf'\b{re.escape(palabra)}\b', re.IGNORECASE) for palabra in sentimientos_negativos]

    # Contar palabras positivas y negativas en el mensaje
    contador_positivas = sum(1 for patron in patrones_positivos if patron.search(contenido_leido))
    contador_negativas = sum(1 for patron in patrones_negativos if patron.search(contenido_leido))

    # Cargar empresas y servicios
    empresas = cargar_empresas_desde_xml()
    empresas_mencionadas = []

    for empresa in empresas:
        # Crear un patrón de regex para el nombre de la empresa, ignorando mayúsculas y minúsculas
        patron_empresa = re.compile(rf'\b{re.escape(empresa["nombre"])}\b', re.IGNORECASE)
        if patron_empresa.search(contenido_leido):
            servicios_mencionados = []
            
            for servicio in empresa["servicios"]:
                # Crear patrones de regex para los aliases de servicios
                patrones_servicio = [re.compile(rf'\b{re.escape(alias)}\b', re.IGNORECASE) for alias in servicio["aliases"]]
                
                # Verificar si alguno de los patrones del servicio coincide en el contenido
                if any(patron.search(contenido_leido) for patron in patrones_servicio):
                    servicios_mencionados.append(servicio["nombre"])

            # Añadir empresa mencionada y sus servicios
            empresas_mencionadas.append({
                "nombre": empresa["nombre"],
                "servicios": servicios_mencionados
            })

    # Calcular porcentaje de sentimientos
    total_palabras = contador_positivas + contador_negativas
    porcentaje_positivo = (contador_positivas / total_palabras) * 100 if total_palabras > 0 else 0
    porcentaje_negativo = (contador_negativas / total_palabras) * 100 if total_palabras > 0 else 0

    # Determinar el sentimiento final, considerando el caso de empate
    if contador_positivas == contador_negativas:
        sentimiento_analizado = "positivo y negativo cuentan con cantidades iguales"
    else:
        sentimiento_analizado = "positivo" if porcentaje_positivo > porcentaje_negativo else "negativo"

    # Generar XML de respuesta
    respuesta_xml = ET.Element("respuesta")
    ET.SubElement(respuesta_xml, "fecha").text = fecha
    ET.SubElement(respuesta_xml, "red_social").text = red_social
    ET.SubElement(respuesta_xml, "usuario").text = usuario

    empresas_xml = ET.SubElement(respuesta_xml, "empresas")
    for empresa in empresas_mencionadas:
        empresa_xml = ET.SubElement(empresas_xml, "empresa", nombre=empresa["nombre"])
        for servicio in empresa["servicios"]:
            ET.SubElement(empresa_xml, "servicio").text = servicio

    ET.SubElement(respuesta_xml, "palabras_positivas").text = str(contador_positivas)
    ET.SubElement(respuesta_xml, "palabras_negativas").text = str(contador_negativas)
    ET.SubElement(respuesta_xml, "sentimiento_positivo").text = f"{porcentaje_positivo:.2f}%"
    ET.SubElement(respuesta_xml, "sentimiento_negativo").text = f"{porcentaje_negativo:.2f}%"
    ET.SubElement(respuesta_xml, "sentimiento_analizado").text = sentimiento_analizado

    # Formatear el XML para que tenga sangría y sea legible
    xml_str = ET.tostring(respuesta_xml, encoding='utf-8')
    xml_pretty_str = minidom.parseString(xml_str).toprettyxml(indent="    ")

    # Guardar el XML de respuesta con formato
    archivo_respuesta_path = os.path.join(directorio, 'MENSAJE_PROCESADO_ARCHIVO.xml')
    with open(archivo_respuesta_path, 'w', encoding='utf-8') as archivo:
        archivo.write(xml_pretty_str)

    # Retornar el contenido del archivo XML procesado
    return xml_pretty_str, 200, {'Content-Type': 'application/xml'}

@app.route('/prueba_de_mensaje', methods=['POST'])
def prueba_de_mensaje():
    # Ruta del archivo XML guardado
    archivo_respuesta_path = './uploads/MENSAJE_PROCESADO_ARCHIVO.xml'
    try:
        # Verificar si el archivo existe
        if not os.path.exists(archivo_respuesta_path):
            return "El archivo XML no existe.", 404, {'Content-Type': 'text/plain'}
        
        # Retornar el archivo directamente para descargar o visualizar
        return send_file(archivo_respuesta_path, mimetype='application/xml')
    
    except Exception as e:
        return f"Error al leer el archivo XML: {e}", 500, {'Content-Type': 'text/plain'}

    


@app.route('/Resumen_clasificacion_fecha', methods=['POST'])
def Resumen_clasificacion_fecha():
    # Ruta del archivo XML
    ruta_xml = "./uploads/resultado_analisis.xml"
    
    # Parseo del archivo XML
    tree = ET.parse(ruta_xml)
    root = tree.getroot()

    # Extraer fechas y empresas
    fechas = set()
    empresas_set = set()  # Usar un set para evitar duplicados

    for respuesta in root.findall('respuesta'):
        fecha = respuesta.find('fecha').text.strip()
        fechas.add(fecha)

        # Extraer empresas
        for empresa in respuesta.findall(".//empresa"):
            nombre_empresa = empresa.get("nombre")
            empresas_set.add(nombre_empresa)  # Agregar al set para evitar duplicados

    fechas = sorted(fechas)  # Ordenar las fechas
    empresas = sorted(empresas_set)  # Ordenar las empresas
    # Agregar "Todas las empresas" al inicio de la lista de empresas
    empresas.insert(0, "todas las empresas")
    

    # Devolver datos en JSON
    return jsonify({
        "fechas": list(fechas),
        "empresas": empresas  # Cambiar a una lista de empresas
    })

@app.route('/RESUMEN_POR_RANGO_DE_FECHAS', methods=['POST'])
def RESUMEN_POR_RANGO_DE_FECHAS():
    # Ruta del archivo XML
    ruta_xml = "./uploads/resultado_analisis.xml"
    
    # Parseo del archivo XML
    tree = ET.parse(ruta_xml)
    root = tree.getroot()

    # Extraer fechas y empresas
    fechas = set()
    empresas_set = set()  # Usar un set para evitar duplicados

    for respuesta in root.findall('respuesta'):
        fecha = respuesta.find('fecha').text.strip()
        fechas.add(fecha)

        # Extraer empresas
        for empresa in respuesta.findall(".//empresa"):
            nombre_empresa = empresa.get("nombre")
            empresas_set.add(nombre_empresa)  # Agregar al set para evitar duplicados

    fechas = sorted(fechas)  # Ordenar las fechas
    empresas = sorted(empresas_set)  # Ordenar las empresas
    # Agregar "Todas las empresas" al inicio de la lista de empresas
    empresas.insert(0, "todas las empresas")
    

    # Devolver datos en JSON
    return jsonify({
        "fechas": list(fechas),
        "empresas": empresas  # Cambiar a una lista de empresas
    })


@app.route('/mostrar_datos_clasificados', methods=['POST'])
def mostrar_datos_clasificados():
    # Obtener datos del JSON enviado desde Django
    data = request.get_json()
    fecha_seleccionada = data['fecha']
    empresa_seleccionada = data['empresa']
    
    # Imprimir en consola los datos recibidos
    print("Fecha seleccionada:", fecha_seleccionada)
    print("Empresa seleccionada:", empresa_seleccionada)
    
    # Ruta al archivo XML
    ruta_xml = "./uploads/resultado_analisis.xml"

    try:
        tree = ET.parse(ruta_xml)
        root = tree.getroot()
        resultados = []
        
        # Recorrer las respuestas en el XML
        for respuesta in root.findall("respuesta"):
            fecha = respuesta.find("fecha").text.strip()
            
            # Comparar la fecha para verificar si coincide
            if fecha.startswith(fecha_seleccionada):
                for empresa in respuesta.find("analisis").findall("empresa"):
                    nombre_empresa = empresa.get("nombre")
                    
                    # Comparar el nombre de la empresa o si se seleccionaron todas
                    if empresa_seleccionada == "todas las empresas" or nombre_empresa == empresa_seleccionada:
                        total = int(empresa.find("mensajes/total").text)  # Convertir a int
                        positivos = int(empresa.find("mensajes/positivos").text)  # Convertir a int
                        negativos = int(empresa.find("mensajes/negativos").text)  # Convertir a int
                        neutros = int(empresa.find("mensajes/neutros").text)  # Convertir a int
                        
                        # Agregar los resultados encontrados a la lista
                        resultados.append({
                            "empresa": nombre_empresa,
                            "total": total,
                            "positivos": positivos,
                            "negativos": negativos,
                            "neutros": neutros
                        })

        print("Resultados encontrados:", resultados)

        # Verificar si hay resultados antes de generar la gráfica
        if resultados:
            crear_grafica(resultados, fecha_seleccionada, empresa_seleccionada)
            return jsonify(resultados), 200
        else:
            return jsonify({"error": "No se encontraron datos"}), 404

    except Exception as e:
        print("Error:", str(e))  # Imprimir el error
        return jsonify({"error": str(e)}), 500
    

@app.route('/mostrar_datos_clasificados_intervalo', methods=['POST'])
def mostrar_datos_clasificados_intervalo():
    # Obtener datos del JSON enviado desde Django
    data = request.get_json()
    fecha_inicio = data['fecha_inicio']  # Cambiado para recibir fecha_inicio
    fecha_fin = data['fecha_fin']         # Cambiado para recibir fecha_fin
    empresa_seleccionada = data['empresa']
    
    # Imprimir en consola los datos recibidos
    print("Fecha inicial seleccionada:", fecha_inicio)
    print("Fecha final seleccionada:", fecha_fin)
    print("Empresa seleccionada:", empresa_seleccionada)
    
    # Ruta al archivo XML
    ruta_xml = "./uploads/resultado_analisis.xml"

    try:
        tree = ET.parse(ruta_xml)
        root = tree.getroot()
        resultados = []
        
        # Recorrer las respuestas en el XML
        for respuesta in root.findall("respuesta"):
            fecha = respuesta.find("fecha").text.strip()
            
            # Comparar la fecha para verificar si está dentro del intervalo
            if fecha_inicio <= fecha <= fecha_fin:  # Verifica si la fecha está en el intervalo
                for empresa in respuesta.find("analisis").findall("empresa"):
                    nombre_empresa = empresa.get("nombre")
                    
                    # Comparar el nombre de la empresa o si se seleccionaron todas
                    if empresa_seleccionada == "todas las empresas" or nombre_empresa == empresa_seleccionada:
                        total = int(empresa.find("mensajes/total").text)  # Convertir a int
                        positivos = int(empresa.find("mensajes/positivos").text)  # Convertir a int
                        negativos = int(empresa.find("mensajes/negativos").text)  # Convertir a int
                        neutros = int(empresa.find("mensajes/neutros").text)  # Convertir a int
                        
                        # Agregar los resultados encontrados a la lista
                        resultados.append({
                            "empresa": nombre_empresa,
                            "total": total,
                            "positivos": positivos,
                            "negativos": negativos,
                            "neutros": neutros,
                            "fecha": fecha  # Agregar la fecha correspondiente
                        })

        print("Resultados encontrados:", resultados)
        crear_pdf_intervalo(fecha_inicio, fecha_fin, empresa_seleccionada) 
        # Verificar si hay resultados antes de generar la gráfica
        if resultados:
            
            
            return jsonify(resultados), 200
        else:
            return jsonify({"error": "No se encontraron datos"}), 404

    except Exception as e:
        print("Error:", str(e))  # Imprimir el error
        return jsonify({"error": str(e)}), 500
    

def crear_grafica(resultados, fecha_seleccionada, empresa_seleccionada):
    # Crear la carpeta IMG si no existe
    os.makedirs('./IMG', exist_ok=True)


    # Extraer datos para la gráfica
    categorias = ['Total', 'Positivos', 'Negativos', 'Neutros']
    valores = [
        sum(res['total'] for res in resultados), 
        sum(res['positivos'] for res in resultados), 
        sum(res['negativos'] for res in resultados), 
        sum(res['neutros'] for res in resultados)
    ]

    print("Datos para la gráfica:", dict(zip(categorias, valores)))  # Imprimir datos para la gráfica

    # Crear la gráfica
    try:
        plt.figure(figsize=(10, 6))
        plt.bar(categorias, valores, color=['blue', 'green', 'red', 'yellow'])
        plt.xlabel('Categorías')
        plt.ylabel('Cantidad')
        plt.title('Clasificación de Mensajes por Fecha')
        plt.grid(axis='y')

        # Guardar la gráfica en un archivo PNG
        plt.savefig('./IMG/grafica_barras_clasificacion_fecha.png')
        plt.close()  # Cerrar la figura para liberar memoria
        print("Gráfica guardada en ./IMG/grafica_barras_clasificacion_fecha.png")  # Mensaje de éxito

        # Crear el PDF
        crear_pdf(fecha_seleccionada, empresa_seleccionada)
    except Exception as e:
        print("Error al guardar la gráfica:", str(e))  # Imprimir el error

def crear_pdf(fecha_seleccionada, empresa_seleccionada):
    # Crear la carpeta Reportes si no existe
    os.makedirs('./Reportes', exist_ok=True)

    # Ruta para el PDF temporal
    ruta_pdf_temp = "./Reportes/Resumen_clasificacion_temp.pdf"
    ruta_pdf_existente = "./Reportes/REPORTES.pdf"

    # Crear el PDF temporal
    pdf = FPDF()
    pdf.add_page()

    # Agregar título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, 'Resumen de Clasificación', ln=True, align='C')

    # Agregar fecha y empresa seleccionada
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f'Fecha Seleccionada: {fecha_seleccionada}', ln=True)
    pdf.cell(250, 30, f'Empresa Seleccionada: {empresa_seleccionada}', ln=True)

    # Agregar la imagen de la gráfica
    pdf.image('./IMG/grafica_barras_clasificacion_fecha.png', x=10, y=50, w=190)

    # Guardar el PDF temporal
    pdf.output(ruta_pdf_temp)
    print(f"PDF temporal guardado en {ruta_pdf_temp}")

    # Combinar el PDF temporal con el PDF existente
    merger = PdfMerger()
    if os.path.exists(ruta_pdf_existente):
        merger.append(ruta_pdf_existente)  # Agrega el PDF existente
    merger.append(ruta_pdf_temp)           # Agrega el nuevo contenido

    # Guardar el PDF combinado en la ruta del PDF existente
    merger.write(ruta_pdf_existente)
    merger.close()

    # Eliminar el PDF temporal
    os.remove(ruta_pdf_temp)
    print(f"Contenido agregado a {ruta_pdf_existente}")


def crear_pdf_intervalo(fecha_inicio, fecha_fin, empresa_seleccionada):
    # Crear la carpeta Reportes si no existe
    os.makedirs('./Reportes', exist_ok=True)

    # Ruta para el PDF temporal
    ruta_pdf_temp = "./Reportes/Resumen_clasificacion_temp.pdf"
    ruta_pdf_existente = "./Reportes/REPORTES.pdf"

    # Crear el PDF temporal
    pdf = FPDF()
    pdf.add_page()

    # Agregar título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, '3. RESUMEN POR RANGO DE FECHAS', ln=True, align='C')

    # Agregar fecha y empresa seleccionada
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f'Fecha Inicio seleccionada: {fecha_inicio}', ln=True)
    pdf.cell(200, 10, f'Fecha Fin seleccionada: {fecha_fin}', ln=True)
    pdf.cell(200, 10, f'Empresa Seleccionada: {empresa_seleccionada}', ln=True)


    # Guardar el PDF temporal
    pdf.output(ruta_pdf_temp)
    print(f"PDF temporal guardado en {ruta_pdf_temp}")

    # Combinar el PDF temporal con el PDF existente
    merger = PdfMerger()
    if os.path.exists(ruta_pdf_existente):
        merger.append(ruta_pdf_existente)  # Agrega el PDF existente
    merger.append(ruta_pdf_temp)           # Agrega el nuevo contenido

    # Guardar el PDF combinado en la ruta del PDF existente
    merger.write(ruta_pdf_existente)
    merger.close()

    # Eliminar el PDF temporal
    os.remove(ruta_pdf_temp)
    print(f"Contenido agregado a {ruta_pdf_existente}")
     
@app.route('/REPORTE_PDF', methods=['POST'])
def REPORTE_PDF():
    Ruta_reportes = "./Reportes"
    Ruta_final = "./REPORTE DEL SISTEMA"

    # Crear la carpeta si no existe
    if not os.path.exists(Ruta_final):
        os.makedirs(Ruta_final)

    # Lista para almacenar los nombres de los archivos PDF
    archivos_pdf = []

    # Recorremos la carpeta y recogemos los archivos PDF
    for filename in sorted(os.listdir(Ruta_reportes)):
        if filename.endswith('.pdf'):
            archivos_pdf.append(os.path.join(Ruta_reportes, filename))

    # Creamos un objeto PdfMerger
    merger = PdfMerger()

    # Añadimos cada archivo PDF al merger
    for pdf in archivos_pdf:
        merger.append(pdf)

    # Guardamos el archivo unido en la nueva ruta
    ruta_pdf_final = os.path.join(Ruta_final, 'REPORTE.pdf')
    merger.write(ruta_pdf_final)
    merger.close()

    print("PDF creado con éxito en:", ruta_pdf_final)
    print("Solicitud POST recibida en Flask para generar PDF.")

    # Aquí no devolvemos nada, solo se genera el PDF
    return '', 204  # Devuelve un código de estado 204 No Content


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
            modelo_text = "Link de la documentacion: https://drive.google.com/drive/folders/1dDmBMhngQ3WZSGbr4k5tKbyJ_AkoQuXN?usp=sharing"
        else:
            return jsonify({'error': 'Modelo no válido'}), 400  

        return jsonify({'titulo': modelo_titulo, 'texto': modelo_text})
    except Exception as e:
        print("Error al procesar la solicitud:", e)
        return jsonify({'error': 'Error procesando la solicitud'}), 400
    

if __name__ == '__main__':
    app.run(port=5000, debug=True)