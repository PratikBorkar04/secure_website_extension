document.addEventListener('DOMContentLoaded', function() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        var currentTab = tabs[0];
        if (currentTab && currentTab.url) {
            fetch('https://secure-website-extension.onrender.com/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ urlinput: currentTab.url }),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                const resultElement = document.getElementById('prediction-result');
                if (data && data.result1 && data.safe_status) {
                    // Convert link_score to star visualization
                    const starVisualization = createStarVisualization(data.link_score);

                    resultElement.innerHTML = `${data.result1}<h4>Website Rating: ${starVisualization}</h4>${data.result2}<br>${data.result3}<br>${data.result4}<br>${data.result5}<br>${data.result6}`;
                    if (data.safe_status === 'safe') {
                        resultElement.classList.add('result-safe');
                        resultElement.classList.remove('result-unsafe');
                    } else {
                        resultElement.classList.add('result-unsafe');
                        resultElement.classList.remove('result-safe');
                    }
                } else {
                    throw new Error('Unexpected response format');
                }
                resultElement.style.display = 'block';
            })
            .catch(error => {
                console.error('Error:', error);
                const resultElement = document.getElementById('prediction-result');
                resultElement.innerHTML = 'An error occurred. Please try again.';
                resultElement.style.display = 'block';
            });
        }
    });

    const closeButton = document.getElementById('close-btn');
    closeButton.addEventListener('click', function() {
        const container = document.querySelector('.container');
        container.style.opacity = '0';

        setTimeout(function() {
            window.close();
        }, 30);
    });
});

function createStarVisualization(score) {
    const [currentScore, outOfScore] = score.split('/');
    const fullStar = '⭐'; // Symbol for a full star
    const emptyStar = '☆'; // Symbol for an empty star
    let visualization = '';

    // Add full stars
    for (let i = 0; i < parseInt(currentScore); i++) {
        visualization += fullStar;
    }

    // Add empty stars for the remaining score
    for (let i = 0; i < (parseInt(outOfScore) - parseInt(currentScore)); i++) {
        visualization += emptyStar;
    }

    // Optional: Display a specific message if the score is 0
    if (parseInt(currentScore) === 0) {
        // You can return just the empty stars or with a message like "No stars"
        // visualization = 'No stars'; // Uncomment if you prefer text over empty stars
    }

    return visualization;
}

