import secrets
import string
import os
import re
import tempfile
import base64
import json

import requests
from requests.auth import HTTPBasicAuth

from thesquad.squad import *


def generate_new_key(username):
    characters = string.ascii_uppercase + string.digits
    print(characters)
    newkey = ""
    for i in range(5):
        print(newkey)
        newkey.join(secrets.choice(characters) for i in range(4))
    return {username: newkey}
def retrieve_riot_api_key():
    stored_key = os.environ.get('RIOT_KEY')
    char_to_replace = '_'
    new_char = '-'
    riot_key = ""
    for char in stored_key:
        if char == char_to_replace:
            riot_key += new_char
        else:
            riot_key += char
    return riot_key
def encrypt_fb_key(stored_key):
    new_key = ""
    new_val = 0
    newline_present = False
    for char in stored_key:
        if newline_present:
            newline_present = False
            continue

        curr_val = ord(char)
        
        if curr_val == 92:
            new_val = 46
            new_char = chr(new_val)
            new_key += new_char
            newline_present = True
        
        else:
            new_val = curr_val
            new_char = chr(new_val)
            new_key += new_char
    return new_key
def decrypt_fb_key(stored_key):
    new_key = ""
    for char in stored_key:
        curr_val = ord(char)
        if curr_val == 46:
            new_val = 10
            new_char = chr(new_val)
            new_key += new_char
            continue
        new_val = curr_val
        new_char = chr(new_val)
        new_key += new_char
    return new_key

def update_firebase_cred():
    fb_key_id = os.environ.get('FB_PRIVATE_KEY_ID')
    fb_priv_key = os.environ.get('FB_PRIVATE_KEY')
    client_id = os.environ.get('FB_CLIENT_ID')
    client_email = os.environ.get('FB_CLIENT_EMAIL')
    with open('firebase.json', 'r') as json_file:
        data = json.load(json_file)
        data['private_key_id'] = fb_key_id
        data['private_key'] = decrypt_fb_key(fb_priv_key)
        data['client_id'] = client_id
        data['client_email'] = client_email
        # ^ "data" is in a dict format
        json_file.close()

    json_data = json.dumps(data, indent=2)
    with open('firebase.json', "w") as outfile:
        outfile.write(json_data)
        outfile.close()
def initialize_firebase():
    # Certificate can be a "file path" or a "dict containing the parsed file contents"
    # As a result, Firebase is unable to use a temporary file and must initialize from
    #   a file in the main directory
    cred = credentials.Certificate('firebase.json')
    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_admin.initialize_app(cred)
def clear_firebase_cred():
    with open('firebase.json', 'r') as json_file:
        data = json.load(json_file)
        data['private_key_id'] = "TEMP"
        data['private_key'] = "TEMP"
        data['client_id'] = "TEMP"
        data['client_email'] = "TEMP"
        # ^ "data" is in a dict format
        json_file.close()

    json_data = json.dumps(data, indent=2)
    with open('firebase.json', "w") as outfile:
        outfile.write(json_data)
        outfile.close()

def LOCAL_find_live_client_info():
    filePath = "C:/Riot Games/League of Legends/lockfile"
    if os.path.exists(filePath):
        with open(filePath, 'r') as file:
            content = file.read().strip()
        
        pattern = r'^(.+?):(\d+):(\d+):(.+?):(.+?)$'
        match = re.match(pattern, content)

        if match:
            portNum = match.group(3)
            passWord = match.group(4)
            return [portNum, passWord]
        else: 
            return "File format does not match the expected pattern."
    else:
        return "File does not exist"

def LOCAL_get_lcu_data(port, password, certPath):

    #Start it off as false
    verify_ssl = False

    # Construct the base URL for the LCU API
    base_url = f"https://127.0.0.1:{port}"
    print("Base URL: " + base_url)

    # Construct the Authorization header
    auth_str = f"riot:{password}"
    auth_bytes = auth_str.encode('ascii')
    auth_base64 = base64.b64encode(auth_bytes).decode('ascii')
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Accept": "application/json"
    }
    print("Headers: ")
    print(headers)
    
    verify_ssl = certPath

    # Verify SSL (usually required)
    # verify_ssl = False
    endpoint = "/lol-champ-select/v1/session"

    try:
        # Make the request
        response = requests.get(base_url + endpoint, headers=headers, verify=verify_ssl)

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error: Received status code {response.status_code}"

    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"
# Parses through a theoretical user input memberList and confirms that each
#   name given and the list as a whole is a valid length.
def is_mem_list_valid(memberList):
    isMemListValid = True
    if len(memberList) > 1 and len(memberList) < 6:
        for name in memberList:
            if not is_mem_name_valid(name):
                isMemListValid = False
    else:
        isMemListValid = False
    return isMemListValid
# Checks that a given name string is within the character limits imposed
#   by the game itself
def is_mem_name_valid(name):
    if len(name) > 2 and len(name) < 17:
        return True
    else:
        return False

def is_count_valid(inputCount):
    try:
        # Try converting the string to an integer
        num = int(inputCount)
        # Check if the converted number is a whole number (integer)
        return True
    except ValueError:
        # If conversion fails, it's not a valid whole number
        return False