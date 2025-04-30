# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import json
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuración para servir archivos estáticos
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

ROSARIO_SOURCES = ['lagallega', 'coto', 'jumbo']
def get_coto(query):
    url = "https://www.cotodigital.com.ar/sitios/cdigi/categoria"
    
    # Parámetros necesarios para la búsqueda
    params = {
        "_dyncharset": "utf-8",
        "Dy": "1",
        "Ntt": query,
        "format": "json",
        "Nf": "product.endDate|GTEQ+1.7459712E12||product.startDate|LTEQ+1.7459712E12",
        "Nr": "AND(product.sDisp_200:1004,product.language:español,OR(product.siteId:CotoDigital))",
        "Ns": "product.displayName|0||sku.activePrice|0",
        "No": "0",  # Offset inicial
        "Nrpp": "12"  # Resultados por página
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
        'Referer': 'https://www.cotodigital.com.ar/'
    }
    
    try:
        print(f"Realizando solicitud a: {url}")
        print(f"Parámetros: {params}")
        response = requests.get(url, headers=headers, params=params, timeout=5)
        print(f"Status Code: {response.status_code}")
        response.raise_for_status()
        
        # Intentar parsear la respuesta JSON
        try:
            data = response.json()
            print("Respuesta JSON recibida correctamente")
            
            # Guardar información relevante para debug
            debug_info = {
                "url": url,
                "params": params,
                "status_code": response.status_code,
                "sample_records": []
            }
            
            productos = []
            
            # Navegar la estructura JSON para encontrar los productos
            if 'contents' in data:
                for content in data['contents']:
                    if isinstance(content, dict) and 'Main' in content:
                        for main_item in content['Main']:
                            if isinstance(main_item, dict) and 'contents' in main_item:
                                for sub_content in main_item['contents']:
                                    if isinstance(sub_content, dict) and 'records' in sub_content:
                                        for record in sub_content['records'][:5]:  # Solo procesar los primeros 5 productos
                                            try:
                                                # Guardar información completa del registro para debug
                                                debug_info["sample_records"].append({
                                                    "raw_record": record,
                                                    "attributes": record.get('attributes', {}),
                                                    "all_fields": list(record.keys())
                                                })
                                                
                                                # Extraer datos del producto
                                                attributes = record.get('attributes', {})
                                                
                                                # Buscar el precio y la imagen en los registros anidados
                                                price = 0.0
                                                image_url = None
                                                if 'records' in record:
                                                    for sub_record in record['records']:
                                                        if isinstance(sub_record, dict) and 'attributes' in sub_record:
                                                            sub_attrs = sub_record['attributes']
                                                            # Buscar precio
                                                            if 'sku.referencePrice' in sub_attrs:
                                                                try:
                                                                    price = float(sub_attrs['sku.referencePrice'][0])
                                                                except (ValueError, IndexError):
                                                                    continue
                                                            # Buscar imagen
                                                            if 'product.mediumImage.url' in sub_attrs:
                                                                image_url = sub_attrs['product.mediumImage.url'][0]
                                                
                                                # Si no hay URL de imagen, usar una imagen por defecto
                                                if not image_url:
                                                    image_url = "https://via.placeholder.com/150?text=Sin+imagen"
                                                
                                                product = {
                                                    "id": str(attributes.get('product.id', '')),
                                                    "name": attributes.get('product.displayName', ['Producto sin nombre'])[0],
                                                    "link": attributes.get('product.detailsURL'),
                                                    "image": image_url,
                                                    "price": price,
                                                    "unavailable": not attributes.get('product.available', True),
                                                    "source": "coto",
                                                    "unitFactor": attributes.get('product.unitFactor', 0),
                                                    "unit": attributes.get('product.unit', ''),
                                                    "unitPrice": float(attributes.get('product.unitPrice', [0])[0])
                                                }
                                                productos.append(product)
                                                print(f"Producto procesado: {product['name']} - Precio: ${product['price']}")
                                            except Exception as e:
                                                print(f"Error procesando producto individual: {str(e)}")
                                                continue
            
            # Guardar información de debug
            with open('debug_coto.json', 'w', encoding='utf-8') as f:
                json.dump(debug_info, f, ensure_ascii=False, indent=2)
            
            print(f"Total de productos encontrados: {len(productos)}")
            return productos
            
        except json.JSONDecodeError as e:
            print(f"Error decodificando JSON: {str(e)}")
            print("Contenido de la respuesta:", response.text[:200])
            return []
                
    except requests.RequestException as e:
        print(f"Error en la solicitud a Coto: {str(e)}")
        return []
    except Exception as e:
        print(f"Error inesperado en get_coto: {str(e)}")
        return []


