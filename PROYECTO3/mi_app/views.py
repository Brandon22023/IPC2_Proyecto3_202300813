import json
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from flask import redirect
import requests
from django.http import JsonResponse
from django.conf import settings
import os

# Vista para cargar datos (Cargar Archivo)
def inicio(request):
    return render(request, 'inicio.html')# Vista para cargar datos (Cargar Archivo)
# Vista para cargar el archivo y mostrar su contenido


def cargar_archivo(request):
    # Si se ha presionado el botón de reset
    if request.method == 'POST' and request.POST.get('reset') == 'reset':
        # Limpiar los datos de la sesión
        request.session['contenido_xml'] = ''
        request.session['archivo_info'] = ''
        request.session['contenido_resultado_xml'] = ''
        request.session['archivo_cargado'] = False  # Resetear estado de archivo cargado

        # Ruta de la carpeta
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
        
        # Renderizar la plantilla sin datos
        return render(request, 'cargar_archivo.html', {
            'contenido_xml': '',
            'archivo_info': '',
            'contenido_resultado_xml': ''
        })
    
    elif request.method == 'POST' and 'archivo' in request.FILES:
        # Cargar archivo XML y enviar a Flask
        archivo = request.FILES['archivo']
        print("Enviando archivo:", archivo.name)  # Log para verificar el archivo

        # Obtener el estado del archivo cargado desde la sesión
        archivo_cargado = request.session.get('archivo_cargado', False)

        try:
            # Enviar archivo y el estado de archivo_cargado a Flask
            respuesta = requests.post(
                'http://127.0.0.1:5000/cargar_archivo',
                files={'archivo': archivo},
                data={'archivo_cargado': archivo_cargado}  # Enviamos el estado
            )
            print("Respuesta del servidor:", respuesta.status_code)  # Log del código de estado

            # Procesar la respuesta de Flask para obtener contenido y ruta
            if respuesta.status_code == 200:
                data = respuesta.json()
                request.session['contenido_xml'] = data.get('contenido_xml', '')
                request.session['archivo_info'] = data.get('ruta_archivo', '')
                request.session['contenido_resultado_xml'] = data.get('contenido_resultado_xml', '')
                request.session['archivo_cargado'] = True  # Marcar como archivo cargado
            else:
                # Captura el mensaje de error del servidor
                error_message = respuesta.json().get('error', 'Error desconocido')
                print("Error al cargar el archivo:", error_message)  # Log del error
                request.session['contenido_xml'] = "Error al cargar el archivo: " + error_message
                request.session['archivo_info'] = ''
                request.session['contenido_resultado_xml'] = ''

        except requests.exceptions.RequestException as e:
            # Manejar excepciones de la solicitud
            print("Error al hacer la solicitud a Flask:", str(e))
            request.session['contenido_xml'] = "Error de conexión con el servidor Flask."
            request.session['archivo_info'] = ''
            request.session['contenido_resultado_xml'] = ''

    # Renderizar la plantilla con los datos actuales desde la sesión
    return render(request, 'cargar_archivo.html', {
        'contenido_xml': request.session.get('contenido_xml', ''),
        'archivo_info': request.session.get('archivo_info', ''),
        'contenido_resultado_xml': request.session.get('contenido_resultado_xml', '')
    })


