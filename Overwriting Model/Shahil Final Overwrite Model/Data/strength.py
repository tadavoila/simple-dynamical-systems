import json
import random



def process_data(json_file_name):
    # Read the existing data
    with open(json_file_name, 'r') as file:
        json_file = json.load(file)

    for i in range(20000):
        for word in json_file['Category']['words'].values():
            exemplars = word['exemplars']
            for key in exemplars:
                exemplars[key] = [value * (1-(1/492)) for value in exemplars[key]]
                    

        # Create a dictionary to store word frequencies
        word_frequencies = {}

        # Extract word frequencies from the data
        for word_key, word_value in json_file['Category']['words'].items():
            frequency = word_value["frequency"]
            word_frequencies[word_key] = frequency

        # Calculate the total frequency
        total_frequency = sum(word_frequencies.values())

        # Choose a random word and exemplar
        '''random_word_key = random.choices(list(json_file['Category']['words'].keys()), weights=[w_value['frequency'] / total_frequency for w_value in json_file['Category']['words'].values()])[0]
        random_word_value = json_file['Category']['words'][random_word_key]
        random_exemplar_key = random.choice(list(random_word_value['exemplars'].keys()))'''

        random_word_key = random.choices(list(json_file['Category']['words'].keys()), weights=[w_value['frequency'] / total_frequency for w_value in json_file['Category']['words'].values()])[0]
        random_word_value = json_file['Category']['words'][random_word_key]

        # Extract keys and corresponding weights
        keys, weights = zip(*[(k, len(v)) for k, v in random_word_value['exemplars'].items()])

        # Choose a key based on weights
        random_exemplar_key = (random.choices(keys, weights=weights)[0])
        


        #random_word_value['exemplars'][random_exemplar_key].append(1)
        if random_exemplar_key in random_word_value['exemplars']:
            random_word_value['exemplars'][random_exemplar_key].append(1)
        else:
            print(f"Key {random_exemplar_key} not found in exemplars")


        #Clean up step to remove any values that are smaller than (1 - (1 / 492))**11318
        for word in json_file['Category']['words'].values():
            exemplars = word['exemplars']
            for key in exemplars:
                exemplars[key] = [value for value in exemplars[key] if value > ((1 - (1 / 492))**11318)]

    # Save the modified data
    with open('initial_data_1cat copy 2.json', 'w') as json_data:
        json.dump(json_file, json_data, indent=4)

process_data('initial_data_1cat copy 2.json')

