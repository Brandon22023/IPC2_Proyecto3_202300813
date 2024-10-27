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
        
        # Renderizar la plantilla sin datos
        return render(request, 'cargar_archivo.html', {
            'contenido_xml': '',
            'archivo_info': ''
        })
    
    elif request.method == 'POST' and 'archivo' in request.FILES:
        # Cargar archivo XML y enviar a Flask
        archivo = request.FILES['archivo']
        respuesta = requests.post(
            'http://127.0.0.1:5000/cargar_archivo',
            files={'archivo': archivo}
        )
        
        # Procesar la respuesta de Flask para obtener contenido y ruta
        if respuesta.status_code == 200:
            data = respuesta.json()
            request.session['contenido_xml'] = data.get('contenido_xml', '')
            request.session['archivo_info'] = data.get('ruta_archivo', '')
        else:
            request.session['contenido_xml'] = "Error al cargar el archivo."
            request.session['archivo_info'] = ''

    # Renderizar la plantilla con los datos actuales desde la sesión
    return render(request, 'cargar_archivo.html', {
        'contenido_xml': request.session.get('contenido_xml', ''),
        'archivo_info': request.session.get('archivo_info', '')
    })


def peticiones(request):
    # Lógica de la vista aquí
    return render(request, 'peticiones.html')


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