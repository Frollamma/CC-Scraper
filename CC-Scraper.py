import argparse
from argparse import ArgumentError

import requests
import json

BASE_URL = "https://ctf.cyberchallenge.it"
s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0"
s.headers["Origin"] = BASE_URL # it works even without Origin

def get_args():
    parser = argparse.ArgumentParser(
        description="CLI for logging in with email and password")
    parser.add_argument('-e', '--email', type=str,
                        help="Your CCIT email")
    parser.add_argument('-p', '--password', type=str,
                        help="Your password")

    args = parser.parse_args()

    return args

def get_auth_details(args):
    email = args.email
    password = args.password

    if not (email and password):
        with open("auth.json", "r") as f:
            data = json.load(f)

        try:
            email = data["email"]
            password = data["password"]
        except Exception:  # IMPR: add specific exception
            pass

    if not (email and password):
        raise ValueError("You must provide an email and a password either as argument or inside the auth.json file")

    return email, password

def login(email, password):
    print(f"Logging in with email {email} and password {password}, using endpoint {BASE_URL + '/api/login'}")
    res = s.post(BASE_URL + "/api/login",
                 json={"email": email, "password": password}, headers={"Referer": BASE_URL + "/login"}) # it works even without Refer

    try:
        data = res.json()
        token = data['token']
        files_token = data['filesToken']
    except Exception as e:
        print("Failed authentication")
        print(f"{res.text = }")
        raise e

    return token, files_token

def get_challenges():
    res = s.get(BASE_URL + "/api/challenges")
    
    data = res.json()
    game_paused = data["gamePause"]["paused"]
    events = data["events"]

    return game_paused, events

def get_challenge(challenge_id):
    res = s.get(f"{BASE_URL}/api/challenges/{challenge_id}")

    # Example:
    # {"id":55,"title":"CR_1.04 - Secure Padding","description":"Passwords should be at least 32 characters long!\nGive us your password, we'll think about it!\n\nThis is a remote challenge, you can connect to the service with:\nnc padding.challs.cyberchallenge.it 9030","files":[{"name":"challenge.py","url":"/api/file/84da89cd-702b-4a2d-a975-ebcaa88e7ca7/challenge.py?download"}],"hints":[{"id":55,"title":"Hint 1","price":50}],"tags":["crypto"],"currentScore":373,"currentAffiliationSolves":4,"currentGlobalSolves":219,"status":{"ok":true,"lastChecked":1688487096794},"solves":[{"playerId":856,"displayedName":"no","timestamp":"2023-05-08T11:36:05.591Z"},{"playerId":853,"displayedName":"Frollo","timestamp":"2023-05-09T19:19:20.348Z"},{"playerId":687,"displayedName":"Giovanni Piccirillo","timestamp":"2023-05-11T13:05:57.097Z"},{"playerId":615,"displayedName":"Christian Marescalco","timestamp":"2023-05-26T15:03:11.390Z"}]}

    return res.json()

def parse_event(event):
    event_id = event["id"]
    name = event["name"]
    sections = event["sections"]
    
    return event_id, name, sections

def parse_section(section):
    section_id = section["id"]
    name = section["name"]
    challenges = section["challenges"]
    
    return section_id, name, challenges

def parse_partial_challenge(challenge):
    challenge_id = challenge["id"]
    title = challenge["title"]
    tags = challenge["tags"]
    current_score = challenge["currentScore"]
    current_affiliation_solves = challenge["currentAffiliationSolves"]
    current_global_solves = challenge["currentGlobalSolves"]
    hidden = challenge["hidden"]
    
    return challenge_id, name, title, tags, current_score, current_affiliation_solves, current_global_solves, hidden


def parse_challenge(challenge):
    challenge_id = challenge["id"]
    name = challenge["name"]
    title = challenge["title"]
    description = challenge["description"]
    files = challenge["files"]
    hints = challenge["hints"]
    tags = challenge["tags"]
    current_score = challenge["currentScore"]
    current_affiliation_solves = challenge["currentAffiliationSolves"]
    current_global_solves = challenge["currentGlobalSolves"]
    solves = challenge["solves"]
    
    return challenge_id, name, title, description, files, hints, tags, current_score, current_affiliation_solves, current_global_solves, solves
    

def scrape_challenge(partial_challenge):
    challenge_id, name, title, tags, current_score, current_affiliation_solves, current_global_solves, hidden = parse_partial_challenge(partial_challenge)

    challenge = get_challenge(challenge_id)
    challenge_id, name, title, description, files, hints, tags, current_score, current_affiliation_solves, current_global_solves, solves = parse_challenge(challenge)

    

def main():
    args = get_args()
    email, password = get_auth_details(args)
    selected_events = args.events
    selected_events = "*" # TEMP

    if selected_events != "*":
        events = [event for event in events if event in selected_events]
    
    token, files_token = login(email, password)
    s.headers["authorization"] = f"Token {token}"

    game_paused, events = get_challenges()
    
    for event in events:
        event_id, name, sections = parse_event(event)

        for section in sections:
            section_id, name, challenges = parse_section(section)

            for challenge in challenges:
                scrape_challenge(challenge)


if __name__ == '__main__':
    main()
