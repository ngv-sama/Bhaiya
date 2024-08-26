window.addEventListener('beforeunload', (event) => {
    console.log('User is leaving the page');
    const data = JSON.stringify({"Status": "User is leaving the page"});
    navigator.sendBeacon('/save_chat_history', data);
});

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('chat-form');
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const imageUpload = document.getElementById('image-upload');
    const imagePreview = document.getElementById('image-preview');
    const username = document.getElementById('username');
    const email = document.getElementById('user-email');
    const newChatButton = document.getElementById('new-chat-button');
    const chatHistoryList = document.getElementById('chat-history-list');

    let conversations = {};
    let currentConversationId = null;

    function loadConversationsFromServer() {
        fetch('/get_chat_history')
            .then(response => response.json())
            .then(data => {
                conversations = data.conversations || {};
                currentConversationId = data.currentConversationId;
                updateConversationsList();
                loadCurrentConversation();
            })
            .catch(error => console.error('Error loading chat history:', error));
    }

    function createNewConversation() {
        const conversationId = Date.now().toString();
        conversations[conversationId] = [];
        saveChatToServer();
        return conversationId;
    }

    function switchConversation(conversationId) {
        saveChatToServer();
        currentConversationId = conversationId;
        loadCurrentConversation();
    }

    function loadCurrentConversation() {
        if (!currentConversationId || !conversations[currentConversationId]) {
            currentConversationId = createNewConversation();
        }
        chatMessages.innerHTML = '';
        conversations[currentConversationId].forEach(message => {
            addMessageToDOM(message.content, message.type, message.imageUrl);
        });
    }

    function updateConversationsList() {
        chatHistoryList.innerHTML = '';
        Object.keys(conversations).forEach((conversationId) => {
            const conversation = conversations[conversationId];
            if (conversation.length > 0) {
                const firstMessage = conversation.find(msg => msg.type === 'sent');
                if (firstMessage) {
                    const li = document.createElement('li');
                    li.className = 'conversation-item';
                    const date = new Date(parseInt(conversationId));
                    const formattedDate = date.toLocaleString('en-US', { 
                        month: 'short', 
                        day: 'numeric', 
                        year: 'numeric', 
                        hour: 'numeric', 
                        minute: 'numeric'
                    });
                    li.innerHTML = `
                        <div class="conversation-date">${formattedDate}</div>
                        <div class="conversation-preview">${firstMessage.content}</div>
                    `;
                    li.onclick = () => switchConversation(conversationId);
                    chatHistoryList.appendChild(li);
                }
            }
        });
    }

    function saveChatToServer() {
        const data = {
            conversations: conversations,
            currentConversationId: currentConversationId
        };

        fetch('/save_chat_history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => console.log('Chat history saved:', data))
        .catch(error => console.error('Error saving chat history:', error));
    }

    function fetchUserProfile() {
        fetch('/get_profile')
        .then(response => response.json())
        .then(data => {
            console.log("Received data:", data);
            username.textContent = data.username;
            email.textContent = data.email;
            if (conversations[currentConversationId].length === 0) {
                addMessage(`Hello, ${username.textContent}! I am bhAIya, your neighbourhood shopkeeper. How can I help?`, 'received');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    function addMessage(content, type, imageUrl = null) {
        addMessageToDOM(content, type, imageUrl);
        if (currentConversationId) {
            conversations[currentConversationId].push({ content, type, imageUrl, timestamp: Date.now() });
            saveChatToServer();
        }
    }

    function addMessageToDOM(content, type, imageUrl = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        let messageContent;
        if(content){
            messageContent = `<p>${content}`;
        }
        if (imageUrl) {
            messageContent = `<img src="${imageUrl}" alt="User uploaded image"><p>${content}`;
        }
        if(messageContent){
            messageDiv.innerHTML = messageContent;
        }
        console.log(messageDiv)
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
                let responseHTML = 'Hey! Found something you might like. Take a look:';
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
                                <a href="/item/${item.id}" class="view-product" data-id="${item.id}" data-image="${base64Image}" data-price="${item.price}">View</a>
                            </div>
                        `;
                    });
                    responseHTML += '</div>';
                } else {
                    responseHTML = 'Sorry, I couldn\'t find any recommendations.';
                }
                addMessage(responseHTML, 'received');
                saveChatToServer();
            })
            .catch(error => {
                console.error('Error:', error);
                removeTypingIndicator(typingIndicator);
                addMessage('Sorry, there was an error processing your request.', 'received');
                saveChatToServer();
            });
        }
    });

    function viewProduct(event) {
        if (event.target.classList.contains('view-product')) {
            event.preventDefault();
            const id = event.target.getAttribute('data-id');
            const image = event.target.getAttribute('data-image');
            const price = event.target.getAttribute('data-price');
    
            // Store the image and price in sessionStorage
            sessionStorage.setItem(`product_${id}_image`, image);
            sessionStorage.setItem(`product_${id}_price`, price);
    
            // Navigate to the product page
            window.location.href = `/item/${id}`;
        }
    }

    document.addEventListener('click', viewProduct);

    newChatButton.addEventListener('click', function() {
        saveChatToServer();
        switchConversation(createNewConversation());
        fetchUserProfile(); // This will add the initial greeting message
    });

    // Sidebar functionality
    const sideDrawer = document.getElementById('sideDrawer');
    const drawerHandle = document.getElementById('drawerHandle');
    let isDragging = false;
    let isHandleActive = false;
    let startX, startLeft;
    let longPressTimer;
    const longPressDuration = 300; // milliseconds
    
    // Initialize the drawer on the right side
    sideDrawer.classList.add('left');
    
    function openDrawer() {
        sideDrawer.classList.add('open');
    }
    
    function closeDrawer() {
        sideDrawer.classList.remove('open');
    }
    
    function toggleDrawer() {
        sideDrawer.classList.toggle('open');
    }
    
    drawerHandle.addEventListener('mousedown', startLongPress);
    drawerHandle.addEventListener('touchstart', startLongPress);
    
    document.addEventListener('mousemove', drag);
    document.addEventListener('touchmove', drag);
    
    document.addEventListener('mouseup', endDrag);
    document.addEventListener('touchend', endDrag);
    
    // Toggle drawer when clicking the handle
    drawerHandle.addEventListener('click', () => {
        toggleDrawer();
    });
    
    function startLongPress(e) {
        e.preventDefault(); // Prevent default behavior
        isHandleActive = true; // Indicate that the handle was the initial target
        startX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
        startLeft = sideDrawer.offsetLeft;
    
        longPressTimer = setTimeout(() => {
            isDragging = true;
            sideDrawer.classList.add('dragging');
        }, longPressDuration);
    }
    
    function drag(e) {
        if (!isDragging) return;
    
        const currentX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
        const diffX = currentX - startX;
        const newLeft = startLeft + diffX;
    
        if (newLeft > window.innerWidth / 2) {
            sideDrawer.style.left = '';
            sideDrawer.style.right = '0';
            sideDrawer.classList.remove('left');
            sideDrawer.classList.add('right');
        } else {
            sideDrawer.style.right = '';
            sideDrawer.style.left = '0';
            sideDrawer.classList.remove('right');
            sideDrawer.classList.add('left');
        }
    
        openDrawer();
    }
    
    function endDrag(e) {
        clearTimeout(longPressTimer);
    
        if (isDragging) {
            isDragging = false;
            sideDrawer.classList.remove('dragging');
        }
    
        // Reset the handle active state
        isHandleActive = false;
    }

    // Initialize
    loadConversationsFromServer();
    fetchUserProfile();
});