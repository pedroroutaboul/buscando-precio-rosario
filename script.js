function searchProducts() {
    const query = document.getElementById('searchInput').value;
    fetch(`pedroroutaboul.pythonanywhere.com/search?query=${query}`)
        .then(response => response.json())
        .then(data => {
            const resultsContainer = document.getElementById('results');
            resultsContainer.innerHTML = '';
            data.products.forEach(product => {
                const productDiv = document.createElement('div');
                productDiv.classList.add('product');
                const productInfo = document.createElement('div');
                productInfo.classList.add('product-info');
                const productName = document.createElement('h2');
                productName.textContent = product.name;
                const productPrice = document.createElement('p');
                productPrice.textContent = `Price: $${product.price}`;
                const productSource = document.createElement('p');
                productSource.textContent = `Source: ${product.source}`;
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
            console.error('Error fetching data:', error);
        });
}
