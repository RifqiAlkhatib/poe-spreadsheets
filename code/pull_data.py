import json

with open("config.json", "r") as j:
    config = json.load(j)

print(config['league'])