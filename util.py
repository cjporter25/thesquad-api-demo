import secrets
import string

def generate_new_key(username):
    characters = string.ascii_uppercase + string.digits
    print(characters)
    newkey = ""
    for i in range(5):
        print(newkey)
        newkey.join(secrets.choice(characters) for i in range(4))
    return {username: newkey}