function searchProducts() {
    const query = document.getElementById('searchInput').value;
    const resultsContainer = document.getElementById('results');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMessage = document.getElementById('errorMessage');

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
        })
        .catch(error => {
            loadingIndicator.style.display = 'none';
            errorMessage.textContent = 'Error fetching data. Please try again.';
            errorMessage.style.display = 'block';
            console.error('Error fetching data:', error);
        });
}

document.getElementById('searchInput').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        searchProducts();
    }
});
