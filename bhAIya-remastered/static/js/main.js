document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('chat-form');
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const imageUpload = document.getElementById('image-upload');
    const imagePreview = document.getElementById('image-preview');

    function addMessage(content, type, imageUrl = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        let messageContent = `<p>${content}</p>`;
        if (imageUrl) {
            messageContent = `<img src="${imageUrl}" alt="User uploaded image"><p>${content}</p>`;
        }
        messageDiv.innerHTML = messageContent;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.innerHTML = '<span></span><span></span><span></span>';
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return typingDiv;
    }

    function removeTypingIndicator(indicator) {
        if (indicator && indicator.parentNode) {
            indicator.parentNode.removeChild(indicator);
        }
    }

    imageUpload.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.innerHTML = `
                    <img src="${e.target.result}" alt="Image preview">
                    <span class="delete-image">&times;</span>
                `;
                imagePreview.querySelector('.delete-image').addEventListener('click', function() {
                    imagePreview.innerHTML = '';
                    imageUpload.value = '';
                });
            }
            reader.readAsDataURL(file);
        }
    });

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        const userMessage = userInput.value.trim();
        const uploadedImage = imageUpload.files[0];

        if (userMessage || uploadedImage) {
            let imageUrl = null;
            if (uploadedImage) {
                imageUrl = URL.createObjectURL(uploadedImage);
            }
            addMessage(userMessage, 'sent', imageUrl);
            userInput.value = '';
            imagePreview.innerHTML = '';
            imageUpload.value = '';
            const typingIndicator = showTypingIndicator();

            fetch('/get_recommendations', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                console.log("Received data:", data);
                removeTypingIndicator(typingIndicator);
                let responseHTML = 'Here are some recommendations:';
                if (Array.isArray(data) && data.length > 0) {
                    responseHTML += '<div class="product-grid">';
                    data.forEach(item => {
                        let base64Image = item.image;
                        if (base64Image.startsWith("b'")) {
                            base64Image = base64Image.slice(2, -1);
                        }
                        responseHTML += `
                            <div class="item">
                                <img src="data:image/jpeg;base64,${base64Image}" alt="${item.id}">
                                <p>Price: ${item.price}</p>
                                <p>ID: ${item.id}</p>
                                <a href="/item/${item.id}">View</a>
                            </div>
                        `;
                    });
                    responseHTML += '</div>';
                } else {
                    responseHTML = 'Sorry, I couldn\'t find any recommendations.';
                }
                addMessage(responseHTML, 'received');
            })
            .catch(error => {
                console.error('Error:', error);
                removeTypingIndicator(typingIndicator);
                addMessage('Sorry, there was an error processing your request.', 'received');
            });
        }
    });
});