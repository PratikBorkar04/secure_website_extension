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
            .then(response => response.json())
            .then(data => {
                const resultElement = document.getElementById('prediction-result');

                // Assume 'data.stars' is the number of stars you wish to display

                resultElement.innerHTML = `${data.result1}<h4>Website Rating: ${data.link_score}</h4>${data.result2}<br>${data.result3}<br>${data.result4}<br>${data.result5}<br>${data.result6}`;
                if (data.safe_status === 'safe') {
                    resultElement.classList.add('result-safe');
                    resultElement.classList.remove('result-unsafe');
                } else {
                    resultElement.classList.add('result-unsafe');
                    resultElement.classList.remove('result-safe');
                }
                resultElement.style.visibility = 'visible';
                resultElement.style.opacity = '1';

                document.getElementById('close-btn').style.display = 'block';
            })
            .catch(error => {
                console.error('Error:', error);
                const resultElement = document.getElementById('prediction-result');
                resultElement.innerHTML = 'An error occurred. Please try again.';
                resultElement.style.visibility = 'visible';
                resultElement.style.opacity = '1';
            });
        }
    });

    const closeButton = document.getElementById('close-btn');
    closeButton.addEventListener('click', function() {
        const container = document.querySelector('.container');
        container.style.opacity = '0'; // Start the fade-out effect

        setTimeout(function() {
            window.close(); // Close the window after the fade-out effect
        }, 10); // Match the CSS transition time
    });
});

