document.addEventListener('DOMContentLoaded', function() {
    const productDetails = document.getElementById('product-details');
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const loadingAnimation = document.getElementById('loading-animation');

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
            showLoadingAnimation();
            fetchProductChat(productId, userMessage);
        }
    });

    function showLoadingAnimation() {
        sendButton.style.display = 'none';
        loadingAnimation.style.display = 'flex';
        userInput.style.borderColor = '#007aff'; // Optional: change border color to match the animation
    }
    
    function hideLoadingAnimation() {
        loadingAnimation.style.display = 'none';
        sendButton.style.display = 'flex';
        userInput.style.borderColor = '#d1d1d6'; // Reset to original border color
    }

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
            
            if (data.error) {
                detailsHTML += `<p>Error: ${data.error}</p>`;
            } else {
                // Display the image
                if (data.image) {
                    let base64Image = data.image;
                    if (base64Image.startsWith("b'")) {
                        base64Image = base64Image.slice(2, -1);
                    }
                    detailsHTML += `<img src="data:image/jpeg;base64,${base64Image}" alt="Product Image" style="max-width: 100%; margin-bottom: 20px;">`;
                }

                // Display other details
                for (const [key, value] of Object.entries(data)) {
                    if (key !== 'image') {
                        detailsHTML += `<p><strong>${key}:</strong> ${value}</p>`;
                    }
                }
            }

            productDetails.innerHTML = detailsHTML;
            generateImageDescription(productId);
        })
        .catch(error => {
            console.error('Error fetching product details:', error);
            productDetails.innerHTML = '<p>Error loading product details.</p>';
        });
    }

    function fetchProductChat(productId, message) {
        // Retrieve the description from local storage
        const description = localStorage.getItem(`product_${productId}_description`) || '';
    
        fetch('/product_chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                id: productId, 
                message: message,
                description: description
            })
        })
        .then(response => response.json())
        .then(data => {
            hideLoadingAnimation();
            addMessage(data.response, 'received');
        })
        .catch(error => {
            hideLoadingAnimation();
            console.error('Error fetching product chat:', error);
            addMessage('Sorry, there was an error processing your request.', 'received');
        });
    }

    function generateImageDescription(productId) {
        fetch('/generate_image_description', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ id: productId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.description) {
                // Save the description in local storage
                localStorage.setItem(`product_${productId}_description`, data.description);
                // Uncomment the next line if you want to display the description as a message
                // addMessage(data.description, 'received');
            } else if (data.error) {
                console.error('Error generating image description:', data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
    
    function addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        // Basic formatting
        content = content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold
            .replace(/\*(.*?)/g, '') 
            .replace(/\*(.*?)\*/g, '<em>$1</em>')  // Italic
            .replace(/`(.*?)`/g, '<code>$1</code>')  // Inline code
            .replace(/\n/g, '<br>')  // Line breaks 
            .replace(/```([\s\S]*?)```/g, function(match, p1) {
                return '<pre><code>' + p1.trim().replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</code></pre>';
            });  // Code blocks
    
        messageDiv.innerHTML = `<p>${content}</p>`;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});