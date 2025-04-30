from app import get_gallega
import json
from datetime import datetime
import requests

def test_gallega():
    # Productos de prueba
    productos_prueba = [
        "leche",
        "pan",
        "coca cola",
        "arroz"
    ]
    
    resultados = {}
    errores_imagenes = []
    
    for producto in productos_prueba:
        print(f"\nBuscando: {producto}")
        productos = get_gallega(producto)
        
        # Verificar imágenes
        for p in productos:
            if p['image']:
                try:
                    response = requests.head(p['image'], timeout=5)
                    if response.status_code != 200:
                        errores_imagenes.append({
                            'producto': p['name'],
                            'url': p['image'],
                            'error': f'Status code: {response.status_code}'
                        })
                except Exception as e:
                    errores_imagenes.append({
                        'producto': p['name'],
                        'url': p['image'],
                        'error': str(e)
                    })
        
        # Guardar resultados
        resultados[producto] = productos
        
        # Mostrar resultados
        print(f"Encontrados {len(productos)} productos:")
        for p in productos:
            print(f"- {p['name']}: ${p['price']}")
            if p['image']:
                print(f"  Imagen: {p['image']}")
    
    # Guardar resultados en un archivo JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"resultados_gallega_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    # Guardar errores de imágenes si los hay
    if errores_imagenes:
        errores_filename = f"errores_imagenes_gallega_{timestamp}.json"
        with open(errores_filename, 'w', encoding='utf-8') as f:
            json.dump(errores_imagenes, f, ensure_ascii=False, indent=2)
        print(f"\nErrores de imágenes guardados en {errores_filename}")
    
    print(f"\nResultados guardados en {filename}")

if __name__ == "__main__":
    test_gallega() 