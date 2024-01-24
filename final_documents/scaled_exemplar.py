import json

# Load data from the JSON file
with open('initial_data_1cat copy 2.json', 'r') as file:
    data = json.load(file)

# Define the new value to associate with the exemplars
new_value = 0

# Iterate through each word and update exemplars
for word, info in data["Category"]["words"].items():
    exemplar_values = info["exemplars"]
    exemplars_dict = {exemplar: new_value for exemplar in exemplar_values}
    info["exemplars"] = exemplars_dict

# Save the updated data back to the JSON file
with open('initial_data_1cat copy 2.json', 'w') as file:
    json.dump(data, file, indent=4)