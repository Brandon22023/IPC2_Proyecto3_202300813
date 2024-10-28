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
    mostrar_textarea = False  # Controla la visualización del textarea
    contenido_resultado_xml = ""  # Contenido para el textarea

    if request.method == 'POST':
        modelo_texto = request.POST.get('modelo_texto')

        if modelo_texto == 'modelo1':
            modelo_mensaje = "Consultar datos seleccionado."
            mostrar_textarea = True  # Activar textarea

            try:
                # Enviar solicitud a Flask y recibir contenido XML
                response = requests.post('http://127.0.0.1:5000/consultar_datos')
                
                # Procesar la respuesta de Flask
                if response.status_code == 200:
                    contenido_resultado_xml = response.text  # Captura el contenido XML
                else:
                    contenido_resultado_xml = "Error al consultar datos en el servidor Flask."
            except requests.exceptions.RequestException as e:
                contenido_resultado_xml = f"Error de conexión: {e}"

        elif modelo_texto == 'modelo2':
            modelo_mensaje = "Resumen de clasificación por fecha seleccionado."
        # Puedes continuar con los otros modelos como antes

    return render(request, 'peticiones.html', {
        'modelo_mensaje': modelo_mensaje,
        'mostrar_textarea': mostrar_textarea,
        'contenido_resultado_xml': contenido_resultado_xml
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