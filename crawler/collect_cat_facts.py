import os
import requests
import argparse
import pandas as pd

BASE_URL = "https://cat-fact.herokuapp.com"
ENDPOINTS = {"all": "/facts", "random": "/facts/random"}
ANIMALS = ["cat", "dog", "snail", "horse"]
FILE_PATH = "crawler/cat_facts.csv"


def is_animal_valid(animal_type):
    return animal_type not in ANIMALS


def get_random_facts(animal_type="cat", amount=1):
    animal_type = animal_type.lower()
    if not is_animal_valid:
        print(f"The animal type '{animal_type}' is not accepted by the API.")
        return
    else:
        r = requests.get(
            url=f"{BASE_URL}{ENDPOINTS['random']}?animal_type={animal_type}&amount={amount}"
        )
        if r.status_code != 200:
            error_message = r.json().get("message", "No error message provided")
            raise requests.RequestException(
                f"API request failed with status code {r.status_code}: {error_message}"
            )

        fact = r.json()
        if isinstance(fact, dict):
            fact = [r.json()]
    return fact


def get_facts():
    r = requests.get(url=f"{BASE_URL}{ENDPOINTS['all']}")
    if r.status_code != 200:
        error_message = r.json().get("message", "No error message provided")
        raise requests.RequestException(
            f"API request failed with status code {r.status_code}: {error_message}"
        )

    facts = r.json()
    return facts


def save_file(facts, append):
    df = pd.DataFrame(facts)
    df = df.drop("used", axis=1) # delete column "used" to match the api's fact model
    if append:
        if os.path.exists(FILE_PATH):
            existing_df = pd.read_csv(FILE_PATH)
            combined_df = pd.concat([existing_df, df]).drop_duplicates(
                subset=["_id"], keep="first"
            )
            combined_df.to_csv(FILE_PATH, index=False)
            return
    df.to_csv(FILE_PATH, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch facts from the Cat Facts API.")
    parser.add_argument("--random", action="store_true", help="Fetch random facts.")
    parser.add_argument(
        "--type",
        type=str,
        default="cat",
        help="Type of animal for random fact (default is 'cat').",
    )
    parser.add_argument(
        "--amount",
        type=int,
        default=1,
        help="Number of random facts to fetch (default is 1).",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to csv file if exists (default will overwrite the file)",
    )
    args = parser.parse_args()

    try:
        if args.random:
            facts = get_random_facts(args.type, args.amount)
        else:
            facts = get_facts()

        if facts:
            save_file(facts, args.append)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
