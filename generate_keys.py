import yaml
import streamlit_authenticator as stauth

names = ["오구의모험","로그인테스트"]
usernames = ["오구", "로그인"]
passwords = ["xxxx","xxxx"]

hashed_passwords = stauth.Hasher(passwords).generate()

data = {
    "credentials" : {
        "usernames":{
            usernames[0]:{
                "name":names[0],
                "password":hashed_passwords[0]
                },
            usernames[1]:{
                "name":names[1],
                "password":hashed_passwords[1]
                }            
            }
    },
    "cookie": {
        "expiry_days" : 0,
        "key": "some_signature_key",
        "name" : "some_cookie_name"
    },
    "preauthorized" : {
        "emails" : [
            "melsby@gmail.com"
        ]
    }
}

with open('config.yaml','w') as file:
    yaml.dump(data, file, default_flow_style=False)
