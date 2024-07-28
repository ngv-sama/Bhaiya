document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('recommendation-form');
    const recommendationsDiv = document.getElementById('recommendations');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);

        // Log form data for debugging
        for (let pair of formData.entries()) {
            console.log(pair[0] + ': ' + pair[1]);
        }
        
        fetch('/get_recommendations', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            console.log("Response status:", response.status);
            return response.json().catch(error => {
                console.error("Error parsing JSON:", error);
                throw new Error("Invalid JSON response");
            });
        })
        .then(data => {
            console.log("Received data:", data);
            recommendationsDiv.innerHTML = '';
            if (Array.isArray(data)) {
                data.forEach(item => {
                    // Clean up the base64 string if it includes extra characters
                    let base64Image = item.image;
                    if (base64Image.startsWith("b'")) {
                        base64Image = base64Image.slice(2, -1);
                    }
                    
                    console.log(base64Image);
                    const itemDiv = document.createElement('div');
                    itemDiv.className = 'item';
                    try {
                        itemDiv.innerHTML = `
                            <img src="data:image/jpeg;base64,${base64Image}" alt="${item.id}">
                            <p>Price: ${item.price}</p>
                            <p>ID: ${item.id}</p>
                            <a href="/item/${item.id}">View</a>
                        `;
                    } catch (error) {
                        console.error("Error rendering item:", error);
                        itemDiv.innerHTML = '<p>Error displaying item</p>';
                    }
                    recommendationsDiv.appendChild(itemDiv);
                });
            } else {
                console.error("Data is not an array:", data);
                recommendationsDiv.innerHTML = '<p>Invalid data format received</p>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            recommendationsDiv.innerHTML = `<p>Error fetching recommendations: ${error.message}</p>`;
        });
    });
});
