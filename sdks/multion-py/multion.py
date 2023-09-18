# multion.py
import os
import webbrowser
import requests
from cryptography.fernet import Fernet
from requests_oauthlib import OAuth2Session
import json
import time
import base64
from PIL import Image
from io import BytesIO
from IPython.display import display

import cognitojwt


class _Multion:
    def __init__(self, token_file="multion_token.enc", secrets_file="secrets.json"):
        self.token = None
        self.token_file = token_file

        secrets_file = os.path.join(os.path.dirname(__file__), secrets_file)
        with open(secrets_file, "r") as f:
            secrets = json.load(f)

        self.multion_id = secrets["MULTION_CLIENT_ID"]
        self.multion_secret = secrets["MULTION_CLIENT_SECRET"]
        self.user_pool_id = secrets["COGNITO_USER_POOL_ID"]
        self.region = secrets["AWS_REGION"]
        self.refresh_url = "https://auth.multion.ai/oauth2/token"

        self.fernet_key = secrets.get("FERNET_KEY")
        if self.fernet_key is None:
            self.fernet_key = Fernet.generate_key().decode()
            secrets["FERNET_KEY"] = self.fernet_key
            with open(secrets_file, "w") as f:
                json.dump(secrets, f, indent=4)

        self.fernet_key = self.fernet_key.encode()
        self.fernet = Fernet(self.fernet_key)

        # Create a .multion directory in the user's home folder if it doesn't exist
        self.home_dir = os.path.expanduser("~")
        self.multion_dir = os.path.join(self.home_dir, ".multion")
        if not os.path.exists(self.multion_dir):
            os.makedirs(self.multion_dir)

        self.token_file = os.path.join(self.multion_dir, "multion_token.enc")

        # Load token if it exists
        self.load_token()

    def verify_cognito_token(self):
        try:
            verified_claims = cognitojwt.decode(
                self.token["id_token"], self.region, self.user_pool_id
            )
            return verified_claims
        except Exception as e:
            # Token verification failed
            print("Could not verify token: ", e)
            return None

    def login(self):
        if self.token is not None:
            verified_claims = self.verify_cognito_token()
            if verified_claims:
                print("Already logged in.")
                return

        # Create a unique client id
        self.client_id = self.register_client()

        # OAuth endpoints
        authorization_base_url = "https://auth.multion.ai/oauth2/authorize"
        redirect_uri = "https://api.multion.ai/callback"

        # Create an OAuth2 session
        oauth = OAuth2Session(
            self.multion_id, redirect_uri=redirect_uri, state=self.client_id
        )

        # Get the authorization URL
        authorization_url, state = oauth.authorization_url(authorization_base_url)
        # Open the authorization URL in a new browser tab
        webbrowser.open(authorization_url)

        # Poll the server for the token
        attempts = 0
        while attempts < 5:
            data = self.get_token()
            if data:
                self.token = data
                self.save_token()  # Save the token after updating it
                break
            attempts +=1
            time.sleep(1)  # Wait before the next poll

    def register_client(self):
        response = requests.post("https://api.multion.ai/register_client")
        if response.status_code == 200:
            data = response.json()
            return data.get("client_id")
        else:
            raise Exception("Failed to register client")

    def load_token(self):
        if os.path.exists(self.token_file) and os.path.getsize(self.token_file) > 0:
            with open(self.token_file, "rb") as f:
                try:
                    encrypted_token = f.read()
                    decrypted_token = self.fernet.decrypt(encrypted_token).decode()
                    self.token = json.loads(decrypted_token)
                except json.JSONDecodeError:
                    print("Error reading token from file. The file might be corrupted.")
                    self.token = None

    def save_token(self):
        encrypted_token = self.fernet.encrypt(json.dumps(self.token).encode())
        with open(self.token_file, "wb") as f:
            f.write(encrypted_token)

    def refresh_token(self):
        # OAuth endpoints
        token_url = "https://auth.multion.ai/oauth2/token"

        extra = {
            "client_id": self.multion_id,
            "client_secret": self.multion_secret,
        }

        def token_saver(token):
            self.token = token

            encrypted_token = self.fernet.encrypt(json.dumps(self.token).encode())
            with open(self.token_file, "wb") as f:
                f.write(encrypted_token)

        client = OAuth2Session(
            self.client_id,
            token=self.token,
            auto_refresh_url=token_url,
            auto_refresh_kwargs=extra,
            token_updater=token_saver,
        )

        try:
            # Pass the old refresh token to refresh the access token
            new_token = client.refresh_token(
                token_url, refresh_token=self.token["refresh_token"]
            )
            token_saver(new_token)
        except Exception as e:
            print(f"An error occurred while refreshing token: {str(e)}")

    def post(self, url, data, tabId=None):
        if self.token is None:
            raise Exception("You must log in before making API calls.")

        headers = {"Authorization": f"Bearer {self.token['access_token']}"}

        # If a tabId is provided, update the existing session
        if tabId is not None:
            url = f"https://api.multion.ai/sessions/{tabId}"

        attempts = 0
        while attempts < 5:  # tries up to 5 times
            response = requests.post(url, json=data, headers=headers)

            if response.ok:  # checks if status_code is 200-400
                try:
                    return response.json()["response"]["data"]
                except json.JSONDecodeError:
                    print("JSONDecodeError: The server didn't respond with valid JSON.")

                break  # if response is valid then exit loop
            elif response.status_code == 401:  # token has expired
                print("Invalid token. Refreshing...")
                self.refresh_token()  # Refresh the token
                headers[
                    "Authorization"
                ] = f"Bearer {self.token['access_token']}"  # Update the authorization header
            elif response.status_code == 404:  # server not connected
                print(
                    "Server Disconnected. Please press connect in the Multion extension popup"
                )

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
        headers = {"Authorization": f"Bearer {self.token['access_token']}"}
        url = "https://api.multion.ai/sessions"

        response = requests.get(url, headers=headers)
        return response.json()["response"]["data"]

    def new_session(self, data):
        url = "https://api.multion.ai/sessions"
        print("running new session")
        return self.post(url, data)

    def update_session(self, tabId, data):
        url = f"https://api.multion.ai/session/{tabId}"
        print("session updated")
        return self.post(url, data)

    def close_session(self, tabId):
        if self.token is None:
            raise Exception("You must log in before closing a session.")
        headers = {"Authorization": f"Bearer {self.token['access_token']}"}
        url = f"https://api.multion.ai/session/{tabId}"
        response = requests.delete(url, headers=headers)

        if response.ok:  # checks if status_code is 200-400
            try:
                return response.json()["response"]["data"]
            except json.JSONDecodeError:
                print("JSONDecodeError: The server didn't respond with valid JSON.")
        else:
            print(f"Failed to close session. Status code: {response.status_code}")

    def list_sessions(self):
        return self.get()

    def get_token(self):
        if self.token is not None and self.token["expires_at"] > time.time():
            return self.token

        response = requests.get(
            f"https://api.multion.ai/get_token?client_id={self.client_id}"
        )
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                return data["access_token"]
            else:
                # print(f"Token not found, {data}")
                return None
        else:
            print("Failed to get token")
            return None

    def delete_token(self):
        if os.path.exists("multion_token.txt"):
            os.remove("multion_token.txt")
        else:
            print("No active session found. Access token has already been revoked.")

    def get_screenshot(self, response, height=None, width=None):
        screenshot = response["screenshot"]

        # Remove the "data:image/png;base64," part from the string
        base64_img_bytes = screenshot.replace("data:image/png;base64,", "")

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


def close_session(tabId):
    return _multion_instance.close_session(tabId)


def list_sessions():
    return _multion_instance.list_sessions()


def delete_token():
    _multion_instance.delete_token()


def get_screenshot(response, height=None, width=None):
    return _multion_instance.get_screenshot(response, height, width)


def refresh_token():
    _multion_instance.refresh_token()


def get_token():
    return _multion_instance.get_token()
