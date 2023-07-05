import argparse
from argparse import ArgumentError

import requests
import json

base_url = "https://ctf.cyberchallenge.it/"
s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0"


def login(email, password):
    print(f"Logging in with email {email} and password {password}")
    res = s.post(base_url + "/api/login",
                 json={"email": email, "password": password})

    return res


def get_challenge(challenge_id):
    res = s.get(f"{base_url}/api/challenges/{challenge_id}")

    # {"id":55,"title":"CR_1.04 - Secure Padding","description":"Passwords should be at least 32 characters long!\nGive us your password, we'll think about it!\n\nThis is a remote challenge, you can connect to the service with:\nnc padding.challs.cyberchallenge.it 9030","files":[{"name":"challenge.py","url":"/api/file/84da89cd-702b-4a2d-a975-ebcaa88e7ca7/challenge.py?download"}],"hints":[{"id":55,"title":"Hint 1","price":50}],"tags":["crypto"],"currentScore":373,"currentAffiliationSolves":4,"currentGlobalSolves":219,"status":{"ok":true,"lastChecked":1688487096794},"solves":[{"playerId":856,"displayedName":"no","timestamp":"2023-05-08T11:36:05.591Z"},{"playerId":853,"displayedName":"Frollo","timestamp":"2023-05-09T19:19:20.348Z"},{"playerId":687,"displayedName":"Giovanni Piccirillo","timestamp":"2023-05-11T13:05:57.097Z"},{"playerId":615,"displayedName":"Christian Marescalco","timestamp":"2023-05-26T15:03:11.390Z"}]}

    return res.json()


def main():
    parser = argparse.ArgumentParser(
        description="CLI for logging in with email and password")
    parser.add_argument('-e', '--email', type=str,
                        help="Your CCIT email")
    parser.add_argument('-p', '--password', type=str,
                        help="Your password")

    args = parser.parse_args()

    email = args.email
    password = args.password

    if not (email and password):
        with open("auth.json", "r") as f:
            data = json.load(f)

        try:
            email = data["email"]
            password = data["password"]
        except Exception:  # IMPR: specific exception
            print(
                "You must provide an email and a password either as argument or inside the auth.json file")
            exit()

    res = login(email, password)

    try:
        data = res.json()
        print(data)
        # token, files_token
    except Exception as e:
        print("Failed authentication")
        print(f"{res.text = }")
        raise e
    else:
        s.headers["authorization"] = f"Token {token}"

    get_challenge(256)

if __name__ == '__main__':
    main()
