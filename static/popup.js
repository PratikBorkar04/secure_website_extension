// Wait for the DOM to fully load before running the script
document.addEventListener('DOMContentLoaded', function() {
    // Query the current active tab in the window
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        var currentTab = tabs[0]; // Assuming there's always at least one tab active
        // Check if the current tab has a URL (to avoid extension pages, blank tabs, etc.)
        if (currentTab && currentTab.url) {
            // Make a POST request to your server with the URL of the current tab
            fetch('https://secure-website-extension.onrender.com/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ urlinput: currentTab.url }), // Send the URL in the request body
            })
            .then(response => {
                // Check if the response is successful
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json(); // Parse the JSON response body
            })
            .then(data => {
                const resultElement = document.getElementById('prediction-result');
                // Validate that the necessary data is present
                if (data && data.result1 && data.safe_status) {
                    // Convert the numerical score to a visual star representation
                    const starVisualization = createStarVisualization(data.link_score);

                    // Display the results in the HTML
                    resultElement.innerHTML = `${data.result1}<h4>Website Rating: ${starVisualization}</h4>${data.result2}<br>${data.result3}<br>${data.result4}<br>${data.result5}<br>${data.result6}`;
                    // Update the class based on the safety status
                    if (data.safe_status === 'safe') {
                        resultElement.classList.add('result-safe');
                        resultElement.classList.remove('result-unsafe');
                    } else {
                        resultElement.classList.add('result-unsafe');
                        resultElement.classList.remove('result-safe');
                    }
                } else {
                    // Handle unexpected response format
                    throw new Error('Unexpected response format');
                }
                // Make sure the result element is visible
                resultElement.style.display = 'block';
            })
            .catch(error => {
                // Log and display errors
                console.error('Error:', error);
                const resultElement = document.getElementById('prediction-result');
                resultElement.innerHTML = 'An error occurred. Please try again.';
                resultElement.style.display = 'block';
            });
        }
    });

    // Close button functionality
    const closeButton = document.getElementById('close-btn');
    closeButton.addEventListener('click', function() {
        // On click, immediately close the window
        window.close();
    });
});

// Function to create a visual representation of the score using stars
function createStarVisualization(score) {
    const [currentScore, outOfScore] = score.split('/');
    const fullStar = '⭐'; // Symbol for a full star
    const emptyStar = '☆'; // Symbol for an empty star
    let visualization = '';

    // Add full stars for the score
    for (let i = 0; i < parseInt(currentScore); i++) {
        visualization += fullStar;
    }

    // Add empty stars for the remainder of the total possible score
    for (let i = 0; i < (parseInt(outOfScore) - parseInt(currentScore)); i++) {
        visualization += emptyStar;
    }

    // Optionally handle the case of a 0 score (this part is commented out but can be customized)
    if (parseInt(currentScore) === 0) {
        // You could customize this part to display "No stars" or similar
    }

    return visualization; // Return the constructed star visualization
}

