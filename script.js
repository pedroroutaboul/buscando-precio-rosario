// Configuración de URLs
const CONFIG = {
    production: 'https://pedroroutaboul.pythonanywhere.com',
    local: 'http://localhost:5001'
};

// Función para obtener el modo actual (local o producción)
function getApiUrl() {
    // Primero intentamos obtener el modo de los parámetros de la URL
    const urlParams = new URLSearchParams(window.location.search);
    const mode = urlParams.get('mode');
    
    if (mode === 'local') {
        return CONFIG.local;
    }
    
    return CONFIG.production;
}

let currentSort = {
    column: 'price',
    direction: 'asc'
};

let currentData = null; // Variable para mantener los datos actuales

function searchProducts() {
    const searchInput = document.getElementById('searchInput');
    const query = searchInput.value.trim();
    
    if (!query) {
        alert('Por favor ingrese un término de búsqueda');
        return;
    }

    const resultsBody = document.getElementById('resultsBody');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMessage = document.getElementById('errorMessage');

    resultsBody.innerHTML = '';
    loadingIndicator.style.display = 'block';
    errorMessage.style.display = 'none';

    fetch(`/search?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            loadingIndicator.style.display = 'none';
            currentData = data; // Guardar los datos actuales
            displayResults(data);
        })
        .catch(error => {
            loadingIndicator.style.display = 'none';
            errorMessage.textContent = 'Error al buscar productos: ' + error.message;
            errorMessage.style.display = 'block';
        });
}

function displayResults(data) {
    const resultsBody = document.getElementById('resultsBody');
    resultsBody.innerHTML = '';

    // Combinar y ordenar resultados
    let allProducts = [];
    Object.entries(data).forEach(([supermarket, products]) => {
        products.forEach(product => {
            allProducts.push({
                ...product,
                supermarket: product.source // Usar el source del producto
            });
        });
    });

    // Ordenar productos
    allProducts.sort((a, b) => {
        if (currentSort.column === 'price') {
            return currentSort.direction === 'asc' 
                ? a.price - b.price 
                : b.price - a.price;
        }
        return 0;
    });

    // Mostrar productos en la tabla
    allProducts.forEach(product => {
        const row = document.createElement('tr');
        const supermarketName = product.supermarket === 'coto' ? 'Coto' : 'La Gallega';
        row.innerHTML = `
            <td><img src="${product.image}" alt="${product.name}" class="product-image"></td>
            <td>${product.name}</td>
            <td class="price">$${product.price.toFixed(2)}</td>
            <td><span class="supermarket-label ${product.supermarket}">${supermarketName}</span></td>
        `;
        resultsBody.appendChild(row);
    });
}

// Agregar event listeners para ordenar por columna
document.querySelectorAll('th').forEach(header => {
    header.addEventListener('click', () => {
        const column = header.textContent.toLowerCase();
        if (column === 'precio') {
            currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
            currentSort.column = 'price';
            if (currentData) {
                displayResults(currentData);
            }
        }
    });
});

document.getElementById('searchInput').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        searchProducts();
    }
});

// Agregar botón para cambiar modo
function toggleMode() {
    const currentUrl = new URL(window.location.href);
    const currentMode = currentUrl.searchParams.get('mode');
    
    if (currentMode === 'local') {
        currentUrl.searchParams.delete('mode');
    } else {
        currentUrl.searchParams.set('mode', 'local');
    }
    
    window.location.href = currentUrl.toString();
}

// Inicialización
window.onload = function() {
    const apiUrl = getApiUrl();
    const modeIndicator = document.getElementById('modeIndicator');
    modeIndicator.textContent = `Modo: ${apiUrl === CONFIG.local ? 'Local' : 'Producción'}`;
};
