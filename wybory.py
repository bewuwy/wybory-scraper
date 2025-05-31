import analyze
import scraper
from os.path import exists
from os import makedirs
import json
from datetime import datetime


def process_powiat(powiat_id, woj_name):
    url_powiat = scraper.get_powiat_results_url(powiat_id)
    raw_data_dir = f"data/{time}/raw/{woj_name}"
    votes_data_dir = f"data/{time}/votes/{woj_name}"
    if not exists(votes_data_dir):
        makedirs(votes_data_dir)
    if not exists(raw_data_dir):
        makedirs(raw_data_dir)
    
    filename_powiat = f"{raw_data_dir}/wybory_data_{woj_name}_{powiat_id}"
    
    # try:
    data_powiat = scraper.get_protobuf_message(url=url_powiat, save_file=filename_powiat)
    votes = analyze.get_votes(data_powiat)

    print(f"Województwo: {woj_name}, Powiat: {powiat_id}")
    for candidate, num_votes in votes.items():
        if candidate in ["Rafał Trzaskowski", "Karol Nawrocki"]:
            total_votes_woj[woj_name][candidate] += num_votes
            print(f"{candidate}: {num_votes:,} votes")
    print()
    
    #  Save the votes data to a file
    votes_filename = f"{votes_data_dir}/votes_{woj_name}_{powiat_id}.json"
    with open(votes_filename, "w", encoding="utf-8") as f:
        json.dump(votes, f, ensure_ascii=False, indent=4)
        
    # except scraper.NotFoundError as e:
    #     print(f"NotFoundError (powiat {powiat_id} in {woj_name}): {e}")
    #     break
        
    # except Exception as e:
    #     print(f"Error processing {url_powiat}: {e}")
    #     continue


if __name__ == "__main__":
    num_powiats = 0
    time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    
    total_votes_woj = {}
    
    for woj_name, woj_id in scraper.WOJ_ID.items():
        
        msg = scraper.get_protobuf_message(url=scraper.get_results_url(woj=woj_id))
        powiat_ids = analyze.get_powiaty(msg)
        
        total_votes_woj[woj_name] = {
            "Rafał Trzaskowski": 0,
            "Karol Nawrocki": 0
        }
        
        for powiat_id in powiat_ids:
            process_powiat(powiat_id, woj_name)
            num_powiats += 1
    
    for woj_name, powiat_id in scraper.SPECIAL_POWIATY:
        total_votes_woj[woj_name] = {
            "Rafał Trzaskowski": 0,
            "Karol Nawrocki": 0
        }
        process_powiat(powiat_id, woj_name)
        num_powiats += 1

    print(f"\nProcessed {num_powiats} (out of 382) powiatów successfully.")
    
    # Calculate total votes across all województwa
    total_votes = {
        "Rafał Trzaskowski": 0,
        "Karol Nawrocki": 0
    }
    for woj_name, votes in total_votes_woj.items():
        for candidate, num_votes in votes.items():
            total_votes[candidate] += num_votes
    
    print("\n\nTotal Votes:")
    for candidate, num_votes in total_votes.items():
        print(f"{candidate}: {num_votes:,} votes")
        print(f"({num_votes / sum(total_votes.values()):.2%})")
        print()

    # save total votes to a file
    total_votes_filename = f"data/{time}/total/votes.json"
    if not exists(f"data/{time}/total"):
        makedirs(f"data/{time}/total")
        
    # Save total votes by województwo
    total_votes_woj_filename = f"data/{time}/total/votes_by_woj.json"
    with open(total_votes_woj_filename, "w", encoding="utf-8") as f:
        json.dump(total_votes_woj, f, ensure_ascii=False, indent=4)
    
    # Save total votes
    with open(total_votes_filename, "w", encoding="utf-8") as f:
        json.dump(total_votes, f, ensure_ascii=False, indent=4)
        
    # upload to gist
    from gist import upload, create_json_data
    gist_data = create_json_data(total_votes, num_powiats/382 * 100)
    upload(json.dumps(gist_data, ensure_ascii=False, indent=4))