def peticiones(request):
    modelo_mensaje = None
    mostrar_textarea = False
    contenido_resultado_xml = ""
    mostrar_combobox = False
    fechas = []
    empresas = []
    resultados = []
    mostrar_textarea_model5 = False
    resultado_model5 = False
    contenido_archivo_xml = ""
    mensaje_confirmacion = ""  # Variable para el mensaje de confirmación
    reportes_pdf = False
    mostrar_fechas_comboox = False
    resultados_intervalo_fecha = []  # Para guardar los resultados de la consulta en modelo3

    if request.method == 'POST':
        modelo_texto = request.POST.get('modelo_texto')
        
        if modelo_texto == 'modelo1':
            modelo_mensaje = "Consultar datos seleccionado."
            mostrar_textarea = True
            try:
                response = requests.post('http://127.0.0.1:5000/consultar_datos')
                if response.status_code == 200:
                    contenido_resultado_xml = response.text
                else:
                    contenido_resultado_xml = "Error al consultar datos en el servidor Flask."
            except requests.exceptions.RequestException as e:
                contenido_resultado_xml = f"Error de conexión: {e}"
        
        elif modelo_texto == 'modelo2':
            modelo_mensaje = "Resumen de clasificación por fecha seleccionado."
            mostrar_combobox = True
            if 'obtener' in request.POST:
                # Obtener los valores seleccionados en los combobox
                fecha_seleccionada = request.POST.get('combo1')
                empresa_seleccionada = request.POST.get('combo2')
                
                # Imprimir los valores seleccionados para verificar
                print("Fecha seleccionada:", fecha_seleccionada)
                print("Empresa seleccionada:", empresa_seleccionada)
                
                try:
                    response = requests.post(
                        'http://127.0.0.1:5000/mostrar_datos_clasificados',
                        json={'fecha': fecha_seleccionada, 'empresa': empresa_seleccionada}
                    )
                    if response.status_code == 200:
                        resultados = response.json()
                    else:
                        modelo_mensaje = "Error en la consulta de datos en Flask."
                except requests.exceptions.RequestException as e:
                    modelo_mensaje = f"Error de conexión: {e}"
                 

            try:
                response = requests.post('http://127.0.0.1:5000/Resumen_clasificacion_fecha')
                if response.status_code == 200:
                    data = response.json()
                    fechas = data.get("fechas", [])
                    empresas = data.get("empresas", [])
                else:
                    modelo_mensaje = "Error al consultar datos en el servidor Flask para modelo 2."
            except requests.exceptions.RequestException as e:
                modelo_mensaje = f"Error de conexión: {e}"




        elif modelo_texto == 'modelo3':
            modelo_mensaje = "Resumen de rango de fechas seleccionado."
            mostrar_fechas_comboox = True
            resultados_intervalo_fecha = None  # Inicializar variable para los resultados
            resultados_intervalo_fecha = []  # Inicializamos como lista vacía


            if request.POST.get('obtener') == 'obtener_datos':
                fecha_inicio = request.POST.get('fecha_inicio')
                fecha_fin = request.POST.get('fecha_fin')
                empresa_seleccionada = request.POST.get('empresa_seleccionada')

                if fecha_inicio and fecha_fin and empresa_seleccionada:
                    try:
                        # Llamada al servicio Flask para obtener los datos
                        response = requests.post(
                            'http://127.0.0.1:5000/mostrar_datos_clasificados_intervalo',
                            json={'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin, 'empresa': empresa_seleccionada}
                        )
                        if response.status_code == 200:
                            resultados_intervalo_fecha = response.json()
                        else:
                            modelo_mensaje = "Error en la consulta de datos en Flask."
                    except requests.exceptions.RequestException as e:
                        modelo_mensaje = f"Error de conexión: {e}"
                else:
                    modelo_mensaje = "Por favor, complete todos los campos del formulario."




            try:
                response = requests.post('http://127.0.0.1:5000/RESUMEN_POR_RANGO_DE_FECHAS')
                if response.status_code == 200:
                    data = response.json()
                    empresas = data.get("empresas", [])
                else:
                    modelo_mensaje = "Error al consultar datos en el servidor Flask para modelo 2."
            except requests.exceptions.RequestException as e:
                modelo_mensaje = f"Error de conexión: {e}"
            




        elif modelo_texto == 'modelo4':
            modelo_mensaje = "Reporte en PDF seleccionado."
            reportes_pdf = True
            print("inicio.")
            # Verificar si el botón para generar el reporte fue presionado
            if request.POST.get("generar_reporte") == "true":
                modelo_mensaje = "Se presionó el botón para generar el reporte."
                print("Botón de 'Generar Reporte' detectado en Django.")    

                try:
                    # Enviar solicitud POST a Flask para generar el PDF
                    response = requests.post('http://127.0.0.1:5000/REPORTE_PDF')
                    print("Solicitud POST enviada a Flask.")

                    # Verificar la respuesta de Flask
                    if response.status_code == 204:
                        modelo_mensaje = "Reporte PDF generado correctamente."
                        print("Flask confirmó generación exitosa del PDF.")
                    else:
                        modelo_mensaje = f"Error al generar el reporte PDF en Flask. Código de estado: {response.status_code}"
                        print("Error en la generación del PDF en Flask:", response.status_code)

                except requests.exceptions.RequestException as e:
                    modelo_mensaje = f"Error de conexión: {e}"
                    print("Error de conexión con Flask:", e)
            else:
                print("Botón de 'Generar Reporte' no detectado en Django.")
            print("fin.")



        elif modelo_texto == 'modelo5':
            modelo_mensaje = "Prueba de mensaje seleccionada."
            mostrar_textarea_model5 = True
            
            try:
                response = requests.post('http://127.0.0.1:5000/archivo_prueba' )
                if response.status_code == 200:
                    contenido_archivo_xml = response.text
                else:
                    contenido_archivo_xml = "Error al consultar datos en el servidor Flask."
            except requests.exceptions.RequestException as e:
                contenido_archivo_xml = f"Error de conexión: {e}"
            print("Contenido del archivo XML fue subido con exito.")
             # Verificación si el botón 'Obtener' fue presionado
            # Verificación si el botón 'Obtener' fue presionado
            if 'boton_obtener' in request.POST:
                contenido_xml = request.POST.get('salida')  # Obtener el contenido del textarea
                print("Contenido enviado a Flask:", contenido_xml)  # Imprimir el contenido que se va a enviar

                try:
                    # Enviar el contenido a Flask
                    response = requests.post('http://127.0.0.1:5000/prueba_mensaje', data={'salida': contenido_xml.encode('utf-8')}, headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'})
                    if response.status_code == 200:
                        contenido_archivo_xml = response.text  # Guardar el contenido del XML procesado
                        mensaje_confirmacion = "Archivo XML guardado correctamente en ./uploads/mensaje_prueba.xml."
                    else:
                        mensaje_confirmacion = "Error al guardar el archivo XML en Flask."
                except requests.exceptions.RequestException as e:
                    mensaje_confirmacion = f"Error de conexión: {e}"

                # Cambiar el estado de los textareas para mostrar el mensaje de confirmación
                resultado_model5 = True
                mostrar_textarea_model5 = False
                


    return render(request, 'peticiones.html', {
        'modelo_mensaje': modelo_mensaje,
        'mostrar_textarea': mostrar_textarea,
        'contenido_resultado_xml': contenido_resultado_xml,
        'mostrar_combobox': mostrar_combobox,
        'fechas': fechas,
        'empresas': empresas,
        'resultados': resultados,
        'resultados_json': json.dumps(resultados),  # Enviar resultados como JSON
        'mostrar_textarea_model5': mostrar_textarea_model5,
        "resultado_model5": resultado_model5,
        'contenido_archivo_xml': contenido_archivo_xml, 
        'mensaje_confirmacion': mensaje_confirmacion,  # Mensaje de confirmación para la plantilla
        'reportes_pdf': reportes_pdf,
        'mostrar_fechas_comboox': mostrar_fechas_comboox,
        'resultados_intervalo_fecha': resultados_intervalo_fecha,  # Enviar a la plantilla
    })



# Vista para ver gráfico (Ayuda)
def ayuda(request):
    modelo_text = ''
    modelo_titulo = ''
    modelo_mensaje = ''
    print("Método de solicitud:", request.method)  # Imprimir el método
    print("Datos del formulario:", request.POST)  # Imprimir los datos del formulario
    if request.method == 'POST':  # Cambiar a POST
        modelo_opcion = request.POST.get('modelo_texto')  # Asegúrate de usar POST para obtener datos
        print("Modelo opción recibido:", modelo_opcion)  # Verificar lo que se recibe

        if modelo_opcion in ['modelo1', 'modelo2']:
            try:
                payload = {'modelo': modelo_opcion}  # Crea el payload para la solicitud
                print(f"Enviando solicitud a Flask para: {payload}")  # Mensaje de depuración

                response = requests.post(
                    'http://127.0.0.1:5000/modelo',
                    json=payload  # Esto establece el Content-Type a application/json
                )
                print(f"Respuesta de Flask: {response.status_code}")  # Imprimir el código de estado de la respuesta

                if response.status_code == 200:
                    data = response.json()
                    modelo_titulo = data.get('titulo')
                    modelo_text = data.get('texto')
                    #modelo_mensaje = f"Se está mostrando: {modelo_opcion}"
                else:
                    modelo_mensaje = f"Error al obtener los datos del modelo. Código de estado: {response.status_code}"

            except requests.exceptions.RequestException as e:
                modelo_mensaje = f"Ocurrió un error en la solicitud: {e}"
                print(modelo_mensaje)

    return render(request, 'ayuda.html', {
        'modelo_text': modelo_text,
        'modelo_titulo': modelo_titulo,
    })