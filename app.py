from flask import Flask, request, render_template,jsonify
from flask_cors import CORS
import pickle
import numpy as np
import requests
import logging
from urllib.parse import urlparse, parse_qs

# Initialize Flask application and enable Cross-Origin Resource Sharing (CORS)
app = Flask(__name__)
CORS(app)

# Load the machine learning model from a .pkl file at the start of the application
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# Configure basic logging for the application
logging.basicConfig(level=logging.INFO)

def is_ssl_certified(url):
    """
    Check if the given URL has a valid SSL certificate.
    """
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
    """
    Check for the presence of a server banner in the response headers.
    """
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
    """
    Check if HTTP Strict Transport Security (HSTS) is enabled.
    """
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
    """
    Check if X-XSS-Protection header is set for the website.
    """
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
    """
    Route to render the home page.
    """
    return render_template('index.html', prediction_text='')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """
    Route to handle URL prediction requests.
    """
    url = request.json['urlinput']  # Extract the URL from the request
    inputurl = f'Entered Website: {url}'
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    prediction_made = True

    # Feature extraction for the URL
    # Counting various elements in the URL to use as features for the model
    qty_hyphen_domain = domain.count('-')
    parsed_url = urlparse(url)
    path = parsed_url.path
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
    
    # Create a list with the extracted features
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
        # Additional features...
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

    # Convert features into a format suitable for the model
    input_data_as_numpy_array = np.asarray(result_list)
    input_data_reshaped = input_data_as_numpy_array.reshape(1, -1)
        
    # Use the loaded model to make a prediction
    prediction = model.predict(input_data_reshaped)
    
    # Interpret the prediction result
    if str(prediction[0]) == '0':
        result1 = f'🟢 Status: The website {url} is SAFE to use.'
    else:
        result1 = f'🔴 Status: The website {url} is SUSPICIOUS. Please proceed with caution.'
        
    # Check additional security features of the URL
    ssl_cert_result = is_ssl_certified(url)
    server_banner_present, server_banner = check_server_banner(url)
    hsts_enabled, hsts_policy = check_hsts(url)
    x_xss_protection_enabled, x_xss_protection_policy = check_x_xss_protection(url)
    
    # Compile all results into a JSON response
    response = jsonify({
        'prediction': result1,
        'ssl_certified': ssl_cert_result,
        'server_banner': server_banner,
        'hsts_enabled': hsts_enabled,
        'hsts_policy': hsts_policy,
        'x_xss_protection_enabled': x_xss_protection_enabled,
        'x_xss_protection_policy': x_xss_protection_policy
    })
    
    return response

if __name__ == "__main__":
    app.run(debug=True)
