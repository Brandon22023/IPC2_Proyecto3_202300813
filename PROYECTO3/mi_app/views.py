from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
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
    return render(request, 'ayuda.html')