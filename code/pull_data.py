from dataclasses import dataclass, field
from typing import Dict

import requests
import json
import pandas as pd


with open("../code/config.json", "r") as j:
    config = json.load(j)


@dataclass(kw_only=True)
class PoeNinja:
    category: str
    base_api: str = config["API"]["base_api"]
    league: str = config["API"]["league"]
    api_group: str = field(init=False)
    api_category: str = field(init=False)
    _url: str = field(init=False)

    
    def __post_init__(self) -> None:
        self.api_group = config["API"][self.category]["group"]
        self.api_category = config["API"][self.category]["category"]
        self._url = self.base_api.format(
            group=self.api_group, league=self.league, category=self.api_category
        )
    

    def _extract_data(self, raw_data: Dict[str, list]) -> pd.DataFrame:
        final_data = []

        if self.api_group == "currency":
            name_key = "currencyTypeName"
            value_key = "chaosEquivalent"

        elif self.api_group == "item":
            name_key = "name"
            value_key = "chaosValue"
        
        else:
            raise ValueError("API `group` can only be 'currency' or 'item'")

        for item in raw_data["lines"]:
            item_data = {
                "name": item[name_key],
                "chaos_value": item[value_key]
            }

            if self.api_group == "currency":
                item_data["chaos_sell"] = item.get("pay", {}).get("value")
                item_data["chaos_buy"] = item.get("receive", {}).get("value")
                
            final_data.append(item_data)
        
        final_df = pd.DataFrame(final_data)

        if self.api_group == "currency":
            final_df['chaos_sell'] = 1 / final_df['chaos_sell']

        return round(final_df, 4)


    def pull_data(self) -> pd.DataFrame:
        try:
            r = requests.get(url=self._url)
            return self._extract_data(r.json())
        
        except Exception as e:
            print(f"Error: {e}")
            return pd.DataFrame()


def main():    
    currency = PoeNinja(category="currency")
    final_data = currency.pull_data()

    final_data.to_csv("../data/_final_data.csv", index=False)


if __name__ == "__main__":
    main()