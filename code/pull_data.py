from typing import TypedDict, Literal
from dataclasses import dataclass

import requests
import json
import pandas as pd


with open("../code/config.json", "r") as j:
    config = json.load(j)

base_api = config["API"]["base_api"]
league = config["API"]["league"]
URL = base_api.format(category="currency", league=league, type="Currency")


def pull_currency_data(url):
    """
    Function to pull currency data from poe.ninja API
    """
    try:
        r = requests.get(url=url)
        return r.json()
    
    except Exception as e:
        print(f"Error: {e}")
        return {}
    

def extract_data(currency_raw):
    """
    Function to extract chaos equivalent value for each currency type
    """
    final_data = []

    for currency in currency_raw["lines"]:
        currency_data = {
            "currency_type": currency["currencyTypeName"],
            "chaos_eq": currency["chaosEquivalent"]
        }

        try:
            currency_data["chaos_sell"] = round(1 / currency["pay"]["value"], 4)
        except:
            currency_data["chaos_sell"] = None

        try:
            currency_data["chaos_buy"] = round(currency["receive"]["value"], 4)
        except:
            currency_data["chaos_buy"] = None

        final_data.append(currency_data)

    return pd.DataFrame(final_data)


def main():
    currency_raw = pull_currency_data(URL)
    final_data = extract_data(currency_raw)

    final_data.to_csv("../data/final_data.csv", index=False)


if __name__ == "__main__":
    main()