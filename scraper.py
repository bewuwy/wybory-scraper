import requests
from typing import Dict
import blackboxprotobuf
import json

WYBORY_ID_WOJ: int = 1747645331
WYBORY_ID_POW: int = 1748025312

RESULTS_URL: str = "https://wybory.gov.pl/prezydent2025/data/obkw/pl_po_woj.1747645331.blob"

WOJ_ID: Dict[str, int] = {
    "mazowieckie": 14,
    "pomorskie": 22,
    "wielkopolskie": 30,
    "dolnośląskie": 2,
    "małopolskie": 12,
    "lubelskie": 6,
    "łódzkie": 10,
    "podlaskie": 20,
    "zachodniopomorskie": 32,
    "kujawsko-pomorskie": 4,
    "śląskie": 24,
    "podkarpackie": 18,
    "warmińsko-mazurskie": 28,
    "lubuskie": 8,
    "opolskie": 16,
    "świętokrzyskie": 26,
}

SPECIAL_POWIATY = [
    ('zagranica', 149900),
    ('statki', 149800)
]

class NotFoundError(Exception):
    """Custom exception for not found errors."""
    pass


def get_results_url(woj: int = None, powiat: int = None, gmina: int = None, komisja: int = None) -> str:
    """
    Get the results URL for the specified administrative level.
    Level is automatically determined by the arguments passed.
    """
    if komisja is not None:
        return f"https://wybory.gov.pl/prezydent2025/data/obkw/kw/{komisja}.{WYBORY_ID_POW}.blob"
    elif gmina is not None:
        if woj is None or powiat is None:
            raise ValueError("woj and powiat must be provided when gmina is specified")
        return f"https://wybory.gov.pl/prezydent2025/data/obkw/gm/{woj}{powiat:02d}{gmina:02d}.{WYBORY_ID_POW}.blob"
    elif powiat is not None:
        if woj is None:
            raise ValueError("woj must be provided when powiat is specified")
        return f"https://wybory.gov.pl/prezydent2025/data/obkw/pow/{woj}{powiat:02d}00.{WYBORY_ID_POW}.blob"
    elif woj is not None:
        return f"https://wybory.gov.pl/prezydent2025/data/obkw/woj/{woj}0000.{WYBORY_ID_WOJ}.blob"
    else:
        return RESULTS_URL


def get_powiat_results_url(powiat_id: int) -> str:
    return f"https://wybory.gov.pl/prezydent2025/data/obkw/pow/{powiat_id}.{WYBORY_ID_POW}.blob"


def decode_bytes_recursively(obj):
    if isinstance(obj, bytes):
        # # Try to interpret bytes as different numeric types
        # if len(obj) == 4:
        #     # Try as 32-bit integer (little endian)
        #     try:
        #         return int.from_bytes(obj, byteorder='little', signed=False)
        #     except:
        #         pass
        # elif len(obj) == 8:
        #     # Try as 64-bit integer (little endian)
        #     try:
        #         return int.from_bytes(obj, byteorder='little', signed=False)
        #     except:
        #         pass
        # Fallback to string decode
        return obj.decode('utf-8', errors='ignore')
    elif isinstance(obj, dict):
        return {key: decode_bytes_recursively(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [decode_bytes_recursively(item) for item in obj]
    else:
        return obj


def get_protobuf_message(url=RESULTS_URL, save_file="wybory_data") -> Dict:
    """
    Fetches the Protobuf message from the specified URL and saves it to a file.
    """

    r = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    })

    if r.status_code != 200:
        print("Status code:", r.status_code)
        
        if (r.status_code == 404):
            raise NotFoundError(f"Data not found at {url}.")
        
        raise Exception(f"Failed to fetch data from {url}")

    # save the raw content to a file
    with open(f"{save_file}.blob", "wb") as f:
        f.write(r.content)

    # decode the Protobuf message
    message, typedef = blackboxprotobuf.decode_message(r.content)

    # recursively convert all bytes in the message to strings
    decoded_message = decode_bytes_recursively(message)

    # save the decoded message to a file
    with open(f"{save_file}.json", "w") as f:
        json.dump(decoded_message, f, indent=2, ensure_ascii=False)
    
    return decoded_message
