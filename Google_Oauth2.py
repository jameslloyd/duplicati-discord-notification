from dotenv import load_dotenv
import os
load_dotenv()

CLIENT_SECRET=os.getenv('CLIENT_SECRET')
CLIENT_ID=os.getenv('CLIENT_ID')
SCOPES = os.getenv('SCOPES').split(',')


from authlib.integrations.requests_client import OAuth2Session
import requests

# function to get googl user info with access token
def get_google_user_info(access_token):
    response = requests.get('https://www.googleapis.com/oauth2/v1/userinfo', headers={'Authorization': 'Bearer ' + access_token })
    return response.json()

def login_url():
    
    client = OAuth2Session(CLIENT_ID, CLIENT_SECRET, scope=SCOPES)
    authorization_url, state = client.create_authorization_url('https://accounts.google.com/o/oauth2/auth', redirect_uri='http://localhost:8888/login')
    return(authorization_url)

def auth_reponse(response_url):
    token_url = 'https://accounts.google.com/o/oauth2/token'
    client = OAuth2Session(CLIENT_ID, CLIENT_SECRET, scope=SCOPES)
    token = client.fetch_token(token_url, authorization_response=response_url, redirect_uri='http://localhost:8888/login')
    try:
        resp = get_google_user_info(token['access_token'])
        return resp
    except Exception as e:
        return False
 