function searchProducts() {
    const query = document.getElementById('searchInput').value;
    const resultsContainer = document.getElementById('results');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMessage = document.getElementById('errorMessage');
    const searchSources = document.getElementById('searchSources'); // Obtener el elemento para mostrar los supermercados

    loadingIndicator.style.display = 'block';
    errorMessage.style.display = 'none';
    resultsContainer.innerHTML = '';

    fetch(`https://pedroroutaboul.pythonanywhere.com/search?query=${query}`)
        .then(response => response.json())
        .then(data => {
            loadingIndicator.style.display = 'none';
            data.products.forEach(product => {
                const productDiv = document.createElement('div');
                productDiv.classList.add('product');
                const productInfo = document.createElement('div');
                productInfo.classList.add('product-info');
                const productName = document.createElement('h2');
                productName.textContent = product.name;
                const productPrice = document.createElement('p');
                productPrice.textContent = `Precio: $${product.price}`;
                const productSource = document.createElement('p');
                productSource.textContent = `Super: ${product.source}`;
                productInfo.appendChild(productName);
                productInfo.appendChild(productPrice);
                productInfo.appendChild(productSource);
                const productImage = document.createElement('img');
                productImage.src = product.image;
                productDiv.appendChild(productImage);
                productDiv.appendChild(productInfo);
                resultsContainer.appendChild(productDiv);
            });

            // Actualizamos el texto de los supermercados
            searchSources.textContent = `Supermercados: ${data.success_scrapper.join(', ')}`;
        })
        .catch(error => {
            loadingIndicator.style.display = 'none';
            errorMessage.textContent = 'Error al obtener los datos. Por favor, inténtelo de nuevo.';
            errorMessage.style.display = 'block';
            console.error('Error al obtener los datos:', error);
        });
}

document.getElementById('searchInput').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        searchProducts();
    }
});
