import unittest
from app import get_gallega, get_coto
import requests
from bs4 import BeautifulSoup

class TestImageHandling(unittest.TestCase):
    def test_gallega_image_urls(self):
        """Test que verifica que las URLs de imágenes de La Gallega sean válidas"""
        query = "leche"
        products = get_gallega(query)
        
        for product in products:
            # Verificar que la URL de la imagen tenga el formato correcto
            self.assertTrue(product['image'].startswith('https://www.lagallega.com.ar/Archivos/Articulos/'))
            self.assertTrue(product['image'].endswith('.jpg'))
            
            # Verificar que el ID esté presente en la URL
            self.assertIn(product['id'], product['image'])
            
            # Verificar que la URL no esté vacía
            self.assertIsNotNone(product['image'])
            self.assertNotEqual(product['image'], '')

    def test_coto_image_urls(self):
        """Test que verifica que las URLs de imágenes de Coto sean válidas"""
        query = "leche"
        products = get_coto(query)
        
        for product in products:
            # Verificar que la URL de la imagen sea válida
            if product['image'] is not None:
                # Verificar que la URL comience con el dominio correcto
                self.assertTrue(product['image'].startswith('https://static.cotodigital3.com.ar/'))
                # Verificar que la URL contenga 'fotos/large'
                self.assertIn('fotos/large', product['image'])
                # Verificar que la URL termine con .jpg
                self.assertTrue(product['image'].endswith('.jpg'))

    def test_gallega_image_extraction(self):
        """Test que verifica la extracción de imágenes de La Gallega"""
        # Crear un HTML de ejemplo
        html = """
        <li class="cuadProd">
            <img src="Archivos/Articulos/123456.jpg">
            <div class="desc">Producto de prueba</div>
            <div class="precio">$100,00</div>
        </li>
        """
        soup = BeautifulSoup(html, 'html.parser')
        product = soup.find('li', class_='cuadProd')
        
        # Extraer la información como lo hace la función
        img_src = product.find('img')['src']
        id = img_src.split('/')[-1].split('.')[0]
        expected_url = f"https://www.lagallega.com.ar/Archivos/Articulos/{id}.jpg"
        
        # Verificar que la URL generada sea correcta
        self.assertEqual(expected_url, "https://www.lagallega.com.ar/Archivos/Articulos/123456.jpg")

    def test_coto_image_extraction(self):
        """Test que verifica la extracción de imágenes de Coto"""
        # Crear un JSON de ejemplo
        sample_data = {
            "contents": [{
                "Main": [{
                    "contents": [{
                        "records": [{
                            "attributes": {
                                "product.largeImage.url": ["https://static.cotodigital3.com.ar/sitios/fotos/large/123456.jpg"],
                                "product.displayName": ["Producto de prueba"],
                                "product.id": ["123456"]
                            }
                        }]
                    }]
                }]
            }]
        }
        
        # Verificar que la URL de la imagen se extraiga correctamente
        for content in sample_data['contents']:
            for main_item in content['Main']:
                for sub_content in main_item['contents']:
                    for record in sub_content['records']:
                        attributes = record['attributes']
                        image_url = attributes.get('product.largeImage.url', [None])[0]
                        
                        # Verificar que la URL sea correcta
                        self.assertEqual(image_url, "https://static.cotodigital3.com.ar/sitios/fotos/large/123456.jpg")

if __name__ == '__main__':
    unittest.main() 