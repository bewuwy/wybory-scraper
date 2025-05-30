from typing import Dict, Any, List
import json

CANDIDATE_ID: Dict[int, str] = {
    103222: "Rafał Trzaskowski",
    103306: "Karol Nawrocki",
    103220: "Memcen",
    103228: "braun",
    103242: "Szymon Hołownia",
    103246: "Adrian Zandberg",
    103274: "Magdalena Biejat"
}


def get_votes(data: Dict[str, Any]) -> Dict[str, int]:
    """
    Extracts the votes from the provided data structure.
    
    :param data: The Protobuf message structure containing election results.
    :return: A dictionary mapping candidate names to their vote counts.
    """
    votes = {}
    votes_raw = data["4"]["16"]["3"]["28"]
    
    for result in votes_raw:
        num_votes = 0
        if "3" in result:  # else the candidate did not receive any votes
            num_votes = result["3"] // 2 
        id = result["8"]
        
        if id in CANDIDATE_ID:
            id = CANDIDATE_ID[id]
        else:
            id = f"Unknown (ID {id})"
        
        votes[id] = num_votes

    return votes


def get_wojewodztwo_name(data: Dict[str, Any]) -> str:
    """
    Extracts the name of the województwo (province) from the data.

    :param data: The Protobuf message structure containing election results.
    :return: The name of the województwo.
    """
    return data["1"]["2"]
    # return data["3"][0]["1"]["2"]


def get_powiaty(data: Dict[str, Any]) -> List[int]:
    """
    Extracts the powiaty (districts) from the data.

    :param data: The Protobuf message structure containing election results.
    :return: A list of powiat IDs.
    """
    powiaty = []
    for powiat in data["3"]:
        id = powiat["1"]["3"] // 2
        powiaty.append(id)
    return powiaty


if __name__ == "__main__":
    
    with open("wybory_data.json", "r", encoding="utf-8") as f:
        data: Dict[str, Any] = json.load(f)
        
    print("Election Results Analysis\n")
        
    votes = get_votes(data)
    results = sorted(votes.items(), key=lambda x: x[1], reverse=True)
    total_votes = sum(votes.values())
    
    for id, num_votes in results:
        print(id, end=": ")
        print(f"{total_votes:,} votes", end=" ")
        print(f"({num_votes / total_votes:.2%})")
    
    print(f"\nTotal votes: {total_votes:,}")
