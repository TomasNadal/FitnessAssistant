from abc import ABC, abstractmethod
import typing
import requests
import logging
from dataclasses import asdict
from flask import jsonify, request
from functools import wraps
import logging
import datetime
import pathlib
import hashlib
import hmac

# Could actually separate this into WhatsappCliente and WhatsappSecurityClient but will do later
class WhatsappClient:
    def __init__(self, access_token: str, api_version: str, phone_number_id: str, verify_token: str, app_secret: str):
        self.access_token = access_token
        self.app_secret = app_secret
        self.api_version = api_version
        self.verify_token = verify_token
        self.phone_number_id = phone_number_id
        self.base_url = f"https://graph.facebook.com/{api_version}"   


    def _get_headers(self) -> dict:
        ''' Get headers for API response '''
        return {
            'Authorization': f'Bearer {self.access_token}',
            "Content-Type": "application/json"
        }
    
    # Relative url: only the url that comes after version: 
    def _get_request(self, relative_url: str) -> requests.Response:
        url = self.base_url + "/" + relative_url
        try:
            response = requests.get(url, headers = self._get_headers(), timeout = 10)
            response.raise_for_status() 
            return response
        
        except requests.Timeout:
            logging.error(f"Timeout occurred")
            return None
        except requests.ConnectionError:
            logging.error(f"Connection error occurred:")
            return None
        except requests.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
            return None
        except requests.RequestException as req_err:
            logging.error(f"Request exception occurred: {req_err}")
            return None
        

    def _post_request(self, relative_url: str, payload: dict) -> requests.Response:
        url = self.base_url + "/" + relative_url
        try:
            response = requests.post(
                url, headers=self._get_headers(), json = payload, timeout=10
            )  
            response.raise_for_status() # Raises an HTTPError if the HTTP request returned an unsuccessful status code
            return response  
        except requests.Timeout:
            logging.error("Timeout occurred whilemaking")
            return jsonify({"status": "error", "message": "Request timed out"}), 408
        except requests.RequestException as e:  # This will catch any general request exception
            logging.error(f"Request failed due to: {e}")
            return jsonify({"status": "error", "message": "Failed to send message"}), 500

    ''' 
    Concrete functions
    '''
    def download_media(self, filename: str, media_id: str) -> pathlib.Path:
        # First get url to download
        get_file_url = f"{media_id}/"
        media_url_response = self._get_request(relative_url  = get_file_url)
        try:
            body = media_url_response.json()
            media_url = body.get("url")
        except ValueError:
            logging.error(f"Invalid JSON response while fetching media URL for media_id: {media_id}")
            return None
        except AttributeError:
            logging.error("Auth token expired")
            return None

        # Second download the file
        file_response = requests.get(media_url, headers=self._get_headers() )

        if file_response.status_code == 200:
            temp_path = pathlib.Path.cwd() / "tmp" 

            temp_path.mkdir(parents =True, exist_ok=True)
            
            if (temp_path / filename).exists():
                name, extension = filename.split(".")
                name = f'{name}-{datetime.datetime.now()}'
                filename = f'{name}.{extension}'
                file_path = temp_path / filename

            else:
                file_path = temp_path / filename

            with open(file_path, 'wb') as file:
                file.write(file_response.content)
            
            return file_path

        else:
            logging.error(f"Failed to download media. Status code: {file_response.status_code}")
            print(f"Response message: {file_response.text}")



        
        

    '''
    Security related functions  
    '''
    # Required webhook verifictaion for WhatsApp
    def verify(self):
        # Parse params from the webhook verification request
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        # Check if a token and mode were sent
        if mode and token:
            # Check the mode and token sent are correct
            if mode == "subscribe" and token == self.verify_token:
                # Respond with 200 OK and challenge token from the request
                logging.info("WEBHOOK_VERIFIED")
                return challenge, 200
            else:
                # Responds with '403 Forbidden' if verify tokens do not match
                logging.info("VERIFICATION_FAILED")
                return jsonify({"status": "error", "message": "Verification failed"}), 403
        else:
            # Responds with '400 Bad Request' if verify tokens do not match
            logging.info("MISSING_PARAMETER")
            return jsonify({"status": "error", "message": "Missing parameters"}), 400
        
    def validate_signature(self, payload, signature):
        """
        Validate the incoming payload's signature against our expected signature
        """
        # Use the App Secret to hash the payload
        expected_signature = hmac.new(
            bytes(self.app_secret, "latin-1"),
            msg=payload.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

        # Check if the signature matches
        return hmac.compare_digest(expected_signature, signature)


    def signature_required(self, f):
        """
        Decorator to ensure that the incoming requests to our webhook are valid and signed with the correct signature.
        """

        @wraps(f)
        def decorated_function(*args, **kwargs):
            signature = request.headers.get("X-Hub-Signature-256", "")[
                7:
            ]  # Removing 'sha256='
            if not self.validate_signature(request.data.decode("utf-8"), signature):
                logging.info("Signature verification failed!")
                return jsonify({"status": "error", "message": "Invalid signature"}), 403
            return f(*args, **kwargs)

        return decorated_function
