document.addEventListener('DOMContentLoaded', function() {
    const productDetails = document.getElementById('product-details');
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');

    // Get the product ID from the URL
    const productId = window.location.pathname.split('/').pop();

    // Fetch product details
    fetchProductDetails(productId);

    // Add initial chatbot message
    addMessage("Hello! How can I help you with this product?", 'received');

    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const userMessage = userInput.value.trim();
        if (userMessage) {
            addMessage(userMessage, 'sent');
            userInput.value = '';
            fetchProductChat(productId, userMessage);
        }
    });

    function fetchProductDetails(productId) {
        fetch('/get_details', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ id: productId })
        })
        .then(response => response.json())
        .then(data => {
            let detailsHTML = '<h2>Product Details</h2>';
            
            // Get the image and price from sessionStorage
            const image = sessionStorage.getItem(`product_${productId}_image`);
            const price = sessionStorage.getItem(`product_${productId}_price`);
            
            if (image) {
                detailsHTML += `<img src="data:image/jpeg;base64,${image}" alt="Product Image" style="max-width: 100%; margin-bottom: 20px;">`;
            }
            
            if (price) {
                detailsHTML += `<p><strong>Price:</strong> ${price}</p>`;
            }
    
            if (Object.keys(data).length === 0) {
                detailsHTML += '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>';
            } else {
                for (const [key, value] of Object.entries(data)) {
                    if (key !== 'price') { // Avoid duplicating price if it's in the API response
                        detailsHTML += `<p><strong>${key}:</strong> ${value}</p>`;
                    }
                }
            }
            productDetails.innerHTML = detailsHTML;
    
            // Clear the sessionStorage after using the data
            sessionStorage.removeItem(`product_${productId}_image`);
            sessionStorage.removeItem(`product_${productId}_price`);
        })
        .catch(error => {
            console.error('Error fetching product details:', error);
            productDetails.innerHTML = '<p>Error loading product details.</p>';
        });
    }

    function fetchProductChat(productId, message) {
        fetch('/product_chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ id: productId, message: message })
        })
        .then(response => response.json())
        .then(data => {
            addMessage(data.response, 'received');
        })
        .catch(error => {
            console.error('Error fetching product chat:', error);
            addMessage('Sorry, there was an error processing your request.', 'received');
        });
    }

    function addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.innerHTML = `<p>${content}</p>`;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});