def get_gallega(query):
    # Crear una sesión
    session = requests.Session()
    errores_imagenes = []

    # Realizar una solicitud inicial para obtener cookies
    response_inicial = session.get('https://www.lagallega.com.ar/')

    # Verificamos si la solicitud fue exitosa (código 200)
    if response_inicial.status_code == 200:
        # Obtenemos las cookies de la respuesta
        cookies = response_inicial.cookies

        # URL de la página
        url = 'https://www.lagallega.com.ar/Productos.asp'

        # Parámetros de la solicitud
        params = {
            'cpoBuscar': query
        }
        headers = {
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9,es-US;q=0.8,es;q=0.7',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Referer': 'https://www.lagallega.com.ar/ccompra.asp',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        }

        print(f"Realizando solicitud a: {url}")
        print(f"Parámetros: {params}")

        # Realizamos la solicitud
        response = session.get(url, params=params, headers=headers)
        print(f"Status Code: {response.status_code}")

        # Verificamos si la solicitud fue exitosa (código 200)
        if response.status_code == 200:
            # Obtenemos el contenido HTML
            html_content = response.text

            # Parseamos el HTML
            soup = BeautifulSoup(html_content, 'html.parser')

            # Encontramos todos los elementos <li> que tienen la clase "cuadProd"
            productos = soup.find_all('li', class_='cuadProd')

            # Creamos una lista para almacenar los datos de los productos
            productos_list = []

            # Iteramos sobre los elementos encontrados
            for producto in productos:
                try:
                    # Extraemos la información relevante de cada producto
                    img_element = producto.find('img')
                    if not img_element or 'src' not in img_element.attrs:
                        continue
                        
                    img_src = img_element['src']
                    nombre = producto.find('div', class_='desc').text.strip()
                    precio_texto = producto.find('div', class_='precio').text.strip()

                    precio = float(precio_texto.replace('$', '').replace('.', '').replace(',','.'))
                    id = img_src.split('/')[-1].split('.')[0]
                    
                    # Construir URL de la imagen
                    image_url = f"https://www.lagallega.com.ar/Fotos/Articulos/{id.strip()}.jpg"
                    
                    # Verificar si la imagen existe
                    try:
                        img_response = requests.head(image_url, timeout=5)
                        if img_response.status_code != 200:
                            print(f"Imagen no encontrada para {nombre}: {image_url}")
                            image_url = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTUwIiBoZWlnaHQ9IjE1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTUwIiBoZWlnaHQ9IjE1MCIgZmlsbD0iI2VlZSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM5OTkiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5TaW4gaW1hZ2VuPC90ZXh0Pjwvc3ZnPg=="
                            errores_imagenes.append({
                                'producto': nombre,
                                'url': image_url,
                                'error': f'Status code: {img_response.status_code}'
                            })
                    except Exception as e:
                        print(f"Error verificando imagen para {nombre}: {str(e)}")
                        image_url = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTUwIiBoZWlnaHQ9IjE1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTUwIiBoZWlnaHQ9IjE1MCIgZmlsbD0iI2VlZSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM5OTkiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5TaW4gaW1hZ2VuPC90ZXh0Pjwvc3ZnPg=="
                        errores_imagenes.append({
                            'producto': nombre,
                            'url': image_url,
                            'error': str(e)
                        })
                    
                    # Creamos el diccionario con la información
                    producto_dict = {
                        "id": id,
                        "name": nombre,
                        "link": None,
                        "image": image_url,
                        "price": precio,
                        "unavailable": False,
                        "source": "lagallega",
                        "unitFactor": 0,
                        "unit": "",
                        "unitPrice": 0
                    }

                    # Agregamos el diccionario a la lista de productos
                    productos_list.append(producto_dict)
                    print(f"Producto procesado: {nombre} - Precio: ${precio}")
                except Exception as e:
                    print(f"Error procesando producto de La Gallega: {str(e)}")
                    continue
            
            # Guardar errores de imágenes si los hay
            if errores_imagenes:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                errores_filename = f"errores_imagenes_gallega_{timestamp}.json"
                with open(errores_filename, 'w', encoding='utf-8') as f:
                    json.dump(errores_imagenes, f, ensure_ascii=False, indent=2)
                print(f"\nErrores de imágenes guardados en {errores_filename}")
            
            print(f"Total de productos encontrados: {len(productos_list)}")
            return productos_list
        else:
            print('Error al obtener la página:', response.status_code)
            return []
    else:
        print('Error al obtener la página inicial:', response_inicial.status_code)
        return []

def get_ratoneando(query):
    url = 'https://api.ratoneando.ar/'
    headers = {
        'authority': 'api.ratoneando.ar',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,es-US;q=0.8,es;q=0.7',
        'dnt': '1',
        'origin': 'https://ratoneando.ar',
        'referer': 'https://ratoneando.ar/',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    params = {
        'q': query
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        return products
    else:
        print('Error:', response.status_code)
        return []

def filter_by(all_products, allowed_sources):
    for p in all_products:
        if p.get('source') not in allowed_sources:
            all_products.remove(p)
    return all_products

def search(query='', allowed_sources=ROSARIO_SOURCES):
    all_products = []
    all_products+=get_gallega(query)
    # all_products.append(get_ratoneando(query))
    all_products+=get_coto(query)
    if allowed_sources:
        all_products = filter_by(all_products, allowed_sources)
    all_products = sorted(all_products, key=lambda x: x['price'])

    return all_products
# Press the green button in the gutter to run the script.

@app.route('/search')
def search_endpoint():
    query = request.args.get('query', '')
    allowed_sources = request.args.get('allowed_sources', ROSARIO_SOURCES)

    search_result = search(query=query, allowed_sources=allowed_sources)
    return jsonify({'products': search_result})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
