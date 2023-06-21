# multion.py

import os
import webbrowser
import requests
from flask import Flask, request
from requests_oauthlib import OAuth2Session
from threading import Thread

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
        redirect_uri = 'http://localhost:5000/callback'

        # Create an OAuth2 session
        oauth = OAuth2Session(self.client_id, redirect_uri=redirect_uri)

        # Get the authorization URL
        authorization_url, state = oauth.authorization_url(authorization_base_url)

        # Open the authorization URL in a new browser tab
        webbrowser.open(authorization_url)

        # Create a Flask app to handle the OAuth2 callback
        app = Flask(__name__)

        @app.route("/callback")
        def callback():
            try:
                # Get the authorization response from the request parameters
                redirect_response = request.url

                # Fetch the access token
                self.token = oauth.fetch_token(token_url, client_secret=self.client_secret, authorization_response=redirect_response)

                # Save the token to the token file
                with open(self.token_file, 'w') as f:
                    f.write(self.token['access_token'])

                # Close the server
                func = request.environ.get('werkzeug.server.shutdown')
                if func is None:
                    raise RuntimeError('Not running with the Werkzeug Server')
                func()

                return "You can close this tab and return to the Jupyter notebook."
            except Exception as e:
                return f"An error occurred: {e}"

        # Run the server in a separate thread
        thread = Thread(target=app.run, kwargs={'port': 5000})
        thread.start()

    def post(self, url, data):
        # Make sure the user is logged in
        if self.token is None:
            raise Exception("You must log in before making API calls.")

        # Include the token in the headers
        headers = {
            'Authorization': f'Bearer {self.token}',
        }

        # Make the POST request
        response = requests.post(url, json=data, headers=headers)

        # Return the response
        return response.json()

# Create a Multion instance
_multion_instance = _Multion()

# Expose the login and post methods at the module level
def login():
    _multion_instance.login()

def post(url, data):
    return _multion_instance.post(url, data)