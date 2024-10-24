from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import requests
from django.http import JsonResponse
# Vista para cargar datos (Cargar Archivo)

def inicio(request):
    return render(request, 'inicio.html')# Vista para cargar datos (Cargar Archivo)
def cargar_archivo(request):
    contenido_xml = ""
    
    if request.method == 'POST' and request.FILES.get('archivo', None):
        archivo = request.FILES['archivo']
        
        # Leer el contenido del archivo .xml
        contenido_xml = archivo.read().decode('utf-8')  # Decodificar a UTF-8 para trabajar con texto
        
        # Guardar el archivo si es necesario
        fs = FileSystemStorage()
        filename = fs.save(archivo.name, archivo)
        file_url = fs.url(filename)
        
        # Pasar el contenido leido al template para mostrar en el textarea de entrada
        return render(request, 'cargar_archivo.html', {
            'file_url': file_url, 
            'contenido_xml': contenido_xml
        })
    
    # Si no se ha cargado archivo, simplemente renderizar el template vacío
    return render(request, 'cargar_archivo.html')

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