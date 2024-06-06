client_id = '2ee0ca64c6294613b3a0108fcea4505d'
client_secret = '44484c2643574b63937a85c18f34d59e'

def getAccessToken(client_id, client_secret):
    import requests
    import base64

    auth_url = 'https://accounts.spotify.com/api/token'
    auth_header = {
        'Authorization': 'Basic ' + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    }
    auth_data = {
        'grant_type': 'client_credentials'
    }
    response = requests.post(auth_url, headers=auth_header, data=auth_data)
    response_data = response.json()
    return response_data['access_token']
