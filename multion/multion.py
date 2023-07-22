# multion.py
import os
import webbrowser
import requests
from flask import Flask, request
from requests_oauthlib import OAuth2Session
from threading import Thread
import json
import time
import base64
from PIL import Image
from io import BytesIO
from IPython.display import display

class _Multion:
    def __init__(self, token_file='multion_token.txt', secrets_file='secrets.json'):
        secrets_file = os.path.join(os.path.dirname(__file__), secrets_file)
        with open(secrets_file, 'r') as f:
            secrets = json.load(f)

        self.client_id = secrets['MULTION_CLIENT_ID']
        self.client_secret = secrets['MULTION_CLIENT_SECRET']
        self.token_file = token_file
        self.token = None
        self.refresh_url = 'https://auth.multion.ai/oauth2/token'

        # Try to load the token from the token file
        if os.path.exists(self.token_file) and os.path.getsize(self.token_file) > 0:  # check if file is not empty
            with open(self.token_file, 'r') as f:
                try:
                    self.token = json.load(f)
                except json.JSONDecodeError:
                    print("Error reading token from file. The file might be corrupted.")
                    self.token = None

    def login(self):
        # If the token is already loaded, no need to log in again
        if self.token is not None:
            print("Already logged in")
            return

        # OAuth endpoints
        authorization_base_url = 'https://auth.multion.ai/oauth2/authorize'
        token_url = 'https://auth.multion.ai/oauth2/token'
        redirect_uri = 'https://localhost:8000/callback'

        # Create an OAuth2 session
        oauth = OAuth2Session(self.client_id, redirect_uri=redirect_uri)

        # Get the authorization URL
        authorization_url, state = oauth.authorization_url(authorization_base_url)

        # Save the state so it can be verified in the callback
        self.state = state

        # Open the authorization URL in a new browser tab
        webbrowser.open(authorization_url)

        # Create a Flask app to handle the OAuth2 callback
        app = Flask(__name__)

        @app.route("/callback")
        def callback():
            try:
                # Get the authorization response from the request parameters
                redirect_response = request.url
                
                if self.state != request.args.get('state'):
                    raise Exception('State mismatch: CSRF Warning!')

                # Fetch the access token
                self.token = oauth.fetch_token(token_url, client_secret=self.client_secret, authorization_response=redirect_response)

                # Save the token to the token file
                with open(self.token_file, 'w') as f:
                    json.dump(self.token, f)  # save the token as JSON instead of a string

                return "You can close this tab and return to the Jupyter notebook."

            except Exception as e:
                return f"An error occurred: {e}"
            
        @app.get('/shutdown')
        def shutdown():
            shutdown_func = request.environ.get('werkzeug.server.shutdown')
            if shutdown_func is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            shutdown_func()
            return 'Server shutting down...'

        # Run the server in a separate thread
        thread = Thread(target=app.run, kwargs={'port': 8000, 'ssl_context': 'adhoc', 'use_reloader': False})
        thread.start()
    
    def refresh_token(self):
    # OAuth endpoints
        authorization_base_url = 'https://auth.multion.ai/oauth2/authorize'
        token_url = 'https://auth.multion.ai/oauth2/token'
        redirect_uri = 'https://localhost:8000/callback'

        extra = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        def token_saver(token):
            self.token = token

            # Save the token to the token file
            with open(self.token_file, 'w') as f:
                f.write(self.token['access_token'])

        client = OAuth2Session(self.client_id, token=self.token, auto_refresh_url=token_url, 
                            auto_refresh_kwargs=extra, token_updater=token_saver)

        try:
            # Pass the old refresh token to refresh the access token
            new_token = client.refresh_token(token_url, refresh_token=self.token['refresh_token'])
            token_saver(new_token)
        except Exception as e:
            print(f"An error occurred while refreshing token: {str(e)}")


    def post(self, url, data, tabId=None):
        if self.token is None:
            raise Exception("You must log in before making API calls.")
        
        headers = {'Authorization': f"Bearer {self.token['access_token']}"}

        # If a tabId is provided, update the existing session
        if tabId is not None:
            url = f"https://multion-api.fly.dev/sessions/{tabId}"
        
        attempts = 0
        while attempts < 5:  # tries up to 5 times
            response = requests.post(url, json=data, headers=headers)

            if response.ok:  # checks if status_code is 200-400
                try:
                    return response.json()["response"]["data"]
                except json.JSONDecodeError:
                    print("JSONDecodeError: The server didn't respond with valid JSON.")
                
                break # if response is valid then exit loop
            elif response.status_code == 401:  # token has expired
                print("Invalid token. Refreshing...")
                self.refresh_token()  # Refresh the token
                headers['Authorization'] = f"Bearer {self.token['access_token']}"  # Update the authorization header
            elif response.status_code == 404: #server not connected
                print("Server Disconnected. Please press connect in the Multion extention popup")
                
            # If we've not returned by now, sleep before the next attempt
            time.sleep(1)  # you may want to increase this value depending on the API

            # Increment the attempts counter
            attempts += 1
        
        # If we've exhausted all attempts and not returned, raise an error
        if attempts == 5:
            print(f"Request failed with status code: {response.status_code}")
            print(f"Response text: {response.text}")
            raise Exception("Failed to get a valid response after 5 attempts")

    def get(self):
        if self.token is None:
            raise Exception("You must log in before making API calls.")
        headers = {'Authorization': f"Bearer {self.token['access_token']}"}
        url = f"https://multion-api.fly.dev/sessions"

        response = requests.get(url, headers=headers)
        return response.json()["response"]["data"]

    def new_session(self, data):
        url = 'https://multion-api.fly.dev/sessions'
        print("running new session")
        return self.post(url, data)
    
    def update_session(self, tabId, data):
        url = f"https://multion-api.fly.dev/session/{tabId}"
        print("session updated")
        return self.post(url, data)
    
    def list_sessions(self):
        return self.get()
    
    def delete_token(self):
        if os.path.exists("multion_token.txt"):
            os.remove("multion_token.txt")
        else:
            print(f"No active session found. Access token has already been revoked.")

    def get_screenshot(self, response, height=None, width=None):
        screenshot = response['screenshot']

        # Remove the "data:image/png;base64," part from the string
        base64_img_bytes = screenshot.replace('data:image/png;base64,', '')

        # Decode the base64 string back to bytes
        img_bytes = base64.b64decode(base64_img_bytes)

        # Create a BytesIO object and read the image bytes
        img_io = BytesIO(img_bytes)
        img = Image.open(img_io)

        # Get the original image dimensions
        original_width, original_height = img.size

        if height is not None and width is None:
            # If only the height is provided, calculate the width while preserving the aspect ratio
            width = int((height / original_height) * original_width)

        elif width is not None and height is None:
            # If only the width is provided, calculate the height while preserving the aspect ratio
            height = int((width / original_width) * original_height)

        # Resize the image if either dimension was provided
        if height is not None and width is not None:
            new_dimensions = (width, height)  # width, height
            img = img.resize(new_dimensions, Image.LANCZOS)

        # Display the image in Jupyter Notebook
        display(img)


# Create a Multion instance
_multion_instance = _Multion()

# Expose the login and post methods at the module level
def login():
    _multion_instance.login()

def post(url, data):
    return _multion_instance.post(url, data)

def get():
    return _multion_instance.get()

def new_session(data):
    return _multion_instance.new_session(data)

def update_session(tabId, data):
    return _multion_instance.update_session(tabId, data)

def list_sessions():
    return _multion_instance.list_sessions()

def delete_token():
    _multion_instance.delete_token()

def get_screenshot(response, height=None, width=None):
    return _multion_instance.get_screenshot(response, height, width)

def refresh_token():
    _multion_instance.refresh_token()