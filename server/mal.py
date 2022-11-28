# Import secrets module (Generate secure random numbers for managing secrets)
import secrets
# Import requests module (HTTP library)
import requests

# MAL API's keys
CLIENT_ID = '20073b9c643bdb67d15bfa06ba361ff5'
CLIENT_SECRET = 'e397899d59021ec4fee81f76e43fe9b173bfe6345923197f9bd260361ebde01a'

# Return a random URL-safe text string, containing 128 random bytes (maximum length handled by MAL's API)
def generate_code_challenge_verifier() -> str:
    return secrets.token_urlsafe(96)

# Request OAuth 2.0 authentication
def get_request_authentication_url(code_challenge: str) -> str:
    url = (
        'https://myanimelist.net/v1/oauth2/authorize?'
        'response_type=code'
        '&client_id={}'
        '&state=randomString'
        '&code_challenge={}'
        '&code_challenge_method=plain'
    ).format(CLIENT_ID, code_challenge)
    return url

# Generate access token to make MAL API's queries
def generate_access_token(code_verifier: str, code: str) -> str:
    url = 'https://myanimelist.net/v1/oauth2/token'
    body = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'code_verifier': code_verifier
    }
    response = requests.post(url, body)
    access_token = ''
    if (response.status_code == requests.codes.ok):
        access_token = response.json().get('access_token')
    response.close()
    return access_token

# Get user's anime list (list composed of anime and for each one, we have its title and its score)
def get_user_anime_list(access_token: str) -> list:
    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }
    response = requests.get('https://api.myanimelist.net/v2/users/@me/animelist?fields=list_status', headers=headers)
    data = {}
    if (response.status_code == requests.codes.ok):
        data = response.json().get('data')
    response.close()
    anime_list = []
    for anime in data:
        anime_list.append({'Title': anime['node']['title'], 'Score': anime['list_status']['score']})
    return anime_list

# Code challenge is the same as the code verifier with the "plain" method
code_challenge = code_verifier = generate_code_challenge_verifier()

print(get_request_authentication_url(code_challenge))
# Get and clean code returned from the authentication request
code = input().strip()
access_token = generate_access_token(code_verifier, code)
if access_token:
    print(get_user_anime_list(access_token))
