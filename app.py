from flask import Flask, request, render_template,jsonify
from flask_cors import CORS
import pickle
import numpy as np
import requests
import logging
from urllib.parse import urlparse, parse_qs
import ssl
import socket
import os

app = Flask(__name__)
CORS(app)

# Load the model at the start of the application

with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# Set up logging
logging.basicConfig(level=logging.INFO)

def is_ssl_certified(url):
    try:
        response = requests.get(url)
        return response.ok
    except requests.exceptions.SSLError as e:
        logging.error(f"SSL certificate error for URL {url}: {e}")
        return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error for URL {url}: {e}")
        return False
def check_server_banner(url):
    try:
        response = requests.get(url, timeout=5)
        logging.info(f"Server banner check response for {url}: {response.status_code}, Headers: {response.headers}")
        if 'Server' in response.headers:
            return True, response.headers['Server']
        else:
            return False, None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in server banner check for {url}: {e}")
        return False, None

def check_hsts(url):
    # Function to check if HTTP Strict Transport Security (HSTS) is enabled
    try:
        response = requests.get(url, timeout=5)
        logging.info(f"HSTS check response for {url}: {response.status_code}, Headers: {response.headers}")
        if 'Strict-Transport-Security' in response.headers:
            return True, response.headers['Strict-Transport-Security']
        else:
            return False, None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in HSTS check for {url}: {e}")
        return False, None

def check_x_xss_protection(url):
    # Function to check if X-XSS-Protection is set
    try:
        response = requests.get(url, timeout=5)
        logging.info(f"X-XSS-Protection check response for {url}: {response.status_code}, Headers: {response.headers}")
        if 'X-XSS-Protection' in response.headers:
            return True, response.headers['X-XSS-Protection']
        else:
            return False, None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in X_XSS-Protection check for {url}: {e}")
        return False, None

@app.route('/')
def home():
    # Route to render the home page
    return render_template('index.html', prediction_text='')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
        # Route to handle URL prediction requests
        url = request.json['urlinput']
        inputurl = f'Entered Website: {url}'
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        prediction_made = True

        score = 0
        total_checks = 5
        # Counting occurrences of characters and vowels in the domain
        qty_hyphen_domain = domain.count('-')

        # Extracting the path and parameters from the URL
        parsed_url = urlparse(url)
        path = parsed_url.path

        # Counting occurrences of characters in the URL
        qty_tilde_url = url.count('~')
        qty_dot_url = url.count('.')
        qty_percent_url = url.count('%')
        params_length = len(parse_qs(parsed_url.query))
        qty_and_params = url.count('&')
        qty_hyphens_params = url.count('-')
        directory_length = len(parsed_url.path.split('/'))
        qty_equal_params = url.count('=')
        qty_equal_url = url.count('=')
        qty_slash_url = url.count('/')
        qty_slash_directory = url.count('/') - 1
        file_length = len(parsed_url.path.split('/')[-1])
        qty_and_url = url.count('&')
        qty_dot_params = url.count('.')

        # Creating a list with the required values
        result_list = [
            len(domain),
            len(path),
            len(url.split('/')[-1]),
            url.count('-'),
            url.count('@'),
            url.count('?'),
            url.count('%'),
            url.count('.'),
            url.count('='),
            url.count('http'),
            url.count('https'),
            url.count('www'),
            sum(c.isdigit() for c in url),
            sum(c.isalpha() for c in url),
            url.count('/'),
            1 if domain.replace('.', '').isdigit() else 0,
            # ... other values ...
            qty_hyphen_domain,
            len(url),
            qty_tilde_url,
            qty_dot_url,
            qty_percent_url,
            len(domain),
            params_length,
            qty_and_params,
            qty_hyphens_params,
            directory_length,
            qty_equal_params,
            qty_equal_url,
            qty_slash_url,
            qty_slash_directory,
            file_length,
            qty_and_url,
            qty_dot_params
        ]
        # Creating a numpy array from the extracted features and reshaping for the model
        input_data_as_numpy_array = np.asarray(result_list)
        input_data_reshaped = input_data_as_numpy_array.reshape(1, -1)
            
        # Making the prediction using the loaded model
        prediction = model.predict(input_data_reshaped)

        # Determining the prediction result and calculating the probability
        if str(prediction[0]) == '0':
            result1 = f'🟢 Status: {url} website is ✅SAFE to visit.'
            probability = model.predict_proba(input_data_reshaped)[0][1] * 100
            probability = round(probability, 2)
            score += 1
            result2 = f"🔒 Safety Probability: {probability}% chance of being ✅safe."
            safe_status='safe'
        else:
            result1 = f'🔴 Status: : {url} website is ❌NOT SAFE to visit.'
            probability = model.predict_proba(input_data_reshaped)[0][1] * 100
            probability = round(probability, 2)
            result2 = f"🔓 Safety Probability: {probability}% chance the Website is ❌malicious!"
            safe_status='unsafe'

        if is_ssl_certified(url):
            result3 = "✅ SSL Certificate: The website has a valid SSL certificate."
            score += 1
        else:
            result3 = "❌ SSL Certificate: The website does not have a valid SSL certificate."
            
        server_banner,server_banner_error  = check_server_banner(url)
        if server_banner:
            result4 = "✅ Server banner is present for the website."
            score += 1
        elif server_banner_error:
            result4 = "❌ Error occurred in checking server banner."
        else:
            result4 = "❌ No server banner detected for the website."

        
        hsts_enabled, hsts_error = check_hsts(url)
        if hsts_enabled:
            result5 = "✅ HSTS is enabled for the website."
            score += 1
        elif hsts_error:
            result5 = "❌ Error occurred in checking HSTS."
        else:
            result5 = "❌ HSTS is not enabled for the website."

        x_xss_protection, x_xss_error = check_x_xss_protection(url)
        if x_xss_protection:
            result6 = "✅ X-XSS-Protection is set for the website."
            score += 1
        elif x_xss_error:
            result6 = "❌ Error occurred in checking X-XSS-Protection."
        else:
            result6 = "❌ X-XSS-Protection is not set for the website."

        link_score = f"{score}/{total_checks}"
        stars_visualization = '⭐' * link
        # Render the prediction results back to the home page template
        response = {
        "prediction_made": prediction_made,
        "inputurl": inputurl,
        "result1": result1,
        "result2": result2,
        "result3": result3,
        "result4": result4,
        "link_score": stars_visualization,
        "result5": result5,
        "result6": result6,
        "safe_status": safe_status
        }
        return jsonify(response)
if __name__ == "__main__":
    app.run(debug=True)
