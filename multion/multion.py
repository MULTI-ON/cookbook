# multion.py
import os
import webbrowser
import requests
from flask import Flask, request
from requests_oauthlib import OAuth2Session
from threading import Thread
import json
import time

class _Multion:
    def __init__(self, token_file='multion_token.txt'):
        self.client_id = os.environ['MULTION_CLIENT_ID']
        self.client_secret = os.environ['MULTION_CLIENT_SECRET']
        self.token_file = token_file
        self.token = None

        # Try to load the token from the token file
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as f:
                self.token = f.read().strip()

    def login(self):
        # If the token is already loaded, no need to log in again
        if self.token is not None:
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
                    f.write(self.token['access_token'])

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

    def post(self, url, data, tabId=None):
        if self.token is None:
            raise Exception("You must log in before making API calls.")
        
        headers = {'Authorization': f"Bearer {self.token['access_token']}"}

        # If a tabId is provided, update the existing session
        if tabId is not None:
            url = f"https://multion-api.fly.dev/session/{tabId}"
        
        print("running post")
        attempts = 0
        while attempts < 5:  # tries up to 5 times
            response = requests.post(url, json=data, headers=headers)

            if response.ok:  # checks if status_code is 200-400
                try:
                    return response.json()["response"]["data"]
                except json.JSONDecodeError:
                    print("JSONDecodeError: The server didn't respond with valid JSON.")
                
                break # if response is valid then exit loop
            
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
        url = "https://multion-api.fly.dev/sessions"

        response = requests.get(url, headers=headers)
        return response.json()["response"]["data"]

    def new_session(self, data):
        url = 'https://multion-api.fly.dev/sessions'
        return self.post(url, data)
    
    def update_session(self, tabId, data):
        url = f"https://multion-api.fly.dev/session/{tabId}"
        return self.post(url, data)
    
    def list_sessions(self):
        return self.get()

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
    return _multion_instance.update_session(tabId,data)

def list_sessions():
    return _multion_instance.list_sessions()