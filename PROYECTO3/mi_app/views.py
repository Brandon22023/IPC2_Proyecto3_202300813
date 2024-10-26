from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import requests
from django.http import JsonResponse
from django.conf import settings
import os

# Vista para cargar datos (Cargar Archivo)

def inicio(request):
    return render(request, 'inicio.html')# Vista para cargar datos (Cargar Archivo)
# Vista para cargar el archivo y mostrar su contenido

def cargar_archivo(request):
    contenido_xml = request.session.get('contenido_xml', "")  # Obtener contenido guardado en la sesión
    archivo_info = ""  # Variable para almacenar la información del archivo

    if request.method == 'POST':
        if 'archivo' in request.FILES:  # Si se sube un archivo
            archivo = request.FILES['archivo']
            fs = FileSystemStorage()  # Crear una instancia de FileSystemStorage

            # Definir el nombre del archivo que se guardará
            nombre_archivo = 'entrada_mandado_flask.xml'
            ruta_archivo = os.path.join(fs.location, nombre_archivo)

            # Sobrescribir el archivo si ya existe
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)  # Eliminar el archivo existente

            # Guardar el nuevo archivo
            archivo_path = fs.save(nombre_archivo, archivo)  # Guardar el archivo en la carpeta de medios

            # Leer el contenido del archivo guardado
            with fs.open(archivo_path) as archivo_guardado:
                contenido_xml = archivo_guardado.read().decode('utf-8')  # Leer y decodificar el archivo a texto

            request.session['contenido_xml'] = contenido_xml  # Guardar en la sesión
            
            # Construir la dirección completa del archivo
            direccion_completa = os.path.abspath(ruta_archivo)  # Obtener la ruta completa
            archivo_info = f"Archivo guardado como: {nombre_archivo} en la dirección: {direccion_completa}"
        elif 'reset' in request.POST:  # Si se presiona el botón Reset
            contenido_xml = ""
            request.session['contenido_xml'] = ""  # Limpiar la sesión

    return render(request, 'cargar_archivo.html', {
        'contenido_xml': contenido_xml,
        'archivo_info': archivo_info  # Pasar la información del archivo al template
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