import json
import toml
with open('first-user-study-0ec01ef3e1ce.json', 'r') as json_file:
    json_data = json.load(json_file)

# Convert JSON to TOML
toml_data = toml.dumps(json_data)

# Write TOML data to file
with open('secrets.toml', 'w') as toml_file:
    toml_file.write(toml_data)