document.addEventListener('DOMContentLoaded', function() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        var currentTab = tabs[0];
        if (currentTab && currentTab.url) {
            console.log("Current tab URL:", currentTab.url);

            fetch('http://localhost:5000/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ urlinput: currentTab.url }),
            })
            .then(response => response.json())
            .then(data => {
                const resultElement = document.getElementById('prediction-result');
                resultElement.innerHTML = `${data.result1}<br>${data.result2}<br>${data.result3}<br>${data.result4}<br>${data.result5}<br>${data.result6}`;
                if (data.safe_status === 'safe') {
                    resultElement.classList.add('result-safe');
                    resultElement.classList.remove('result-unsafe');
                } else {
                    resultElement.classList.add('result-unsafe');
                    resultElement.classList.remove('result-safe');
                }
                resultElement.style.visibility = 'visible';

                // Make the Close button visible after the result is displayed
                document.getElementById('close-btn').style.display = 'block';
            });
        }
    });

    const closeButton = document.getElementById('close-btn');
    if(closeButton) {
        closeButton.addEventListener('click', function() {
            const container = document.querySelector('.container');
            container.style.opacity = '0'; // Start the fade-out effect

            // Wait for the fade-out to finish before closing the window
            setTimeout(function() {
                window.close();
            }, 500); // This delay should match the CSS transition time
        });
    }
});
