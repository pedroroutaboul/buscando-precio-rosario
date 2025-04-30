#!/bin/bash

# Activar el entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Instalar dependencias si no están instaladas
if [ ! -f "requirements.txt" ]; then
    echo "Creando requirements.txt..."
    echo "flask==3.0.2" > requirements.txt
    echo "requests==2.31.0" >> requirements.txt
    echo "beautifulsoup4==4.12.3" >> requirements.txt
    echo "flask-cors==4.0.0" >> requirements.txt
fi

pip install -r requirements.txt

# Levantar el servidor Flask
echo "Iniciando servidor en http://localhost:5000"
python app.py 