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
FILENAME = os.getenv('FILENAME', 'elections.json')  # Default to 'data.json' if not set


def upload(json_data):
    # Prepare the update payload
    payload = {
        "files": {
            FILENAME: {
                "content": json_data
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
        print("Raw URL:", response.json()["files"][FILENAME]["raw_url"])
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
        "turnout": 0,
        "precincts_reporting": percentage_powiats,
        "time": datetime.today().strftime('%d.%m %H:%M')  # Current time
    }
    
    return {
        "candidates": candidates,
        "stats": stats
    }
