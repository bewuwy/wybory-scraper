import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Read configuration from environment variables
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GIST_ID = os.getenv('GIST_ID')

NUM_PEOPLE_ALLOWED_TO_VOTE = 29252340

def upload(data, filename):
    # Prepare the update payload
    payload = {
        "files": {
            filename: {
                "content": data
            }
        }
    }

    # Headers for GitHub API
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }

    # Send PATCH request to update the Gist
    response = requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print("Gist updated successfully.")
        print("Gist URL:", response.json()["html_url"])
        print("Raw URL:", response.json()["files"][filename]["raw_url"])
    else:
        print("Failed to update the Gist.")
        print(response.status_code, response.text)


def create_json_data(elections_data: dict, percentage_powiats: float) -> dict:
    # reformat the data to match this structure:
    
    # {
    #   "candidates": [
    #     {
    #       "candidate_name": "Rafał Trzaskowski",
    #       "votes": 9249741,
    #       "percentage": 45.9
    #     },
    #     {
    #       "candidate_name": "Karol Nawrocki",
    #       "votes": 9282700,
    #       "percentage": 54.1
    #     }
    #   ],
    #   "stats": {
    #     "total_votes": 18532441,
    #     "turnout": 74.38,
    #     "precincts_reporting": 100.0,
    #     "time": "12:12"
    #   }
    # }

    candidates = []
    total_votes = 0
    for candidate, votes in elections_data.items():
        candidates.append({
            "candidate_name": candidate,
            "votes": votes,
            "percentage": round((votes / sum(elections_data.values())) * 100, 1)
        })
        total_votes += votes
    stats = {
        "total_votes": total_votes,
        "turnout":  round((total_votes / NUM_PEOPLE_ALLOWED_TO_VOTE) * 100, 2),
        "precincts_reporting": round(percentage_powiats, 1),
        "time": datetime.today().strftime('%d.%m %H:%M')  # Current time
    }
    
    return {
        "candidates": candidates,
        "stats": stats
    }


voivedship_to_code = {
    "wielkopolskie": "WP",
    "kujawsko-pomorskie": "KP",
    "małopolskie": "MA",
    "łódzkie": "LD",
    "dolnośląskie": "DS",
    "lubuskie": "LB",
    "lubelskie": "LU",
    "mazowieckie": "MZ",
    "opolskie": "OP",
    "podlaskie": "PD",
    "pomorskie": "PM",
    "śląskie": "SL",
    "podkarpackie": "PK",
    "świętokrzyskie": "SK",
    "warmińsko-mazurskie": "WN",
    "zachodniopomorskie": "ZP",
    "zagranica": "ZG",
    "statki": "ST"
}

max_powiaty = {
    "mazowieckie": 42,
    "pomorskie": 20,
    "wielkopolskie": 35,
    "dolnośląskie": 30,
    "małopolskie": 22,
    "lubelskie": 24,
    "łódzkie": 24,
    "podlaskie": 17,
    "zachodniopomorskie": 21,
    "kujawsko-pomorskie": 23,
    "śląskie": 36,
    "podkarpackie": 25,
    "warmińsko-mazurskie": 21,
    "lubuskie": 14,
    "opolskie": 12,
    "świętokrzyskie": 14,
    "zagranica": 1,
    "statki": 1
}

def create_csv_data(voivodeships_data):
    # Create CSV in this format:
    # region	RT	KN	certainty	name
    # WP	1	16	0.1	Wielkopolskie
    # KP	2	15	0.2	Kujawsko-pomorskie
    # MA	3	14	0.3	Małopolskie
    # LD	4	13	0.4	Łódzkie
    # DS	5	12	0.5	Dolnośląskie
    # LB	6	11	0.6	Lubuskie
    # LU	7	10	0.7	Lubelskie
    # MZ	8	9	0.8	Mazowieckie
    # OP	9	8	0.9	Opolskie
    # PD	10	7	1	Podlaskie
    # PM	11	6	0.25	Pomorskie
    # SL	12	5	0.35	Śląskie
    # PK	13	4	0.45	Podkarpackie
    # SK	14	3	0.55	Świetokrzyskie
    # WN	15	2	0.65	Warmińsko-mazurskie
    # ZP	16	1	0.75	Zachodniopomorskie

    csv_data = "region\tRT\tKN\tcertainty\tname\n"
    # certainty is the percentage of precincts reporting in the region
    
    for region, data in voivodeships_data.items():
        
        if region not in voivedship_to_code:
            continue
        
        rt_votes = data["Rafał Trzaskowski"]
        kn_votes = data["Karol Nawrocki"]
        certainty = data["powiaty_reporting"] / max_powiaty[region] if region in max_powiaty else 0

        csv_data += f"{ voivedship_to_code[region] }\t{rt_votes}\t{kn_votes}\t{certainty}\t{region.capitalize()}\n"
        
    return csv_data.strip()
